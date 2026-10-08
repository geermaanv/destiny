import secrets
import uuid
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.aspects import angle_between, aspect_sentence, classify_aspect
from app.astro import approximate_longitude_for_sign
from app.compatibility import compatibility_signals, sun_longitude
from app.config import settings
from app.auth import require_self, session_profile_id
from app.database import get_db
from app.models import Invitation, Profile
from app.schemas import InvitationIn, InvitationOut, InvitationPreloadOut, PartialReportOut, RevealOut

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
    invitation = Invitation(
        ref_id=ref_id,
        inviter_profile_id=inviter.id,
        friend_name=payload.friend_name,
        friend_sun_sign=payload.friend_sun_sign,
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

    link = f"{settings.web_base_url}/onboarding/invitacion?ref={ref_id}"
    # El mensaje lo manda quien invita desde su WhatsApp: le habla al amigo en primera persona.
    message = (
        f"¡Hola {payload.friend_name}! Te invito a Destiny ✨ Con tu signo ({payload.friend_sun_sign}) y mi carta, "
        f"parece que {aspect_sentence(aspect['aspect']).replace('sus soles', 'nuestros soles')}. Completá tu carta acá y vemos los dos la resonancia real: {link}"
    )
    whatsapp_url = f"https://wa.me/?text={quote(message)}"

    return InvitationOut(ref_id=ref_id, whatsapp_url=whatsapp_url, partial_report=partial_report, message=message)


@router.get("/{ref_id}", response_model=InvitationPreloadOut)
def get_invitation(ref_id: str, db: Session = Depends(get_db)) -> InvitationPreloadOut:
    invitation = db.get(Invitation, ref_id)
    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitation not found")

    inviter = db.get(Profile, invitation.inviter_profile_id)
    friend_lon = approximate_longitude_for_sign(invitation.friend_sun_sign)
    aspect = classify_aspect(angle_between(sun_longitude(inviter.birth_date, inviter.birth_time), friend_lon))

    return InvitationPreloadOut(
        ref_id=ref_id,
        friend_name=invitation.friend_name,
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
