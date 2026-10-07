import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.compatibility import compatibility_signals
from app.database import get_db
from app.icebreaker import IcebreakerGenerator, get_icebreaker_generator
from app.models import ChatMessage, Match, Profile
from app.schemas import ChatMessageOut, MatchIn, MatchOut, SendMessageIn

router = APIRouter(tags=["matches"])


def _profile_payload(profile: Profile) -> dict:
    return {"birth_date": str(profile.birth_date), "birth_time": str(profile.birth_time)}


def _get_profile(profile_id: uuid.UUID, db: Session) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/matches", response_model=MatchOut, status_code=201)
def create_match(
    payload: MatchIn,
    db: Session = Depends(get_db),
    generator: IcebreakerGenerator = Depends(get_icebreaker_generator),
) -> MatchOut:
    profile_a = _get_profile(payload.profile_a_id, db)
    profile_b = _get_profile(payload.profile_b_id, db)
    if profile_a.birth_date is None or profile_b.birth_date is None:
        raise HTTPException(status_code=422, detail="Ambos perfiles necesitan datos natales")

    match = Match(profile_a_id=profile_a.id, profile_b_id=profile_b.id)
    db.add(match)
    db.flush()

    signals = compatibility_signals(profile_a, profile_b)
    icebreaker_text = generator.generate(_profile_payload(profile_a), _profile_payload(profile_b), signals)

    message = ChatMessage(match_id=match.id, sender="system_icebreaker", text=icebreaker_text)
    db.add(message)
    db.commit()

    return MatchOut(id=match.id, icebreaker=icebreaker_text)


@router.get("/chats/{match_id}/messages", response_model=list[ChatMessageOut])
def list_messages(match_id: uuid.UUID, db: Session = Depends(get_db)) -> list[ChatMessageOut]:
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")

    messages = db.scalars(
        select(ChatMessage).where(ChatMessage.match_id == match_id).order_by(ChatMessage.created_at)
    ).all()
    return [ChatMessageOut(sender=m.sender, text=m.text, created_at=m.created_at) for m in messages]


@router.post("/chats/{match_id}/messages", response_model=ChatMessageOut, status_code=201)
def send_message(match_id: uuid.UUID, payload: SendMessageIn, db: Session = Depends(get_db)) -> ChatMessageOut:
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")

    message = ChatMessage(match_id=match_id, sender=str(payload.profile_id), text=payload.text)
    db.add(message)
    db.commit()
    db.refresh(message)
    return ChatMessageOut(sender=message.sender, text=message.text, created_at=message.created_at)
