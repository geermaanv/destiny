import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import CLAIM_WINDOW, DEVICE_COOKIE, end_session, hash_token, session_profile_id, start_session
from app.config import settings
from app.database import get_db
from app.models import PhoneVerificationCode, Profile
from app.public_profile import sun_sign
from app.schemas import ClaimIn, LoginStartOut, LoginStatusOut, ProfileOut, ProfileRefIn
from app.whatsapp import build_wa_link, is_mock_mode, issue_login_code

# Sesión con WhatsApp (spec A5).
router = APIRouter(tags=["sessions"])


@router.post("/sessions/claim", status_code=204)
def claim_session(payload: ClaimIn, response: Response, db: Session = Depends(get_db)) -> Response:
    """El navegador que pidió el código toma la sesión, una vez que llegó el mensaje de WhatsApp."""
    entry = db.scalar(
        select(PhoneVerificationCode).where(PhoneVerificationCode.claim_token_hash == hash_token(payload.claim_token))
    )
    now = datetime.now(timezone.utc)
    if (
        entry is None
        or entry.used_at is None
        or entry.claimed_at is not None
        or entry.result_profile_id is None
        or now - entry.used_at > CLAIM_WINDOW
    ):
        raise HTTPException(status_code=409, detail="Todavía no hay una sesión para tomar con este comprobante")

    profile = db.get(Profile, entry.result_profile_id)
    if profile is None or profile.verification_status != "verificado":
        raise HTTPException(status_code=409, detail="El perfil no está verificado")

    entry.claimed_at = now
    start_session(db, response, profile.id)
    response.status_code = 204
    return response


@router.post("/sessions/start", status_code=204)
def start_without_whatsapp(
    payload: ProfileRefIn, request: Request, response: Response, db: Session = Depends(get_db)
) -> Response:
    """Spec A10: al terminar el registro se inicia la sesión en el dispositivo, sin WhatsApp.
    Solo el navegador que creó el perfil (cookie destiny_device) puede hacerlo."""
    if settings.verificacion_obligatoria:
        raise HTTPException(status_code=403, detail="verificacion_obligatoria")
    profile = db.get(Profile, payload.profile_id)
    token = request.cookies.get(DEVICE_COOKIE)
    if profile is None or not token or profile.device_token_hash != hash_token(token):
        raise HTTPException(status_code=403, detail="Este dispositivo no creó el perfil")
    if profile.birth_date is None or not profile.display_name:
        raise HTTPException(status_code=409, detail="Completá tus datos de nacimiento y tu nombre")
    if profile.activated_at is None:
        profile.activated_at = datetime.now(timezone.utc)
    start_session(db, response, profile.id)
    response.status_code = 204
    return response


@router.post("/sessions/login", response_model=LoginStartOut)
def start_login(db: Session = Depends(get_db)) -> LoginStartOut:
    """'Ya tengo cuenta': código para mandar por WhatsApp desde el número con el que se verificó."""
    entry, claim_token = issue_login_code(db)
    return LoginStartOut(
        login_id=entry.id,
        code=entry.code,
        wa_link=build_wa_link(entry.code),
        expires_at=entry.expires_at,
        claim_token=claim_token,
        mock=is_mock_mode(),
    )


@router.get("/sessions/login/{login_id}", response_model=LoginStatusOut)
def login_status(login_id: uuid.UUID, db: Session = Depends(get_db)) -> LoginStatusOut:
    entry = db.get(PhoneVerificationCode, login_id)
    if entry is None or entry.purpose != "login":
        raise HTTPException(status_code=404, detail="Login not found")
    if entry.outcome:
        return LoginStatusOut(status=entry.outcome)
    if entry.expires_at <= datetime.now(timezone.utc):
        return LoginStatusOut(status="vencido")
    return LoginStatusOut(status="pendiente")


@router.get("/me", response_model=ProfileOut)
def me(current: uuid.UUID | None = Depends(session_profile_id), db: Session = Depends(get_db)) -> ProfileOut:
    profile = db.get(Profile, current) if current else None
    if profile is None:
        raise HTTPException(status_code=401, detail="Sin sesión")
    return ProfileOut.model_validate(profile).model_copy(update={"sun_sign": sun_sign(profile)})


@router.post("/sessions/logout", status_code=204)
def logout(request: Request, response: Response, db: Session = Depends(get_db)) -> Response:
    end_session(db, request, response)
    response.status_code = 204
    return response
