"""Spec A7: motor oficial de compatibilidad Destiny 1.0 (calculadoras de Pablo).

Los resultados esperados salen del motor de referencia de Pablo (auditorías del paquete DESTINY 1.0),
no de nuestro código: `scripts/build_motor_fixtures.py` los copia a tests/fixtures/motor_oficial_casos.json.
"""

import json
from datetime import date, datetime, time
from pathlib import Path

import pytest

from app.synastry import profile_synastry
from app.synastry.chart import compute_chart
from app.synastry.engine import calcular, load_config
from tests.helpers import BUENOS_AIRES, verified_user

FIXTURES = json.loads((Path(__file__).parent / "fixtures" / "motor_oficial_casos.json").read_text())
CASES = FIXTURES["casos"]
MODES = {
    "completa_completa": ("completa", "completa"),
    "completa_aproximada": ("completa", "aproximada"),
    "aproximada_aproximada": ("aproximada", "aproximada"),
}
AXES = ["atraccion", "afecto", "comunicacion", "compromiso"]
TOL = 1e-8


def _angle(a, b):
    return abs((a - b + 180) % 360 - 180)


def _run(case, mode, neutralizar=False):
    a_kind, b_kind = MODES[mode]
    return calcular(case["A"][a_kind], case["B"][b_kind], neutralizar=neutralizar)


# 1. Tablas completas
def test_tablas_completas():
    cfg = load_config()
    ejes = cfg["ejes"]
    assert cfg["version"] == "destiny-1.0"
    assert sum(ejes["atraccion"]["pesos"]) == 100 and len(ejes["atraccion"]["matrices"]) == 8
    assert abs(sum(ejes["afecto"]["pesos"]) - 1) < 1e-12
    assert abs(sum(ejes["comunicacion"]["pesos"]) - 1) < 1e-12
    assert abs(sum(ejes["compromiso"]["pesos"]) - 100) < 1e-12
    for axis in AXES:
        assert all(len(m) == 12 and all(len(row) == 12 for row in m) for m in ejes[axis]["matrices"])
        e5 = cfg["modificadores_e5"][axis]
        assert len(e5["gran_trigono"]) > 800 and len(e5["gran_cruz"]) > 4000


# 2, 3 y 4. Base, E5 e integrado iguales al motor de Pablo en las 3 modalidades
@pytest.mark.parametrize("mode", MODES)
def test_coincide_con_el_motor_de_pablo(mode):
    for case in CASES:
        expected = case["esperado"][mode]
        actual = _run(case, mode)
        for axis in AXES:
            assert actual["base"][axis] == pytest.approx(expected["base"][axis], abs=TOL), (case["n"], axis, "base")
            for col in ("GT", "GC", "AA", "mod"):
                assert actual["e5"][axis][col] == pytest.approx(expected["e5"][axis][col], abs=TOL), (case["n"], axis, col)
            assert actual["integrado"][axis] == pytest.approx(expected["integrado"][axis], abs=TOL), (case["n"], axis)
        assert actual["cobertura_compromiso"] == pytest.approx(expected["cobertura_compromiso"], abs=TOL)


def test_la_muestra_tiene_todos_los_patrones_activos():
    for col in ("GT", "GC", "AA"):
        assert any(c["esperado"][m]["e5"][axis][col] != 0 for c in CASES for m in MODES for axis in AXES), col


# 5. Demos del paquete, con neutralización de E4
@pytest.mark.parametrize("demo", FIXTURES["demos"], ids=lambda d: d["modalidad"])
def test_demos_del_paquete(demo):
    actual = calcular(demo["A"], demo["B"], neutralizar=True)
    assert actual["modalidad"] == demo["modalidad"]
    for axis in AXES:
        assert actual["integrado"][axis] == pytest.approx(demo["ejes_finales"][axis], abs=TOL)
    for kind, value in demo["globales"].items():
        assert actual["globales"][kind] == pytest.approx(value, abs=TOL)
    assert actual["visibles"] == demo["visibles"]


# 6. Cobertura de E4 y neutralización
def test_cobertura_y_neutralizacion_de_compromiso():
    case = CASES[0]
    for mode, coverage in zip(MODES, (100, 83, 66)):
        raw = _run(case, mode, neutralizar=False)
        neutral = _run(case, mode, neutralizar=True)
        assert raw["cobertura_compromiso"] == pytest.approx(coverage)
        if coverage == 100:
            assert neutral["base"]["compromiso"] == raw["base"]["compromiso"]
        else:
            assert neutral["base"]["compromiso"] == pytest.approx(50 + coverage / 100 * (raw["base"]["compromiso"] - 50))


