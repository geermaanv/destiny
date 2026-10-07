from datetime import date, datetime, timezone
from functools import lru_cache

import astronomy

ZODIAC_SIGNS = [
    "Aries", "Tauro", "Gemini", "Cáncer", "Leo", "Virgo",
    "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis",
]

# Nombre de fase lunar cada 45° de ángulo de fase (0 = luna nueva, 180 = luna llena).
MOON_PHASE_NAMES = [
    (0, "Luna nueva"),
    (45, "Luna creciente"),
    (90, "Cuarto creciente"),
    (135, "Luna gibosa creciente"),
    (180, "Luna llena"),
    (225, "Luna gibosa menguante"),
    (270, "Cuarto menguante"),
    (315, "Luna menguante"),
]


def zodiac_sign(ecliptic_longitude: float) -> str:
    return ZODIAC_SIGNS[int(ecliptic_longitude // 30) % 12]


def approximate_longitude_for_sign(sign: str) -> float:
    """Punto medio del signo (15°). Usado cuando solo se conoce el signo
    solar, no la fecha exacta (C8-invitacion-whatsapp.md: fricción mínima
    al invitar — el resultado es necesariamente aproximado/"borroso")."""
    index = ZODIAC_SIGNS.index(sign)
    return index * 30 + 15


@lru_cache(maxsize=32)
def moon_longitude(day: date) -> float:
    t = astronomy.Time.Make(day.year, day.month, day.day, 12, 0, 0)
    return astronomy.EclipticGeoMoon(t).lon


def moon_phase_name(phase_angle: float) -> str:
    closest = min(MOON_PHASE_NAMES, key=lambda entry: abs(entry[0] - phase_angle) % 360)
    return closest[1]


@lru_cache(maxsize=8)
def astro_weather_for_date(day: date) -> str:
    t = astronomy.Time.Make(day.year, day.month, day.day, 12, 0, 0)
    phase_angle = astronomy.MoonPhase(t)
    return f"{moon_phase_name(phase_angle)} en {zodiac_sign(moon_longitude(day))}"


def today_astro_weather() -> str:
    return astro_weather_for_date(datetime.now(timezone.utc).date())
