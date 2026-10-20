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


# Franja del día si no se sabe la hora exacta: las 5 franjas de Pablo (spec A7), se usa
# el punto medio y la carta queda aproximada (sin ascendente, medio cielo ni casas).
BirthTimePeriod = Literal["madrugada", "manana", "mediodia", "tarde", "noche"]
PERIOD_MIDPOINTS: dict[str, time] = {
    "madrugada": time(2, 30),  # 00 a 05
    "manana": time(8, 0),  # 05 a 11
    "mediodia": time(12, 30),  # 11 a 14
    "tarde": time(16, 30),  # 14 a 19
    "noche": time(21, 30),  # 19 a 24
}
UNKNOWN_TIME = PERIOD_MIDPOINTS["mediodia"]  # sin hora ni franja: se estima como mediodía (decisión de German)


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


# Spec B8: género y a quién ver en Descubrir ("pareja").
Gender = Literal["mujer", "hombre", "no_binario"]


class PreferencesIn(BaseModel):
    gender: Gender | None = None
    gender_detail: str | None = Field(default=None, max_length=40)
    show_me: list[Gender] = Field(default_factory=list, max_length=3)
    appear_in: list[Literal["mujer", "hombre"]] = Field(default_factory=list, max_length=2)
    show_gender: bool = False

    @field_validator("gender_detail", mode="before")
    @classmethod
    def strip_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


# Spec A12: aviso de privacidad y qué busca.
class PrivacyIn(BaseModel):
    version: str = Field(min_length=1, max_length=40)
    contexto: Literal["registro", "test"]


class LookingForIn(BaseModel):
    looking_for: Literal["pareja", "amistad", "laboral", "ocasional"]


# Spec B9: dónde vive (del buscador de ciudades: con coordenadas).
class ResidenceIn(BaseModel):
    query: str = Field(min_length=1, max_length=200)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


# Spec A11: fotos del perfil.
class PhotoOut(BaseModel):
    id: uuid.UUID
    url: str
    principal: bool


class PhotosOut(BaseModel):
    photos: list[PhotoOut]
    max: int


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
    gender: str | None = None
    gender_detail: str | None = None
    show_me: list[str] = []
    appear_in: list[str] = []
    show_gender: bool = False
    residence_label: str | None = None
    residence_lat: float | None = None
    residence_lon: float | None = None
    privacy_version: str | None = None
    test_privacy_version: str | None = None
    looking_for: str | None = None

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


class NatalFoundationOut(BaseModel):
    """Un indicador de la carta que explica una dimensión (spec A8)."""

    tipo: Literal["signo", "casa", "aspecto"]
    punto: str
    signo: str | None = None
    casa: int | None = None
    otro: str | None = None
    aspecto: str | None = None
    texto: str


class NatalDimensionOut(BaseModel):
    clave: str
    nombre: str
    pregunta: str
    fundamentos: list[NatalFoundationOut]
    preguntas: list[str]
    faltan_por_hora: list[str]


class NatalDimensionsOut(BaseModel):
    aproximado: bool
    falta: Literal["hora", "lugar"] | None = None
    cielo: list[dict[str, str | float]] = []
    dimensiones: list[NatalDimensionOut]


class NatalSynthesisOut(BaseModel):
    texto: str
    ia: bool


class ShareStatusOut(BaseModel):
    """Compartir mi carta (spec A9)."""

    activo: bool
    token: str | None = None
    vistas: int = 0


class PublicDimensionOut(BaseModel):
    clave: str
    nombre: str
    pregunta: str
    sintesis: str


class PublicCartaOut(BaseModel):
    """Lo único que muestra el link público: Destiny filtra los datos (spec A9)."""

    nombre: str
    signos: dict[str, str]
    cielo: list[dict[str, str | float]]
    dimensiones: list[PublicDimensionOut]
    paleta: dict[str, dict[str, str]]
    tipografia: str
    fondo: str
    elementos: dict[str, int]


class AstroModeOut(BaseModel):
    clave: str
    nombre: str
    descripcion: str


class AstroMessageOut(BaseModel):
    rol: Literal["persona", "destiny"]
    texto: str
    modo: str
    creado: datetime


