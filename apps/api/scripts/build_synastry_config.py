"""Genera app/synastry/config/synastry_v1.json (spec B5-motor-sinastria.md).

Las tablas de contenido astrológico se escriben acá de forma legible (reglas)
y el script las expande al JSON que lee el motor. Las matrices 12×12 se
generan a partir de la relación entre signos (mismo signo, sextil, cuadratura,
trígono, quincuncio, oposición…) y quedan en el JSON como 144 valores
editables por eje: si un astrólogo quiere ajustar una combinación puntual,
la edita en el JSON (y anota el cambio en "notas").

Uso: .venv/bin/python scripts/build_synastry_config.py
"""

import json
import re
from pathlib import Path

SIGNS = [
    "Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
    "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis",
]

AXES = {
    "atraccion": "Atracción / química sexual",
    "afecto": "Afecto / emoción",
    "comunicacion": "Comunicación",
    "compromiso": "Compromiso",
    "modificadores": "Modificadores",
}

# Nivel 3 — puntos por relación entre signos (distancia en signos, 0..6), por eje.
# Rango -3..+5. Atracción premia la polaridad y la fricción (chispa);
# afecto y compromiso premian la armonía (trígono, mismo elemento);
# comunicación premia el ida y vuelta (sextil, mismo signo).
SIGN_RELATION = ["mismo_signo", "semisextil", "sextil", "cuadratura", "trigono", "quincuncio", "oposicion"]
SIGN_RELATION_POINTS = {
    #               mismo semisx sextil cuadr  trig  quinc  opos
    "atraccion":     [3,    -1,    3,     3,    3,    1,     5],
    "afecto":        [4,     0,    3,    -2,    5,   -2,     1],
    "comunicacion":  [4,     1,    5,    -2,    4,   -2,     1],
    "compromiso":    [3,     0,    3,    -3,    5,   -2,     0],
    "modificadores": [2,    -1,    2,    -2,    3,   -2,     1],
}

# Planetas de cada eje: pares (planeta de A, planeta de B) con su peso.
# Se evalúan en los dos sentidos (A→B y B→A). Puntos: sol, luna, mercurio,
# venus, marte, jupiter, saturno, urano, neptuno, pluton, asc.
AXIS_PAIRS = {
    "atraccion": [
        ["venus", "marte", 3.0], ["marte", "marte", 1.5], ["venus", "venus", 1.0],
        ["sol", "marte", 1.5], ["luna", "marte", 1.0], ["pluton", "venus", 1.0],
        ["pluton", "marte", 1.0], ["asc", "marte", 1.0], ["asc", "venus", 1.0],
    ],
    "afecto": [
        ["sol", "luna", 3.0], ["luna", "luna", 2.0], ["luna", "venus", 2.5],
        ["venus", "venus", 1.5], ["sol", "venus", 1.5], ["neptuno", "venus", 0.5],
        ["neptuno", "luna", 0.5],
    ],
    "comunicacion": [
        ["mercurio", "mercurio", 3.0], ["mercurio", "sol", 2.0], ["mercurio", "luna", 1.5],
        ["mercurio", "jupiter", 1.5], ["mercurio", "urano", 1.0], ["mercurio", "asc", 1.0],
        ["sol", "sol", 1.0],
    ],
    "compromiso": [
        ["saturno", "sol", 2.5], ["saturno", "luna", 2.5], ["saturno", "venus", 2.5],
        ["sol", "luna", 2.0], ["jupiter", "venus", 1.5], ["jupiter", "sol", 1.5],
        ["sol", "sol", 1.0], ["saturno", "saturno", 1.0],
    ],
    "modificadores": [
        ["sol", "sol", 2.0], ["luna", "luna", 2.0], ["asc", "asc", 1.0],
    ],
}

# Nivel 4 — aspectos mayores y menores: ángulo, orbe máximo y puntos por eje.
# Nivel 5 — el impacto se multiplica por (1 - desvío/orbe): exacto = 100 %,
# en el borde del orbe = 0 %. Si interviene el Sol o la Luna, el orbe de los
# aspectos mayores suma "orbe_extra_luminarias".
ASPECTS = {
    #                 ángulo orbe  atr  afe  com  comp
    "conjuncion":       [0,   8,   6,   5,   5,   5],
    "semisextil":       [30,  2,   1,   1,   1,   1],
    "semicuadratura":   [45,  2,   1,  -1,  -1,  -1],
    "sextil":           [60,  6,   4,   4,   5,   3],
    "cuadratura":       [90,  7,   5,  -3,  -4,  -3],
    "trigono":          [120, 7,   4,   6,   5,   5],
    "sesquicuadratura": [135, 2,   1,  -1,  -1,  -1],
    "quincuncio":       [150, 3,   2,  -2,  -2,  -2],
    "oposicion":        [180, 8,   5,  -1,  -2,   0],
}
MAJOR_ASPECTS = ["conjuncion", "sextil", "cuadratura", "trigono", "oposicion"]

