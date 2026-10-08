"""Los 10 niveles del cuadro "Flujo de la app — Sinastría astrológica"
(spec B5-motor-sinastria.md). Todas las tablas salen de config/synastry_v1.json.
"""

import json
import math
from functools import lru_cache
from pathlib import Path

from app.synastry.chart import Chart

CONFIG_PATH = Path(__file__).parent / "config" / "synastry_v1.json"
SCORED_AXES = ("atraccion", "afecto", "comunicacion", "compromiso")
ELEMENT_OF_SIGN = ["fuego", "tierra", "aire", "agua"] * 3  # Aries fuego, Tauro tierra, Géminis aire, Cáncer agua…


@lru_cache(maxsize=1)
def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def _angle(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return 360 - d if d > 180 else d


def _pairs(axis: str, cfg: dict):
    """Pares (punto de A, punto de B, peso) en los dos sentidos."""
    for p, q, w in cfg["planetas_por_eje"][axis]:
        yield p, q, w
        if p != q:
            yield q, p, w


def level_3_signs(axis: str, a: Chart, b: Chart, cfg: dict) -> float:
    m = cfg["nivel_3_matriz_signos"]
    matrix = m["matrices"][axis]
    total = 0.0
    for p, q, w in _pairs(axis, cfg):
        sa, sb = a.sign(p), b.sign(q)
        if sa is None or sb is None:
            continue
        total += matrix[sa][sb] * w * m["factor"]
    return total


def levels_4_5_aspects(axis: str, a: Chart, b: Chart, cfg: dict) -> tuple[float, list[dict]]:
    """Nivel 4 (aspectos) con el ajuste por orbe del nivel 5. Devuelve el total y el detalle."""
    if axis not in SCORED_AXES:
        return 0.0, []
    extra = cfg["nivel_5_orbe"]["orbe_extra_luminarias"]
    total, found = 0.0, []
    for p, q, w in _pairs(axis, cfg):
        la, lb = a.points.get(p), b.points.get(q)
        if la is None or lb is None:
            continue
        angle = _angle(la, lb)
        for name, asp in cfg["nivel_4_aspectos"].items():
            orb = asp["orbe"] + (extra if asp["mayor"] and ({p, q} & {"sol", "luna"}) else 0)
            deviation = abs(angle - asp["angulo"])
            if deviation <= orb:
                strength = 1 - deviation / orb  # nivel 5: lineal
                points = asp["puntos"][axis] * w * strength
                total += points
                found.append({"a": p, "b": q, "aspecto": name, "orbe": round(deviation, 1), "puntos": round(points, 2)})
                break
    return total, found


def level_6_houses(axis: str, a: Chart, b: Chart, cfg: dict) -> float | None:
    """Planetas de una persona en las casas relevantes de la otra. None si no se puede (sin hora exacta o sin lugar)."""
    rules = cfg["nivel_6_casas"]["por_eje"][axis]
    if not rules["casas"]:
        return 0.0
    if not (a.time_known and b.time_known) or a.houses is None or b.houses is None:
        return None
    total = 0.0
    for owner, guest in ((a, b), (b, a)):
        for planet, weight in rules["planetas"].items():
            lon = guest.points.get(planet)
            house = owner.house_of(lon) if lon is not None else None
            if house is not None and str(house) in rules["casas"]:
                total += rules["casas"][str(house)] * weight
    return total


def _normalize(axis: str, raw: float, cfg: dict) -> float:
    norm = cfg["normalizacion"]
    return 50 + 50 * math.tanh((raw - norm["centro"][axis]) / norm["escala"][axis])


def _distribution(chart: Chart, cfg: dict) -> dict[str, list[float]]:
    weights = cfg["nivel_8_eje5"]["puntos_que_cuentan"]
    elements, modalities, yang, total = [0.0] * 4, [0.0] * 3, 0.0, 0.0
    for point, w in weights.items():
        sign = chart.sign(point)
        if sign is None:
            continue
        elements[sign % 4] += w
        modalities[sign % 3] += w
        yang += w if sign % 2 == 0 else 0
        total += w
    total = total or 1
    return {
        "elementos": [e / total for e in elements],
        "modalidades": [m / total for m in modalities],
        "yang": [yang / total],
    }


def level_8_modifier_factors(a: Chart, b: Chart, cfg: dict) -> dict[str, float]:
    """Eje 5: elementos, polaridades, modalidades y compensatorios, cada uno de 0 a 1."""
    e5 = cfg["nivel_8_eje5"]
    names = e5["elementos"]
    da, db = _distribution(a, cfg), _distribution(b, cfg)
    affinity = e5["afinidad_elementos"]
    elementos = sum(
        da["elementos"][i] * db["elementos"][j] * affinity[names[i]][names[j]] for i in range(4) for j in range(4)
    )
    polaridades = 1 - abs(da["yang"][0] - db["yang"][0])
    same_modality = sum(x * y for x, y in zip(da["modalidades"], db["modalidades"]))
    modalidades = 1 - 0.6 * same_modality
    compensated = sum(
        1
        for i in range(4)
        if (da["elementos"][i] < 0.1 and db["elementos"][i] > 0.3) or (db["elementos"][i] < 0.1 and da["elementos"][i] > 0.3)
    )
    compensatorios = min(1.0, compensated / 2)
    return {
        "elementos": round(elementos, 3),
        "polaridades": round(polaridades, 3),
        "modalidades": round(modalidades, 3),
        "compensatorios": round(compensatorios, 3),
    }


def synastry(a: Chart, b: Chart, relationship: str | None = None) -> dict:
    """Corre los 10 niveles. Devuelve puntaje por eje (0-100), total y detalle."""
    cfg = load_config()
    types = cfg["nivel_7_y_10_tipos_de_relacion"]
    relationship = relationship if relationship in types["tipos"] else types["por_defecto"]
    approximate = not (a.time_known and b.time_known)

    factors = level_8_modifier_factors(a, b, cfg)
    e5 = cfg["nivel_8_eje5"]
    lo, hi = e5["multiplicador"]["minimo"], e5["multiplicador"]["maximo"]

    axes, detail = {}, {}
    for axis in SCORED_AXES:
        signs = level_3_signs(axis, a, b, cfg)  # nivel 3
        aspects, aspect_list = levels_4_5_aspects(axis, a, b, cfg)  # niveles 4 y 5
        houses = level_6_houses(axis, a, b, cfg)  # nivel 6
        raw = signs + aspects + (houses or 0)
        base = _normalize(axis, raw, cfg)  # nivel 7 (0-100)
        weights = e5["peso_de_cada_factor_por_eje"][axis]
        modifier = lo + (hi - lo) * sum(factors[k] * w for k, w in weights.items())  # nivel 8
        final = max(0.0, min(100.0, base * modifier))  # nivel 9
        axes[axis] = round(final)
        detail[axis] = {
            "matriz_signos": round(signs, 2),
            "aspectos": round(aspects, 2),
            "casas": None if houses is None else round(houses, 2),
            "puntaje_base": round(base, 1),
            "multiplicador_eje5": round(modifier, 3),
            "aspectos_encontrados": sorted(aspect_list, key=lambda x: -abs(x["puntos"]))[:5],
        }

    weights = types["tipos"][relationship]["pesos"]
    total = sum(axes[k] * w for k, w in weights.items()) / (sum(weights.values()) or 1)  # nivel 10
    return {
        "tipo_de_relacion": relationship,
        "total": round(total),
        "ejes": axes,
        "eje5_factores": factors,
        "aproximado": approximate,
        "detalle": detail,
        "version_tablas": cfg["version"],
    }
