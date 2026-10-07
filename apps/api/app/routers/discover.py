import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.aspects import aspect_label
from app.compatibility import compatibility_signals
from app.database import get_db
from app.explainer import ResonanceExplainer, get_explainer
from app.models import Profile
from app.schemas import DiscoverCandidateOut, ExplanationOut

router = APIRouter(prefix="/discover", tags=["discover"])

MAX_CANDIDATES = 5  # "lista curada y chica" (B5-pantalla-descubrir.md)


def _require_verified_profile(profile_id: uuid.UUID, db: Session) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.verification_status != "verificado":
        raise HTTPException(status_code=403, detail="Identidad no verificada")
    return profile


def _chart_payload(profile: Profile) -> dict:
    return {
        "birth_date": str(profile.birth_date),
        "birth_time": str(profile.birth_time),
        "intent": "pareja",  # v1 asume un solo contexto de relación, ver BACKLOG P0
    }


@router.get("", response_model=list[DiscoverCandidateOut])
def list_discover(viewer_id: uuid.UUID = Query(...), db: Session = Depends(get_db)) -> list[DiscoverCandidateOut]:
    viewer = _require_verified_profile(viewer_id, db)
    if viewer.birth_date is None:
        raise HTTPException(status_code=409, detail="Perfil sin datos natales")

    candidates = db.scalars(
        select(Profile)
        .where(
            Profile.verification_status == "verificado",
            Profile.id != viewer_id,
            Profile.birth_date.is_not(None),
        )
        .limit(MAX_CANDIDATES)
    ).all()

    results = []
    for candidate in candidates:
        signals = compatibility_signals(viewer, candidate)
        results.append(
            DiscoverCandidateOut(
                profile_id=candidate.id,
                compatibility_pct=signals["percentage"],
                preview=aspect_label(signals["aspect"]),
            )
        )
    return results


@router.get("/{candidate_id}/explanation", response_model=ExplanationOut)
def get_explanation(
    candidate_id: uuid.UUID,
    viewer_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
    explainer: ResonanceExplainer = Depends(get_explainer),
) -> ExplanationOut:
    viewer = _require_verified_profile(viewer_id, db)
    candidate = _require_verified_profile(candidate_id, db)

    if viewer.birth_date is None or candidate.birth_date is None:
        raise HTTPException(status_code=422, detail="Perfil sin datos natales")

    signals = compatibility_signals(viewer, candidate)
    text = explainer.explain(_chart_payload(viewer), _chart_payload(candidate), signals)
    return ExplanationOut(text=text)
