"""Explicación de la resonancia en Descubrir (B5), redactada con IA (spec X1).

La IA recibe solo el resultado ya calculado (`ai_facts`), nunca datos personales.
Sin key o si falla, se usa el texto de plantilla.
"""

import json
from dataclasses import dataclass
from typing import Protocol

from app.llm import LLMResult, complete, is_configured
from app.synastry import relevant_axes

MAX_CHARS = 420

EDITORIAL_GUIDELINE = (
    "Sos la voz editorial de Destiny, una app argentina de conexiones con astrología. "
    "Escribí en castellano rioplatense, con voseo, cálido y concreto, sin jerga astrológica difícil. "
    "Explicá en 2 o 3 oraciones (máximo 60 palabras), para el tipo de vínculo indicado, qué une a estas dos "
    "personas (el eje 'lo_que_mas_los_une') y qué van a tener que trabajar (el eje 'lo_que_tienen_que_trabajar'). "
    "Esos dos ejes ya vienen decididos: no los cambies. Usá los 'niveles' (alto, medio, bajo) para describirlos; "
    "los puntajes van de 0 a 100 y 50 es lo promedio. Ejes: atraccion = química, afecto = lo emocional, "
    "comunicacion = forma de comunicarse, compromiso = construir algo estable. "
    "Nada de predicciones ('van a ser felices'), nada de contenido sexual explícito, no menciones que sos una IA. "
    "Texto plano, sin markdown. Respondé solo con el texto."
)

AXIS_PHRASE = {
    "atraccion": "la química",
    "afecto": "lo emocional",
    "comunicacion": "la forma de comunicarse",
    "compromiso": "la capacidad de construir algo estable",
}
CONTEXT_PHRASE = {
    "pareja": "como pareja, ",
    "amistad": "como amigos, ",
    "laboral": "para trabajar juntos, ",
    "ocasional": "para algo casual, ",
}


@dataclass
class Written:
    text: str
    ai: LLMResult | None  # None = texto de plantilla


class ResonanceExplainer(Protocol):
    def explain(self, facts: dict, style: str = "") -> Written: ...


def template_explanation(facts: dict) -> str:
    """El eje más fuerte y el más flojo entre los que importan para el vínculo."""
    axes = facts["ejes"]
    relevant = relevant_axes(facts)
    best = max(relevant, key=axes.get)
    worst = min(relevant, key=axes.get)
    text = (
        f"{CONTEXT_PHRASE.get(facts['tipo_de_relacion'], '')}lo que más los une es {AXIS_PHRASE[best]} "
        f"({axes[best]}/100), y lo que más van a tener que trabajar es {AXIS_PHRASE[worst]} ({axes[worst]}/100). "
        f"En total, {facts['total']}% de resonancia. No es una garantía, es una invitación."
    )
    if facts.get("aproximado"):
        text += " (Aproximado: alguno de los dos no sabe su hora exacta.)"
    return text[0].upper() + text[1:]


class TemplateResonanceExplainer:
    def explain(self, facts: dict, style: str = "") -> Written:
        return Written(template_explanation(facts), None)


class OpenRouterResonanceExplainer:
    def explain(self, facts: dict, style: str = "") -> Written:
        """`style`: instrucciones del estilo de quien lee (spec X2), se suman a la guía editorial."""
        system = f"{EDITORIAL_GUIDELINE} {style}".strip()
        result = complete(system, json.dumps(facts, ensure_ascii=False), MAX_CHARS)
        return Written(result.text, result) if result else Written(template_explanation(facts), None)


def get_explainer() -> ResonanceExplainer:
    return OpenRouterResonanceExplainer() if is_configured() else TemplateResonanceExplainer()
