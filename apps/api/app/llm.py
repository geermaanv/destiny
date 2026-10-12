"""Redacción con IA vía OpenRouter (spec X1, ADR 0011: la IA solo redacta).

Una sola función, `complete`: manda un prompt al modelo configurado y devuelve
el texto limpio y recortado, o None si no hay key, falla, tarda o viene vacío
(en ese caso quien llama usa su texto de plantilla).
"""

import logging
import re
from dataclasses import dataclass

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
TIMEOUT_SECONDS = 8
MAX_TOKENS = 300
TEMPERATURE = 0.7
# Los tests lo reemplazan por un OpenRouter simulado (httpx.MockTransport).
TRANSPORT: httpx.BaseTransport | None = None


@dataclass
class LLMResult:
    text: str
    model: str
    prompt_tokens: int | None
    completion_tokens: int | None


def is_configured() -> bool:
    return bool(settings.openrouter_api_key and settings.openrouter_model)


def clean(text: str) -> str:
    return text.strip().strip('"“”«»\'').strip()


def trim_by_sentence(text: str, max_chars: int) -> str:
    """Recorta al máximo de caracteres sin cortar una oración por la mitad."""
    if len(text) <= max_chars:
        return text
    out = ""
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        candidate = f"{out} {sentence}".strip()
        if len(candidate) > max_chars:
            break
        out = candidate
    return out or text[:max_chars].rsplit(" ", 1)[0] + "…"


def complete(system: str, user: str, max_chars: int) -> LLMResult | None:
    if not is_configured():
        return None
    try:
        with httpx.Client(transport=TRANSPORT, timeout=TIMEOUT_SECONDS) as client:
            response = client.post(
                OPENROUTER_URL,
                headers={"Authorization": f"Bearer {settings.openrouter_api_key}", "X-Title": "Destiny"},
                json={
                    "model": settings.openrouter_model,
                    "max_tokens": MAX_TOKENS,
                    "temperature": TEMPERATURE,
                    # Los modelos que "piensan" gastaban los tokens pensando y devolvían vacío (spec X1).
                    "reasoning": {"enabled": False},
                    "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                },
            )
            response.raise_for_status()
            data = response.json()
        text = clean(data["choices"][0]["message"]["content"] or "")
        if not text:
            return None
        usage = data.get("usage") or {}
        return LLMResult(
            text=trim_by_sentence(text, max_chars),
            model=data.get("model") or settings.openrouter_model,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
        )
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
        logger.warning("OpenRouter falló, se usa la plantilla: %s", exc)
        return None
