"""Spec C13: un link de invitación sirve para varias personas."""

import pytest

from tests.helpers import verified_user
from tests.test_a10_verificacion_opcional import active_user


@pytest.fixture
def link(new_client):
    a = new_client()
    pablo = verified_user(a, "5491111111111", name="Pablo")
    r = a.post("/invitations", json={"inviter_id": pablo, "friend_name": "Amigos"})
    return a, pablo, r.json()["ref_id"]


def connections(client, pid):
    return client.get("/connections", params={"profile_id": pid}).json()


# 1
def test_dos_personas_usan_el_mismo_link(link, new_client):
    a, pablo, ref = link
    b, c = new_client(), new_client()
    mavi = active_user(b, name="Mavi")
    carla = active_user(c, name="Carla")
    r1, r2 = b.post(f"/invitations/{ref}/accept"), c.post(f"/invitations/{ref}/accept")
    assert r1.status_code == 200 and r2.status_code == 200, (r1.text, r2.text)
    assert r1.json()["match_id"] != r2.json()["match_id"]
    otros = {x["other"]["display_name"] for x in connections(a, pablo) if x["status"] == "aceptada"}
    assert otros == {"Mavi", "Carla"}
    assert mavi and carla


# 2
def test_la_misma_persona_acepta_dos_veces(link, new_client):
    a, pablo, ref = link
    b = new_client()
    active_user(b, name="Mavi")
    first = b.post(f"/invitations/{ref}/accept").json()["match_id"]
    assert b.post(f"/invitations/{ref}/accept").json()["match_id"] == first
    assert len(connections(a, pablo)) == 1


# 3
def test_la_pregunta_extra_suma_por_cada_una(link, new_client):
    a, pablo, ref = link
    for name in ["Mavi", "Carla"]:
        c = new_client()
        active_user(c, name=name)
        c.post(f"/invitations/{ref}/accept")
    assert a.get(f"/profiles/{pablo}/astrochat").json()["extra_por_invitados"] == 2


# 4
def test_mis_invitaciones_cuenta_quienes_aceptaron(link, new_client):
    a, pablo, ref = link
    for name in ["Mavi", "Carla"]:
        c = new_client()
        active_user(c, name=name)
        c.post(f"/invitations/{ref}/accept")
    [mine] = a.get("/invitations/mine", params={"profile_id": pablo}).json()
    assert mine["aceptaron"] == 2
