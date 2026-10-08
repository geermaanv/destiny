import uuid
from datetime import datetime, timezone
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.auth import require_self, session_profile_id
from app.compatibility import compatibility_signals
from app.database import get_db
from app.icebreaker import IcebreakerGenerator, get_icebreaker_generator
from app.models import ChatMessage, Match, Profile
from app.public_profile import public_fields
from app.schemas import (
    ChatMessageOut,
    ConnectionOut,
    MatchIn,
    MatchOut,
    ProfileRefIn,
    PublicProfileOut,
    SendMessageIn,
    WhatsappHandoffOut,
)

# Conexión mutua + chat con rompehielos + paso a WhatsApp (spec B7 v2).
router = APIRouter(tags=["matches"])


def _profile_payload(profile: Profile) -> dict:
    return {"birth_date": str(profile.birth_date), "birth_time": str(profile.birth_time)}


def _get_profile(profile_id: uuid.UUID, db: Session) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


def _get_own_match(match_id: uuid.UUID, current: uuid.UUID | None, db: Session) -> Match:
    """Una conexión solo la ven sus dos participantes (spec A5)."""
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    if current is None:
        raise HTTPException(status_code=401, detail="Necesitás iniciar sesión")
    if current not in (match.profile_a_id, match.profile_b_id):
        raise HTTPException(status_code=403, detail="No participás de este chat")
    return match


def _other_id(match: Match, me: uuid.UUID) -> uuid.UUID:
    return match.profile_b_id if match.profile_a_id == me else match.profile_a_id


def _whatsapp_state(match: Match, me: uuid.UUID, db: Session) -> WhatsappHandoffOut:
    me_is_a = match.profile_a_id == me
    me_ok = match.whatsapp_a_ok if me_is_a else match.whatsapp_b_ok
    other_ok = match.whatsapp_b_ok if me_is_a else match.whatsapp_a_ok
    link = None
    if me_ok and other_ok:
        me_profile = db.get(Profile, me)
        other = db.get(Profile, _other_id(match, me))
        if other and other.phone_e164:
            name = (me_profile.display_name if me_profile else None) or "alguien"
            greeting = quote(f"¡Hola! Soy {name}, nos conocimos en Destiny ✨")
            link = f"https://wa.me/{other.phone_e164.lstrip('+')}?text={greeting}"
    return WhatsappHandoffOut(me_ok=me_ok, other_ok=other_ok, link=link)


def _connection_out(match: Match, me: uuid.UUID, db: Session) -> ConnectionOut:
    other = db.get(Profile, _other_id(match, me))
    fields = public_fields(other) if other else {}
    last = db.scalars(
        select(ChatMessage).where(ChatMessage.match_id == match.id).order_by(ChatMessage.created_at.desc()).limit(1)
    ).first()
    return ConnectionOut(
        match_id=match.id,
        status=match.status,
        direction="enviada" if match.profile_a_id == me else "recibida",
        other=PublicProfileOut(
            profile_id=_other_id(match, me),
            **{k: fields.get(k) for k in ("display_name", "age", "sun_sign", "photo_url", "avatar")},
        ),
        last_message=last.text if last and match.status == "aceptada" else None,
        last_message_at=last.created_at if last and match.status == "aceptada" else None,
        whatsapp=_whatsapp_state(match, me, db),
    )


