"""Cálculo del test de personalidad de Pablo (spec A6, ADR 0011).

Port exacto de las funciones de docs/referencias/pablo_test_express_v4.html
(scoreChoices, compareAxis y el total por modalidad). Todos los números salen de
config/test_v4.json; los tests comparan contra resultados generados con el
código original de Pablo (tests/fixtures/pablo_golden.json).
"""

import json
from functools import lru_cache
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config" / "test_v4.json"
AXES = ("E1", "E2", "E3", "E4")


@lru_cache(maxsize=1)
def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def _items(cfg: dict) -> dict:
    return {item["id"]: item for item in cfg["questions"] + cfg["crosses"]}


def normalize_choices(values) -> list[int]:
    """Hasta dos opciones distintas entre 0 y 4, en orden (principal, secundaria)."""
    out: list[int] = []
    for v in values if isinstance(values, list) else [values]:
        if isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 4 and v not in out:
            out.append(v)
        if len(out) == 2:
            break
    return out


def _answer(answers: dict, qid: str) -> list[int] | None:
    choices = normalize_choices(answers.get(qid, []))
    return choices or None


def score_choices(pa: list[int] | None, pb: list[int] | None, matrix: list[list[float]], cfg: dict) -> float | None:
    """scoreChoices de Pablo: con dos opciones, emparejamiento óptimo 70/30 (transporte 2×2)."""
    if not pa or not pb:
        return None
    one, two = cfg["preference_weights"]["one"], cfg["preference_weights"]["two"]
    wa = one if len(pa) == 1 else two
    wb = one if len(pb) == 1 else two
    if len(pa) == 1 and len(pb) == 1:
        return matrix[pa[0]][pb[0]]
    if len(pa) == 1:
        return sum(wb[j] * matrix[pa[0]][v] for j, v in enumerate(pb))
    if len(pb) == 1:
        return sum(wa[i] * matrix[v][pb[0]] for i, v in enumerate(pa))
    p, q = wa[0], wb[0]
    lo, hi = max(0.0, p + q - 1), min(p, q)

    def value(t: float) -> float:
        return (
            t * matrix[pa[0]][pb[0]]
            + (p - t) * matrix[pa[0]][pb[1]]
            + (q - t) * matrix[pa[1]][pb[0]]
            + (1 - p - q + t) * matrix[pa[1]][pb[1]]
        )

    return max(value(lo), value(hi))


def compare_axis(axis: str, answers_a: dict, answers_b: dict) -> dict:
    """compareAxis de Pablo: promedio ponderado de preguntas y cruces del eje, con topes en E4."""
    cfg = load_config()
    weighted = used = possible = 0.0

    def record(weight: float, score: float | None) -> None:
        nonlocal weighted, used, possible
        possible += weight
        if score is not None:
            weighted += weight * score
            used += weight

    for q in cfg["questions"]:
        if q["axis"] == axis:
            record(q["weight"], score_choices(_answer(answers_a, q["id"]), _answer(answers_b, q["id"]), q["matrix"], cfg))

    factor = cfg["cross_direction_weight_factor"]
    for c in cfg["crosses"]:
        if c["axis"] != axis:
            continue
        w = c["weight"] * factor
        # A necesita / B ofrece, y B necesita / A ofrece.
        record(w, score_choices(_answer(answers_a, c["need"]), _answer(answers_b, c["give"]), c["matrix"], cfg))
        record(w, score_choices(_answer(answers_b, c["need"]), _answer(answers_a, c["give"]), c["matrix"], cfg))

    raw = weighted / used if used else None
    cap, flags = 100.0, []
    caps = cfg["e4_caps"]
    if axis == "E4":
        for rule in caps["caps"]:
            x, y = _answer(answers_a, rule["id"]), _answer(answers_b, rule["id"])
            if x and y and abs(x[0] - y[0]) == 4:
                cap = min(cap, rule["max"])
                flags.append(rule)
    score = None if raw is None else (min(raw, cap) if caps["enabled"] else raw)
    return {"axis": axis, "raw": raw, "score": score, "coverage": used / possible if possible else 0.0, "flags": flags}


def weighted_total(scores: dict[str, float | None], mode: str) -> float | None:
    """Total por modalidad de Pablo: suma de ejes × peso / 100 (None si falta un eje con peso)."""
    weights = load_config()["modes"][mode]["weights"]
    if any(weights[ax] != 0 and scores[ax] is None for ax in AXES):
        return None
    return sum((scores[ax] or 0) * weights[ax] / 100 for ax in AXES)


def completed(answers: dict) -> int:
    return sum(1 for q in load_config()["questions"] if _answer(answers, q["id"]))


def compare(answers_a: dict, answers_b: dict, mode: str) -> dict:
    """Comparación completa. El total solo se informa con los dos tests completos (como en el HTML de Pablo)."""
    results = {ax: compare_axis(ax, answers_a, answers_b) for ax in AXES}
    total_questions = len(load_config()["questions"])
    complete = completed(answers_a) == total_questions and completed(answers_b) == total_questions
    scores = {ax: r["score"] for ax, r in results.items()}
    return {
        "mode": mode,
        "axes": scores,
        "coverage": {ax: r["coverage"] for ax, r in results.items()},
        "flags": [f["label"] for r in results.values() for f in r["flags"]],
        "total": weighted_total(scores, mode) if complete else None,
        "complete": complete,
    }