# Nivel 6 — casas relevantes de cada eje (del cuadro) y qué planetas cuentan:
# suma puntos cuando un planeta de una persona cae en esa casa de la otra.
HOUSES = {
    "atraccion":    {"casas": {"8": 4, "5": 4}, "planetas": {"venus": 1.5, "marte": 1.5, "sol": 1, "luna": 1, "pluton": 1}},
    "afecto":       {"casas": {"7": 3, "4": 4, "5": 3, "8": 2}, "planetas": {"luna": 1.5, "venus": 1.5, "sol": 1}},
    "comunicacion": {"casas": {"3": 4, "9": 3, "11": 3}, "planetas": {"mercurio": 1.5, "sol": 1, "jupiter": 1}},
    "compromiso":   {"casas": {"7": 4, "4": 3, "10": 3, "5": 2}, "planetas": {"saturno": 1.5, "sol": 1, "luna": 1, "venus": 1, "jupiter": 1}},
    "modificadores": {"casas": {}, "planetas": {}},
}

CONFIG = {
    "version": "v1-provisoria",
    "notas": [
        "Tablas iniciales armadas por Claude a partir de criterios clásicos de sinastría, para que el equipo las revise.",
        "Nada de esto está validado todavía por un astrólogo: cada número se puede ajustar sin tocar código.",
        "Para regenerar desde las reglas: .venv/bin/python scripts/build_synastry_config.py (pisa los cambios hechos a mano en las matrices).",
    ],
    "signos": SIGNS,
    "ejes": AXES,
    "nivel_3_matriz_signos": {
        "descripcion": "Puntos por combinación de signos (fila = signo del planeta de A, columna = signo del planeta de B).",
        "factor": 0.6,
        "matrices": {
            axis: [[SIGN_RELATION_POINTS[axis][min(abs(i - j), 12 - abs(i - j))] for j in range(12)] for i in range(12)]
            for axis in AXES
        },
        "regla_de_generacion": {"relaciones": SIGN_RELATION, "puntos": SIGN_RELATION_POINTS},
    },
    "planetas_por_eje": AXIS_PAIRS,
    "nivel_4_aspectos": {
        name: {
            "angulo": v[0],
            "orbe": v[1],
            "mayor": name in MAJOR_ASPECTS,
            "puntos": {"atraccion": v[2], "afecto": v[3], "comunicacion": v[4], "compromiso": v[5]},
        }
        for name, v in ASPECTS.items()
    },
    "nivel_5_orbe": {"regla": "lineal", "orbe_extra_luminarias": 2},
    "nivel_6_casas": {
        "sistema": "casas_iguales_desde_ascendente",
        "por_eje": HOUSES,
        "sin_hora_exacta": "Si la hora de alguna de las dos personas es estimada, el nivel 6 no se aplica (las casas dependen de la hora) y el resultado se marca como aproximado.",
    },
    "normalizacion": {
        "descripcion": "Puntaje 0-100 = 50 + 50 * tanh((puntos - centro) / escala). 'centro' y 'escala' se calibran solos con parejas al azar (ver calibrar() en el script): una pareja promedio da 50 y ~2 de cada 3 caen entre 32 y 68.",
        "centro": {},
        "escala": {},
    },
    "nivel_8_eje5": {
        "descripcion": "El Eje 5 calcula cuatro factores (0 a 1) a partir de los elementos, polaridades y modalidades de las dos cartas, y ajusta cada eje con un multiplicador entre 'minimo' y 'maximo' según cuánto le importa cada factor.",
        "puntos_que_cuentan": {"sol": 3, "luna": 3, "asc": 2, "mercurio": 1, "venus": 1, "marte": 1},
        "elementos": ["fuego", "tierra", "aire", "agua"],
        "afinidad_elementos": {
            "fuego": {"fuego": 1.0, "tierra": 0.4, "aire": 0.9, "agua": 0.3},
            "tierra": {"fuego": 0.4, "tierra": 1.0, "aire": 0.4, "agua": 0.9},
            "aire": {"fuego": 0.9, "tierra": 0.4, "aire": 1.0, "agua": 0.4},
            "agua": {"fuego": 0.3, "tierra": 0.9, "aire": 0.4, "agua": 1.0},
        },
        "factores": {
            "elementos": "Afinidad entre los elementos predominantes de cada carta.",
            "polaridades": "Equilibrio activo/receptivo (signos de fuego y aire vs. tierra y agua): 1 = mismo equilibrio.",
            "modalidades": "Mezcla de cardinal/fijo/mutable: dos cartas muy fijas (o muy cardinales) chocan.",
            "compensatorios": "Un elemento que le falta a uno y le sobra al otro suma (se complementan).",
        },
        "peso_de_cada_factor_por_eje": {
            "atraccion": {"elementos": 0.3, "polaridades": 0.4, "modalidades": 0.1, "compensatorios": 0.2},
            "afecto": {"elementos": 0.45, "polaridades": 0.15, "modalidades": 0.15, "compensatorios": 0.25},
            "comunicacion": {"elementos": 0.4, "polaridades": 0.1, "modalidades": 0.3, "compensatorios": 0.2},
            "compromiso": {"elementos": 0.35, "polaridades": 0.1, "modalidades": 0.35, "compensatorios": 0.2},
        },
        "multiplicador": {"minimo": 0.85, "maximo": 1.15},
    },
    "nivel_7_y_10_tipos_de_relacion": {
        "descripcion": "Peso de cada eje en la compatibilidad total según el tipo de relación. Con pesos iguales es el promedio simple del cuadro.",
        "tipos": {
            "ocasional": {"nombre": "Relación sexual ocasional", "pesos": {"atraccion": 0.55, "afecto": 0.15, "comunicacion": 0.2, "compromiso": 0.1}},
            "pareja": {"nombre": "Pareja formal", "pesos": {"atraccion": 0.25, "afecto": 0.3, "comunicacion": 0.2, "compromiso": 0.25}},
            "amistad": {"nombre": "Amistad", "pesos": {"atraccion": 0.05, "afecto": 0.35, "comunicacion": 0.4, "compromiso": 0.2}},
            "laboral": {"nombre": "Profesional / laboral / socios", "pesos": {"atraccion": 0.0, "afecto": 0.15, "comunicacion": 0.45, "compromiso": 0.4}},
        },
        "por_defecto": "pareja",
    },
}