# 7. Simetría
def test_invertir_a_y_b_da_lo_mismo():
    for case in CASES[:40]:
        forward = calcular(case["A"]["completa"], case["B"]["aproximada"])
        back = calcular(case["B"]["aproximada"], case["A"]["completa"])
        for axis in AXES:
            assert forward["integrado"][axis] == pytest.approx(back["integrado"][axis], abs=TOL)


# 8. Carta sin hora exacta
def test_carta_aproximada_sin_angulos_y_con_nodo_sur():
    chart = compute_chart(date(1989, 6, 4), time(2, 30), False, -34.6037, -58.3816, "America/Argentina/Buenos_Aires")
    assert "asc" not in chart.points and "mc" not in chart.points and chart.houses is None
    assert chart.points["nodo_sur"] == pytest.approx((chart.points["nodo_norte"] + 180) % 360)
    exact = compute_chart(date(1989, 6, 4), time(2, 30), True, -34.6037, -58.3816, "America/Argentina/Buenos_Aires")
    assert "asc" in exact.points and "mc" in exact.points


# 9. Posiciones iguales a las de las auditorías de Pablo
TOLERANCE = {"nodo_norte": 0.05, "nodo_medio": 0.05, "asc": 0.02, "mc": 0.02}


def test_posiciones_coinciden_con_las_auditorias():
    for case in CASES[:60]:
        for side in ("A", "B"):
            born = case[side]["nacimiento"]
            for kind, key in (("completa", "utc_exact"), ("aproximada", "utc_mid")):
                utc = datetime.fromisoformat(born[key])
                chart = compute_chart(utc.date(), utc.time(), kind == "completa", born["lat"], born["lon"], "UTC")
                for point, expected in case[side][kind].items():
                    diff = _angle(chart.points[point], expected)
                    assert diff < TOLERANCE.get(point, 0.01), (case["n"], side, kind, point, diff)


# 10. Franjas de Pablo
@pytest.mark.parametrize(
    "period,midpoint",
    [("madrugada", "02:30:00"), ("manana", "08:00:00"), ("mediodia", "12:30:00"), ("tarde", "16:30:00"), ("noche", "21:30:00"), (None, "12:30:00")],
)
def test_franjas_de_pablo(client, period, midpoint):
    pid = client.post("/profiles", json={}).json()["id"]
    body = {"birth_date": "1990-05-20", "birth_place": BUENOS_AIRES}
    if period:
        body["birth_time_period"] = period
    r = client.post(f"/profiles/{pid}/birth-data", json=body)
    assert r.status_code == 200, r.text
    assert r.json()["birth_time"] == midpoint and r.json()["birth_time_estimated"] is True


# 11. Pesos oficiales por tipo de relación
def test_total_con_los_pesos_oficiales(new_client):
    from app.models import Profile
    from app.database import SessionLocal

    a, b = new_client(), new_client()
    ana = verified_user(a, "5491111111111", name="Ana", birth_date="1990-05-20", birth_time="14:30")
    beto = verified_user(b, "5492222222222", name="Beto", birth_date="1988-11-03", birth_time="21:45")
    with SessionLocal() as db:
        pa, pb = db.get(Profile, ana), db.get(Profile, beto)
        results = {kind: profile_synastry(pa, pb, kind) for kind in ("ocasional", "laboral")}
    weights = {"ocasional": (0.70, 0.10, 0.15, 0.05), "laboral": (0.10, 0.10, 0.40, 0.40)}
    for kind, result in results.items():
        exact = result["ejes_exactos"]
        assert result["total"] == int(sum(w * exact[axis] for w, axis in zip(weights[kind], AXES)) + 0.5)
        assert result["ejes"] == {axis: int(exact[axis] + 0.5) for axis in AXES}
        assert result["version_tablas"] == "destiny-1.0"


# 12. Parametrizable
def test_cambiar_un_numero_del_json_cambia_el_resultado(monkeypatch):
    case = CASES[0]
    before = _run(case, "completa_completa")["integrado"]["atraccion"]
    cfg = load_config()
    monkeypatch.setitem(cfg["ejes"]["atraccion"]["expansion"], "factor", 1.0)
    after = _run(case, "completa_completa")["integrado"]["atraccion"]
    assert after != pytest.approx(before, abs=1e-6)
