import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CalendarAnnotation, Profile
from app.schemas import AnnotationIn, AnnotationOut, CalendarDayDetailOut, CalendarDayOut, TransitOut
from app.transits import day_transit, month_transits

router = APIRouter(prefix="/calendar", tags=["calendar"])


def _get_profile_or_404(profile_id: uuid.UUID, db: Session) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.birth_date is None or profile.birth_time is None:
        raise HTTPException(status_code=422, detail="Perfil sin datos natales")
    return profile


@router.get("/day/{day}", response_model=CalendarDayDetailOut)
def get_day(day: date, profile_id: uuid.UUID = Query(...), db: Session = Depends(get_db)) -> CalendarDayDetailOut:
    profile = _get_profile_or_404(profile_id, db)
    transit = day_transit(profile, day)

    annotations = db.scalars(
        select(CalendarAnnotation)
        .where(CalendarAnnotation.profile_id == profile_id, CalendarAnnotation.day == day)
        .order_by(CalendarAnnotation.created_at)
    ).all()

    return CalendarDayDetailOut(
        transits=[TransitOut(aspect=transit["aspect"])],
        annotations=[AnnotationOut(text=a.text, created_at=a.created_at) for a in annotations],
    )


@router.post("/day/{day}/annotations", response_model=AnnotationOut, status_code=201)
def create_annotation(day: date, payload: AnnotationIn, db: Session = Depends(get_db)) -> AnnotationOut:
    annotation = CalendarAnnotation(profile_id=payload.profile_id, day=day, text=payload.text)
    db.add(annotation)
    db.commit()
    db.refresh(annotation)
    return AnnotationOut(text=annotation.text, created_at=annotation.created_at)


@router.get("/{year}/{month}", response_model=list[CalendarDayOut])
def get_month(
    year: int, month: int, profile_id: uuid.UUID = Query(...), db: Session = Depends(get_db)
) -> list[CalendarDayOut]:
    profile = _get_profile_or_404(profile_id, db)
    transits = month_transits(profile, year, month)
    return [CalendarDayOut(date=t["date"], has_key_transit=t["is_major"]) for t in transits]
