import json
from typing import Protocol

from app.aspects import aspect_label
from app.config import settings

EDITORIAL_GUIDELINE = (
    "Sos la voz editorial de Destiny. Generá, en español, un primer mensaje de "
    "chat (1-2 oraciones) entre dos personas que acaban de matchear, basado en "
    "el aspecto astrológico más fuerte entre sus cartas. Cálido, concreto, con "
    "una pregunta o gancho que invite a responder. Nunca un genérico 'hola, "
    "¿cómo estás?'."
)


class IcebreakerGenerator(Protocol):
    def generate(self, profile_a: dict, profile_b: dict, signals: dict) -> str: ...


class MockIcebreakerGenerator:
    """Sin ANTHROPIC_API_KEY: copy editorial borrador, mismo adapter que
    ResonanceExplainer (app/explainer.py) y KYC (ADR 0006)."""

    def generate(self, profile_a: dict, profile_b: dict, signals: dict) -> str:
        return (
            f"Che, Destiny dice que lo nuestro es «{aspect_label(signals['aspect']).lower()}». "
            "¿Vos sentís que sos de las personas intensas o de las tranquilas del grupo?"
        )


class ClaudeIcebreakerGenerator:
    def __init__(self, api_key: str) -> None:
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key)

    def generate(self, profile_a: dict, profile_b: dict, signals: dict) -> str:
        message = self._client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=200,
            system=EDITORIAL_GUIDELINE,
            messages=[
                {
                    "role": "user",
                    "content": json.dumps({"profile_a": profile_a, "profile_b": profile_b, "signals": signals}),
                }
            ],
        )
        return "".join(block.text for block in message.content if block.type == "text")


def get_icebreaker_generator() -> IcebreakerGenerator:
    if settings.anthropic_api_key:
        return ClaudeIcebreakerGenerator(settings.anthropic_api_key)
    return MockIcebreakerGenerator()
