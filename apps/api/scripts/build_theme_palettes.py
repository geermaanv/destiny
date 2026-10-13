"""Genera las paletas de los temas visuales (spec X2 v2) en app/personalization/config/estilos_v1.json.

Parte de la paleta clásica (colores del logo) y, para cada elemento, cambia solo el matiz y la
saturación de cada escala: la luminosidad de cada tono queda igual, así el contraste de textos y
botones no cambia. Los matices siguen la paleta orientativa del whitepaper (§3.2).

Uso: .venv/bin/python scripts/build_theme_palettes.py
"""

import colorsys
import json
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1] / "app" / "personalization" / "config" / "estilos_v1.json"

CLASSIC = {
    "slate": {"50": "#f9f7f1", "100": "#f4f1e8", "200": "#e3e0f2", "300": "#c9c6e3", "400": "#a6a3cc", "500": "#807daa",
              "600": "#5b5890", "700": "#3a3779", "800": "#25225b", "900": "#1a1844", "950": "#0e0d29"},
    "violet": {"50": "#fff1f0", "100": "#ffe0de", "200": "#ffc6c2", "300": "#ff9e98", "400": "#fe7068", "500": "#fc4b43",
               "600": "#e9342c", "700": "#c4261f", "800": "#a2231e", "900": "#86231f", "950": "#490d0a"},
    "gold": {"100": "#fdf4d3", "200": "#fbe7a2", "300": "#f8d66b", "400": "#f5c542", "500": "#e0aa1f"},
}
# (matiz en grados, factor de saturación) por escala: slate = fondo y neutros, violet = acción, gold = acento.
THEMES = {
    "fuego": {"nombre": "Fuego", "descripcion": "rojo profundo, terracota y dorado",
              "slate": (345, 0.9), "violet": (16, 0.85), "gold": (40, 1.0)},
    "tierra": {"nombre": "Tierra", "descripcion": "verde bosque, arena y cobre",
               "slate": (152, 0.55), "violet": (24, 0.7), "gold": (38, 0.55)},
    "aire": {"nombre": "Aire", "descripcion": "azul claro, plata y lavanda",
             "slate": (212, 0.6), "violet": (262, 0.75), "gold": (195, 0.55)},
    "agua": {"nombre": "Agua", "descripcion": "índigo, océano y violeta",
             "slate": (222, 1.0), "violet": (276, 0.8), "gold": (172, 0.7)},
}


def shift(hex_color: str, hue: float, sat_factor: float) -> str:
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    _, light, sat = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(hue / 360, light, min(1.0, sat * sat_factor))
    return "#" + "".join(f"{round(x * 255):02x}" for x in (r, g, b))


def main():
    config = json.loads(CONFIG.read_text())
    temas = {"clasico": {"nombre": "Clásico", "descripcion": "los colores del logo: azul noche, coral y dorado", "paleta": CLASSIC}}
    for key, t in THEMES.items():
        temas[key] = {
            "nombre": t["nombre"],
            "descripcion": t["descripcion"],
            "paleta": {scale: {step: shift(c, *t[scale]) for step, c in steps.items()} for scale, steps in CLASSIC.items()},
        }
    config["tema"] = {
        "que_define": "los colores de la app",
        "descripcion": "Elemento predominante de la carta: P(e) = suma de pesos de los puntos en ese elemento / suma de pesos (whitepaper §3.2). Empate: el elemento del Sol.",
        "pesos": {"sol": 3, "luna": 3, "asc": 2, "mercurio": 1, "venus": 1, "marte": 1},
        "desempate": "sol",
        "por_elemento": {"fuego": "fuego", "tierra": "tierra", "aire": "aire", "agua": "agua"},
        "temas": temas,
    }
    CONFIG.write_text(json.dumps(config, ensure_ascii=False, indent=1) + "\n")
    print(f"Escrito {CONFIG}: temas {list(temas)}")


if __name__ == "__main__":
    main()
