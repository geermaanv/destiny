"""Spec A6-test-personalidad: el test de Pablo, fiel a su código original.

Los resultados esperados (tests/fixtures/pablo_golden.json) se generan ejecutando
el HTML de Pablo: node scripts/pablo_golden.mjs
"""

import json
from pathlib import Path

import pytest

from tests.helpers import verified_user

GOLDEN = json.loads((Path(__file__).parent / "fixtures" / "pablo_golden.json").read_text())
AXES = ["E1", "E2", "E3", "E4"]


def _all(value):
    from app.personality.engine import load_config

    return {q["id"]: value for q in load_config()["questions"]}


# --- El modelo (sin API) ----------------------------------------------------


def test_configuracion_igual_al_html_de_pablo():
    from app.personality.engine import load_config

    cfg = load_config()
    assert len(cfg["questions"]) == 32
    assert all(sum(q["axis"] == ax for q in cfg["questions"]) == 8 for ax in AXES)
    assert len(cfg["crosses"]) == 4
    assert [c["id"] for c in cfg["e4_caps"]["caps"]] == ["E4.01", "E4.02", "E4.08", "E4.07"]
    assert cfg["preference_weights"]["two"] == [0.7, 0.3]


def test_respuestas_identicas_dan_100():
    from app.personality.engine import compare

    r = compare(_all([2]), _all([2]), "formal")
    assert r["axes"] == {ax: pytest.approx(100) for ax in AXES}
    assert r["total"] == pytest.approx(100) and r["complete"] is True


@pytest.mark.parametrize("pair", GOLDEN, ids=[p["name"] for p in GOLDEN])
def test_mismos_numeros_que_el_codigo_de_pablo(pair):
    from app.personality.engine import compare_axis, weighted_total

    scores = []
    for expected in pair["axes"]:
        got = compare_axis(expected["axis"], pair["a"], pair["b"])
        if expected["score"] is None:
            assert got["score"] is None
        else:
            assert got["score"] == pytest.approx(expected["score"], abs=0.01)
            assert got["raw"] == pytest.approx(expected["raw"], abs=0.01)
        assert got["coverage"] == pytest.approx(expected["coverage"], abs=0.001)
        assert [f["id"] for f in got["flags"]] == expected["flags"]
        scores.append(got["score"])
    for mode, total in pair["totals"].items():
        got_total = weighted_total(dict(zip(AXES, scores)), mode)
        assert (got_total is None) if total is None else got_total == pytest.approx(total, abs=0.01), mode


def test_tope_por_hijos_y_convivencia():
    from app.personality.engine import compare

    hijos = compare({**_all([2]), "E4.08": [0]}, {**_all([2]), "E4.08": [4]}, "formal")
    assert hijos["axes"]["E4"] == pytest.approx(59)
    convivencia = compare({**_all([3]), "E4.07": [0]}, {**_all([3]), "E4.07": [4]}, "formal")
    assert convivencia["axes"]["E4"] == pytest.approx(69)


def test_cambiar_la_configuracion_cambia_el_resultado(monkeypatch):
    from app.personality.engine import compare, load_config

    a, b = _all([1]), _all([2])
    antes = compare(a, b, "formal")["axes"]["E1"]
    cfg = load_config()
    q = next(q for q in cfg["questions"] if q["id"] == "E1.15")
    monkeypatch.setitem(q, "weight", 0)
    assert compare(a, b, "formal")["axes"]["E1"] != antes


def test_pesos_por_tipo_de_la_sinastria_iguales_a_los_de_pablo():
    from app.personality.engine import load_config as personality
    from app.synastry.engine import load_config as synastry

    equivalencia = {"pareja": "formal", "ocasional": "sexual", "amistad": "amistad", "laboral": "laboral"}
    ejes = {"atraccion": "E1", "afecto": "E2", "comunicacion": "E3", "compromiso": "E4"}
    tipos = synastry()["nivel_7_y_10_tipos_de_relacion"]["tipos"]
    for destiny, pablo in equivalencia.items():
        esperado = personality()["modes"][pablo]["weights"]
        for eje, e in ejes.items():
            assert tipos[destiny]["pesos"][eje] == pytest.approx(esperado[e] / 100), (destiny, eje)


# --- La API -----------------------------------------------------------------


def test_preguntas_publicas_sin_matrices(client):
    test = client.get("/personality/test").json()
    assert len(test["questions"]) == 32
    assert "matrix" not in test["questions"][0] and len(test["questions"][0]["options"]) == 5


