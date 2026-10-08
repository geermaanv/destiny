"""Motor de sinastría por ejes (spec B5-motor-sinastria.md).

- chart.py: carta natal completa (planetas, ascendente, casas).
- engine.py: los 10 niveles del cuadro, leyendo todas las tablas de
  config/synastry_v1.json (nada de contenido astrológico en el código).
"""

AXIS_LABELS = {
    "atraccion": "Química",
    "afecto": "Afecto",
    "comunicacion": "Comunicación",
    "compromiso": "Compromiso",
}
RELATIONSHIP_TYPES = ("pareja", "amistad", "laboral", "ocasional")


def profile_synastry(viewer, candidate, relationship: str | None = None) -> dict:
    """Sinastría completa entre dos perfiles (spec B5-motor-sinastria.md)."""
    from app.synastry.chart import chart_for_profile
    from app.synastry.engine import synastry

    return synastry(chart_for_profile(viewer), chart_for_profile(candidate), relationship)


def relevant_axes(result: dict, min_weight: float = 0.1) -> list[str]:
    """Ejes que pesan en el tipo de relación (ej. en amistad la química casi no cuenta)."""
    from app.synastry.engine import load_config

    weights = load_config()["nivel_7_y_10_tipos_de_relacion"]["tipos"][result["tipo_de_relacion"]]["pesos"]
    return [axis for axis in AXIS_LABELS if weights.get(axis, 0) >= min_weight]


def headline(result: dict) -> str:
    """Etiqueta corta para la tarjeta de Descubrir: el eje más fuerte entre los que importan."""
    best = max(relevant_axes(result), key=lambda axis: result["ejes"][axis])
    return f"Fuerte en {AXIS_LABELS[best].lower()}"
