import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_self, session_profile_id
from app.database import get_db
from app.models import CalendarAnnotation, Profile
from app.schemas import (
    AnnotationIn,
    AnnotationOut,
    CalendarDayDetailOut,
    CalendarDayOut,
    TransitOut,
    UpcomingEventOut,
)
from app.transits import TRANSIT_TEXT, day_transit, month_transits, upcoming_events

router = APIRouter(prefix="/calendar", tags=["calendar"])


def _get_profile_or_404(profile_id: uuid.UUID, db: Session) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.birth_date is None or profile.birth_time is None:
        raise HTTPException(status_code=422, detail="Perfil sin datos natales")
    return profile


@router.get("/upcoming", response_model=list[UpcomingEventOut])
def get_upcoming(
    profile_id: uuid.UUID = Query(...),
    from_date: date | None = Query(default=None, alias="from"),
    limit: int = Query(default=10, ge=1, le=30),
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> list[UpcomingEventOut]:
    """Próximos tránsitos importantes desde hoy (o `from`, la fecha local del usuario)."""
    require_self(profile_id, current)
    profile = _get_profile_or_404(profile_id, db)
    events = upcoming_events(profile, from_date or date.today(), limit)
    if not events:
        return []

    noted_days = set(
        db.scalars(
            select(CalendarAnnotation.day).where(
                CalendarAnnotation.profile_id == profile_id,
                CalendarAnnotation.day >= events[0]["start"],
                CalendarAnnotation.day <= events[-1]["end"],
            )
        )
    )
    return [
        UpcomingEventOut(
            **e, has_notes=any(e["start"] <= d <= e["end"] for d in noted_days)
        )
        for e in events
    ]


@router.get("/day/{day}", response_model=CalendarDayDetailOut)
def get_day(
    day: date, profile_id: uuid.UUID = Query(...), db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> CalendarDayDetailOut:
    require_self(profile_id, current)
    profile = _get_profile_or_404(profile_id, db)
    transit = day_transit(profile, day)

    annotations = db.scalars(
        select(CalendarAnnotation)
        .where(CalendarAnnotation.profile_id == profile_id, CalendarAnnotation.day == day)
        .order_by(CalendarAnnotation.created_at)
    ).all()

    return CalendarDayDetailOut(
        transits=[
            TransitOut(
                aspect=transit["aspect"],
                title=TRANSIT_TEXT.get(transit["aspect"], (None, None))[0],
                text=TRANSIT_TEXT.get(transit["aspect"], (None, None))[1],
            )
        ],
        annotations=[AnnotationOut(text=a.text, created_at=a.created_at) for a in annotations],
    )


@router.post("/day/{day}/annotations", response_model=AnnotationOut, status_code=201)
def create_annotation(
    day: date, payload: AnnotationIn, db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> AnnotationOut:
    require_self(payload.profile_id, current)
    annotation = CalendarAnnotation(profile_id=payload.profile_id, day=day, text=payload.text)
    db.add(annotation)
    db.commit()
    db.refresh(annotation)
    return AnnotationOut(text=annotation.text, created_at=annotation.created_at)


@router.get("/{year}/{month}", response_model=list[CalendarDayOut])
def get_month(
    year: int,
    month: int,
    profile_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> list[CalendarDayOut]:
    require_self(profile_id, current)
    profile = _get_profile_or_404(profile_id, db)
    transits = month_transits(profile, year, month)
    return [CalendarDayOut(date=t["date"], has_key_transit=t["is_major"]) for t in transits]
