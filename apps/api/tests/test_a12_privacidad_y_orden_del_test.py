"""Spec A12: aviso de privacidad aceptado (registro y test) y test ordenado por lo que buscás."""

import pytest

from tests.helpers import create_profile
from tests.test_a10_verificacion_opcional import active_user


def privacy(client, pid, contexto, version="privacidad_v1"):
    return client.post(f"/profiles/{pid}/privacy", json={"version": version, "contexto": contexto})


# 1
def test_aceptar_el_aviso_del_registro(client):
    pid = create_profile(client, name="Ana", privacy=False)
    assert client.get(f"/profiles/{pid}").json()["privacy_version"] is None
    assert privacy(client, pid, "registro").status_code == 200
    me = client.get(f"/profiles/{pid}").json()
    assert me["privacy_version"] == "privacidad_v1" and me["test_privacy_version"] is None


# 2
def test_no_se_termina_el_registro_sin_aceptar(client):
    pid = create_profile(client, name="Ana", privacy=False)
    r = client.post("/sessions/start", json={"profile_id": pid})
    assert r.status_code == 409 and "privacidad" in r.json()["detail"].lower()
    privacy(client, pid, "registro")
    assert client.post("/sessions/start", json={"profile_id": pid}).status_code == 204


# 3
def test_el_test_pide_su_aviso(client):
    pid = create_profile(client, name="Ana", privacy=False)
    privacy(client, pid, "registro")
    client.post("/sessions/start", json={"profile_id": pid})
    assert client.get(f"/profiles/{pid}/personality").json()["privacy_accepted"] is False
    r = client.put(f"/profiles/{pid}/personality", json={"answers": {"E2.01": [1]}})
    assert r.status_code == 409
    privacy(client, pid, "test")
    assert client.get(f"/profiles/{pid}/personality").json()["privacy_accepted"] is True
    assert client.put(f"/profiles/{pid}/personality", json={"answers": {"E2.01": [1]}}).status_code == 200


# 4
@pytest.mark.parametrize(
    "looking_for,order",
    [
        (None, ["E2", "E3", "E4", "E1"]),
        ("pareja", ["E2", "E3", "E4", "E1"]),
        ("ocasional", ["E1", "E3", "E2", "E4"]),
        ("amistad", ["E3", "E2", "E4", "E1"]),
        ("laboral", ["E3", "E4", "E2", "E1"]),
    ],
)
def test_orden_segun_lo_que_busca(client, looking_for, order):
    pid = active_user(client)
    if looking_for:
        r = client.post(f"/profiles/{pid}/looking-for", json={"looking_for": looking_for})
        assert r.status_code == 200 and r.json()["looking_for"] == looking_for
    assert client.get(f"/profiles/{pid}/personality").json()["axis_order"] == order


# 5
def test_validaciones(client):
    pid = active_user(client)
    assert client.post(f"/profiles/{pid}/looking-for", json={"looking_for": "todo"}).status_code == 422
    assert privacy(client, pid, "otro").status_code == 422
