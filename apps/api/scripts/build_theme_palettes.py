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
    "fuego": {"tipografia": "sora", "nombre": "Fuego", "descripcion": "rojo profundo, terracota y dorado",
              "slate": (345, 0.9), "violet": (16, 0.85), "gold": (40, 1.0)},
    "tierra": {"tipografia": "lora", "nombre": "Tierra", "descripcion": "verde bosque, arena y cobre",
               "slate": (152, 0.55), "violet": (24, 0.7), "gold": (38, 0.55)},
    "aire": {"tipografia": "josefin", "nombre": "Aire", "descripcion": "azul claro, plata y lavanda",
             "slate": (212, 0.6), "violet": (262, 0.75), "gold": (195, 0.55)},
    "agua": {"tipografia": "cormorant", "nombre": "Agua", "descripcion": "índigo, océano y violeta",
             "slate": (222, 1.0), "violet": (276, 0.8), "gold": (172, 0.7)},
}


def shift(hex_color: str, hue: float, sat_factor: float) -> str:
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    _, light, sat = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(hue / 360, light, min(1.0, sat * sat_factor))
    return "#" + "".join(f"{round(x * 255):02x}" for x in (r, g, b))


def invert(hex_color: str, factor: float = 1.0) -> str:
    """Modo claro: mismo matiz y saturación, luminosidad invertida (L → (1 − L) × factor)."""
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    hue, light, sat = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(hue, (1 - light) * factor, sat)
    return "#" + "".join(f"{round(x * 255):02x}" for x in (r, g, b))


# Modo claro: se invierten fondos/textos (slate), el acento (gold) y los tonos de acción que se usan como
# texto o fondo suave (violet 50-400 y 950); los botones (violet 500-900, con texto blanco) quedan iguales.
LIGHT_INVERTED = {"slate": "all", "gold": "all", "violet": {"50", "100", "200", "300", "400", "950"}}
# Los amarillos/dorados tienen mucha luminancia: invertidos quedan claros sobre fondo claro; se oscurecen más.
LIGHT_FACTOR = {"slate": 1.0, "violet": 1.0, "gold": 0.6}


def light(palette: dict) -> dict:
    out = {}
    for scale, steps in palette.items():
        rule = LIGHT_INVERTED[scale]
        out[scale] = {s: invert(c, LIGHT_FACTOR[scale]) if rule == "all" or s in rule else c for s, c in steps.items()}
    return out


def main():
    config = json.loads(CONFIG.read_text())
    temas = {"clasico": {"nombre": "Clásico", "descripcion": "los colores del logo: azul noche, coral y dorado",
                         "tipografia": "clasica", "paleta": CLASSIC, "paleta_claro": light(CLASSIC)}}
    for key, t in THEMES.items():
        palette = {scale: {step: shift(c, *t[scale]) for step, c in steps.items()} for scale, steps in CLASSIC.items()}
        temas[key] = {
            "nombre": t["nombre"],
            "descripcion": t["descripcion"],
            "tipografia": t["tipografia"],
            "paleta": palette,
            "paleta_claro": light(palette),
        }
    config["tema"] = {
        "que_define": "los colores de la app",
        "descripcion": "Elemento predominante de la carta: P(e) = suma de pesos de los puntos en ese elemento / suma de pesos (whitepaper §3.2). Empate: el elemento del Sol.",
        "pesos": {"sol": 3, "luna": 3, "asc": 2, "mercurio": 1, "venus": 1, "marte": 1},
        "desempate": "sol",
        "por_elemento": {"fuego": "fuego", "tierra": "tierra", "aire": "aire", "agua": "agua"},
        "temas": temas,
        # v3: el acento (escala gold) sale del elemento de Venus cuando el tema lo decide la carta.
        "acento": {"planeta": "venus", "descripcion": "Venus define lo que te atrae y te gusta: le da el color de acento."},
        "modos": ["oscuro", "claro"],
        # Fondo generado con la carta: la persona elige (spec X2 v3; German eligió la constelación por defecto).
        "fondos": ["constelacion", "aura", "elemental", "horizonte", "ninguno"],
        "fondo_por_defecto": "constelacion",
        "modo_por_defecto": "oscuro",
        # Tipografía solo para títulos: la de lectura queda igual en todos los temas (whitepaper §3.2).
        "tipografias": {
            "clasica": "la de siempre",
            "sora": "Sora: expresiva y con fuerza",
            "lora": "Lora: serif orgánica y sobria",
            "josefin": "Josefin Sans: liviana y geométrica",
            "cormorant": "Cormorant Garamond: fluida y contemplativa",
        },
    }
    CONFIG.write_text(json.dumps(config, ensure_ascii=False, indent=1) + "\n")
    print(f"Escrito {CONFIG}: temas {list(temas)}")


if __name__ == "__main__":
    main()
