"""Biblioteca de textos del tránsito del día (spec B4 v2).

`transitos_v1.json`: un texto por tipo de tránsito × signo por el que pasa la Luna.
Generada una vez con `scripts/generate_transit_texts.py`; editable a mano; Pablo
la revisa (campo `revisado_por_pablo`).
"""

import json
from functools import lru_cache
from pathlib import Path

from app.transits import TRANSIT_TEXT

LIBRARY_PATH = Path(__file__).parent / "transitos_v1.json"
ASPECTS = ["conjunción", "sextil", "cuadratura", "trígono", "oposición", "sin aspecto mayor"]
GENERIC_QUIET = ("Día tranquilo", "Sin tránsitos fuertes sobre tu Sol: buen día para ir a tu ritmo y escucharte.")


@lru_cache(maxsize=1)
def load_library() -> dict:
    return json.loads(LIBRARY_PATH.read_text())


def text_for(aspect: str, moon_sign: str) -> tuple[str, str]:
    entry = load_library()["textos"].get(aspect, {}).get(moon_sign)
    if entry and entry.get("titulo") and entry.get("texto"):
        return entry["titulo"], entry["texto"]
    return TRANSIT_TEXT.get(aspect, GENERIC_QUIET)


def reviewed() -> bool:
    return bool(load_library().get("revisado_por_pablo"))
