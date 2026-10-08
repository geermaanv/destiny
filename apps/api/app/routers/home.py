from datetime import datetime, timezone

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.astro import today_astro_weather
from app.auth import require_self, session_profile_id
from app.database import get_db
from app.models import MoodCheckin, Profile
from app.schemas import AstroWeatherOut, FrequencyCountOut, MoodCheckinIn

router = APIRouter(prefix="/home", tags=["home"])


@router.get("/today", response_model=AstroWeatherOut)
def get_today() -> AstroWeatherOut:
    return AstroWeatherOut(astro_weather=today_astro_weather(), date=datetime.now(timezone.utc).date())


@router.get("/frequency-count", response_model=FrequencyCountOut)
def get_frequency_count(
    profile_id: uuid.UUID | None = Query(default=None), db: Session = Depends(get_db)
) -> FrequencyCountOut:
    # Heurística v1: todos los perfiles verificados comparten el tránsito del
    # día (ver B4-home-tu-momento.md, "fuera de alcance": agrupación
    # geográfica y afinidad fina de tránsitos quedan para una iteración
    # posterior).
    # Mismo universo que /discover: verificados con datos natales y nombre, sin contarse a uno mismo.
    query = select(func.count()).select_from(Profile).where(
        Profile.verification_status == "verificado",
        Profile.birth_date.is_not(None),
        Profile.display_name.is_not(None),
    )
    if profile_id is not None:
        query = query.where(Profile.id != profile_id)
    count = db.scalar(query)
    return FrequencyCountOut(count=count or 0)


mood_router = APIRouter(tags=["home"])


@mood_router.post("/mood-checkins", status_code=201)
def create_mood_checkin(
    payload: MoodCheckinIn, db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> dict[str, str]:
    require_self(payload.profile_id, current)
    checkin = MoodCheckin(profile_id=payload.profile_id, mood=payload.mood)
    db.add(checkin)
    db.commit()
    return {"status": "ok"}
