import math
import unicodedata
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.auth import is_active, require_self, session_profile_id
from app.config import settings
from app.database import get_db
from app.explainer import ResonanceExplainer, get_explainer
from app.models import PersonalityAnswers, Profile
from app.personality import CONTEXT_TO_MODE
from app.personality.engine import compare
from app.public_profile import age, public_fields
from app.ai_texts import cached, explanation_key, record
from app.personalization.style import prompt_instructions, style_for
from app.synastry import AXIS_LABELS, ai_facts, headline, profile_synastry
from app.schemas import DiscoverCandidateOut, ExplanationOut, PersonalityCompatOut, SystemOut

router = APIRouter(prefix="/discover", tags=["discover"])

Relationship = Literal["pareja", "amistad", "laboral", "ocasional"]
MAX_CANDIDATES = 5  # "lista curada y chica" (B5-pantalla-descubrir.md)


def account_filter():
    """Quién aparece en Descubrir y en "tu frecuencia": verificados o, si la verificación no es
    obligatoria (spec A10), cualquier cuenta activa."""
    verified = Profile.verification_status == "verificado"
    return verified if settings.verificacion_obligatoria else or_(verified, Profile.activated_at.is_not(None))


def _require_verified_profile(profile_id: uuid.UUID, db: Session) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    allowed = profile.verification_status == "verificado" if settings.verificacion_obligatoria else is_active(profile)
    if not allowed:
        raise HTTPException(status_code=403, detail="Identidad no verificada")
    return profile


SISTEMAS = ("astrologia", "personalidad")
MAX_SEARCH = 20  # búsqueda por nombre (spec B8)
# Ejes del test de Pablo ↔ ejes de la astrología: miden las mismas cuatro dimensiones (spec B9).
TEST_AXES = {"E1": "atraccion", "E2": "afecto", "E3": "comunicacion", "E4": "compromiso"}
EARTH_KM = 6371.0


def _mean(values: list[float | None]) -> float | None:
    present = [v for v in values if v is not None]
    return sum(present) / len(present) if present else None


def distance_km(a: Profile, b: Profile) -> int | None:
    """Distancia entre dónde viven (haversine), en km redondeados; mínimo 1 (spec B9)."""
    if None in (a.residence_lat, a.residence_lon, b.residence_lat, b.residence_lon):
        return None
    lat1, lon1, lat2, lon2 = map(math.radians, (a.residence_lat, a.residence_lon, b.residence_lat, b.residence_lon))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return max(1, round(2 * EARTH_KM * math.asin(math.sqrt(h))))


def _fold(text: str) -> str:
    """Minúsculas y sin acentos, para buscar "jose" y encontrar "José"."""
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")


def _wants(viewer: Profile, other: Profile) -> bool:
    """Si `other` entra en lo que `viewer` eligió ver (spec B8). Sin "Mostrame" ve a todos."""
    if not viewer.show_me:
        return True
    if other.gender is None:
        return False  # no sabemos si encaja
    if other.gender in viewer.show_me:
        return True
    return other.gender == "no_binario" and any(g in viewer.show_me for g in other.appear_in)


def gender_match(viewer: Profile, candidate: Profile) -> bool:
    """Mutuo: cada uno entra en lo que el otro quiere ver."""
    return _wants(viewer, candidate) and _wants(candidate, viewer)


