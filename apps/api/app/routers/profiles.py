import uuid
from datetime import time
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.adapters.kyc import IdentityVerificationAdapter, get_kyc_adapter
from app.auth import hash_token, require_owner_if_verified, session_profile_id, start_session
from app.config import settings
from app.public_profile import sun_sign
from app.database import get_db
from app.models import PhoneVerificationCode, Profile
from app.schemas import (
    PERIOD_MIDPOINTS,
    BasicInfoIn,
    ClaimIn,
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
def get_profile(
    profile_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> ProfileOut:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    require_owner_if_verified(profile, current)
    return ProfileOut.model_validate(profile).model_copy(update={"sun_sign": sun_sign(profile)})


@router.post("/{profile_id}/birth-data", response_model=ProfileOut)
def set_birth_data(
    profile_id: uuid.UUID,
    payload: BirthDataIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    require_owner_if_verified(profile, current)

    profile.birth_date = payload.birth_date
    if payload.birth_time is None:
        # "No sé mi hora exacta" -> punto medio de la franja si la recuerda
        # (madrugada/mañana/tarde/noche), si no 12:00; flag de estimada. Derivado
        # server-side: no se confía en un flag de estimada mandado por el cliente.
        profile.birth_time = PERIOD_MIDPOINTS.get(payload.birth_time_period or "", time(12, 0))
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
    profile_id: uuid.UUID,
    payload: NotificationPreferenceIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    require_owner_if_verified(profile, current)

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
    current: uuid.UUID | None = Depends(session_profile_id),
) -> VerificationOut:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    require_owner_if_verified(profile, current)

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

    entry, claim_token = issue_code(db, profile)
    return WhatsappCodeOut(
        code=entry.code,
        wa_link=build_wa_link(entry.code),
        expires_at=entry.expires_at,
        mock=is_mock_mode(),
        claim_token=claim_token,
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
def continue_with_existing_profile(
    profile_id: uuid.UUID, payload: ClaimIn, response: Response, db: Session = Depends(get_db)
) -> ContinueExistingOut:
    """Tras duplicado_detectado: seguir con la cuenta que ya tiene ese número.

    El perfil nuevo (todavía sin verificar) se descarta y se inicia sesión en el
    existente. Requiere el comprobante del navegador que mandó el código (spec A5).
    """
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.verification_status != "duplicado_detectado" or profile.duplicate_of_id is None:
        raise HTTPException(status_code=409, detail="Profile is not a detected duplicate")

    existing = db.get(Profile, profile.duplicate_of_id)
    if existing is None or existing.verification_status != "verificado":
        raise HTTPException(status_code=409, detail="Existing profile not available")

    proof = db.scalar(
        select(PhoneVerificationCode).where(
            PhoneVerificationCode.profile_id == profile.id,
            PhoneVerificationCode.claim_token_hash == hash_token(payload.claim_token),
            PhoneVerificationCode.used_at.is_not(None),
        )
    )
    if proof is None:
        raise HTTPException(status_code=403, detail="Comprobante inválido")

    db.execute(delete(PhoneVerificationCode).where(PhoneVerificationCode.profile_id == profile.id))
    db.delete(profile)
    db.commit()
    start_session(db, response, existing.id)
    return ContinueExistingOut(profile_id=existing.id)


# Perfil liviano (spec A4).
PHOTO_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_PHOTO_BYTES = 5 * 1024 * 1024


@router.post("/{profile_id}/basic-info", response_model=ProfileOut)
def set_basic_info(
    profile_id: uuid.UUID,
    payload: BasicInfoIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    require_owner_if_verified(profile, current)

    profile.display_name = payload.display_name
    profile.energy_period = payload.energy_period
    profile.interests = list(dict.fromkeys(payload.interests))
    profile.bio = payload.bio
    profile.neighborhood = payload.neighborhood
    profile.avatar = payload.avatar
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/{profile_id}/photo", response_model=ProfileOut)
async def upload_photo(
    profile_id: uuid.UUID,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    require_owner_if_verified(profile, current)
    extension = PHOTO_TYPES.get(photo.content_type or "")
    if extension is None:
        raise HTTPException(status_code=415, detail="La foto tiene que ser JPG, PNG o WebP")
    content = await photo.read(MAX_PHOTO_BYTES + 1)
    if len(content) > MAX_PHOTO_BYTES:
        raise HTTPException(status_code=413, detail="La foto no puede pesar más de 5 MB")

    uploads = Path(settings.uploads_dir)
    uploads.mkdir(parents=True, exist_ok=True)
    if profile.photo_path:
        Path(profile.photo_path).unlink(missing_ok=True)
    path = uploads / f"{profile.id}{extension}"
    path.write_bytes(content)

    profile.photo_path = str(path)
    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/{profile_id}/photo", response_model=ProfileOut)
def delete_photo(
    profile_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    require_owner_if_verified(profile, current)
    if profile.photo_path:
        Path(profile.photo_path).unlink(missing_ok=True)
        profile.photo_path = None
        db.commit()
        db.refresh(profile)
    return profile


@router.get("/{profile_id}/photo")
def get_photo(profile_id: uuid.UUID, db: Session = Depends(get_db)) -> FileResponse:
    profile = db.get(Profile, profile_id)
    if profile is None or not profile.photo_path or not Path(profile.photo_path).exists():
        raise HTTPException(status_code=404, detail="Photo not found")
    return FileResponse(profile.photo_path, headers={"Cache-Control": "no-cache"})
