import uuid
from datetime import datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.astrochat.chat import is_crisis, load_config, suggested_mode, system_prompt
from app.auth import require_self, session_profile_id
from app.database import advisory_lock, get_db
from app.llm import converse
from app.models import AstroMessage, Invitation, InvitationAcceptance, PersonalityAnswers, Profile
from app.personalization.style import prompt_instructions, style_for
from app.schemas import AstroAnswerOut, AstroAskIn, AstrochatOut, AstroMessageOut, AstroModeOut

# Astrochat: preguntale a Destiny (spec X3).
router = APIRouter(tags=["astrochat"])


def _own(profile_id: uuid.UUID, current: uuid.UUID | None, db: Session) -> Profile:
    require_self(profile_id, current)
    profile = db.get(Profile, profile_id)
    if profile is None or profile.birth_date is None:
        raise HTTPException(status_code=409, detail="Perfil sin datos natales")
    return profile


def _used_today(db: Session, profile_id: uuid.UUID) -> int:
    """Preguntas que cuentan para el límite, hoy (UTC). Incluye las de conversaciones borradas."""
    start = datetime.combine(datetime.now(timezone.utc).date(), time(0), tzinfo=timezone.utc)
    return db.scalar(
        select(func.count()).select_from(AstroMessage).where(
            AstroMessage.profile_id == profile_id,
            AstroMessage.role == "persona",
            AstroMessage.counts.is_(True),
            AstroMessage.created_at >= start,
        )
    ) or 0


def _invite_bonus(db: Session, profile_id: uuid.UUID) -> int:
    """Spec C11: amigos distintos que crearon su perfil después de tu invitación y la aceptaron."""
    cfg = load_config()["invitados"]
    # Spec C13: cuenta a cada persona distinta que aceptó alguno de tus links.
    friends = db.scalar(
        select(func.count(func.distinct(InvitationAcceptance.invitee_profile_id)))
        .join(Invitation, Invitation.ref_id == InvitationAcceptance.ref_id)
        .join(Profile, Profile.id == InvitationAcceptance.invitee_profile_id)
        .where(Invitation.inviter_profile_id == profile_id, Profile.created_at > Invitation.created_at)
    )
    return min(friends * cfg["preguntas_por_invitado"], cfg["bonus_maximo"])


def _history(db: Session, profile_id: uuid.UUID, limit: int | None = None) -> list[AstroMessage]:
    query = (
        select(AstroMessage)
        .where(AstroMessage.profile_id == profile_id, AstroMessage.deleted_at.is_(None))
        .order_by(AstroMessage.created_at.desc())
    )
    if limit:
        query = query.limit(limit)
    return list(reversed(db.scalars(query).all()))


def _out(m: AstroMessage) -> AstroMessageOut:
    return AstroMessageOut(rol=m.role, texto=m.text, modo=m.mode, creado=m.created_at)


def _current_mode(profile: Profile) -> str:
    """El modo sale del estilo actual de la persona (se cambia en Tu estilo, no en el chat)."""
    return suggested_mode(style_for(profile))


@router.get("/profiles/{profile_id}/astrochat", response_model=AstrochatOut)
def get_astrochat(
    profile_id: uuid.UUID, db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> AstrochatOut:
    profile = _own(profile_id, current, db)
    cfg = load_config()
    bonus = _invite_bonus(db, profile_id)
    return AstrochatOut(
        modo=_current_mode(profile),
        modos=[AstroModeOut(clave=k, nombre=m["nombre"], descripcion=m["descripcion"]) for k, m in cfg["modos"].items()],
        mensajes=[_out(m) for m in _history(db, profile_id)],
        restantes_hoy=max(0, cfg["limite_diario"] + bonus - _used_today(db, profile_id)),
        limite=cfg["limite_diario"] + bonus,
        extra_por_invitados=bonus,
        ejemplos=cfg["ejemplos"],
    )


@router.post("/profiles/{profile_id}/astrochat", response_model=AstroAnswerOut)
def ask_astrochat(
    profile_id: uuid.UUID,
    payload: AstroAskIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> AstroAnswerOut:
    profile = _own(profile_id, current, db)
    cfg = load_config()
    text = payload.texto.strip()
    if not text or len(text) > cfg["max_entrada"]:
        raise HTTPException(status_code=422, detail=f"La pregunta tiene que tener entre 1 y {cfg['max_entrada']} caracteres")
    mode = payload.modo or _current_mode(profile)
    if mode not in cfg["modos"]:
        raise HTTPException(status_code=422, detail="Modo inexistente")
    # Spec R2: las preguntas de una persona se procesan de a una, así el límite no se pasa en paralelo.
    advisory_lock(db, f"astrochat:{profile_id}")
    used = _used_today(db, profile_id)
    limit = cfg["limite_diario"] + _invite_bonus(db, profile_id)
    now = datetime.now(timezone.utc)

    def save(question_counts: bool, answer: str, result=None) -> AstroMessage:
        db.add(AstroMessage(profile_id=profile_id, role="persona", text=text, mode=mode, counts=question_counts, created_at=now))
        reply = AstroMessage(
            profile_id=profile_id,
            role="destiny",
            text=answer,
            mode=mode,
            created_at=now + timedelta(milliseconds=1),
            model=result.model if result else None,
            prompt_tokens=result.prompt_tokens if result else None,
            completion_tokens=result.completion_tokens if result else None,
        )
        db.add(reply)
        db.commit()
        db.refresh(reply)
        return reply

    # Crisis: respuesta fija con dónde pedir ayuda, sin IA y sin contar para el límite.
    if is_crisis(text):
        reply = save(False, cfg["crisis"]["respuesta"])
        return AstroAnswerOut(respuesta=_out(reply), ia=False, restantes_hoy=max(0, limit - used))

    if used >= limit:
        raise HTTPException(status_code=429, detail=cfg["limite_alcanzado"])

    context = [
        {"role": "user" if m.role == "persona" else "assistant", "content": m.text}
        for m in _history(db, profile_id, cfg["mensajes_de_contexto"])
    ]
    test = db.get(PersonalityAnswers, profile_id)
    system = system_prompt(
        profile, mode, prompt_instructions(style_for(profile)), now.date(), test.answers if test else None, payload.dia
    )
    result = converse(
        system,
        [*context, {"role": "user", "content": text}],
        cfg["max_salida"],
        max_tokens=cfg["max_tokens"],
        timeout=cfg["timeout_segundos"],
    )
    reply = save(True, result.text if result else cfg["sin_ia"], result)
    return AstroAnswerOut(respuesta=_out(reply), ia=result is not None, restantes_hoy=max(0, limit - used - 1))


@router.delete("/profiles/{profile_id}/astrochat", status_code=204)
def delete_astrochat(
    profile_id: uuid.UUID, db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> Response:
    require_self(profile_id, current)
    now = datetime.now(timezone.utc)
    for m in _history(db, profile_id):
        m.deleted_at = now
    db.commit()
    return Response(status_code=204)
