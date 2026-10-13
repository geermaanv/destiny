"""Spec C8 v2: invitación a comparar el test de personalidad."""

import pytest

from tests.helpers import complete_personality, create_profile, verify, verified_user


def _invite(client, inviter, **extra):
    payload = {"inviter_id": inviter, "friend_name": "Juan", "kind": "test", "relationship": "laboral", **extra}
    return client.post("/invitations", json=payload)


def test_sin_test_completo_no_se_puede_invitar(client):
    pid = verified_user(client, "5491111111111", name="Ger")
    assert _invite(client, pid).status_code == 409


def test_con_test_completo_arma_el_mensaje_sin_pedir_signo(client):
    pid = verified_user(client, "5491111111111", name="Ger")
    complete_personality(client, pid)
    r = _invite(client, pid)
    assert r.status_code == 201
    assert r.json()["message"].startswith("¡Hola Juan! ¿Por qué con algunas personas fluye y con otras no?")
    assert "Ya completé mi test de personalidad en Destiny" in r.json()["message"]
    assert "https://destiny.test/onboarding/invitacion?ref=" in r.json()["message"]


def test_invitacion_astrologica_sigue_pidiendo_signo(client):
    pid = verified_user(client, "5491111111111", name="Ger")
    r = client.post("/invitations", json={"inviter_id": pid, "friend_name": "Juan", "kind": "astro"})
    assert r.status_code == 422


def test_vinculo_invalido(client):
    pid = verified_user(client, "5491111111111", name="Ger")
    complete_personality(client, pid)
    assert _invite(client, pid, relationship="jefe").status_code == 422


def test_el_link_muestra_quien_invita_tipo_y_vinculo(new_client):
    a, b = new_client(), new_client()
    pid = verified_user(a, "5491111111111", name="Ger")
    complete_personality(a, pid)
    ref = _invite(a, pid).json()["ref_id"]
    pre = b.get(f"/invitations/{ref}").json()
    assert pre["kind"] == "test" and pre["inviter_name"] == "Ger" and pre["relationship"] == "laboral"


@pytest.fixture
def invitacion_aceptada(new_client):
    a, b = new_client(), new_client()
    ger = verified_user(a, "5491111111111", name="Ger")
    complete_personality(a, ger)
    ref = _invite(a, ger).json()["ref_id"]
    juan = verified_user(b, "5492222222222", name="Juan")
    r = b.post(f"/invitations/{ref}/accept")
    return a, ger, b, juan, ref, r


def test_al_aceptar_quedan_conectados_con_el_vinculo(invitacion_aceptada):
    a, ger, b, juan, ref, r = invitacion_aceptada
    assert r.status_code == 200
    match_id = r.json()["match_id"]
    conexion = b.get(f"/matches/{match_id}").json()
    assert conexion["status"] == "aceptada" and conexion["other"]["display_name"] == "Ger"
    assert b.get(f"/matches/{match_id}/compatibility").json()["relationship"] == "laboral"
    again = b.post(f"/invitations/{ref}/accept")
    assert again.json()["match_id"] == match_id
    assert len(a.get("/connections", params={"profile_id": ger}).json()) == 1


def test_aceptar_sin_sesion_o_la_propia(new_client, invitacion_aceptada):
    a, ger, b, juan, ref, r = invitacion_aceptada
    anon = new_client()
    assert anon.post(f"/invitations/{ref}/accept").status_code == 401
    assert a.post(f"/invitations/{ref}/accept").status_code == 409


def test_estado_de_mis_invitaciones(new_client):
    a, b = new_client(), new_client()
    ger = verified_user(a, "5491111111111", name="Ger")
    complete_personality(a, ger)
    ref = _invite(a, ger).json()["ref_id"]

    def estado():
        mias = a.get("/invitations/mine", params={"profile_id": ger}).json()
        return mias[0]["status"], mias[0]["match_id"]

    assert estado() == ("enviada", None)
    juan = verified_user(b, "5492222222222", name="Juan")
    match_id = b.post(f"/invitations/{ref}/accept").json()["match_id"]
    assert estado() == ("registrado", match_id)
    complete_personality(b, juan)
    assert estado() == ("test_completo", match_id)
