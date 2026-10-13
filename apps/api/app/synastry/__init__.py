"""Motor oficial de compatibilidad Destiny 1.0 (spec A7, calculadoras de Pablo).

- chart.py: carta natal completa (planetas, nodos, ascendente, casas por signo entero).
- engine.py: E1–E4 y modificadores E5, leyendo todas las tablas de
  config/synastry_v2.json (generado desde los Excel; nada de contenido astrológico en el código).
"""

AXIS_LABELS = {
    "atraccion": "Química",
    "afecto": "Afecto",
    "comunicacion": "Comunicación",
    "compromiso": "Compromiso",
}
RELATIONSHIP_TYPES = ("pareja", "amistad", "laboral", "ocasional")


def profile_synastry(viewer, candidate, relationship: str | None = None) -> dict:
    """Sinastría completa entre dos perfiles (spec A7)."""
    from app.synastry.chart import chart_for_profile
    from app.synastry.engine import synastry

    return synastry(chart_for_profile(viewer), chart_for_profile(candidate), relationship)


def relevant_axes(result: dict) -> list[str]:
    """Ejes que pesan en el tipo de relación (ej. en Trabajo la química casi no cuenta). Umbral en la configuración."""
    from app.synastry.engine import load_config

    cfg = load_config()
    min_weight = cfg["explicacion"]["peso_minimo_eje"]
    weights = cfg["tipos_de_relacion"]["tipos"][result["tipo_de_relacion"]]["pesos"]
    return [axis for axis in AXIS_LABELS if weights.get(axis, 0) >= min_weight]


def headline(result: dict) -> str:
    """Etiqueta corta para la tarjeta de Descubrir: el eje más fuerte entre los que importan."""
    best = max(relevant_axes(result), key=lambda axis: result["ejes"][axis])
    return f"Fuerte en {AXIS_LABELS[best].lower()}"


ASPECT_NAMES = {
    "conjuncion": "conjunción", "semisextil": "semisextil", "semicuadratura": "semicuadratura", "sextil": "sextil",
    "cuadratura": "cuadratura", "trigono": "trígono", "sesquicuadratura": "sesquicuadratura",
    "quincuncio": "quincuncio", "oposicion": "oposición", "quintil": "quintil", "biquintil": "biquintil",
}
POINT_NAMES = {
    "sol": "Sol", "luna": "Luna", "mercurio": "Mercurio", "venus": "Venus", "marte": "Marte", "jupiter": "Júpiter",
    "saturno": "Saturno", "urano": "Urano", "neptuno": "Neptuno", "pluton": "Plutón", "asc": "Ascendente",
    "mc": "Medio Cielo", "nodo_norte": "Nodo Norte",
}


def ai_facts(result: dict, personality: dict | None = None) -> dict:
    """Lo único que se le manda a la IA (spec X1): resultados calculados, sin datos personales."""
    aspects = sorted(
        (a | {"eje": axis} for axis, d in result["detalle"].items() for a in d["aspectos_encontrados"]),
        key=lambda a: -abs(a["puntos"]),
    )[:4]
    # El modelo decide qué es fuerte y qué es débil; la IA solo lo redacta (spec X1).
    relevant = relevant_axes(result)
    facts = {
        "tipo_de_relacion": result["tipo_de_relacion"],
        "total": result["total"],
        "ejes": result["ejes"],
        "niveles": {
            axis: "alto" if value >= 60 else "bajo" if value < 40 else "medio" for axis, value in result["ejes"].items()
        },
        "lo_que_mas_los_une": max(relevant, key=result["ejes"].get),
        "lo_que_tienen_que_trabajar": min(relevant, key=result["ejes"].get),
        "aproximado": result["aproximado"],
        "aspectos_destacados": [
            f"{POINT_NAMES.get(a['a'], a['a'])} de una persona en {ASPECT_NAMES.get(a['aspecto'], a['aspecto'])} "
            f"con {POINT_NAMES.get(a['b'], a['b'])} de la otra ({AXIS_LABELS[a['eje']].lower()})"
            for a in aspects
        ],
    }
    if personality:
        facts["test_de_personalidad"] = {"ejes": personality.get("axes"), "total": personality.get("total")}
    return facts
