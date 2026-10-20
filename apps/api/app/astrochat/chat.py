"""Astrochat (spec X3): la IA conversa con los datos ya calculados por el motor (ADR 0011).

Al modelo le llegan solo los signos, los fundamentos de Mi carta y Tu día de hoy:
nada de nombre, fecha, hora o lugar de nacimiento, teléfono ni datos de otras personas.
Modos, límites, reglas y textos fijos en config/astrochat_v1.json.
"""

import json
import unicodedata
from datetime import date
from functools import lru_cache
from pathlib import Path

from app.astro import ZODIAC_SIGNS
from app.day.detail import day_detail, upcoming_transits
from app.natal.dimensions import load_config as natal_config
from app.natal.dimensions import natal_dimensions
from app.personality.engine import load_config as personality_config
from app.synastry.chart import chart_for_profile

CONFIG_PATH = Path(__file__).parent / "config" / "astrochat_v1.json"


@lru_cache(maxsize=1)
def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def suggested_mode(style: dict) -> str:
    cfg = load_config()
    return cfg["modo_por_registro"].get(style["registro"], next(iter(cfg["modos"])))


def _plain(text: str) -> str:
    return unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()


def is_crisis(text: str) -> bool:
    plain = _plain(text)
    return any(_plain(word) in plain for word in load_config()["crisis"]["palabras"])


POINT_NAMES = {
    "sol": "Sol", "luna": "Luna", "mercurio": "Mercurio", "venus": "Venus", "marte": "Marte", "jupiter": "Júpiter",
    "saturno": "Saturno", "urano": "Urano", "neptuno": "Neptuno", "pluton": "Plutón", "asc": "Ascendente", "mc": "Medio Cielo",
}


def _angle(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


def full_chart(chart) -> tuple[dict, list[str]]:
    """v2: todos los puntos con signo (y casa con hora y lugar) y los aspectos natales mayores."""
    planets = {}
    for key, name in POINT_NAMES.items():
        if key not in chart.points:
            continue
        info = {"signo": ZODIAC_SIGNS[int(chart.points[key] // 30)]}
        if chart.houses and key not in ("asc", "mc"):
            info["casa"] = chart.house_of(chart.points[key])
        planets[name] = info
    aspects_cfg = natal_config()["aspectos"]
    keys = [k for k in POINT_NAMES if k in chart.points]
    aspects = []
    for i, a in enumerate(keys):
        for b in keys[i + 1 :]:
            sep = _angle(chart.points[a], chart.points[b])
            found = [(abs(sep - x["angulo"]), x["nombre"]) for x in aspects_cfg.values() if abs(sep - x["angulo"]) <= x["orbe"]]
            if found:
                orb, name = min(found)
                aspects.append(f"{POINT_NAMES[a]} en {name} con {POINT_NAMES[b]} (orbe {orb:.1f}°)")
    return planets, aspects


def personality_facts(answers: dict | None) -> dict:
    """v2: preguntas respondidas con las opciones elegidas, en orden. Solo los ejes configurados
    (por defecto sin E1, que tiene datos sensibles)."""
    if not answers:
        return {}
    axes = set(load_config()["contexto"]["personalidad_ejes"])
    out = {}
    for q in personality_config()["questions"]:
        choices = answers.get(q["id"])
        if q["axis"] in axes and choices:
            out[q["question"]] = [q["options"][c] for c in choices if 0 <= c < len(q["options"])]
    return out


def chart_facts(profile, today: date, answers: dict | None = None, asked_day: date | None = None) -> dict:
    """Lo único que ve la IA: ya calculado, sin datos personales."""
    chart = chart_for_profile(profile)
    signs = {
        name: ZODIAC_SIGNS[int(chart.points[point] // 30)]
        for point, name in (("sol", "Sol"), ("luna", "Luna"), ("asc", "Ascendente"))
        if point in chart.points
    }
    dims = natal_dimensions(profile)
    day = day_detail(profile, today)
    planets, natal_aspects = full_chart(chart)
    ctx = load_config()["contexto"]
    facts = {
        "signos": signs,
        "hora_exacta": chart.time_known,
        "mi_carta": {d["nombre"]: [f["texto"] for f in d["fundamentos"]] for d in dims["dimensiones"]},
        "tu_dia_hoy": {
            "luna": {k: v for k, v in day["luna"].items() if v is not None},
            "transitos": [t["texto"] for t in day["transitos"]],
            "areas": {a["nombre"]: a["estado"] for a in day["areas"]},
        },
        "planetas": planets,
        "aspectos_natales": natal_aspects,
        "proximos_30_dias": upcoming_transits(profile, today, ctx["proximos_dias"], ctx["maximo_transitos_proximos"]),
    }
    if asked_day is not None:
        # Spec U2: pregunta sobre un día del calendario.
        other = day_detail(profile, asked_day)
        facts["dia_consultado"] = {
            "fecha": asked_day.isoformat(),
            "luna": {k: v for k, v in other["luna"].items() if v is not None},
            "transitos": [t["texto"] for t in other["transitos"]],
            "areas": {a["nombre"]: a["estado"] for a in other["areas"]},
        }
    test = personality_facts(answers)
    if test:
        facts["test_de_personalidad"] = test
    return facts


def system_prompt(
    profile, mode: str, style_instructions: str, today: date, answers: dict | None = None, asked_day: date | None = None
) -> str:
    cfg = load_config()
    facts = json.dumps(chart_facts(profile, today, answers, asked_day), ensure_ascii=False)
    return f"{cfg['guia']} {cfg['modos'][mode]['instruccion']} {style_instructions}\n\nDatos de su carta (calculados por Destiny): {facts}"
