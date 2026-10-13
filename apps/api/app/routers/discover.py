import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_self, session_profile_id
from app.database import get_db
from app.explainer import ResonanceExplainer, get_explainer
from app.models import PersonalityAnswers, Profile
from app.personality import CONTEXT_TO_MODE
from app.personality.engine import compare
from app.public_profile import public_fields
from app.ai_texts import cached, explanation_key, record
from app.synastry import ai_facts, headline, profile_synastry
from app.schemas import DiscoverCandidateOut, ExplanationOut, PersonalityCompatOut

router = APIRouter(prefix="/discover", tags=["discover"])

Relationship = Literal["pareja", "amistad", "laboral", "ocasional"]
MAX_CANDIDATES = 5  # "lista curada y chica" (B5-pantalla-descubrir.md)


def _require_verified_profile(profile_id: uuid.UUID, db: Session) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.verification_status != "verificado":
        raise HTTPException(status_code=403, detail="Identidad no verificada")
    return profile


@router.get("", response_model=list[DiscoverCandidateOut])
def list_discover(
    viewer_id: uuid.UUID = Query(...),
    context: Relationship = Query(default="pareja"),
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> list[DiscoverCandidateOut]:
    require_self(viewer_id, current)
    viewer = _require_verified_profile(viewer_id, db)
    if viewer.birth_date is None:
        raise HTTPException(status_code=409, detail="Perfil sin datos natales")

    candidates = db.scalars(
        select(Profile)
        .where(
            Profile.verification_status == "verificado",
            Profile.id != viewer_id,
            Profile.birth_date.is_not(None),
            # Perfil incompleto (sin nombre, spec A4) no aparece en Descubrir.
            Profile.display_name.is_not(None),
        )
    ).all()

    # Test de personalidad de Pablo (A6): separado de la astrología, solo el resultado.
    mode = CONTEXT_TO_MODE[context]
    answers = {
        row.profile_id: row.answers
        for row in db.scalars(
            select(PersonalityAnswers).where(PersonalityAnswers.profile_id.in_([viewer.id, *[c.id for c in candidates]]))
        )
    }
    mine = answers.get(viewer.id)

    # Lista curada y chica: los de mayor compatibilidad para el contexto elegido (B5).
    results = []
    for candidate in candidates:
        result = profile_synastry(viewer, candidate, context)
        theirs = answers.get(candidate.id)
        personality = PersonalityCompatOut(**compare(mine, theirs, mode)) if mine and theirs else None
        results.append(
            DiscoverCandidateOut(
                profile_id=candidate.id,
                compatibility_pct=result["total"],
                preview=headline(result),
                axes=result["ejes"],
                relationship=result["tipo_de_relacion"],
                approximate=result["aproximado"],
                personality=personality,
                **public_fields(candidate),
            )
        )
    results.sort(key=lambda r: r.compatibility_pct, reverse=True)
    return results[:MAX_CANDIDATES]


@router.get("/{candidate_id}/explanation", response_model=ExplanationOut)
def get_explanation(
    candidate_id: uuid.UUID,
    viewer_id: uuid.UUID = Query(...),
    context: Relationship = Query(default="pareja"),
    db: Session = Depends(get_db),
    explainer: ResonanceExplainer = Depends(get_explainer),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> ExplanationOut:
    require_self(viewer_id, current)
    viewer = _require_verified_profile(viewer_id, db)
    candidate = _require_verified_profile(candidate_id, db)

    if viewer.birth_date is None or candidate.birth_date is None:
        raise HTTPException(status_code=422, detail="Perfil sin datos natales")

    # Cache (spec X1): misma pareja + vínculo + modelo + tablas → no se vuelve a pagar.
    key = explanation_key(viewer, candidate, context)
    if (text := cached(db, key)) is not None:
        return ExplanationOut(text=text)

    result = profile_synastry(viewer, candidate, context)
    mine, theirs = db.get(PersonalityAnswers, viewer.id), db.get(PersonalityAnswers, candidate.id)
    personality = (
        compare(mine.answers, theirs.answers, CONTEXT_TO_MODE[context]) if mine and theirs and mine.answers and theirs.answers else None
    )
    written = explainer.explain(ai_facts(result, personality))
    record(db, key, "explicacion", written)
    return ExplanationOut(text=written.text)
