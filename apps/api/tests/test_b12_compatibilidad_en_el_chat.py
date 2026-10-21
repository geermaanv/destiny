"""Spec B12: compatibilidad del chat (número que resume todo, ejes por sistema, tabla por vínculo)."""

import pytest

from tests.helpers import complete_personality, verified_user

VINCULOS = ["pareja", "amistad", "laboral", "ocasional"]


@pytest.fixture
def conexion(new_client):
    a, b = new_client(), new_client()
    pid_a = verified_user(a, "5491111111111", name="Ana")
    pid_b = verified_user(b, "5492222222222", name="Beto", birth_date="1992-08-03")
    m = a.post("/matches", json={"profile_a_id": pid_a, "profile_b_id": pid_b}).json()
    return a, pid_a, b, pid_b, m["id"]


def summary(client, mid):
    r = client.get(f"/matches/{mid}/compatibility/summary")
    assert r.status_code == 200, r.text
    return r.json()


def mean(values):
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values))


# 1 y 2
def test_cuatro_vinculos_y_numero_que_resume(conexion):
    a, pid_a, b, pid_b, mid = conexion
    b.post(f"/matches/{mid}/accept", json={"profile_id": pid_b})
    complete_personality(a, pid_a, choice=1)
    complete_personality(b, pid_b, choice=3)
    s = summary(a, mid)
    assert [v["vinculo"] for v in s["por_vinculo"]] == VINCULOS
    for v in s["por_vinculo"]:
        compat = a.get(f"/matches/{mid}/compatibility", params={"context": v["vinculo"]}).json()
        assert v["astrologia"] == compat["astrology"]["total"]
        assert v["personalidad"] == round(compat["personality"]["total"])
        assert v["global_pct"] == mean([compat["astrology"]["total"], compat["personality"]["total"]])
    assert abs(s["global_pct"] - sum(v["global_pct"] for v in s["por_vinculo"]) / 4) <= 1
    for axis, value in s["axes_global"].items():
        assert value == mean([s["systems"]["astrologia"]["axes"][axis], s["systems"]["personalidad"]["axes"][axis]])


# 3
def test_sin_test(conexion):
    a, pid_a, b, pid_b, mid = conexion
    b.post(f"/matches/{mid}/accept", json={"profile_id": pid_b})
    s = summary(a, mid)
    assert s["systems"]["personalidad"] is None
    for v in s["por_vinculo"]:
        assert v["personalidad"] is None and v["global_pct"] == v["astrologia"]


# 4
def test_solo_los_participantes(conexion, new_client):
    a, pid_a, b, pid_b, mid = conexion
    b.post(f"/matches/{mid}/accept", json={"profile_id": pid_b})
    tercero = new_client()
    verified_user(tercero, "5493333333333", name="Caro")
    assert tercero.get(f"/matches/{mid}/compatibility/summary").status_code == 403


# 5
def test_conexion_pendiente(conexion):
    a, pid_a, b, pid_b, mid = conexion
    assert a.get(f"/matches/{mid}/compatibility/summary").status_code == 409
