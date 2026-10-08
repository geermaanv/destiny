import uuid
from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String, Time
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    birth_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    birth_time_estimated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    birth_place_query: Mapped[str | None] = mapped_column(String, nullable=True)
    birth_place_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    birth_place_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    birth_place_timezone: Mapped[str | None] = mapped_column(String, nullable=True)

    notification_rhythm: Mapped[str | None] = mapped_column(String, nullable=True)

    verification_status: Mapped[str] = mapped_column(String, default="pendiente", nullable=False)
    verification_id: Mapped[str | None] = mapped_column(String, nullable=True)
    verification_method: Mapped[str | None] = mapped_column(String, nullable=True)  # "whatsapp" (v1) | "kyc_video" (v2)
    # Teléfono verificado por WhatsApp, E.164. Nunca se expone a otros usuarios.
    phone_e164: Mapped[str | None] = mapped_column(String, nullable=True, unique=True)
    # Perfil liviano (spec A4). Lo ven otros usuarios; nunca teléfono ni datos natales exactos.
    display_name: Mapped[str | None] = mapped_column(String, nullable=True)
    bio: Mapped[str | None] = mapped_column(String, nullable=True)
    neighborhood: Mapped[str | None] = mapped_column(String, nullable=True)
    energy_period: Mapped[str | None] = mapped_column(String, nullable=True)
    interests: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    avatar: Mapped[str | None] = mapped_column(String, nullable=True)
    photo_path: Mapped[str | None] = mapped_column(String, nullable=True)

    @property
    def has_photo(self) -> bool:
        return self.photo_path is not None

    # Si la verificación dio duplicado_detectado: el perfil que ya tiene ese número.
    duplicate_of_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)


class PhoneVerificationCode(Base):
    __tablename__ = "phone_verification_codes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Sin profile_id cuando es un código de "Ya tengo cuenta" (purpose="login", spec A5).
    profile_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=True)
    purpose: Mapped[str] = mapped_column(String, default="verify", nullable=False)  # "verify" | "login"
    code: Mapped[str] = mapped_column(String, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Spec A5: solo el navegador que pidió el código (y recibió este comprobante) puede tomar la sesión.
    claim_token_hash: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Perfil con el que se entra una vez que llegó el mensaje; outcome del login: "listo" | "sin_cuenta".
    result_profile_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    outcome: Mapped[str | None] = mapped_column(String, nullable=True)


class UserSession(Base):
    """Sesión del navegador (spec A5). Se guarda solo el hash del token de la cookie."""

    __tablename__ = "sessions"

    token_hash: Mapped[str] = mapped_column(String, primary_key=True)
    profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CalendarAnnotation(Base):
    __tablename__ = "calendar_annotations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    day: Mapped[date] = mapped_column(Date, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MoodCheckin(Base):
    __tablename__ = "mood_checkins"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    mood: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Invitation(Base):
    __tablename__ = "invitations"

    ref_id: Mapped[str] = mapped_column(String, primary_key=True)
    inviter_profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    friend_name: Mapped[str] = mapped_column(String, nullable=False)
    friend_sun_sign: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # profile_a pidió la conexión, profile_b la recibe (spec B7 v2).
    profile_a_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    profile_b_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String, default="pendiente", nullable=False)  # pendiente|aceptada|rechazada|bloqueada
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # "Pasar a WhatsApp": cada uno da su OK; con los dos se revelan los números.
    whatsapp_a_ok: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    whatsapp_b_ok: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    whatsapp_shared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    blocked_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    sender: Mapped[str] = mapped_column(String, nullable=False)  # profile_id como str, o "system_icebreaker"
    text: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
