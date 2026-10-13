"""Carta natal completa para el motor oficial (spec A7).

Posiciones eclípticas geocéntricas con astronomy-engine (ADR 0005), Nodo Norte
verdadero (osculante) y medio, ascendente y medio cielo a partir de la hora
sideral local, y casas por signo entero (las de las calculadoras de Pablo).
Sin hora exacta (franja o desconocida) NO hay ascendente, medio cielo ni casas:
el motor de Pablo prohíbe inventarlos.
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
    points: dict[str, float]  # longitud 0-360 de planetas y nodos (y "asc"/"mc" con hora exacta y lugar)
    houses: tuple[float, ...] | None  # 12 cúspides por signo entero; None sin hora exacta o sin lugar
    time_known: bool  # False si la hora es estimada (franja del día o desconocida → mediodía, spec A7)

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


def _true_node(t: astronomy.Time) -> float:
    """Nodo Norte verdadero (osculante): nodo ascendente del plano de la órbita lunar instantánea."""
    s = astronomy.RotateState(astronomy.Rotation_EQJ_ECT(t), astronomy.GeoMoonState(t))
    hx = s.y * s.vz - s.z * s.vy
    hy = s.z * s.vx - s.x * s.vz
    return _norm(math.degrees(math.atan2(hx, -hy)))


def _mean_node(t: astronomy.Time) -> float:
    """Nodo Norte medio (Meeus, cap. 47)."""
    c = t.tt / 36525.0
    return _norm(125.0445479 - 1934.1362891 * c + 0.0020754 * c**2 + c**3 / 467441 - c**4 / 60616000)


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
    points["nodo_norte"] = _true_node(t)
    points["nodo_sur"] = _norm(points["nodo_norte"] + 180)
    points["nodo_medio"] = _mean_node(t)

    houses = None
    if time_known and lat is not None and lon is not None:
        asc, mc = _ascendant_mc(t, lat, lon)
        points["asc"] = asc
        points["mc"] = mc
        houses = tuple(30.0 * ((int(asc // 30) + i) % 12) for i in range(12))  # signo entero

    return Chart(points=points, houses=houses, time_known=time_known)


def chart_for_profile(profile) -> Chart:
    return compute_chart(
        profile.birth_date,
        profile.birth_time or time(12, 30),  # sin hora ni franja: franja mediodía (spec A7)
        not profile.birth_time_estimated,
        profile.birth_place_lat,
        profile.birth_place_lon,
        profile.birth_place_timezone,
    )
