"""Fotos del perfil (spec A11) y su chequeo automático con IA (ADR 0013).

A la IA va solo la imagen: ningún dato del perfil. Si no responde, la foto se
acepta "sin revisar" para no bloquear a nadie por una caída.
"""

import base64
import json
import re
from dataclasses import dataclass
from pathlib import Path

from app import llm
from app.config import settings

CONFIG_PATH = Path(__file__).parent / "config" / "fotos_v1.json"


def is_image(content: bytes) -> bool:
    """Spec R1: JPG, PNG o WebP de verdad (sus primeros bytes), no vacía."""
    return (
        content.startswith(b"\xff\xd8\xff")
        or content.startswith(b"\x89PNG\r\n\x1a\n")
        or (content[:4] == b"RIFF" and content[8:12] == b"WEBP")
    )


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


@dataclass
class Verdict:
    revisada: bool  # False = la IA no respondió: se acepta "sin revisar"
    apta: bool = True
    motivo: str | None = None
    persona: bool | None = None


def _parse(text: str) -> Verdict | None:
    match = re.search(r"\{.*\}", text, re.S)  # a veces viene entre ```json ... ```
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except ValueError:
        return None
    if not isinstance(data, dict) or not isinstance(data.get("apta"), bool):
        return None
    persona = data.get("persona")
    return Verdict(
        revisada=True,
        apta=data["apta"],
        motivo=data.get("motivo") if isinstance(data.get("motivo"), str) else None,
        persona=persona if isinstance(persona, bool) else None,
    )


def check(content: bytes, content_type: str) -> Verdict:
    cfg = load_config()["moderacion"]
    image = f"data:{content_type};base64,{base64.b64encode(content).decode()}"
    result = llm.converse(
        cfg["prompt"],
        [{"role": "user", "content": [{"type": "image_url", "image_url": {"url": image}}]}],
        max_chars=500,
        max_tokens=cfg["max_tokens"],
        timeout=cfg["timeout_segundos"],
        model=settings.openrouter_moderation_model,
        temperature=0,
        # Que el proveedor no guarde ni use la imagen (ADR 0013).
        extra={"provider": {"data_collection": "deny"}},
    )
    verdict = _parse(result.text) if result else None
    return verdict or Verdict(revisada=False)


def rejection_message(verdict: Verdict) -> str:
    cfg = load_config()
    motivo = cfg["motivos"].get(verdict.motivo or "otro", cfg["motivos"]["otro"])
    return cfg["rechazo"].format(motivo=motivo)