def test_guardar_respuestas_parciales_y_leerlas(client):
    pid = verified_user(client, "5491111111111")
    r = client.put(f"/profiles/{pid}/personality", json={"answers": {"E1.01": [2], "E1.02": [1, 3]}})
    assert r.status_code == 200
    mine = client.get(f"/profiles/{pid}/personality").json()
    assert mine["answers"] == {"E1.01": [2], "E1.02": [1, 3]}
    assert mine["completed"] == 2 and mine["total_questions"] == 32
    client.put(f"/profiles/{pid}/personality", json={"answers": {"E1.01": [4]}})
    assert client.get(f"/profiles/{pid}/personality").json()["answers"]["E1.01"] == [4]
    assert client.get(f"/profiles/{pid}/personality").json()["answers"]["E1.02"] == [1, 3]


@pytest.mark.parametrize(
    "answers",
    [{"E1.01": [0, 1, 2]}, {"E1.01": [5]}, {"E9.99": [1]}, {"E1.01": [1, 1]}, {"E1.01": []}],
)
def test_respuestas_invalidas_se_rechazan(client, answers):
    pid = verified_user(client, "5491111111111")
    assert client.put(f"/profiles/{pid}/personality", json={"answers": answers}).status_code == 422


def test_respuestas_de_otro_estan_protegidas(new_client):
    a, b, anon = new_client(), new_client(), new_client()
    pid_a = verified_user(a, "5491111111111")
    verified_user(b, "5492222222222")
    assert anon.get(f"/profiles/{pid_a}/personality").status_code == 401
    assert b.get(f"/profiles/{pid_a}/personality").status_code == 403
    assert b.put(f"/profiles/{pid_a}/personality", json={"answers": {"E1.01": [1]}}).status_code == 403


def _discover_one(client, viewer, context="pareja"):
    return client.get("/discover", params={"viewer_id": viewer, "context": context}).json()[0]


def test_descubrir_con_los_dos_tests_completos(new_client):
    a, b = new_client(), new_client()
    pid_a = verified_user(a, "5491111111111", name="Ana")
    pid_b = verified_user(b, "5492222222222", name="Beto")
    a.put(f"/profiles/{pid_a}/personality", json={"answers": _all([2])})
    b.put(f"/profiles/{pid_b}/personality", json={"answers": _all([2])})
    p = _discover_one(b, pid_b)["personality"]
    assert p["complete"] is True and p["total"] == pytest.approx(100)
    assert set(p["axes"]) == set(AXES)


def test_descubrir_con_un_test_incompleto_es_provisorio(new_client):
    a, b = new_client(), new_client()
    pid_a = verified_user(a, "5491111111111", name="Ana")
    pid_b = verified_user(b, "5492222222222", name="Beto")
    a.put(f"/profiles/{pid_a}/personality", json={"answers": {"E1.01": [2], "E2.01": [1]}})
    b.put(f"/profiles/{pid_b}/personality", json={"answers": _all([2])})
    p = _discover_one(b, pid_b)["personality"]
    assert p["complete"] is False and p["total"] is None
    assert 0 < p["coverage"]["E1"] < 1 and p["axes"]["E3"] is None


def test_descubrir_sin_respuestas_del_otro(new_client):
    a, b = new_client(), new_client()
    verified_user(a, "5491111111111", name="Ana")
    pid_b = verified_user(b, "5492222222222", name="Beto")
    b.put(f"/profiles/{pid_b}/personality", json={"answers": _all([2])})
    assert _discover_one(b, pid_b)["personality"] is None


def test_descubrir_nunca_expone_las_respuestas(new_client):
    a, b = new_client(), new_client()
    pid_a = verified_user(a, "5491111111111", name="Ana")
    pid_b = verified_user(b, "5492222222222", name="Beto")
    a.put(f"/profiles/{pid_a}/personality", json={"answers": _all([3])})
    b.put(f"/profiles/{pid_b}/personality", json={"answers": _all([2])})
    body = b.get("/discover", params={"viewer_id": pid_b}).text
    assert "E1.01" not in body and "answers" not in body


def test_el_contexto_usa_los_pesos_de_pablo(new_client):
    a, b = new_client(), new_client()
    pid_a = verified_user(a, "5491111111111", name="Ana")
    pid_b = verified_user(b, "5492222222222", name="Beto")
    a.put(f"/profiles/{pid_a}/personality", json={"answers": {**_all([2]), **{q: [0] for q in ["E1.01", "E1.02"]}}})
    b.put(f"/profiles/{pid_b}/personality", json={"answers": _all([2])})
    casual = _discover_one(b, pid_b, "ocasional")["personality"]
    trabajo = _discover_one(b, pid_b, "laboral")["personality"]
    assert casual["total"] != trabajo["total"]
