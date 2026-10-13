import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_self, session_profile_id
from app.database import get_db
from app.models import Profile
from app.personalization.style import style_for
from app.schemas import StyleIn, StyleOut

# Hiperpersonalización v1: "Cómo te hablamos" (spec X2).
router = APIRouter(tags=["style"])


def _own(profile_id: uuid.UUID, current: uuid.UUID | None, db: Session) -> Profile:
    require_self(profile_id, current)
    profile = db.get(Profile, profile_id)
    if profile is None or profile.birth_date is None:
        raise HTTPException(status_code=409, detail="Perfil sin datos natales")
    return profile


@router.get("/profiles/{profile_id}/style", response_model=StyleOut)
def get_style(
    profile_id: uuid.UUID, db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> StyleOut:
    return StyleOut(**style_for(_own(profile_id, current, db)))


@router.put("/profiles/{profile_id}/style", response_model=StyleOut)
def set_style(
    profile_id: uuid.UUID,
    payload: StyleIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> StyleOut:
    profile = _own(profile_id, current, db)
    if "registro" in payload.model_fields_set:
        profile.style_registro = payload.registro
    if "tema" in payload.model_fields_set:
        profile.style_tema = payload.tema
    if "modo" in payload.model_fields_set:
        profile.style_modo = payload.modo
    if "fondo" in payload.model_fields_set:
        profile.style_fondo_tipo = payload.fondo
    db.commit()
    db.refresh(profile)
    return StyleOut(**style_for(profile))
