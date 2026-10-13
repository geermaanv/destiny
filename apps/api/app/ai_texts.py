"""Cache y registro de uso de los textos de IA (spec X1)."""

import hashlib

from sqlalchemy.orm import Session

from app.config import settings
from app.explainer import Written
from app.models import AIText, Profile
from app.synastry.engine import load_config


def _chart_fingerprint(profile: Profile) -> str:
    """Si cambian los datos natales, cambia la clave y no se usa la explicación vieja (spec A1 v2)."""
    return (
        f"{profile.birth_date}|{profile.birth_time}|{profile.birth_time_estimated}|"
        f"{profile.birth_place_lat}|{profile.birth_place_lon}|{profile.birth_place_timezone}"
    )


def explanation_key(viewer: Profile, candidate: Profile, context: str, style: dict | None = None) -> str:
    """`style` (spec X2): si cambia el estilo de quien lee, se vuelve a redactar."""
    style_part = f"{style['registro']}/{style['tono']}/{style['formato']}" if style else "-"
    raw = (
        f"explicacion:{viewer.id}:{_chart_fingerprint(viewer)}:{candidate.id}:{_chart_fingerprint(candidate)}:"
        f"{context}:{style_part}:{settings.openrouter_model}:{load_config()['version']}"
    )
    return hashlib.sha256(raw.encode()).hexdigest()


def carta_key(profile: Profile, dimension: str, style: dict, versions: str) -> str:
    """Síntesis de Mi carta (spec A8): cambia si cambian los datos natales, el estilo, el modelo o los textos."""
    raw = (
        f"carta:{profile.id}:{_chart_fingerprint(profile)}:{dimension}:"
        f"{style['registro']}/{style['tono']}/{style['formato']}:{settings.openrouter_model}:{versions}"
    )
    return hashlib.sha256(raw.encode()).hexdigest()


def day_key(profile: Profile, day, style: dict, version: str) -> str:
    """Lectura de Tu día completo (spec B4 v3): una por persona y día, por estilo y modelo."""
    raw = (
        f"dia:{profile.id}:{_chart_fingerprint(profile)}:{day}:{style['registro']}/{style['tono']}/{style['formato']}:"
        f"{settings.openrouter_model}:{version}"
    )
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
