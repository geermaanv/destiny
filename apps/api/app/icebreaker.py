"""Rompehielos: primer mensaje del chat (B7), redactado con IA (spec X1).

Recibe solo el resultado ya calculado (`ai_facts`). Sin key o si falla, plantilla.
"""

import json
from typing import Protocol

from app.explainer import Written
from app.llm import complete, is_configured
from app.synastry import AXIS_LABELS, relevant_axes

MAX_CHARS = 280

EDITORIAL_GUIDELINE = (
    "Sos la voz editorial de Destiny, una app argentina de conexiones con astrología. "
    "Escribí, en castellano rioplatense y con voseo, el primer mensaje de un chat entre dos personas que "
    "acaban de conectar: 1 o 2 oraciones, en primera persona del plural, inspiradas en el eje "
    "'lo_que_mas_los_une' (ya viene decidido; atraccion = química, afecto = lo emocional, comunicacion = forma de "
    "comunicarse, compromiso = construir algo estable), y que terminen en una pregunta para empezar a charlar. "
    "No cites números. Nada genérico tipo 'hola, ¿cómo estás?', nada sexual explícito, no menciones que sos una IA. "
    "Texto plano, sin markdown. Respondé solo con el mensaje."
)


class IcebreakerGenerator(Protocol):
    def generate(self, facts: dict) -> Written: ...


def template_icebreaker(facts: dict) -> str:
    best = max(relevant_axes(facts), key=facts["ejes"].get)
    return (
        f"Che, Destiny dice que lo nuestro es fuerte en {AXIS_LABELS[best].lower()}. "
        "¿Vos sentís que sos de las personas intensas o de las tranquilas del grupo?"
    )


class TemplateIcebreakerGenerator:
    def generate(self, facts: dict) -> Written:
        return Written(template_icebreaker(facts), None)


class OpenRouterIcebreakerGenerator:
    def generate(self, facts: dict) -> Written:
        result = complete(EDITORIAL_GUIDELINE, json.dumps(facts, ensure_ascii=False), MAX_CHARS)
        return Written(result.text, result) if result else Written(template_icebreaker(facts), None)


def get_icebreaker_generator() -> IcebreakerGenerator:
    return OpenRouterIcebreakerGenerator() if is_configured() else TemplateIcebreakerGenerator()
