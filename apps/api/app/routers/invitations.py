import secrets
import uuid
from datetime import datetime, timezone
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.aspects import angle_between, aspect_sentence, classify_aspect
from app.astro import approximate_longitude_for_sign
from app.public_profile import sun_sign
from app.config import settings
from app.auth import is_active, require_self, session_profile_id
from app.database import get_db
from app.icebreaker import IcebreakerGenerator, get_icebreaker_generator
from app.ai_texts import record
from app.models import ChatMessage, Invitation, InvitationAcceptance, Match, PersonalityAnswers, Profile
from app.personality.engine import completed, load_config
from app.synastry import ai_facts, headline, profile_synastry
from app.schemas import (
    InvitationAcceptOut,
    InvitationIn,
    InvitationOut,
    InvitationPreviewOut,
    InvitationPreloadOut,
    MyInvitationOut,
    PartialReportOut,
    RevealOut,
)

router = APIRouter(prefix="/invitations", tags=["invitations"])

# Gancho de Destiny (VISION.md, spec C8 v3): va después del saludo en los dos mensajes.
HOOK = "¿Por qué con algunas personas fluye y con otras no?"
TEST_LINE = "Ya completé mi test de personalidad"


def _get_profile(profile_id: uuid.UUID, db: Session) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


def _test_complete(db: Session, profile_id: uuid.UUID) -> bool:
    mine = db.get(PersonalityAnswers, profile_id)
    return completed(mine.answers if mine else {}) == len(load_config()["questions"])


def _sun_aspect(inviter: Profile, friend_sun_sign: str | None) -> dict | None:
    """Adelanto por signo, aproximado (del amigo solo tenemos el signo solar). Spec C12: si es flojo
    (los soles no forman un aspecto mayor) no sirve de gancho y no se muestra."""
    if not friend_sun_sign:
        return None
    # Signo con signo (los dos en su punto medio): comparar el Sol exacto con el medio del signo del
    # amigo dejaba sin aspecto mayor a quien tiene el Sol cerca del borde de un signo.
    mine = approximate_longitude_for_sign(sun_sign(inviter))
    aspect = classify_aspect(angle_between(mine, approximate_longitude_for_sign(friend_sun_sign)))
    return aspect if aspect["is_major"] else None


def _message(inviter: Profile, payload: InvitationIn, with_test: bool, link: str) -> str:
    """Spec C12: el mensaje se arma solo con lo que haya (signo del amigo, mi test completo)."""
    parts = [f"¡Hola {payload.friend_name}! {HOOK}"]
    if aspect := _sun_aspect(inviter, payload.friend_sun_sign):
        sentence = aspect_sentence(aspect["aspect"]).replace("sus soles", "nuestros soles")
        parts.append(f"Con tu signo ({payload.friend_sun_sign}) y mi carta, parece que {sentence}.")
    if with_test:
        parts.append(f"{TEST_LINE}: hacelo vos y comparamos.")
    parts.append(f"Descubrilo en Destiny ✨ {link}")
    return " ".join(parts)


def _inviter_for(payload: InvitationIn, db: Session, current: uuid.UUID | None) -> Profile:
    require_self(payload.inviter_id, current)
    inviter = _get_profile(payload.inviter_id, db)
    if inviter.birth_date is None:
        raise HTTPException(status_code=422, detail="Completá tu carta natal antes de invitar")
    return inviter


