import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_self, session_profile_id
from app.database import get_db
from app.models import PersonalityAnswers, Profile
from app.personality import CONTEXT_TO_MODE
from app.personality.engine import completed, load_config
from app.schemas import PersonalityAnswersIn, PersonalityMineOut

# Test de personalidad de Pablo dentro del perfil (spec A6).
router = APIRouter(tags=["personality"])


@router.get("/personality/test")
def get_test() -> dict:
    """Preguntas y opciones para mostrar (sin matrices ni pesos)."""
    cfg = load_config()
    return {
        "version": cfg["version"],
        "max_choices": cfg["max_choices"],
        "preference_weights": cfg["preference_weights"],
        "axes": cfg["axes"],
        "questions": [
            {"id": q["id"], "axis": q["axis"], "kind": q["kind"], "question": q["question"], "options": q["options"]}
            for q in cfg["questions"]
        ],
    }


def _own_profile(profile_id: uuid.UUID, current: uuid.UUID | None, db: Session) -> Profile:
    require_self(profile_id, current)
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


MAX_CHANGES_PER_DAY = 10  # spec P2: respuestas que se pueden cambiar por día con el test completo

# Spec A12: a igual peso (o sin saber qué busca), Atracción va al final.
BASE_AXIS_ORDER = ["E2", "E3", "E4", "E1"]


def axis_order(looking_for: str | None) -> list[str]:
    """Grupos del test de mayor a menor peso de Pablo para lo que busca la persona."""
    if looking_for not in CONTEXT_TO_MODE:
        return list(BASE_AXIS_ORDER)
    weights = load_config()["modes"][CONTEXT_TO_MODE[looking_for]]["weights"]
    return sorted(BASE_AXIS_ORDER, key=lambda axis: (-weights[axis], BASE_AXIS_ORDER.index(axis)))


def _mine(row: PersonalityAnswers | None, profile: Profile) -> PersonalityMineOut:
    answers = row.answers if row else {}
    return PersonalityMineOut(
        answers=answers,
        completed=completed(answers),
        total_questions=len(load_config()["questions"]),
        axis_order=axis_order(profile.looking_for),
        privacy_accepted=profile.test_privacy_accepted_at is not None,
    )


@router.get("/profiles/{profile_id}/personality", response_model=PersonalityMineOut)
def get_my_answers(
    profile_id: uuid.UUID, db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> PersonalityMineOut:
    profile = _own_profile(profile_id, current, db)
    return _mine(db.get(PersonalityAnswers, profile_id), profile)


@router.put("/profiles/{profile_id}/personality", response_model=PersonalityMineOut)
def save_answers(
    profile_id: uuid.UUID,
    payload: PersonalityAnswersIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> PersonalityMineOut:
    """Guarda respuestas (parciales): las que vienen reemplazan a las anteriores de esas preguntas."""
    profile = _own_profile(profile_id, current, db)
    if profile.test_privacy_accepted_at is None:
        raise HTTPException(status_code=409, detail="Aceptá el aviso de privacidad del test para guardar respuestas")
    row = db.get(PersonalityAnswers, profile_id)
    if row is None:
        row = PersonalityAnswers(profile_id=profile_id, answers={})
        db.add(row)
    # Spec P2: con el test completo, cambios limitados por día (sino sirve de oráculo de las respuestas ajenas).
    if completed(row.answers) == len(load_config()["questions"]):
        changed = sum(1 for qid, value in payload.answers.items() if row.answers.get(qid) != value)
        today = date.today()
        if row.changes_on != today:
            row.changes_on, row.changes_count = today, 0
        if row.changes_count + changed > MAX_CHANGES_PER_DAY:
            raise HTTPException(status_code=429, detail="Podés seguir cambiando respuestas mañana")
        row.changes_count += changed
    row.answers = {**row.answers, **payload.answers}
    db.commit()
    db.refresh(row)
    return _mine(row, profile)
