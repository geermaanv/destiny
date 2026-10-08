import uuid
from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, Field, field_validator

NotificationRhythm = Literal["ritmo_diario", "pulso_cosmos"]


class NotificationPreferenceIn(BaseModel):
    rhythm: NotificationRhythm


class BirthPlaceIn(BaseModel):
    query: str
    lat: float | None = None
    lon: float | None = None
    timezone: str | None = None


class PlaceOut(BaseModel):
    label: str
    lat: float
    lon: float
    timezone: str


MIN_AGE = 18  # spec A1: Destiny es para mayores de edad


# Franja del día si no se sabe la hora exacta (spec A1): se usa el punto medio,
# así el desvío máximo baja de 12 a 3 horas.
BirthTimePeriod = Literal["madrugada", "manana", "tarde", "noche"]
PERIOD_MIDPOINTS: dict[str, time] = {
    "madrugada": time(3, 0),
    "manana": time(9, 0),
    "tarde": time(15, 0),
    "noche": time(21, 0),
}


class BirthDataIn(BaseModel):
    birth_date: date
    birth_time: time | None = None
    birth_time_period: BirthTimePeriod | None = None
    birth_place: BirthPlaceIn

    @field_validator("birth_date")
    @classmethod
    def must_be_adult(cls, value: date) -> date:
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < MIN_AGE:
            raise ValueError(f"must be at least {MIN_AGE} years old")
        return value


# Perfil liviano (spec A4).
EnergyPeriod = Literal["madrugada", "manana", "tarde", "noche"]
Interest = Literal[
    "musica", "deporte", "arte", "tecnologia", "viajes", "espiritualidad",
    "lectura", "cine", "naturaleza", "cocina", "emprendimientos", "juegos",
]
Avatar = Literal["signo", "luna", "sol", "estrella", "planeta", "fuego", "ola", "hoja", "mariposa", "rayo"]


class BasicInfoIn(BaseModel):
    display_name: str = Field(min_length=1, max_length=40)
    energy_period: EnergyPeriod | None = None
    interests: list[Interest] = Field(default_factory=list, max_length=5)
    bio: str | None = Field(default=None, max_length=140)
    neighborhood: str | None = Field(default=None, max_length=40)
    avatar: Avatar | None = None

    @field_validator("display_name", "bio", "neighborhood", mode="before")
    @classmethod
    def strip_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


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
    display_name: str | None = None
    bio: str | None = None
    neighborhood: str | None = None
    energy_period: str | None = None
    interests: list[str] = []
    avatar: str | None = None
    has_photo: bool = False
    sun_sign: str | None = None  # solo lo completa GET /profiles/{id}

    class Config:
        from_attributes = True


class VerificationOut(BaseModel):
    verification_id: str | None
    status: str
    method: str | None = None


class ContinueExistingOut(BaseModel):
    profile_id: uuid.UUID


# Sesión con WhatsApp (spec A5).
class ClaimIn(BaseModel):
    claim_token: str


class LoginStartOut(BaseModel):
    login_id: uuid.UUID
    code: str
    wa_link: str
    expires_at: datetime
    claim_token: str
    mock: bool


class LoginStatusOut(BaseModel):
    status: Literal["pendiente", "listo", "sin_cuenta", "vencido"]


class WhatsappCodeOut(BaseModel):
    code: str
    wa_link: str
    expires_at: datetime
    mock: bool  # true si no hay credenciales de WhatsApp: la pantalla ofrece "Simular envío (dev)"
    claim_token: str  # spec A5: con esto el navegador toma la sesión cuando llega el mensaje


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
    # Motor de sinastría (spec B5-motor-sinastria.md): puntaje por eje y contexto.
    axes: dict[str, int] = {}
    relationship: str | None = None
    approximate: bool = False
    # Perfil liviano (spec A4): solo datos públicos.
    display_name: str | None = None
    age: int | None = None
    sun_sign: str | None = None
    photo_url: str | None = None
    avatar: str | None = None
    energy_period: str | None = None
    interests: list[str] = []
    bio: str | None = None
    neighborhood: str | None = None


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
    title: str | None = None
    text: str | None = None


class UpcomingEventOut(BaseModel):
    start: date
    end: date
    aspect: str
    title: str
    text: str
    has_notes: bool


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
    status: str = "aceptada"


# Conexión mutua + chat híbrido (spec B7 v2).
class PublicProfileOut(BaseModel):
    profile_id: uuid.UUID
    display_name: str | None = None
    age: int | None = None
    sun_sign: str | None = None
    photo_url: str | None = None
    avatar: str | None = None


class WhatsappHandoffOut(BaseModel):
    me_ok: bool
    other_ok: bool
    link: str | None = None  # solo cuando los dos aceptaron


class ConnectionOut(BaseModel):
    match_id: uuid.UUID
    status: str
    direction: Literal["enviada", "recibida"]
    other: PublicProfileOut
    last_message: str | None = None
    last_message_at: datetime | None = None
    whatsapp: WhatsappHandoffOut


class ProfileRefIn(BaseModel):
    profile_id: uuid.UUID


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