class AstrochatOut(BaseModel):
    """Astrochat (spec X3)."""

    modo: str
    modos: list[AstroModeOut]
    mensajes: list[AstroMessageOut]
    restantes_hoy: int
    limite: int
    # Spec C11: preguntas extra por amigos que se registraron con tu invitación (ya incluidas en `limite`).
    extra_por_invitados: int = 0
    ejemplos: list[str]


class AstroAskIn(BaseModel):
    texto: str
    modo: str | None = None
    # Spec U2: pregunta sobre un día del calendario; la IA recibe los datos de ese día.
    dia: date | None = None


class AstroAnswerOut(BaseModel):
    respuesta: AstroMessageOut
    ia: bool
    restantes_hoy: int


class StyleOut(BaseModel):
    """Estilo de redacción (spec X2)."""

    registro: str
    tono: str
    formato: str
    source: Literal["carta", "elegido"]
    por_que: str
    registro_carta: str
    # Tema visual (spec X2 v2)
    tema: str
    tema_carta: str
    tema_source: Literal["carta", "elegido"]
    tema_por_que: str
    elementos: dict[str, int]
    paleta: dict[str, dict[str, str]]
    # v3
    modo: Literal["oscuro", "claro"]
    acento: str
    tipografia: str
    fondo: Literal["constelacion", "aura", "elemental", "horizonte", "ninguno"]
    cielo: list[dict[str, str | float]]
    cielo_leyenda: str


class StyleIn(BaseModel):
    """Solo se cambian los campos que se mandan; null = que decida la carta."""

    registro: Literal["directo", "practico", "analitico", "intuitivo"] | None = None
    tema: Literal["fuego", "tierra", "aire", "agua", "clasico"] | None = None
    modo: Literal["oscuro", "claro"] | None = None
    fondo: Literal["constelacion", "aura", "elemental", "horizonte", "ninguno"] | None = None


class DayMoonOut(BaseModel):
    signo: str
    fase: str
    casa: int | None = None
    tema_casa: str | None = None


class DayTransitOut(BaseModel):
    planeta: str
    punto: str
    aspecto: str
    orbe: float
    fuerza: float
    exacto: date | None = None
    texto: str


class DayAreaOut(BaseModel):
    clave: str
    nombre: str
    estado: Literal["fluye", "cuidado", "tranquilo"]
    motivo: str | None = None


class DayReadingOut(BaseModel):
    texto: str
    ia: bool


class MyDayDetailOut(BaseModel):
    """Tu día completo (spec B4 v3)."""

    date: date
    luna: DayMoonOut
    transitos: list[DayTransitOut]
    areas: list[DayAreaOut]
    lectura: DayReadingOut
    pregunta: str
    aproximado: bool
    falta: Literal["hora", "lugar"] | None = None


class MyDayOut(BaseModel):
    """ "Tu día" (spec B4 v2)."""

    date: date
    aspect: str
    is_major: bool
    moon_sign: str
    title: str
    text: str
    reviewed: bool  # la biblioteca ya la revisó Pablo


class FrequencyCountOut(BaseModel):
    count: int


# Test de personalidad de Pablo (spec A6).
class PersonalityAnswersIn(BaseModel):
    answers: dict[str, list[int]]

    @field_validator("answers")
    @classmethod
    def valid_answers(cls, value: dict[str, list[int]]) -> dict[str, list[int]]:
        from app.personality.engine import load_config

        cfg = load_config()
        known = {q["id"] for q in cfg["questions"]}
        for qid, choices in value.items():
            if qid not in known:
                raise ValueError(f"pregunta desconocida: {qid}")
            if not 1 <= len(choices) <= cfg["max_choices"] or len(set(choices)) != len(choices):
                raise ValueError(f"{qid}: elegí 1 o {cfg['max_choices']} opciones distintas")
            if any(not 0 <= c <= 4 for c in choices):
                raise ValueError(f"{qid}: opción fuera de A-E")
        return value


class PersonalityMineOut(BaseModel):
    answers: dict[str, list[int]]
    completed: int
    total_questions: int
    # Spec A12: orden de los grupos según lo que busca y si aceptó el aviso del test.
    axis_order: list[str] = []
    privacy_accepted: bool = False


