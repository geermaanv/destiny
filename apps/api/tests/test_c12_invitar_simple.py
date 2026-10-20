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


SIGNS = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]


def signs_by_strength(pid):
    """(signo con aspecto mayor, signo flojo) para la carta de quien invita."""
    from app.astro import approximate_longitude_for_sign
    from app.aspects import angle_between, classify_aspect
    from app.database import SessionLocal
    from app.models import Profile
    from app.public_profile import sun_sign

    with SessionLocal() as db:
        sun = approximate_longitude_for_sign(sun_sign(db.get(Profile, pid)))
    major = {s: classify_aspect(angle_between(sun, approximate_longitude_for_sign(s)))["is_major"] for s in SIGNS}
    return next(s for s in SIGNS if major[s]), next(s for s in SIGNS if not major[s])


# 2
def test_con_su_signo(client):
    pid = verified_user(client, "5491111111111", name="Ana")
    strong, _ = signs_by_strength(pid)
    body = invite(client, pid, friend_sun_sign=strong)
    assert f"Con tu signo ({strong})" in body["message"]
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
    strong, _ = signs_by_strength(pid)
    r = client.post("/invitations/preview", json={"inviter_id": pid, "friend_name": "Juan", "friend_sun_sign": strong})
    assert r.status_code == 200, r.text
    message = r.json()["message"]
    assert message.startswith(f"¡Hola Juan! {HOOK}") and f"Con tu signo ({strong})" in message and message.endswith("[link]")
    assert client.get("/invitations/mine", params={"profile_id": pid}).json() == []


# 7
def test_pagina_del_invitado_sin_signo_ni_test(new_client):
    a, b = new_client(), new_client()
    pid = verified_user(a, "5491111111111", name="Ana")
    ref = invite(a, pid)["ref_id"]
    teaser = b.get(f"/invitations/{ref}").json()["teaser"]
    assert "Ana" in teaser


# 8
def test_adelanto_flojo_no_se_incluye(new_client):
    a, b = new_client(), new_client()
    pid = verified_user(a, "5491111111111", name="Ana")
    _, weak = signs_by_strength(pid)
    body = invite(a, pid, friend_sun_sign=weak)
    assert "Con tu signo" not in body["message"] and body["partial_report"] is None
    assert "Con tu signo" not in b.get(f"/invitations/{body['ref_id']}").json()["teaser"]
