import uuid
from datetime import time

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.adapters.kyc import IdentityVerificationAdapter, get_kyc_adapter
from app.database import get_db
from app.models import Profile
from app.schemas import BirthDataIn, NotificationPreferenceIn, ProfileOut, VerificationOut

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
    db.commit()

    return VerificationOut(verification_id=result.verification_id, status=result.status)


@router.get("/{profile_id}/verification", response_model=VerificationOut)
def get_verification(profile_id: uuid.UUID, db: Session = Depends(get_db)) -> VerificationOut:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return VerificationOut(verification_id=profile.verification_id, status=profile.verification_status)
