import uuid
from datetime import date, time
from typing import Literal

from pydantic import BaseModel

NotificationRhythm = Literal["ritmo_diario", "pulso_cosmos"]


class NotificationPreferenceIn(BaseModel):
    rhythm: NotificationRhythm


class BirthPlaceIn(BaseModel):
    query: str
    lat: float | None = None
    lon: float | None = None
    timezone: str | None = None


class BirthDataIn(BaseModel):
    birth_date: date
    birth_time: time | None = None
    birth_place: BirthPlaceIn


class ProfileOut(BaseModel):
    id: uuid.UUID
    birth_date: date | None
    birth_time: time | None
    birth_time_estimated: bool
    birth_place_query: str | None
    birth_place_lat: float | None
    birth_place_lon: float | None
    birth_place_timezone: str | None
    notification_rhythm: NotificationRhythm | None
    verification_status: str
    verification_id: str | None

    class Config:
        from_attributes = True


class VerificationOut(BaseModel):
    verification_id: str | None
    status: str


Mood = Literal["energico", "tranquilo", "reflexivo", "ansioso", "inspirado"]


class MoodCheckinIn(BaseModel):
    profile_id: uuid.UUID
    mood: Mood


class AstroWeatherOut(BaseModel):
    astro_weather: str
    date: date


class FrequencyCountOut(BaseModel):
    count: int
