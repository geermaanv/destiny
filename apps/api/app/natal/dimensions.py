"""Mi carta por dimensiones (spec A8): indicadores calculados de la carta + textos de la biblioteca.

Qué indicadores forman cada dimensión, los orbes y las palabras de cada punto están en
config/dimensiones_v1.json; los textos, en app/content/carta_v1.json. Acá no hay contenido astrológico.
"""

import json
from functools import lru_cache
from pathlib import Path

from app.astro import ZODIAC_SIGNS
from app.content.carta import load_library
from app.synastry.chart import Chart, chart_for_profile

CONFIG_PATH = Path(__file__).parent / "config" / "dimensiones_v1.json"


@lru_cache(maxsize=1)
def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def _points(chart: Chart) -> dict[str, float]:
    points = dict(chart.points)
    if "asc" in points:
        points["desc"] = (points["asc"] + 180) % 360
    if "mc" in points:
        points["ic"] = (points["mc"] + 180) % 360
    return points


def _angle(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


def _aspect(sep: float, aspects: dict) -> str | None:
    found = [(abs(sep - a["angulo"]), key) for key, a in aspects.items() if abs(sep - a["angulo"]) <= a["orbe"]]
    return min(found)[1] if found else None


def dimension_result(key: str, dim: dict, chart: Chart, cfg: dict, library: dict) -> dict:
    points = _points(chart)
    names = cfg["puntos"]
    fundamentos, missing = [], []
    for ind in dim["indicadores"]:
        point = ind["punto"]
        name = names[point]["nombre"]
        if point not in points:
            missing.append(name)
            continue
        lon = points[point]
        if ind.get("signo"):
            sign = ZODIAC_SIGNS[int(lon // 30)]
            fundamentos.append({"tipo": "signo", "punto": point, "signo": sign, "texto": library["signo"][point][sign]})
        if ind.get("casa"):
            if chart.houses is None:
                missing.append(f"la casa de {name}")
            else:
                house = chart.house_of(lon)
                fundamentos.append({"tipo": "casa", "punto": point, "casa": house, "texto": library["casa"][point][str(house)]})

    targets = dim["aspectos_a"]
    for target in targets:
        if target not in points:
            continue
        for other in cfg["puntos_de_aspecto"]:
            if other == target or other not in points:
                continue
            if other in targets and targets.index(other) < targets.index(target):
                continue  # el par ya se contó desde el otro punto
            aspect = _aspect(_angle(points[target], points[other]), cfg["aspectos"])
            if aspect is None:
                continue
            a = cfg["aspectos"][aspect]
            fundamentos.append({
                "tipo": "aspecto", "punto": target, "otro": other, "aspecto": aspect,
                "texto": (
                    f"{names[target]['nombre']} en {a['nombre']} con {names[other]['nombre']}: "
                    f"{names[target]['palabra']} y {names[other]['palabra']} {a['significado']}."
                ),
            })
    return {
        "clave": key,
        "nombre": dim["nombre"],
        "pregunta": dim["pregunta"],
        "fundamentos": fundamentos,
        "preguntas": dim["preguntas"],
        "faltan_por_hora": missing,
    }


def natal_dimensions(profile) -> dict:
    cfg = load_config()
    chart = chart_for_profile(profile)
    library = load_library()
    return {
        "aproximado": not chart.time_known,
        "dimensiones": [dimension_result(k, d, chart, cfg, library) for k, d in cfg["dimensiones"].items()],
    }
