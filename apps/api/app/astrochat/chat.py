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
from app.day.detail import day_detail
from app.natal.dimensions import natal_dimensions
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


def chart_facts(profile, today: date) -> dict:
    """Lo único astrológico que ve la IA: ya calculado, sin datos personales."""
    chart = chart_for_profile(profile)
    signs = {
        name: ZODIAC_SIGNS[int(chart.points[point] // 30)]
        for point, name in (("sol", "Sol"), ("luna", "Luna"), ("asc", "Ascendente"))
        if point in chart.points
    }
    dims = natal_dimensions(profile)
    day = day_detail(profile, today)
    return {
        "signos": signs,
        "hora_exacta": chart.time_known,
        "mi_carta": {d["nombre"]: [f["texto"] for f in d["fundamentos"]] for d in dims["dimensiones"]},
        "tu_dia_hoy": {
            "luna": {k: v for k, v in day["luna"].items() if v is not None},
            "transitos": [t["texto"] for t in day["transitos"]],
            "areas": {a["nombre"]: a["estado"] for a in day["areas"]},
        },
    }


def system_prompt(profile, mode: str, style_instructions: str, today: date) -> str:
    cfg = load_config()
    facts = json.dumps(chart_facts(profile, today), ensure_ascii=False)
    return f"{cfg['guia']} {cfg['modos'][mode]['instruccion']} {style_instructions}\n\nDatos de su carta (calculados por Destiny): {facts}"
