"""Compatibilidad resumida para Círculo y el chat (specs B9, B12; ADR 0014, provisorio).

Cada sistema se calcula con el modelo de Pablo y sus pesos por vínculo; el global de un vínculo
es el promedio simple de los sistemas con dato, y el número que se muestra es el promedio de los
cuatro vínculos (no depende de lo que se busca). Los ejes son los mismos para todos los vínculos.
"""

from app.personality import CONTEXT_TO_MODE
from app.personality.engine import weighted_total
from app.synastry import AXIS_LABELS

VINCULOS = ["pareja", "amistad", "laboral", "ocasional"]
# Ejes del test de Pablo ↔ ejes de la astrología: miden las mismas cuatro dimensiones.
TEST_AXES = {"E1": "atraccion", "E2": "afecto", "E3": "comunicacion", "E4": "compromiso"}
SISTEMAS = ("astrologia", "personalidad")


def _mean(values) -> float | None:
    present = [v for v in values if v is not None]
    return sum(present) / len(present) if present else None


def _round(value: float | None) -> int | None:
    return round(value) if value is not None else None


def _round5(value: float | None) -> int | None:
    """Spec P2: los ejes del test que ve otra persona, en múltiplos de 5 (menos precisión, menos oráculo)."""
    return int(5 * round(value / 5)) if value is not None else None


def public_personality(compared: dict | None) -> dict | None:
    """Spec P2: la compatibilidad del test solo con los dos tests completos, con los ejes redondeados."""
    if compared is None or compared.get("total") is None:
        return None
    return {**compared, "axes": {k: _round5(v) for k, v in compared["axes"].items()}}


def summarize(synastry: dict, personality: dict | None, included=SISTEMAS) -> dict:
    """`synastry`: resultado del motor (con `totales_por_vinculo`); `personality`: `compare()` o None.

    El test cuenta solo con los dos tests completos (total no nulo), como en el HTML de Pablo.
    """
    astro_on = "astrologia" in included
    test_on = "personalidad" in included and personality is not None and personality.get("total") is not None
    por_vinculo = []
    for vinculo in VINCULOS:
        astro = synastry["totales_por_vinculo"][vinculo] if astro_on else None
        test = weighted_total(personality["axes"], CONTEXT_TO_MODE[vinculo]) if test_on else None
        por_vinculo.append({"vinculo": vinculo, "global": _mean([astro, test]), "astrologia": astro, "personalidad": test})

    systems = {"astrologia": None, "personalidad": None}
    if astro_on:
        systems["astrologia"] = {
            "total": _round(_mean([v["astrologia"] for v in por_vinculo])),
            "axes": dict(synastry["ejes"]),
        }
    if test_on:
        systems["personalidad"] = {
            "total": _round(_mean([v["personalidad"] for v in por_vinculo])),
            "axes": {TEST_AXES[k]: _round5(v) for k, v in personality["axes"].items()},
        }
    axes_global = {
        axis: _round(_mean([s["axes"].get(axis) for s in systems.values() if s])) for axis in AXIS_LABELS
    }
    return {
        "global": _mean([v["global"] for v in por_vinculo]),
        "systems": systems,
        "axes_global": axes_global,
        "por_vinculo": [
            {
                "vinculo": v["vinculo"],
                "global_pct": _round(v["global"]),
                "astrologia": v["astrologia"],
                "personalidad": _round(v["personalidad"]),
            }
            for v in por_vinculo
        ],
    }
