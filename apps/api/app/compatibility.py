from datetime import date, time

import astronomy

from app.aspects import angle_between, classify_aspect
from app.models import Profile

# v1: solo Sol-Sol, simplificación deliberada (ver B5-pantalla-descubrir.md
# y BACKLOG.md) — una carta completa (Luna, Venus, Marte, ascendente) queda
# para una iteración posterior, no es necesaria para validar el mecanismo.


def sun_longitude(birth_date: date, birth_time: time) -> float:
    t = astronomy.Time.Make(birth_date.year, birth_date.month, birth_date.day, birth_time.hour, birth_time.minute, 0)
    return astronomy.SunPosition(t).elon


def compatibility_signals(a: Profile, b: Profile) -> dict:
    lon_a = sun_longitude(a.birth_date, a.birth_time)
    lon_b = sun_longitude(b.birth_date, b.birth_time)
    return classify_aspect(angle_between(lon_a, lon_b))
