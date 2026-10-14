from datetime import date, datetime, timezone

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.astro import astro_weather_for_date, moon_longitude, today_astro_weather, zodiac_sign
from app.auth import require_self, session_profile_id
from app.content.transits import reviewed, text_for
from app.personalization.style import style_for
from app.database import get_db
from app.models import MoodCheckin, Profile
from app.schemas import AstroWeatherOut, FrequencyCountOut, MoodCheckinIn, MyDayOut
from app.transits import day_transit
from app.ai_texts import cached, day_key, record
from app.day.detail import day_detail, load_config as day_config, write_reading
from app.personalization.style import prompt_instructions
from app.schemas import MyDayDetailOut

router = APIRouter(prefix="/home", tags=["home"])


@router.get("/today", response_model=AstroWeatherOut)
def get_today(day: date | None = Query(default=None, alias="date")) -> AstroWeatherOut:
    """Clima del día. La app manda su fecha local, así coincide con "Tu día" (sin fecha: hoy en UTC)."""
    if day is None:
        return AstroWeatherOut(astro_weather=today_astro_weather(), date=datetime.now(timezone.utc).date())
    return AstroWeatherOut(astro_weather=astro_weather_for_date(day), date=day)


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


@router.get("/my-day", response_model=MyDayOut)
def get_my_day(
    profile_id: uuid.UUID = Query(...),
    day: date = Query(alias="date"),
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> MyDayOut:
    """"Tu día" (spec B4 v2): el modelo calcula el tránsito; el texto sale de la biblioteca fija (sin IA)."""
    require_self(profile_id, current)
    profile = db.get(Profile, profile_id)
    if profile is None or profile.birth_date is None:
        raise HTTPException(status_code=409, detail="Perfil sin datos natales")
    transit = day_transit(profile, day)
    moon_sign = zodiac_sign(moon_longitude(day))
    title, text = text_for(transit["aspect"], moon_sign, style_for(profile)["registro"])
    return MyDayOut(
        date=day,
        aspect=transit["aspect"],
        is_major=transit["is_major"],
        moon_sign=moon_sign,
        title=title,
        text=text,
        reviewed=reviewed(),
    )


@router.get("/my-day/detail", response_model=MyDayDetailOut)
def get_my_day_detail(
    profile_id: uuid.UUID = Query(...),
    day: date = Query(alias="date"),
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> MyDayDetailOut:
    """Tu día completo (spec B4 v3): el motor calcula; la IA redacta la lectura una vez por día."""
    require_self(profile_id, current)
    profile = db.get(Profile, profile_id)
    if profile is None or profile.birth_date is None:
        raise HTTPException(status_code=409, detail="Perfil sin datos natales")
    detail = day_detail(profile, day)
    style = style_for(profile)
    key = day_key(profile, day, style, day_config()["version"])
    if (text := cached(db, key)) is not None:
        detail["lectura"] = {"texto": text, "ia": True}
    else:
        written = write_reading(detail, prompt_instructions(style))
        record(db, key, "dia", written)
        detail["lectura"] = {"texto": written.text, "ia": written.ai is not None}
    return MyDayDetailOut(**detail)


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
