"""Spec C12: invitar en un paso (nombre, signo opcional; el mensaje se arma solo)."""

from tests.helpers import complete_personality, verified_user
from tests.test_a10_verificacion_opcional import active_user

HOOK = "¿Por qué con algunas personas fluye y con otras no?"
TEST = "Ya completé mi test de personalidad"


def invite(client, pid, **extra):
    r = client.post("/invitations", json={"inviter_id": pid, "friend_name": "Juan", **extra})
    assert r.status_code == 201, r.text
    return r.json()


# 1
def test_solo_el_nombre(client):
    pid = verified_user(client, "5491111111111", name="Ana")
    body = invite(client, pid)
    assert body["message"].startswith(f"¡Hola Juan! {HOOK}")
    assert "/onboarding/invitacion?ref=" in body["message"]
    assert "Con tu signo" not in body["message"] and TEST not in body["message"]
    assert body["kind"] == "astro" and body["partial_report"] is None


# 2
def test_con_su_signo(client):
    pid = verified_user(client, "5491111111111", name="Ana")
    body = invite(client, pid, friend_sun_sign="Leo")
    assert "Con tu signo (Leo)" in body["message"]
    assert body["partial_report"]["teaser"]


# 3
def test_con_mi_test_completo(client):
    pid = verified_user(client, "5491111111111", name="Ana")
    complete_personality(client, pid)
    body = invite(client, pid)
    assert TEST in body["message"] and body["kind"] == "test"


# 4
def test_sin_mi_test_completo_igual_se_crea(client):
    pid = verified_user(client, "5491111111111", name="Ana")
    client.put(f"/profiles/{pid}/personality", json={"answers": {"E2.01": [1]}})
    body = invite(client, pid, friend_sun_sign="Leo")
    assert TEST not in body["message"]


# 5
def test_vinculo(new_client):
    a, b = new_client(), new_client()
    ana = active_user(a, name="Ana")
    a.post(f"/profiles/{ana}/looking-for", json={"looking_for": "amistad"})
    beto = active_user(b, name="Beto")
    invite(a, ana)
    invite(b, beto)
    assert a.get("/invitations/mine", params={"profile_id": ana}).json()[0]["relationship"] == "amistad"
    assert b.get("/invitations/mine", params={"profile_id": beto}).json()[0]["relationship"] == "pareja"


# 6
def test_vista_previa(client):
    pid = verified_user(client, "5491111111111", name="Ana")
    r = client.post("/invitations/preview", json={"inviter_id": pid, "friend_name": "Juan", "friend_sun_sign": "Leo"})
    assert r.status_code == 200, r.text
    message = r.json()["message"]
    assert message.startswith(f"¡Hola Juan! {HOOK}") and "Con tu signo (Leo)" in message and message.endswith("[link]")
    assert client.get("/invitations/mine", params={"profile_id": pid}).json() == []


# 7
def test_pagina_del_invitado_sin_signo_ni_test(new_client):
    a, b = new_client(), new_client()
    pid = verified_user(a, "5491111111111", name="Ana")
    ref = invite(a, pid)["ref_id"]
    teaser = b.get(f"/invitations/{ref}").json()["teaser"]
    assert "Ana" in teaser
