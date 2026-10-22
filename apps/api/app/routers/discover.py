import logging
import math
import unicodedata
import uuid
from typing import Literal, get_args

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.auth import is_active, require_self, session_profile_id
from app.config import settings
from app.database import get_db
from app.explainer import ResonanceExplainer, get_explainer
from app.models import Match, PersonalityAnswers, Profile
from app.personality import CONTEXT_TO_MODE
from app.personality.engine import compare
from app.public_profile import age, public_fields
from app.ai_texts import cached, explanation_key, record
from app.personalization.style import prompt_instructions, style_for
from app.compat_summary import SISTEMAS, public_personality, summarize
from app.synastry import AXIS_LABELS, ai_facts, profile_synastry
from app.schemas import DiscoverCandidateOut, ExplanationOut, Interest, PersonalityCompatOut, SystemOut

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/discover", tags=["discover"])

Relationship = Literal["pareja", "amistad", "laboral", "ocasional"]
MAX_CANDIDATES = 5  # "lista curada y chica" (B5-pantalla-descubrir.md)


def account_filter():
    """Quién aparece en Descubrir y en "tu frecuencia": verificados o, si la verificación no es
    obligatoria (spec A10), cualquier cuenta activa."""
    verified = Profile.verification_status == "verificado"
    return verified if settings.verificacion_obligatoria else or_(verified, Profile.activated_at.is_not(None))


def _blocked_ids(db: Session, profile_id: uuid.UUID) -> set[uuid.UUID]:
    rows = db.execute(
        select(Match.profile_a_id, Match.profile_b_id).where(
            Match.status == "bloqueada", or_(Match.profile_a_id == profile_id, Match.profile_b_id == profile_id)
        )
    ).all()
    return {b if a == profile_id else a for a, b in rows}


def _require_verified_profile(profile_id: uuid.UUID, db: Session) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    allowed = profile.verification_status == "verificado" if settings.verificacion_obligatoria else is_active(profile)
    if not allowed:
        raise HTTPException(status_code=403, detail="Identidad no verificada")
    return profile


MAX_SEARCH = 20  # búsqueda por nombre (spec B8)
EARTH_KM = 6371.0
INTERESTS = get_args(Interest)  # lista de intereses de A4, en su orden


DISTANCE_BANDS = (5, 10, 25, 50, 100)


def distance_band(km: int | None) -> int | None:
    """Spec P2: la distancia que se muestra es una franja (contra la triangulación)."""
    if km is None:
        return None
    for band in DISTANCE_BANDS:
        if km <= band:
            return band
    return -(-km // 100) * 100


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


def _candidate_out(viewer, candidate, context, mode, mine, answers, included, search, edad_min, edad_max, max_km, wanted, min_pct):
    """Una tarjeta de Descubrir, o None si el candidato no pasa los filtros."""
    distance = distance_km(viewer, candidate)
    theirs = answers.get(candidate.id)
    raw_personality = compare(mine, theirs, mode) if mine and theirs else None
    shown = public_personality(raw_personality)  # spec P2: solo con los dos tests completos
    personality = PersonalityCompatOut(**shown) if shown else None
    if not search:
        # La búsqueda por nombre ignora sistemas, compatibilidad, edad y distancia (specs B8, B9).
        candidate_age = age(candidate.birth_date)
        if candidate_age is None or not edad_min <= candidate_age <= edad_max:
            return None
        if max_km is not None and (distance is None or distance > max_km):
            return None
        # Intereses (spec B10): tiene que tener todos los marcados.
        if not wanted <= set(candidate.interests or []):
            return None
    result = profile_synastry(viewer, candidate, context)

    # Número global (specs B9, B12; ADR 0014): promedio de los cuatro vínculos, igual que en el chat.
    summary = summarize(result, raw_personality, included)
    if summary["global"] is None:
        if search:
            summary["global"] = result["total"]  # la búsqueda muestra a la persona aunque no tenga test
        else:
            return None  # solo test y esta persona no lo completó
    global_pct = round(summary["global"])
    if not search and global_pct < min_pct:
        return None
    systems = {k: (SystemOut(**v) if v else None) for k, v in summary["systems"].items()}
    axes_global = summary["axes_global"]
    return (
        DiscoverCandidateOut(
            profile_id=candidate.id,
            compatibility_pct=global_pct,
            global_pct=global_pct,
            axes_global=axes_global,
            systems=systems,
            distance_km=distance_band(distance),
            common_interests=[i for i in INTERESTS if i in (viewer.interests or []) and i in (candidate.interests or [])],
            astrology_pct=result["total"],
            # Spec B12: del eje combinado más fuerte, igual para cualquier vínculo (como el número global).
            preview=f"Fuerte en {AXIS_LABELS[max(axes_global, key=lambda k: axes_global[k] or 0)].lower()}",
            axes=result["ejes"],
            relationship=result["tipo_de_relacion"],
            approximate=result["aproximado"],
            personality=personality,
            verificado=candidate.verification_status == "verificado",
            **public_fields(candidate),
        )
    )


@router.get("", response_model=list[DiscoverCandidateOut])
def list_discover(
    viewer_id: uuid.UUID = Query(...),
    context: Relationship = Query(default="pareja"),
    sistemas: str = Query(default="astrologia,personalidad"),
    min_pct: int = Query(default=0, ge=0, le=100),
    edad_min: int = Query(default=18, ge=18, le=99),
    edad_max: int = Query(default=99, ge=18, le=99),
    max_km: int | None = Query(default=None),
    intereses: str = Query(default=""),
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
    wanted = {i.strip() for i in intereses.split(",") if i.strip()}
    if not wanted <= set(INTERESTS):
        raise HTTPException(status_code=422, detail="Interés desconocido")
    if max_km is not None and max_km not in DISTANCE_BANDS:  # spec P2: solo franjas
        raise HTTPException(status_code=422, detail="La distancia tiene que ser 5, 10, 25, 50 o 100 km")
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
    # Spec P2: con un bloqueo entre los dos (de cualquiera), no se ven.
    blocked = _blocked_ids(db, viewer.id)
    candidates = [c for c in candidates if c.id not in blocked]
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
        try:
            out = _candidate_out(
                viewer, candidate, context, mode, mine, answers, included, search, edad_min, edad_max, max_km, wanted, min_pct
            )
        except Exception:  # spec R1: datos rotos de una persona no tiran Descubrir para todos
            logger.exception("Descubrir: se saltea a %s por datos inválidos", candidate.id)
            continue
        if out is not None:
            results.append(out)

    # Lista curada y chica: los de mayor número global (B5, B9); a igual número, más intereses en común (B10).
    results.sort(key=lambda r: (r.global_pct, len(r.common_interests)), reverse=True)
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
    if candidate.id in _blocked_ids(db, viewer.id):
        raise HTTPException(status_code=404, detail="Profile not found")

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
