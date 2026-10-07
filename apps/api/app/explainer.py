import json
from typing import Protocol

from app.aspects import aspect_sentence
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
        pct = signals["percentage"]
        return (
            f"{aspect_sentence(signals['aspect']).capitalize()}, con un {pct}% de resonancia. "
            "No es una garantía, es una invitación: el momento parece acompañar "
            "el encuentro, vale la pena ver qué pasa cuando se cruzan."
        )


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