CALIBRATION_PAIRS = 1500
TARGET_SPREAD = 18  # puntos de desvío alrededor de 50


def calibrar(config: dict) -> None:
    """Centra cada eje en 50 con parejas al azar (fechas 1960-2005, hora conocida, Buenos Aires)."""
    import math
    import random
    import statistics
    import sys
    from datetime import date, time

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from app.synastry import engine
    from app.synastry.chart import compute_chart

    rng = random.Random(42)

    def random_chart():
        d = date(rng.randint(1960, 2005), rng.randint(1, 12), rng.randint(1, 28))
        return compute_chart(d, time(rng.randint(0, 23), rng.randint(0, 59)), True, -34.6, -58.4, None)

    raws = {axis: [] for axis in engine.SCORED_AXES}
    for _ in range(CALIBRATION_PAIRS):
        a, b = random_chart(), random_chart()
        for axis in engine.SCORED_AXES:
            houses = engine.level_6_houses(axis, a, b, config)
            raws[axis].append(
                engine.level_3_signs(axis, a, b, config)
                + engine.levels_4_5_aspects(axis, a, b, config)[0]
                + (houses or 0)
            )
    for axis, values in raws.items():
        center = statistics.median(values)
        spread = statistics.pstdev(values) or 1
        config["normalizacion"]["centro"][axis] = round(center, 2)
        config["normalizacion"]["escala"][axis] = round(spread / math.atanh(TARGET_SPREAD / 50), 2)


calibrar(CONFIG)

out = Path(__file__).resolve().parents[1] / "app" / "synastry" / "config" / "synastry_v1.json"
text = json.dumps(CONFIG, ensure_ascii=False, indent=1)
# Listas cortas (filas de matrices, pares de planetas) en una sola línea, para que se lean como tabla.
text = re.sub(r"\[\s+([^\[\]{}]*?)\s+\]", lambda m: "[" + " ".join(m.group(1).split()) + "]", text)
out.write_text(text + "\n")
print(f"Escrito {out}")
