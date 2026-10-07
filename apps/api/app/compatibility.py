from datetime import date, time

import astronomy

from app.models import Profile

# Aspectos mayores (grado, nombre, orbe de tolerancia, % de compatibilidad base).
# v1: solo Sol-Sol, simplificación deliberada (ver B5-pantalla-descubrir.md
# y BACKLOG.md) — una carta completa (Luna, Venus, Marte, ascendente) queda
# para una iteración posterior, no es necesaria para validar el mecanismo.
ASPECTS = [
    (0, "conjunción", 8, 90),
    (60, "sextil", 6, 75),
    (90, "cuadratura", 6, 45),
    (120, "trígono", 8, 85),
    (180, "oposición", 8, 50),
]
DEFAULT_ASPECT = ("sin aspecto mayor", 60)


def sun_longitude(birth_date: date, birth_time: time) -> float:
    t = astronomy.Time.Make(birth_date.year, birth_date.month, birth_date.day, birth_time.hour, birth_time.minute, 0)
    return astronomy.SunPosition(t).elon


def compatibility_signals(a: Profile, b: Profile) -> dict:
    lon_a = sun_longitude(a.birth_date, a.birth_time)
    lon_b = sun_longitude(b.birth_date, b.birth_time)
    diff = abs(lon_a - lon_b) % 360
    if diff > 180:
        diff = 360 - diff

    for degree, name, orb, percentage in ASPECTS:
        if abs(diff - degree) <= orb:
            return {"aspect": name, "angle": round(diff, 1), "percentage": percentage}

    name, percentage = DEFAULT_ASPECT
    return {"aspect": name, "angle": round(diff, 1), "percentage": percentage}
