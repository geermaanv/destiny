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


def moon_phase_name(phase_angle: float) -> str:
    closest = min(MOON_PHASE_NAMES, key=lambda entry: abs(entry[0] - phase_angle) % 360)
    return closest[1]


@lru_cache(maxsize=8)
def astro_weather_for_date(day: date) -> str:
    time = astronomy.Time.Make(day.year, day.month, day.day, 12, 0, 0)
    moon_lon = astronomy.EclipticGeoMoon(time).lon
    phase_angle = astronomy.MoonPhase(time)
    return f"{moon_phase_name(phase_angle)} en {zodiac_sign(moon_lon)}"


def today_astro_weather() -> str:
    return astro_weather_for_date(datetime.now(timezone.utc).date())
