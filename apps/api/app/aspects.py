# Aspectos mayores (grado, nombre, orbe de tolerancia, % de compatibilidad base).
# Compartido entre compatibility.py (Sol-Sol entre dos cartas) y transits.py
# (Luna del día vs. Sol natal). v1: simplificación deliberada, ver
# B5-pantalla-descubrir.md / B6-calendario-memoria.md y BACKLOG.md.
ASPECTS = [
    (0, "conjunción", 8, 90),
    (60, "sextil", 6, 75),
    (90, "cuadratura", 6, 45),
    (120, "trígono", 8, 85),
    (180, "oposición", 8, 50),
]
DEFAULT_ASPECT = ("sin aspecto mayor", 60)


def angle_between(lon_a: float, lon_b: float) -> float:
    diff = abs(lon_a - lon_b) % 360
    return 360 - diff if diff > 180 else diff


def classify_aspect(angle: float) -> dict:
    for degree, name, orb, percentage in ASPECTS:
        if abs(angle - degree) <= orb:
            return {"aspect": name, "angle": round(angle, 1), "percentage": percentage, "is_major": True}

    name, percentage = DEFAULT_ASPECT
    return {"aspect": name, "angle": round(angle, 1), "percentage": percentage, "is_major": False}


# Textos en lenguaje simple para mostrar al usuario (evitar jerga y frases
# rotas como "hay un sin aspecto mayor"): etiqueta corta + frase completa.
ASPECT_TEXT = {
    "conjunción": ("Energía parecida", "sus soles están en sintonía: tienen una energía muy parecida"),
    "sextil": ("Se complementan", "sus soles se complementan con facilidad"),
    "cuadratura": ("Tensión que impulsa", "entre sus soles hay una tensión que puede ser motor"),
    "trígono": ("Fluyen fácil", "sus soles fluyen naturalmente juntos"),
    "oposición": ("Polos opuestos", "sus soles son polos opuestos que se atraen"),
    "sin aspecto mayor": ("Por descubrir", "sus soles no marcan un vínculo fuerte: la conexión está por descubrirse"),
}


def aspect_label(name: str) -> str:
    return ASPECT_TEXT.get(name, (name.capitalize(), name))[0]


def aspect_sentence(name: str) -> str:
    return ASPECT_TEXT.get(name, (name, name))[1]
