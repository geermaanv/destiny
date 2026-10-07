import uuid
from datetime import time

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.adapters.kyc import IdentityVerificationAdapter, get_kyc_adapter
from app.database import get_db
from app.models import PhoneVerificationCode, Profile
from app.schemas import (
    BirthDataIn,
    ContinueExistingOut,
    NotificationPreferenceIn,
    ProfileOut,
    VerificationOut,
    WhatsappCodeOut,
)
from app.whatsapp import build_wa_link, is_mock_mode, issue_code

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("", response_model=ProfileOut, status_code=201)
def create_profile(db: Session = Depends(get_db)) -> Profile:
    profile = Profile()
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{profile_id}", response_model=ProfileOut)
def get_profile(profile_id: uuid.UUID, db: Session = Depends(get_db)) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/{profile_id}/birth-data", response_model=ProfileOut)
def set_birth_data(profile_id: uuid.UUID, payload: BirthDataIn, db: Session = Depends(get_db)) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile.birth_date = payload.birth_date
    if payload.birth_time is None:
        # "No sé mi hora exacta" -> 12:00 interno, flag de estimada. Derivado
        # server-side: no se confía en un flag de estimada mandado por el cliente.
        profile.birth_time = time(12, 0)
        profile.birth_time_estimated = True
    else:
        profile.birth_time = payload.birth_time
        profile.birth_time_estimated = False

    profile.birth_place_query = payload.birth_place.query
    profile.birth_place_lat = payload.birth_place.lat
    profile.birth_place_lon = payload.birth_place.lon
    profile.birth_place_timezone = payload.birth_place.timezone

    db.commit()
    db.refresh(profile)
    return profile


@router.post("/{profile_id}/notification-preference", response_model=ProfileOut)
def set_notification_preference(
    profile_id: uuid.UUID, payload: NotificationPreferenceIn, db: Session = Depends(get_db)
) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile.notification_rhythm = payload.rhythm

    db.commit()
    db.refresh(profile)
    return profile


@router.post("/{profile_id}/verification", response_model=VerificationOut)
async def start_verification(
    profile_id: uuid.UUID,
    media: UploadFile = File(...),
    db: Session = Depends(get_db),
    adapter: IdentityVerificationAdapter = Depends(get_kyc_adapter),
) -> VerificationOut:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    media_bytes = await media.read()
    result = adapter.start_verification(str(profile_id), media_bytes)

    profile.verification_id = result.verification_id
    profile.verification_status = result.status
    profile.verification_method = "kyc_video"
    db.commit()

    return VerificationOut(verification_id=result.verification_id, status=result.status, method="kyc_video")


@router.post("/{profile_id}/verification/whatsapp", response_model=WhatsappCodeOut)
def start_whatsapp_verification(profile_id: uuid.UUID, db: Session = Depends(get_db)) -> WhatsappCodeOut:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.verification_status == "verificado":
        raise HTTPException(status_code=409, detail="Profile already verified")
    if profile.birth_date is None:
        # La verificación cierra el onboarding: sin datos natales no hay Descubrir posible.
        raise HTTPException(status_code=409, detail="Profile has no birth data")

    entry = issue_code(db, profile)
    return WhatsappCodeOut(
        code=entry.code, wa_link=build_wa_link(entry.code), expires_at=entry.expires_at, mock=is_mock_mode()
    )


@router.get("/{profile_id}/verification", response_model=VerificationOut)
def get_verification(profile_id: uuid.UUID, db: Session = Depends(get_db)) -> VerificationOut:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return VerificationOut(
        verification_id=profile.verification_id,
        status=profile.verification_status,
        method=profile.verification_method,
    )


@router.post("/{profile_id}/verification/continue-existing", response_model=ContinueExistingOut)
def continue_with_existing_profile(profile_id: uuid.UUID, db: Session = Depends(get_db)) -> ContinueExistingOut:
    """Tras duplicado_detectado: seguir con la cuenta que ya tiene ese número.

    El perfil nuevo (todavía sin verificar) se descarta y se devuelve el existente.
    """
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.verification_status != "duplicado_detectado" or profile.duplicate_of_id is None:
        raise HTTPException(status_code=409, detail="Profile is not a detected duplicate")

    existing = db.get(Profile, profile.duplicate_of_id)
    if existing is None or existing.verification_status != "verificado":
        raise HTTPException(status_code=409, detail="Existing profile not available")

    db.execute(delete(PhoneVerificationCode).where(PhoneVerificationCode.profile_id == profile.id))
    db.delete(profile)
    db.commit()
    return ContinueExistingOut(profile_id=existing.id)
