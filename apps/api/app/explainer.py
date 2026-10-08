import json
from typing import Protocol

from app.aspects import aspect_sentence
from app.synastry import relevant_axes
from app.config import settings

EDITORIAL_GUIDELINE = (
    "Sos la voz editorial de Destiny. Explicá en 2-3 oraciones, en español, "
    "cálido y cercano, por qué estas dos personas podrían resonar ahora. "
    "Nunca determinista ni supersticioso: la astrología es una invitación a "
    "mirar, no una predicción cerrada. Nunca muestres el porcentaje en bruto "
    "sin esta explicación."
)


class ResonanceExplainer(Protocol):
    def explain(self, viewer: dict, candidate: dict, signals: dict) -> str: ...


class MockResonanceExplainer:
    """Sin ANTHROPIC_API_KEY configurada: texto editorial borrador, no LLM.

    Reemplazable por ClaudeResonanceExplainer sin tocar el router ni el
    contrato de datos (mismo principio de adapter que ADR 0006 para KYC).
    """

    def explain(self, viewer: dict, candidate: dict, signals: dict) -> str:
        if "ejes" in signals:
            return self._explain_axes(signals)
        pct = signals["percentage"]
        return (
            f"{aspect_sentence(signals['aspect']).capitalize()}, con un {pct}% de resonancia. "
            "No es una garantía, es una invitación: el momento parece acompañar "
            "el encuentro, vale la pena ver qué pasa cuando se cruzan."
        )


    def _explain_axes(self, signals: dict) -> str:
        # Motor de sinastría (B5): el eje más fuerte y el más flojo, en lenguaje simple.
        axes = signals["ejes"]
        relevant = relevant_axes(signals)
        best = max(relevant, key=axes.get)
        worst = min(relevant, key=axes.get)
        context = CONTEXT_PHRASE.get(signals["tipo_de_relacion"], "")
        text = (
            f"{context}lo que más los une es {AXIS_PHRASE[best]} ({axes[best]}/100)"
            f", y lo que más van a tener que trabajar es {AXIS_PHRASE[worst]} ({axes[worst]}/100). "
            f"En total, {signals['total']}% de resonancia. No es una garantía, es una invitación."
        )
        if signals.get("aproximado"):
            text += " (Aproximado: alguno de los dos no sabe su hora exacta.)"
        return text[0].upper() + text[1:]


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


class ClaudeResonanceExplainer:
    def __init__(self, api_key: str) -> None:
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key)

    def explain(self, viewer: dict, candidate: dict, signals: dict) -> str:
        message = self._client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=300,
            system=EDITORIAL_GUIDELINE,
            messages=[
                {
                    "role": "user",
                    "content": json.dumps({"viewer": viewer, "candidate": candidate, "signals": signals}),
                }
            ],
        )
        return "".join(block.text for block in message.content if block.type == "text")


def get_explainer() -> ResonanceExplainer:
    if settings.anthropic_api_key:
        return ClaudeResonanceExplainer(settings.anthropic_api_key)
    return MockResonanceExplainer()
