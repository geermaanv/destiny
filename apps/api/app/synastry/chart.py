"""Carta natal completa para la sinastría (spec B5-motor-sinastria.md).

Posiciones eclípticas geocéntricas con astronomy-engine (ADR 0005), ascendente
y medio cielo a partir de la hora sideral local, y casas iguales desde el
ascendente (sistema configurable a futuro; Placidus no está definido por
encima de ~66° de latitud).
"""

import math
from dataclasses import dataclass
from datetime import date, datetime, time
from functools import lru_cache
from zoneinfo import ZoneInfo

import astronomy

DEFAULT_TIMEZONE = "America/Argentina/Buenos_Aires"

BODIES = {
    "mercurio": astronomy.Body.Mercury,
    "venus": astronomy.Body.Venus,
    "marte": astronomy.Body.Mars,
    "jupiter": astronomy.Body.Jupiter,
    "saturno": astronomy.Body.Saturn,
    "urano": astronomy.Body.Uranus,
    "neptuno": astronomy.Body.Neptune,
    "pluton": astronomy.Body.Pluto,
}


@dataclass(frozen=True)
class Chart:
    points: dict[str, float]  # longitud eclíptica 0-360 de cada planeta (y "asc"/"mc" si se conoce el lugar)
    houses: tuple[float, ...] | None  # 12 cúspides; None sin lugar de nacimiento
    time_known: bool  # False si la hora es estimada (12:00 o franja del día, spec A1)

    def sign(self, point: str) -> int | None:
        lon = self.points.get(point)
        return None if lon is None else int(lon // 30) % 12

    def house_of(self, lon: float) -> int | None:
        """Casa (1-12) en la que cae una longitud, según las cúspides de esta carta."""
        if self.houses is None:
            return None
        for i in range(12):
            start, end = self.houses[i], self.houses[(i + 1) % 12]
            span = (end - start) % 360
            if (lon - start) % 360 < span:
                return i + 1
        return 12


def _norm(deg: float) -> float:
    return deg % 360


def _obliquity(t: astronomy.Time) -> float:
    centuries = t.tt / 36525.0
    return 23.439291 - 0.0130042 * centuries


def _ascendant_mc(t: astronomy.Time, lat: float, lon: float) -> tuple[float, float]:
    ramc = math.radians(_norm((astronomy.SiderealTime(t) + lon / 15.0) * 15.0))
    eps = math.radians(_obliquity(t))
    phi = math.radians(lat)
    mc = math.degrees(math.atan2(math.sin(ramc), math.cos(ramc) * math.cos(eps)))
    asc = math.degrees(
        math.atan2(math.cos(ramc), -(math.sin(ramc) * math.cos(eps) + math.tan(phi) * math.sin(eps)))
    )
    return _norm(asc), _norm(mc)


@lru_cache(maxsize=2048)
def compute_chart(
    birth_date: date,
    birth_time: time,
    time_known: bool,
    lat: float | None,
    lon: float | None,
    timezone: str | None,
) -> Chart:
    local = datetime.combine(birth_date, birth_time, tzinfo=ZoneInfo(timezone or DEFAULT_TIMEZONE))
    utc = local.astimezone(ZoneInfo("UTC"))
    t = astronomy.Time.Make(utc.year, utc.month, utc.day, utc.hour, utc.minute, utc.second)

    points = {
        "sol": _norm(astronomy.SunPosition(t).elon),
        "luna": _norm(astronomy.EclipticGeoMoon(t).lon),
    }
    for name, body in BODIES.items():
        points[name] = _norm(astronomy.Ecliptic(astronomy.GeoVector(body, t, True)).elon)

    houses = None
    if lat is not None and lon is not None:
        asc, mc = _ascendant_mc(t, lat, lon)
        points["asc"] = asc
        points["mc"] = mc
        houses = tuple(_norm(asc + 30 * i) for i in range(12))  # casas iguales

    return Chart(points=points, houses=houses, time_known=time_known)


def chart_for_profile(profile) -> Chart:
    return compute_chart(
        profile.birth_date,
        profile.birth_time or time(12, 0),
        not profile.birth_time_estimated,
        profile.birth_place_lat,
        profile.birth_place_lon,
        profile.birth_place_timezone,
    )