@router.post("/matches", response_model=MatchOut, status_code=201)
def create_match(
    payload: MatchIn,
    db: Session = Depends(get_db),
    generator: IcebreakerGenerator = Depends(get_icebreaker_generator),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> MatchOut:
    """"Conectar": crea la solicitud, o la acepta si la otra persona ya había pedido."""
    require_self(payload.profile_a_id, current)
    if payload.profile_a_id == payload.profile_b_id:
        raise HTTPException(status_code=422, detail="No podés conectar con vos mismo")
    profile_a = _get_profile(payload.profile_a_id, db)
    profile_b = _get_profile(payload.profile_b_id, db)
    if profile_a.birth_date is None or profile_b.birth_date is None:
        raise HTTPException(status_code=422, detail="Ambos perfiles necesitan datos natales")

    existing = db.scalars(
        select(Match).where(
            or_(
                and_(Match.profile_a_id == profile_a.id, Match.profile_b_id == profile_b.id),
                and_(Match.profile_a_id == profile_b.id, Match.profile_b_id == profile_a.id),
            )
        )
    ).first()
    if existing is not None:
        if existing.status == "bloqueada":
            raise HTTPException(status_code=409, detail="Esta conexión no está disponible")
        if existing.status == "pendiente" and existing.profile_b_id == profile_a.id:
            # Las dos personas se pidieron conexión: se acepta sola.
            existing.status = "aceptada"
            existing.accepted_at = datetime.now(timezone.utc)
            db.commit()
        icebreaker = db.scalars(
            select(ChatMessage.text).where(
                ChatMessage.match_id == existing.id, ChatMessage.sender == "system_icebreaker"
            )
        ).first()
        return MatchOut(id=existing.id, icebreaker=icebreaker or "", status=existing.status)

    match = Match(profile_a_id=profile_a.id, profile_b_id=profile_b.id, status="pendiente")
    db.add(match)
    db.flush()

    signals = compatibility_signals(profile_a, profile_b)
    icebreaker_text = generator.generate(_profile_payload(profile_a), _profile_payload(profile_b), signals)
    db.add(ChatMessage(match_id=match.id, sender="system_icebreaker", text=icebreaker_text))
    db.commit()

    return MatchOut(id=match.id, icebreaker=icebreaker_text, status=match.status)


@router.get("/connections", response_model=list[ConnectionOut])
def list_connections(
    profile_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> list[ConnectionOut]:
    require_self(profile_id, current)
    matches = db.scalars(
        select(Match)
        .where(
            or_(Match.profile_a_id == profile_id, Match.profile_b_id == profile_id),
            Match.status.in_(("pendiente", "aceptada")),
        )
        .order_by(Match.created_at.desc())
    ).all()
    return [_connection_out(m, profile_id, db) for m in matches]


@router.get("/matches/{match_id}", response_model=ConnectionOut)
def get_match(
    match_id: uuid.UUID, db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> ConnectionOut:
    match = _get_own_match(match_id, current, db)
    return _connection_out(match, current, db)


def _respond(match_id: uuid.UUID, payload: ProfileRefIn, current: uuid.UUID | None, db: Session, accept: bool):
    require_self(payload.profile_id, current)
    match = _get_own_match(match_id, current, db)
    if match.profile_b_id != current or match.status != "pendiente":
        raise HTTPException(status_code=409, detail="No hay una solicitud pendiente para responder")
    match.status = "aceptada" if accept else "rechazada"
    if accept:
        match.accepted_at = datetime.now(timezone.utc)
    db.commit()
    return _connection_out(match, current, db)


@router.post("/matches/{match_id}/accept", response_model=ConnectionOut)
def accept_match(
    match_id: uuid.UUID,
    payload: ProfileRefIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> ConnectionOut:
    return _respond(match_id, payload, current, db, accept=True)


@router.post("/matches/{match_id}/reject", response_model=ConnectionOut)
def reject_match(
    match_id: uuid.UUID,
    payload: ProfileRefIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> ConnectionOut:
    return _respond(match_id, payload, current, db, accept=False)


@router.post("/matches/{match_id}/block", response_model=ConnectionOut)
def block_match(
    match_id: uuid.UUID,
    payload: ProfileRefIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> ConnectionOut:
    require_self(payload.profile_id, current)
    match = _get_own_match(match_id, current, db)
    match.status = "bloqueada"
    match.blocked_by = current
    db.commit()
    return _connection_out(match, current, db)


@router.post("/matches/{match_id}/whatsapp", response_model=ConnectionOut)
def agree_whatsapp(
    match_id: uuid.UUID,
    payload: ProfileRefIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> ConnectionOut:
    """"Pasar a WhatsApp": registra mi OK; con los dos, se revela el link al número del otro."""
    require_self(payload.profile_id, current)
    match = _get_own_match(match_id, current, db)
    if match.status != "aceptada":
        raise HTTPException(status_code=409, detail="La conexión no está activa")
    if match.profile_a_id == current:
        match.whatsapp_a_ok = True
    else:
        match.whatsapp_b_ok = True
    if match.whatsapp_a_ok and match.whatsapp_b_ok and match.whatsapp_shared_at is None:
        match.whatsapp_shared_at = datetime.now(timezone.utc)
    db.commit()
    return _connection_out(match, current, db)


@router.get("/chats/{match_id}/messages", response_model=list[ChatMessageOut])
def list_messages(
    match_id: uuid.UUID, db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> list[ChatMessageOut]:
    match = _get_own_match(match_id, current, db)
    if match.status != "aceptada":
        return []

    messages = db.scalars(
        select(ChatMessage).where(ChatMessage.match_id == match_id).order_by(ChatMessage.created_at)
    ).all()
    return [ChatMessageOut(sender=m.sender, text=m.text, created_at=m.created_at) for m in messages]


@router.post("/chats/{match_id}/messages", response_model=ChatMessageOut, status_code=201)
def send_message(
    match_id: uuid.UUID,
    payload: SendMessageIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> ChatMessageOut:
    require_self(payload.profile_id, current)
    match = _get_own_match(match_id, current, db)
    if match.status != "aceptada":
        raise HTTPException(status_code=409, detail="Solo se puede escribir con la conexión aceptada")
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Mensaje vacío")

    message = ChatMessage(match_id=match_id, sender=str(payload.profile_id), text=text[:1000])
    db.add(message)
    db.commit()
    db.refresh(message)
    return ChatMessageOut(sender=message.sender, text=message.text, created_at=message.created_at)
