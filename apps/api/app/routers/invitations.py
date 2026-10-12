import secrets
import uuid
from datetime import datetime, timezone
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.aspects import angle_between, aspect_sentence, classify_aspect
from app.astro import approximate_longitude_for_sign
from app.compatibility import compatibility_signals, sun_longitude
from app.config import settings
from app.auth import require_self, session_profile_id
from app.database import get_db
from app.icebreaker import IcebreakerGenerator, get_icebreaker_generator
from app.ai_texts import record
from app.models import ChatMessage, Invitation, Match, PersonalityAnswers, Profile
from app.personality.engine import completed, load_config
from app.synastry import ai_facts, profile_synastry
from app.schemas import (
    InvitationAcceptOut,
    InvitationIn,
    InvitationOut,
    InvitationPreloadOut,
    MyInvitationOut,
    PartialReportOut,
    RevealOut,
)

router = APIRouter(prefix="/invitations", tags=["invitations"])


def _get_profile(profile_id: uuid.UUID, db: Session) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("", response_model=InvitationOut, status_code=201)
def create_invitation(
    payload: InvitationIn, db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> InvitationOut:
    require_self(payload.inviter_id, current)
    inviter = _get_profile(payload.inviter_id, db)
    if inviter.birth_date is None:
        raise HTTPException(status_code=422, detail="Completá tu carta natal antes de invitar")

    ref_id = secrets.token_urlsafe(6)
    link = f"{settings.web_base_url}/onboarding/invitacion?ref={ref_id}"

    if payload.kind == "test":
        # C8 v2: comparar el test de personalidad. Solo con mi test completo (el mensaje lo dice).
        mine = db.get(PersonalityAnswers, inviter.id)
        if completed(mine.answers if mine else {}) < len(load_config()["questions"]):
            raise HTTPException(status_code=409, detail="Completá tu test de personalidad antes de invitar a compararlo")
        db.add(
            Invitation(
                ref_id=ref_id,
                inviter_profile_id=inviter.id,
                friend_name=payload.friend_name,
                kind="test",
                relationship=payload.relationship or "pareja",
            )
        )
        db.commit()
        message = (
            f"¡Hola {payload.friend_name}! Ya completé mi test de personalidad en Destiny ✨ Hacelo vos "
            "(son 32 preguntas) y vemos qué tan compatibles somos en atracción, afecto, comunicación y "
            f"compromiso: {link}"
        )
        return InvitationOut(
            ref_id=ref_id, kind="test", message=message, whatsapp_url=f"https://wa.me/?text={quote(message)}"
        )

    invitation = Invitation(
        ref_id=ref_id,
        inviter_profile_id=inviter.id,
        friend_name=payload.friend_name,
        friend_sun_sign=payload.friend_sun_sign,
        relationship=payload.relationship,
    )
    db.add(invitation)
    db.commit()

    # Resultado necesariamente aproximado: solo tenemos el signo solar del
    # amigo, no su fecha/hora exacta (fricción mínima al invitar).
    friend_lon = approximate_longitude_for_sign(payload.friend_sun_sign)
    inviter_lon = sun_longitude(inviter.birth_date, inviter.birth_time)
    aspect = classify_aspect(angle_between(inviter_lon, friend_lon))

    teaser = (
        f"Con el sol en {payload.friend_sun_sign}, {payload.friend_name} podría tener esta "
        f"conexión con vos: {aspect_sentence(aspect['aspect'])}. Para ver la resonancia real (y revelarla para los "
        "dos) necesitamos que complete su carta natal."
    )
    partial_report = PartialReportOut(
        teaser=teaser,
        locked_fields=["hora_de_nacimiento", "ascendente", "compatibilidad_exacta"],
    )

    # El mensaje lo manda quien invita desde su WhatsApp: le habla al amigo en primera persona.
    message = (
        f"¡Hola {payload.friend_name}! Te invito a Destiny ✨ Con tu signo ({payload.friend_sun_sign}) y mi carta, "
        f"parece que {aspect_sentence(aspect['aspect']).replace('sus soles', 'nuestros soles')}. Completá tu carta acá y vemos los dos la resonancia real: {link}"
    )
    whatsapp_url = f"https://wa.me/?text={quote(message)}"

    return InvitationOut(ref_id=ref_id, whatsapp_url=whatsapp_url, partial_report=partial_report, message=message)


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
    if invitation.invitee_profile_id not in (None, current):
        raise HTTPException(status_code=409, detail="Esta invitación ya la usó otra persona")

    inviter = _get_profile(invitation.inviter_profile_id, db)
    invitee = _get_profile(current, db)
    if invitee.verification_status != "verificado":
        raise HTTPException(status_code=403, detail="Verificá tu identidad antes de aceptar")

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
    if invitation.invitee_profile_id is None:
        invitation.invitee_profile_id = invitee.id
        invitation.accepted_at = datetime.now(timezone.utc)
    db.commit()
    return InvitationAcceptOut(match_id=match_id)


@router.get("/{ref_id}", response_model=InvitationPreloadOut)
def get_invitation(ref_id: str, db: Session = Depends(get_db)) -> InvitationPreloadOut:
    invitation = db.get(Invitation, ref_id)
    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitation not found")

    inviter = db.get(Profile, invitation.inviter_profile_id)
    if invitation.kind == "test":
        name = inviter.display_name or "Alguien"
        return InvitationPreloadOut(
            ref_id=ref_id,
            friend_name=invitation.friend_name,
            kind="test",
            inviter_name=inviter.display_name,
            relationship=invitation.relationship,
            teaser=(
                f"{name} completó su test de personalidad en Destiny y quiere ver qué tan compatibles son. "
                "Registrate, hacé el test (32 preguntas) y lo descubren juntos."
            ),
        )
    friend_lon = approximate_longitude_for_sign(invitation.friend_sun_sign)
    aspect = classify_aspect(angle_between(sun_longitude(inviter.birth_date, inviter.birth_time), friend_lon))

    return InvitationPreloadOut(
        ref_id=ref_id,
        friend_name=invitation.friend_name,
        inviter_name=inviter.display_name,
        teaser=(
            f"Alguien te invitó a Destiny. Con tu signo, puede que {aspect_sentence(aspect['aspect'])}. "
            "Completá tu carta para la revelación real."
        ),
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

    signals = compatibility_signals(inviter, invitee)
    text = (
        f"Resonancia real revelada entre {invitation.friend_name} y quien lo invitó: "
        f"{aspect_sentence(signals['aspect'])} ({signals['percentage']}%)."
    )
    return RevealOut(aspect=signals["aspect"], percentage=signals["percentage"], text=text)
