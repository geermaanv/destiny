"""Tu día completo (spec B4 v3): el motor calcula clima, tránsitos y áreas; la IA solo redacta.

Orbes, pesos, áreas, temas de casas y preguntas en config/dia_v1.json.
"""

import json
from datetime import date, time, timedelta
from functools import lru_cache
from pathlib import Path

import astronomy

from app.astro import ZODIAC_SIGNS, moon_phase_name
from app.explainer import Written
from app.llm import complete, is_configured
from app.synastry.chart import Chart, chart_for_profile, compute_chart

CONFIG_PATH = Path(__file__).parent / "config" / "dia_v1.json"

GUIDELINE = (
    "Sos la voz editorial de Destiny, una app argentina de autoconocimiento con astrología. Escribí en castellano "
    "rioplatense, con voseo, cálido y concreto, sin jerga difícil. Te doy el día de una persona ya calculado: la Luna "
    "(signo, fase y el área de su vida por donde pasa), sus tránsitos más fuertes y cómo está cada área. Escribí una "
    "lectura de 3 a 5 oraciones (máximo 100 palabras) que los integre y termine con algo práctico para hoy. No agregues "
    "nada que no esté en los datos. Nada de predicciones cerradas ni miedo: es una lectura simbólica para orientarse. "
    "No menciones que sos una IA. Texto plano, sin markdown. Respondé solo con el texto."
)


@lru_cache(maxsize=1)
def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def _angle(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


def sky_for(day: date) -> Chart:
    """Planetas del día a las 12:00 UTC (como "Tu día")."""
    return compute_chart(day, time(12, 0), False, None, None, "UTC")


def _aspect(sep: float, cfg: dict, orb: float) -> tuple[str, float] | None:
    found = [(abs(sep - a["angulo"]), k) for k, a in cfg["aspectos"].items() if abs(sep - a["angulo"]) <= orb]
    if not found:
        return None
    diff, key = min(found)
    return key, diff


def _tone(planet: str, aspect: str, cfg: dict) -> int:
    if aspect == "conjuncion":
        return cfg["conjuncion_por_planeta"].get(planet, 0)
    return cfg["aspectos"][aspect]["tono"]


def _exact_day(planet: str, natal_lon: float, angle: float, day: date, cfg: dict) -> date | None:
    """Día dentro de la ventana en que el aspecto queda más exacto (si no es un borde de la ventana)."""
    if planet == "luna":
        return None
    window = cfg["ventana_exacto_dias"]
    days = [day + timedelta(days=d) for d in range(-window, window + 1)]
    diffs = [abs(_angle(sky_for(d).points[planet], natal_lon) - angle) for d in days]
    best = min(range(len(days)), key=diffs.__getitem__)
    return days[best] if 0 < best < len(days) - 1 else None


def transits(natal: Chart, sky: Chart, day: date, cfg: dict) -> list[dict]:
    names = cfg["nombres"]
    found = []
    for planet in cfg["planetas_del_dia"]:
        for point in cfg["puntos_natales"]:
            if point not in natal.points:
                continue
            sep = _angle(sky.points[planet], natal.points[point])
            hit = _aspect(sep, cfg, cfg["orbes"][planet])
            if hit is None:
                continue
            aspect, orb = hit
            closeness = 1 - orb / cfg["orbes"][planet] if cfg["orbes"][planet] else 0
            strength = cfg["peso_planeta"][planet] * cfg["peso_punto"][point] * closeness
            found.append({
                "planeta": planet, "punto": point, "aspecto": aspect, "orbe": orb, "fuerza": round(strength, 4),
                "tono": _tone(planet, aspect, cfg),
                "texto": (
                    f"{names[planet]['planeta']} {cfg['aspectos'][aspect]['verbo']} {names[point]['punto']}: "
                    f"{names[planet]['palabra']} y {names[point]['palabra']}."
                ),
            })
    found.sort(key=lambda t: -t["fuerza"])
    for t in found[: cfg["maximo_transitos"]]:
        exact = _exact_day(t["planeta"], natal.points[t["punto"]], cfg["aspectos"][t["aspecto"]]["angulo"], day, cfg)
        t["exacto"] = exact.isoformat() if exact else None
    return found


def areas(all_transits: list[dict], cfg: dict) -> list[dict]:
    out = []
    for key, area in cfg["areas"].items():
        touching = [t for t in all_transits if t["punto"] in area["puntos"] or t["planeta"] in area["planetas"]]
        score = sum(t["tono"] * t["fuerza"] for t in touching) / (sum(t["fuerza"] for t in touching) or 1)
        threshold = cfg["umbral_estado"]
        state = "fluye" if score >= threshold else "cuidado" if score <= -threshold else "tranquilo"
        main = max(touching, key=lambda t: t["fuerza"], default=None)
        out.append({"clave": key, "nombre": area["nombre"], "estado": state, "motivo": main["texto"] if main else None})
    return out


def day_detail(profile, day: date) -> dict:
    cfg = load_config()
    natal = chart_for_profile(profile)
    sky = sky_for(day)
    moon = sky.points["luna"]
    phase = moon_phase_name(astronomy.MoonPhase(astronomy.Time.Make(day.year, day.month, day.day, 12, 0, 0)))
    house = natal.house_of(moon) if natal.houses else None
    all_transits = transits(natal, sky, day, cfg)
    area_list = areas(all_transits, cfg)
    active = max(
        (a for a in area_list if a["estado"] != "tranquilo"),
        key=lambda a: sum(t["fuerza"] for t in all_transits if t["texto"] == a["motivo"]),
        default=None,
    )
    return {
        "date": day,
        "luna": {
            "signo": ZODIAC_SIGNS[int(moon // 30)],
            "fase": phase,
            "casa": house,
            "tema_casa": cfg["temas_casas"][str(house)] if house else None,
        },
        "transitos": [{k: v for k, v in t.items() if k != "tono"} for t in all_transits[: cfg["maximo_transitos"]]],
        "areas": area_list,
        "pregunta": cfg["preguntas"][active["clave"] if active else "tranquilo"],
        "aproximado": not natal.time_known,
    }


def template_reading(detail: dict) -> str:
    luna = detail["luna"]
    text = f"Hoy la {luna['fase'].lower()} pasa por {luna['signo']}"
    text += f" y por tu casa {luna['casa']}: el foco está en {luna['tema_casa']}." if luna["casa"] else "."
    if detail["transitos"]:
        text += " " + detail["transitos"][0]["texto"]
    return text


def write_reading(detail: dict, style_instructions: str) -> Written:
    if is_configured():
        facts = {
            "luna": detail["luna"],
            "transitos": [t["texto"] for t in detail["transitos"]],
            "areas": {a["nombre"]: a["estado"] for a in detail["areas"]},
        }
        result = complete(f"{GUIDELINE} {style_instructions}".strip(), json.dumps(facts, ensure_ascii=False), load_config()["lectura"]["max_caracteres"])
        if result:
            return Written(result.text, result)
    return Written(template_reading(detail), None)
