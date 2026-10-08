import calendar
from datetime import date, timedelta

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


# Qué significa cada tránsito Luna vs. Sol natal, en lenguaje simple (B6).
TRANSIT_TEXT = {
    "conjunción": ("La Luna en tu signo", "Día para empezar cosas y mostrarte: tu energía y tus emociones van juntas."),
    "sextil": ("Día fluido", "Buen momento para conectar, proponer y conocer gente."),
    "cuadratura": ("Día de tensión", "Las emociones pueden chocar con lo que querés: bueno para resolver, no para forzar."),
    "trígono": ("Día armónico", "Todo fluye más fácil: disfrutá, compartí y aprovechá para vincularte."),
    "oposición": ("Tu luna llena personal", "Emociones a flor de piel y foco en los otros: ideal para charlas importantes."),
}

UPCOMING_HORIZON_DAYS = 120


def upcoming_events(profile: Profile, start: date, limit: int = 10) -> list[dict]:
    """Próximos tránsitos importantes desde `start`, agrupando los días seguidos
    con el mismo aspecto en un solo evento (la Luna tarda ~1-2 días en pasar)."""
    events: list[dict] = []
    current: dict | None = None
    for offset in range(UPCOMING_HORIZON_DAYS):
        day = start + timedelta(days=offset)
        transit = day_transit(profile, day)
        if not transit["is_major"]:
            current = None
            continue
        if current and current["aspect"] == transit["aspect"] and current["end"] == day - timedelta(days=1):
            current["end"] = day
            continue
        if len(events) == limit:
            break
        title, text = TRANSIT_TEXT.get(transit["aspect"], (transit["aspect"].capitalize(), ""))
        current = {"start": day, "end": day, "aspect": transit["aspect"], "title": title, "text": text}
        events.append(current)
    return events
