"""Estilo de redacción de cada persona según su carta (spec X2 v1).

Registro ← elemento de Mercurio; tono ← elemento de la Luna; formato ← modalidad
dominante (empate: la de Mercurio). Todo el mapeo sale de config/estilos_v1.json.
"""

import json
from functools import lru_cache
from pathlib import Path

from app.astro import ZODIAC_SIGNS
from app.models import Profile
from app.synastry.chart import Chart, chart_for_profile

CONFIG_PATH = Path(__file__).parent / "config" / "estilos_v1.json"
SKY_POINTS = ("sol", "luna", "mercurio", "venus", "marte", "jupiter", "saturno", "urano", "neptuno", "pluton", "asc", "mc")
PLANET_NAMES = {"mercurio": "Mercurio", "luna": "Luna"}


@lru_cache(maxsize=1)
def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def registros() -> list[str]:
    return list(load_config()["registro"]["estilos"])


def _sign(chart: Chart, point: str) -> int:
    return int(chart.points[point] // 30) % 12


def style_from_chart(chart: Chart) -> dict:
    cfg = load_config()
    elements, modalities = cfg["elementos"], cfg["modalidades"]
    reg_planet, tone_planet = cfg["registro"]["planeta"], cfg["tono"]["planeta"]
    reg_element = elements[_sign(chart, reg_planet) % 4]
    tone_element = elements[_sign(chart, tone_planet) % 4]

    totals = [0.0] * 3
    for point, weight in cfg["formato"]["pesos"].items():
        if point in chart.points:
            totals[_sign(chart, point) % 3] += weight
    best = max(totals)
    tied = [i for i, t in enumerate(totals) if t == best]
    modality = modalities[tied[0] if len(tied) == 1 else _sign(chart, cfg["formato"]["desempate"]) % 3]

    reg_sign = ZODIAC_SIGNS[_sign(chart, reg_planet)]
    registro = cfg["registro"]["por_elemento"][reg_element]
    return {
        "registro": registro,
        "tono": cfg["tono"]["por_elemento"][tone_element],
        "formato": cfg["formato"]["por_modalidad"][modality],
        "por_que": (
            f"Te hablamos con un estilo {cfg['registro']['estilos'][registro]['nombre'].lower()} porque tu "
            f"{PLANET_NAMES.get(reg_planet, reg_planet)} está en {reg_sign} ({reg_element}): define "
            f"{cfg['registro']['que_define']}."
        ),
    }


def theme_from_chart(chart: Chart) -> dict:
    """Tema visual (spec X2 v2): elemento predominante, P(e) = Σ pesos en e / Σ pesos. Empate → elemento del Sol."""
    cfg = load_config()
    elements, theme_cfg = cfg["elementos"], cfg["tema"]
    totals = dict.fromkeys(elements, 0.0)
    for point, weight in theme_cfg["pesos"].items():
        if point in chart.points:
            totals[elements[_sign(chart, point) % 4]] += weight
    best = max(totals.values())
    tied = [e for e in elements if totals[e] == best]
    element = tied[0] if len(tied) == 1 else elements[_sign(chart, theme_cfg["desempate"]) % 4]
    total = sum(totals.values()) or 1
    pct = {e: round(100 * v / total) for e, v in totals.items()}
    return {
        "tema_carta": theme_cfg["por_elemento"][element],
        "elementos": pct,
        "tema_por_que": f"En tu carta predomina el {element} ({pct[element]} %).",
    }


def style_for(profile: Profile) -> dict:
    """Estilo de la carta, con las elecciones manuales (registro, tema) si las hay."""
    chart = chart_for_profile(profile)
    style = style_from_chart(chart) | theme_from_chart(chart)
    style["registro_carta"] = style["registro"]
    style["source"] = "carta"
    if profile.style_registro:
        style["registro"] = profile.style_registro
        style["source"] = "elegido"
    style["tema"], style["tema_source"] = style["tema_carta"], "carta"
    if profile.style_tema:
        style["tema"], style["tema_source"] = profile.style_tema, "elegido"
    theme_cfg = load_config()["tema"]
    # v3: modo claro/oscuro, acento por Venus (si el tema lo decide la carta), tipografía y cielo de nacimiento.
    style["modo"] = profile.style_modo or theme_cfg["modo_por_defecto"]
    key = "paleta_claro" if style["modo"] == "claro" else "paleta"
    style["acento"] = load_config()["elementos"][_sign(chart, theme_cfg["acento"]["planeta"]) % 4]
    accent_theme = style["acento"] if style["tema_source"] == "carta" else style["tema"]
    style["paleta"] = theme_cfg["temas"][style["tema"]][key] | {"gold": theme_cfg["temas"][accent_theme][key]["gold"]}
    style["tipografia"] = theme_cfg["temas"][style["tema"]]["tipografia"]
    style["fondo"] = True if profile.style_fondo is None else profile.style_fondo
    style["cielo"] = [{"punto": p, "lon": chart.points[p]} for p in SKY_POINTS if p in chart.points]
    return style


def prompt_instructions(style: dict) -> str:
    cfg = load_config()
    return " ".join(
        [
            cfg["registro"]["estilos"][style["registro"]]["instruccion"],
            cfg["tono"]["estilos"][style["tono"]]["instruccion"],
            cfg["formato"]["estilos"][style["formato"]]["instruccion"],
        ]
    )