@router.post("/preview", response_model=InvitationPreviewOut)
def preview_invitation(
    payload: InvitationIn, db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> InvitationPreviewOut:
    """Spec C12: el mensaje en vivo mientras se completa el formulario; no crea nada."""
    inviter = _inviter_for(payload, db, current)
    return InvitationPreviewOut(message=_message(inviter, payload, _test_complete(db, inviter.id), "[link]"))


@router.post("", response_model=InvitationOut, status_code=201)
def create_invitation(
    payload: InvitationIn, db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> InvitationOut:
    inviter = _inviter_for(payload, db, current)
    with_test = _test_complete(db, inviter.id)
    ref_id = secrets.token_urlsafe(6)
    link = f"{settings.web_base_url}/onboarding/invitacion?ref={ref_id}"
    kind = "test" if with_test else "astro"
    db.add(
        Invitation(
            ref_id=ref_id,
            inviter_profile_id=inviter.id,
            friend_name=payload.friend_name,
            friend_sun_sign=payload.friend_sun_sign,
            kind=kind,
            relationship=inviter.looking_for or "pareja",
        )
    )
    db.commit()

    partial_report = None
    if aspect := _sun_aspect(inviter, payload.friend_sun_sign):
        partial_report = PartialReportOut(
            teaser=(
                f"Con el sol en {payload.friend_sun_sign}, {payload.friend_name} podría tener esta "
                f"conexión con vos: {aspect_sentence(aspect['aspect'])}. Para ver la resonancia real (y revelarla para los "
                "dos) necesitamos que complete su carta natal."
            ),
            locked_fields=["hora_de_nacimiento", "ascendente", "compatibilidad_exacta"],
        )
    # El mensaje lo manda quien invita desde su WhatsApp: le habla al amigo en primera persona.
    message = _message(inviter, payload, with_test, link)
    return InvitationOut(
        ref_id=ref_id,
        kind=kind,
        message=message,
        whatsapp_url=f"https://wa.me/?text={quote(message)}",
        partial_report=partial_report,
    )


@router.get("/mine", response_model=list[MyInvitationOut])
def my_invitations(
    profile_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> list[MyInvitationOut]:
    """Mis invitaciones con su estado (C8 v2): enviada → registrado → test_completo."""
    require_self(profile_id, current)
    invitations = db.scalars(
        select(Invitation).where(Invitation.inviter_profile_id == profile_id).order_by(Invitation.created_at.desc())
    ).all()
    total_questions = len(load_config()["questions"])
    out = []
    for inv in invitations:
        status, match_id = "enviada", None
        if inv.invitee_profile_id:
            status = "registrado"
            match_id = _match_between(db, inv.inviter_profile_id, inv.invitee_profile_id)
            theirs = db.get(PersonalityAnswers, inv.invitee_profile_id)
            if completed(theirs.answers if theirs else {}) == total_questions:
                status = "test_completo"
        out.append(
            MyInvitationOut(
                ref_id=inv.ref_id,
                friend_name=inv.friend_name,
                kind=inv.kind,
                relationship=inv.relationship,
                status=status,
                match_id=match_id,
                created_at=inv.created_at,
                aceptaron=db.scalar(
                    select(func.count()).select_from(InvitationAcceptance).where(InvitationAcceptance.ref_id == inv.ref_id)
                ),
            )
        )
    return out


def _match_between(db: Session, a: uuid.UUID, b: uuid.UUID) -> uuid.UUID | None:
    match = db.scalars(
        select(Match).where(
            or_(
                and_(Match.profile_a_id == a, Match.profile_b_id == b),
                and_(Match.profile_a_id == b, Match.profile_b_id == a),
            )
        )
    ).first()
    return match.id if match else None


@router.post("/{ref_id}/accept", response_model=InvitationAcceptOut)
def accept_invitation(
    ref_id: str,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
    generator: IcebreakerGenerator = Depends(get_icebreaker_generator),
) -> InvitationAcceptOut:
    """El invitado (ya verificado, con sesión) queda conectado con quien lo invitó (C8 v2). Idempotente."""
    if current is None:
        raise HTTPException(status_code=401, detail="Necesitás iniciar sesión")
    invitation = db.get(Invitation, ref_id)
    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitation not found")
    if invitation.inviter_profile_id == current:
        raise HTTPException(status_code=409, detail="No podés aceptar tu propia invitación")
    # Spec C13: el mismo link sirve para varias personas (se reenvía o se manda a un grupo).

    inviter = _get_profile(invitation.inviter_profile_id, db)
    invitee = _get_profile(current, db)
    if not is_active(invitee):  # spec A10: alcanza con una cuenta activa
        raise HTTPException(status_code=403, detail="Terminá tu registro antes de aceptar")

    match_id = _match_between(db, inviter.id, invitee.id)
    if match_id is None:
        match = Match(
            profile_a_id=inviter.id,
            profile_b_id=invitee.id,
            status="aceptada",
            accepted_at=datetime.now(timezone.utc),
            relationship=invitation.relationship or "pareja",
            source="invitacion",
        )
        db.add(match)
        db.flush()
        written = generator.generate(ai_facts(profile_synastry(inviter, invitee, match.relationship)))
        db.add(ChatMessage(match_id=match.id, sender="system_icebreaker", text=written.text))
        record(db, f"rompehielos:{match.id}", "rompehielos", written)
        match_id = match.id
    if invitation.invitee_profile_id is None:  # la primera persona (compatibilidad con C8)
        invitation.invitee_profile_id = invitee.id
        invitation.accepted_at = datetime.now(timezone.utc)
    # Spec R1: dos toques a la vez no dan error (ON CONFLICT DO NOTHING).
    db.execute(
        pg_insert(InvitationAcceptance)
        .values(ref_id=ref_id, invitee_profile_id=invitee.id)
        .on_conflict_do_nothing(index_elements=["ref_id", "invitee_profile_id"])
    )
    db.commit()
    return InvitationAcceptOut(match_id=match_id)


@router.get("/{ref_id}", response_model=InvitationPreloadOut)
def get_invitation(ref_id: str, db: Session = Depends(get_db)) -> InvitationPreloadOut:
    invitation = db.get(Invitation, ref_id)
    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitation not found")

    inviter = db.get(Profile, invitation.inviter_profile_id)
    name = inviter.display_name or "Alguien"
    # Spec C12: adelanto si hay signo, invitación al test si quien invita lo hizo, o un mensaje general.
    parts = []
    if aspect := _sun_aspect(inviter, invitation.friend_sun_sign):
        parts.append(f"Con tu signo, puede que {aspect_sentence(aspect['aspect'])}. Completá tu carta para la revelación real.")
    if invitation.kind == "test":
        parts.append(
            f"{name} completó su test de personalidad en Destiny y quiere ver qué tan compatibles son. "
            "Registrate, hacé el test (32 preguntas) y lo descubren juntos."
        )
    if not parts:
        parts.append(f"{name} te invitó a Destiny para descubrir cuánto fluyen. Registrate y lo ven juntos.")
    return InvitationPreloadOut(
        ref_id=ref_id,
        friend_name=invitation.friend_name,
        kind=invitation.kind,
        inviter_name=inviter.display_name,
        relationship=invitation.relationship,
        teaser=" ".join(parts),
    )


@router.get("/{ref_id}/reveal", response_model=RevealOut)
def reveal_invitation(
    ref_id: str, invitee_id: uuid.UUID, db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> RevealOut:
    require_self(invitee_id, current)
    invitation = db.get(Invitation, ref_id)
    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitation not found")

    inviter = _get_profile(invitation.inviter_profile_id, db)
    invitee = _get_profile(invitee_id, db)
    if invitee.birth_date is None:
        raise HTTPException(status_code=422, detail="El invitado necesita completar su carta natal")

    # Mismo motor que Descubrir (spec C8, corrección 2026-10-12), con el vínculo de la invitación.
    result = profile_synastry(inviter, invitee, invitation.relationship or "pareja")
    label = headline(result)
    text = (
        f"Resonancia real revelada entre {invitation.friend_name} y quien lo invitó: "
        f"{result['total']}% ({label.lower()})."
    )
    return RevealOut(aspect=label, percentage=result["total"], text=text)
