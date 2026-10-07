import uuid
from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, Float, String, Time
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


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_a_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    profile_b_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    sender: Mapped[str] = mapped_column(String, nullable=False)  # profile_id como str, o "system_icebreaker"
    text: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
