"""Cache y registro de uso de los textos de IA (spec X1)."""

import hashlib
import uuid

from sqlalchemy.orm import Session

from app.config import settings
from app.explainer import Written
from app.models import AIText
from app.synastry.engine import load_config


def explanation_key(viewer: uuid.UUID, candidate: uuid.UUID, context: str) -> str:
    raw = f"explicacion:{viewer}:{candidate}:{context}:{settings.openrouter_model}:{load_config()['version']}"
    return hashlib.sha256(raw.encode()).hexdigest()


def cached(db: Session, key: str) -> str | None:
    row = db.get(AIText, key)
    return row.text if row else None


def record(db: Session, key: str, kind: str, written: Written) -> None:
    """Guarda solo lo que escribió la IA (las plantillas no se cachean ni cuestan)."""
    if written.ai is None or db.get(AIText, key) is not None:
        return
    db.add(
        AIText(
            key=key,
            kind=kind,
            text=written.text,
            model=written.ai.model,
            prompt_tokens=written.ai.prompt_tokens,
            completion_tokens=written.ai.completion_tokens,
        )
    )
    db.commit()
