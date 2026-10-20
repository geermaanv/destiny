"""Spec C11: una pregunta diaria más en Indagar por cada amigo que se registra con tu invitación."""

from tests.helpers import verified_user
from tests.test_a10_verificacion_opcional import active_user
from tests.test_x1_redaccion_con_ia import openrouter  # noqa: F401


def _config():
    from app.astrochat.chat import load_config

    return load_config()


def invite(client, pid, name="Juan"):
    r = client.post("/invitations", json={"inviter_id": pid, "friend_name": name, "friend_sun_sign": "Leo"})
    assert r.status_code == 201, r.text
    return r.json()["ref_id"]


def chat(client, pid):
    return client.get(f"/profiles/{pid}/astrochat").json()


# 1
def test_sin_invitados(client):
    pid = verified_user(client, "5491111111111")
    body = chat(client, pid)
    assert body["limite"] == _config()["limite_diario"] and body["extra_por_invitados"] == 0


# 2
def test_un_amigo_se_registra_y_acepta(new_client, openrouter, monkeypatch):  # noqa: F811
    monkeypatch.setitem(_config(), "limite_diario", 1)
    a, b = new_client(), new_client()
    pid = verified_user(a, "5491111111111", name="Ana")
    ref = invite(a, pid)
    juan = active_user(b, name="Juan")
    assert b.post(f"/invitations/{ref}/accept").status_code == 200
    body = chat(a, pid)
    assert body["limite"] == 2 and body["extra_por_invitados"] == 1
    assert a.post(f"/profiles/{pid}/astrochat", json={"texto": "uno"}).status_code == 200
    assert a.post(f"/profiles/{pid}/astrochat", json={"texto": "dos"}).status_code == 200
    assert a.post(f"/profiles/{pid}/astrochat", json={"texto": "tres"}).status_code == 429
    assert juan


# 3
def test_invitacion_sin_aceptar_no_suma(new_client):
    a, b = new_client(), new_client()
    pid = verified_user(a, "5491111111111", name="Ana")
    invite(a, pid)
    active_user(b, name="Juan")
    assert chat(a, pid)["extra_por_invitados"] == 0


# 4
def test_quien_ya_tenia_cuenta_no_suma(new_client):
    a, b = new_client(), new_client()
    pid = verified_user(a, "5491111111111", name="Ana")
    active_user(b, name="Juan")  # ya estaba registrado
    ref = invite(a, pid)
    assert b.post(f"/invitations/{ref}/accept").status_code == 200
    assert chat(a, pid)["extra_por_invitados"] == 0


# 5
def test_la_misma_persona_suma_una_vez(new_client):
    a, b = new_client(), new_client()
    pid = verified_user(a, "5491111111111", name="Ana")
    ref1, ref2 = invite(a, pid), invite(a, pid, "Juancito")
    active_user(b, name="Juan")
    b.post(f"/invitations/{ref1}/accept")
    b.post(f"/invitations/{ref2}/accept")
    assert chat(a, pid)["extra_por_invitados"] == 1


# 6
def test_tope(new_client, monkeypatch):
    monkeypatch.setitem(_config()["invitados"], "bonus_maximo", 1)
    a, b, c = new_client(), new_client(), new_client()
    pid = verified_user(a, "5491111111111", name="Ana")
    ref1, ref2 = invite(a, pid), invite(a, pid, "Beto")
    active_user(b, name="Juan")
    b.post(f"/invitations/{ref1}/accept")
    active_user(c, name="Beto")
    c.post(f"/invitations/{ref2}/accept")
    assert chat(a, pid)["extra_por_invitados"] == 1
