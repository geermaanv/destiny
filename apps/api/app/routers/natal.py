import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai_texts import cached, carta_key, record
from app.auth import require_self, session_profile_id
from app.content.carta import load_library
from app.database import get_db
from app.models import Profile
from app.natal.dimensions import load_config, natal_dimensions
from app.natal.synthesis import synthesize
from app.personalization.style import prompt_instructions, style_for
from app.schemas import NatalDimensionsOut, NatalSynthesisOut

# Mi carta: autoconocimiento por dimensiones (spec A8).
router = APIRouter(tags=["natal"])


def _own(profile_id: uuid.UUID, current: uuid.UUID | None, db: Session) -> Profile:
    require_self(profile_id, current)
    profile = db.get(Profile, profile_id)
    if profile is None or profile.birth_date is None:
        raise HTTPException(status_code=409, detail="Perfil sin datos natales")
    return profile


@router.get("/profiles/{profile_id}/natal/dimensions", response_model=NatalDimensionsOut)
def get_dimensions(
    profile_id: uuid.UUID, db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> NatalDimensionsOut:
    return NatalDimensionsOut(**natal_dimensions(_own(profile_id, current, db)))


@router.get("/profiles/{profile_id}/natal/dimensions/{clave}/synthesis", response_model=NatalSynthesisOut)
def get_synthesis(
    profile_id: uuid.UUID,
    clave: str,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> NatalSynthesisOut:
    profile = _own(profile_id, current, db)
    if clave not in load_config()["dimensiones"]:
        raise HTTPException(status_code=404, detail="Dimensión inexistente")
    result = natal_dimensions(profile)
    dimension = next(d for d in result["dimensiones"] if d["clave"] == clave)
    text, ai = dimension_synthesis(db, profile, dimension, result["aproximado"], style_for(profile))
    return NatalSynthesisOut(texto=text, ia=ai)


def dimension_synthesis(db: Session, profile: Profile, dimension: dict, approximate: bool, style: dict) -> tuple[str, bool]:
    """Síntesis de una dimensión, desde la cache si ya se redactó (la usa también Compartir mi carta, spec A9)."""
    versions = f"{load_config()['version']}/{load_library().get('version', '')}"
    key = carta_key(profile, dimension["clave"], style, versions)
    if (text := cached(db, key)) is not None:
        return text, True
    written = synthesize(dimension, approximate, prompt_instructions(style))
    record(db, key, "carta", written)
    return written.text, written.ai is not None