class PersonalityCompatOut(BaseModel):
    axes: dict[str, float | None]
    coverage: dict[str, float]
    flags: list[str]
    total: float | None
    complete: bool


class SystemOut(BaseModel):
    """Un sistema de compatibilidad (spec B9): su total con los pesos de Pablo para el vínculo y sus ejes."""

    total: int
    axes: dict[str, int | None]


class DiscoverCandidateOut(BaseModel):
    profile_id: uuid.UUID
    # Número global (spec B9, ADR 0014): promedio de los sistemas incluidos; compatibility_pct es el mismo.
    compatibility_pct: int
    global_pct: int = 0
    axes_global: dict[str, int | None] = {}
    systems: dict[str, SystemOut | None] = {}
    distance_km: int | None = None
    # Spec B10: intereses que coinciden con los de quien mira.
    common_interests: list[str] = []
    astrology_pct: int = 0
    preview: str
    # Motor de sinastría (spec B5-motor-sinastria.md): puntaje por eje y contexto.
    axes: dict[str, int] = {}
    relationship: str | None = None
    approximate: bool = False
    # Test de personalidad de Pablo (spec A6): separado de la astrología; None si alguno no respondió nada.
    personality: PersonalityCompatOut | None = None
    # Spec A10: marca "Verificado" (WhatsApp).
    verificado: bool = False
    # Perfil liviano (spec A4): solo datos públicos.
    display_name: str | None = None
    age: int | None = None
    sun_sign: str | None = None
    photo_url: str | None = None
    # Spec A11: todas sus fotos, la principal primero.
    photos: list[str] = []
    # Spec B8: solo si la persona eligió mostrar su género.
    gender_label: str | None = None
    avatar: str | None = None
    energy_period: str | None = None
    interests: list[str] = []
    bio: str | None = None
    neighborhood: str | None = None


class ExplanationOut(BaseModel):
    text: str


DayType = Literal["fluye", "desafia", "intenso", "tranquilo"]


class CalendarDayOut(BaseModel):
    date: date
    has_key_transit: bool
    tipo: DayType = "tranquilo"  # spec B11


class TransitOut(BaseModel):
    aspect: str
    title: str | None = None
    text: str | None = None


class UpcomingEventOut(BaseModel):
    start: date
    end: date
    aspect: str
    tipo: DayType = "tranquilo"  # spec B11
    title: str
    text: str


class CalendarDayDetailOut(BaseModel):
    # Las notas del día se sacaron (spec U2).
    transits: list[TransitOut]


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


class CompatibilityOut(BaseModel):
    relationship: str
    astrology: dict
    personality: "PersonalityCompatOut | None"


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


Relationship = Literal["pareja", "amistad", "laboral", "ocasional"]


class InvitationIn(BaseModel):
    # Spec C12: nombre y, si lo sabe, el signo. El tipo y el vínculo se deducen solos.
    inviter_id: uuid.UUID
    friend_name: str = Field(min_length=1, max_length=40)
    friend_sun_sign: (
        Literal[
            "Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
            "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis",
        ]
        | None
    ) = None


class InvitationPreviewOut(BaseModel):
    message: str


class PartialReportOut(BaseModel):
    teaser: str
    locked_fields: list[str]


class InvitationOut(BaseModel):
    message: str = ""  # texto que se manda por WhatsApp (para mostrarlo antes de enviar)
    ref_id: str
    whatsapp_url: str
    partial_report: PartialReportOut | None = None  # solo con el signo del amigo
    kind: str = "astro"


class InvitationAcceptOut(BaseModel):
    match_id: uuid.UUID


class MyInvitationOut(BaseModel):
    ref_id: str
    friend_name: str
    kind: str
    relationship: str | None
    status: Literal["enviada", "registrado", "test_completo"]
    match_id: uuid.UUID | None
    created_at: datetime


class InvitationPreloadOut(BaseModel):
    ref_id: str
    friend_name: str
    teaser: str
    kind: str = "astro"
    inviter_name: str | None = None
    relationship: str | None = None


class RevealOut(BaseModel):
    aspect: str
    percentage: int
    text: str


CompatibilityOut.model_rebuild()