@router.get("", response_model=list[DiscoverCandidateOut])
def list_discover(
    viewer_id: uuid.UUID = Query(...),
    context: Relationship = Query(default="pareja"),
    sistemas: str = Query(default="astrologia,personalidad"),
    min_pct: int = Query(default=0, ge=0, le=100),
    edad_min: int = Query(default=18, ge=18, le=99),
    edad_max: int = Query(default=99, ge=18, le=99),
    max_km: int | None = Query(default=None, ge=1, le=20000),
    q: str | None = Query(default=None, max_length=40),
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> list[DiscoverCandidateOut]:
    require_self(viewer_id, current)
    viewer = _require_verified_profile(viewer_id, db)
    if viewer.birth_date is None:
        raise HTTPException(status_code=409, detail="Perfil sin datos natales")
    if edad_min > edad_max:
        raise HTTPException(status_code=422, detail="La edad mínima no puede ser mayor que la máxima")
    included = {s.strip() for s in sistemas.split(",") if s.strip()}
    if not included or not included <= set(SISTEMAS):
        raise HTTPException(status_code=422, detail="Elegí al menos un sistema: astrologia o personalidad")
    search = _fold(q.strip()) if q and q.strip() else None
    if max_km is not None and not search and viewer.residence_lat is None:
        raise HTTPException(status_code=409, detail="Contanos dónde vivís para filtrar por distancia")

    candidates = db.scalars(
        select(Profile)
        .where(
            account_filter(),
            Profile.id != viewer_id,
            Profile.birth_date.is_not(None),
            # Perfil incompleto (sin nombre, spec A4) no aparece en Descubrir.
            Profile.display_name.is_not(None),
            # Sin foto no se aparece (spec A11).
            Profile.photo_path.is_not(None),
        )
    ).all()
    # Género y "Mostrame" (spec B8): solo para pareja, también en la búsqueda.
    if context == "pareja":
        candidates = [c for c in candidates if gender_match(viewer, c)]
    if search:
        candidates = [c for c in candidates if search in _fold(c.display_name or "")]

    # Test de personalidad de Pablo (A6): separado de la astrología, solo el resultado.
    mode = CONTEXT_TO_MODE[context]
    answers = {
        row.profile_id: row.answers
        for row in db.scalars(
            select(PersonalityAnswers).where(PersonalityAnswers.profile_id.in_([viewer.id, *[c.id for c in candidates]]))
        )
    }
    mine = answers.get(viewer.id)
    if included == {"personalidad"} and not mine and not search:
        raise HTTPException(status_code=409, detail="Completá tu test de personalidad para usar este filtro")

    results = []
    for candidate in candidates:
        distance = distance_km(viewer, candidate)
        theirs = answers.get(candidate.id)
        personality = PersonalityCompatOut(**compare(mine, theirs, mode)) if mine and theirs else None
        if not search:
            # La búsqueda por nombre ignora sistemas, compatibilidad, edad y distancia (specs B8, B9).
            candidate_age = age(candidate.birth_date)
            if candidate_age is None or not edad_min <= candidate_age <= edad_max:
                continue
            if max_km is not None and (distance is None or distance > max_km):
                continue
        result = profile_synastry(viewer, candidate, context)

        # Cada sistema con los pesos de Pablo para el vínculo; el global es su promedio simple (ADR 0014).
        systems: dict[str, SystemOut | None] = {"astrologia": None, "personalidad": None}
        totals: list[float] = []
        if "astrologia" in included:
            systems["astrologia"] = SystemOut(total=result["total"], axes=dict(result["ejes"]))
            totals.append(result["total"])
        if "personalidad" in included and personality is not None and personality.total is not None:
            test_axes = {TEST_AXES[k]: (round(v) if v is not None else None) for k, v in personality.axes.items()}
            systems["personalidad"] = SystemOut(total=round(personality.total), axes=test_axes)
            totals.append(personality.total)
        if not totals:
            if search:
                totals.append(result["total"])  # la búsqueda muestra a la persona aunque no tenga test
            else:
                continue  # solo test y esta persona no lo completó
        global_pct = round(sum(totals) / len(totals))
        if not search and global_pct < min_pct:
            continue
        axes_global = {
            axis: (round(m) if (m := _mean([s.axes.get(axis) for s in systems.values() if s])) is not None else None)
            for axis in AXIS_LABELS
        }
        results.append(
            DiscoverCandidateOut(
                profile_id=candidate.id,
                compatibility_pct=global_pct,
                global_pct=global_pct,
                axes_global=axes_global,
                systems=systems,
                distance_km=distance,
                astrology_pct=result["total"],
                preview=headline(result),
                axes=result["ejes"],
                relationship=result["tipo_de_relacion"],
                approximate=result["aproximado"],
                personality=personality,
                verificado=candidate.verification_status == "verificado",
                **public_fields(candidate),
            )
        )
    # Lista curada y chica: los de mayor número global (B5, B9).
    results.sort(key=lambda r: r.global_pct, reverse=True)
    return results[: MAX_SEARCH if search else MAX_CANDIDATES]


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
    # Hiperpersonalización (spec X2): se redacta en el estilo de quien lee.
    style = style_for(viewer)
    key = explanation_key(viewer, candidate, context, style)
    if (text := cached(db, key)) is not None:
        return ExplanationOut(text=text)

    result = profile_synastry(viewer, candidate, context)
    mine, theirs = db.get(PersonalityAnswers, viewer.id), db.get(PersonalityAnswers, candidate.id)
    personality = (
        compare(mine.answers, theirs.answers, CONTEXT_TO_MODE[context]) if mine and theirs and mine.answers and theirs.answers else None
    )
    written = explainer.explain(ai_facts(result, personality), prompt_instructions(style))
    record(db, key, "explicacion", written)
    return ExplanationOut(text=written.text)
