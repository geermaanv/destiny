import uuid
from datetime import date, datetime, time
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


class DiscoverCandidateOut(BaseModel):
    profile_id: uuid.UUID
    compatibility_pct: int
    preview: str


class ExplanationOut(BaseModel):
    text: str


class CalendarDayOut(BaseModel):
    date: date
    has_key_transit: bool


class AnnotationIn(BaseModel):
    profile_id: uuid.UUID
    text: str


class AnnotationOut(BaseModel):
    text: str
    created_at: datetime


class TransitOut(BaseModel):
    aspect: str


class CalendarDayDetailOut(BaseModel):
    transits: list[TransitOut]
    annotations: list[AnnotationOut]


class MatchIn(BaseModel):
    profile_a_id: uuid.UUID
    profile_b_id: uuid.UUID


class ChatMessageOut(BaseModel):
    sender: str
    text: str
    created_at: datetime


class MatchOut(BaseModel):
    id: uuid.UUID
    icebreaker: str


class SendMessageIn(BaseModel):
    profile_id: uuid.UUID
    text: str


class InvitationIn(BaseModel):
    inviter_id: uuid.UUID
    friend_name: str
    friend_sun_sign: Literal[
        "Aries", "Tauro", "Gemini", "Cáncer", "Leo", "Virgo",
        "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis",
    ]


class PartialReportOut(BaseModel):
    teaser: str
    locked_fields: list[str]


class InvitationOut(BaseModel):
    ref_id: str
    whatsapp_url: str
    partial_report: PartialReportOut


class InvitationPreloadOut(BaseModel):
    ref_id: str
    friend_name: str
    teaser: str


class RevealOut(BaseModel):
    aspect: str
    percentage: int
    text: str
