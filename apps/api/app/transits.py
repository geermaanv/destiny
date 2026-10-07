import calendar
from datetime import date

from app.aspects import angle_between, classify_aspect
from app.astro import moon_longitude
from app.compatibility import sun_longitude
from app.models import Profile


def day_transit(profile: Profile, day: date) -> dict:
    """Tránsito del día: Luna vs. Sol natal del usuario (simplificación v1,
    ver B6-calendario-memoria.md — una carta completa queda para después)."""
    aspect = classify_aspect(angle_between(moon_longitude(day), sun_longitude(profile.birth_date, profile.birth_time)))
    return {"date": day, "aspect": aspect["aspect"], "is_major": aspect["is_major"]}


def month_transits(profile: Profile, year: int, month: int) -> list[dict]:
    days_in_month = calendar.monthrange(year, month)[1]
    return [day_transit(profile, date(year, month, d)) for d in range(1, days_in_month + 1)]
