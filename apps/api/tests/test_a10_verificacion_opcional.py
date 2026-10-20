"""Spec A10: verificación por WhatsApp opcional (MVP)."""

import pytest

from tests.helpers import BUENOS_AIRES, accept_privacy, add_photo, create_profile, verified_user
from tests.test_x1_redaccion_con_ia import FakeOpenRouter  # noqa: F401
from tests.test_x1_redaccion_con_ia import sin_key  # noqa: F401


def active_user(client, name="Ana", birth_date="1990-05-20", birth_time="14:30", photo=True) -> str:
    """Registro completo sin WhatsApp: perfil, datos, nombre y sesión en el dispositivo (y foto, spec A11)."""
    pid = create_profile(client, birth_date=birth_date, birth_time=birth_time, name=name)
    accept_privacy(client, pid)
    r = client.post("/sessions/start", json={"profile_id": pid})
    assert r.status_code == 204, r.text
    if photo:
        add_photo(client, pid)
    return pid


# 1
def test_registro_sin_whatsapp_inicia_sesion(client):
    pid = active_user(client)
    me = client.get("/me")
    assert me.status_code == 200 and me.json()["id"] == pid


# 2
def test_otro_navegador_no_puede_iniciar_esa_sesion(new_client):
    owner, other = new_client(), new_client()
    pid = create_profile(owner, name="Ana")
    assert other.post("/sessions/start", json={"profile_id": pid}).status_code == 403


# 3
@pytest.mark.parametrize("kwargs", [{"name": None}, {"birth_date": None}], ids=["sin-nombre", "sin-datos"])
def test_perfil_incompleto(client, kwargs):
    if kwargs.get("birth_date", "x") is None:
        pid = client.post("/profiles").json()["id"]
        client.post(f"/profiles/{pid}/basic-info", json={"display_name": "Ana"})
    else:
        pid = create_profile(client, name=None)
    assert client.post("/sessions/start", json={"profile_id": pid}).status_code == 409


# 4
def test_con_verificacion_obligatoria(client, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "verificacion_obligatoria", True)
    pid = create_profile(client, name="Ana")
    r = client.post("/sessions/start", json={"profile_id": pid})
    assert r.status_code == 403 and r.json()["detail"] == "verificacion_obligatoria"


# 5
def test_perfil_activo_solo_lo_toca_su_duenio(client, new_client):
    pid = active_user(client)
    stranger = new_client()
    assert stranger.get(f"/profiles/{pid}").status_code == 401
    birth = {"birth_date": "1991-01-01", "birth_place": BUENOS_AIRES}
    assert stranger.post(f"/profiles/{pid}/birth-data", json=birth).status_code == 401
    assert stranger.post(f"/profiles/{pid}/basic-info", json={"display_name": "Otro"}).status_code == 401
    # Sin esto, alguien podría verificar el perfil ajeno con su teléfono y quedarse con la cuenta.
    assert stranger.post(f"/profiles/{pid}/verification/whatsapp").status_code == 401
    assert client.post(f"/profiles/{pid}/verification/whatsapp").status_code == 200


# 6
def test_descubrir_muestra_activos_verificados_y_no(new_client):
    a, b, c, d = new_client(), new_client(), new_client(), new_client()
    viewer = active_user(a, name="Vera")
    sin_verificar = active_user(b, name="Beto")
    verificada = verified_user(c, "5493333333333", name="Cami")
    abandonado = create_profile(d, name="Dani")  # nunca terminó el registro
    found = {x["profile_id"]: x for x in a.get("/discover", params={"viewer_id": viewer}).json()}
    assert found[sin_verificar]["verificado"] is False
    assert found[verificada]["verificado"] is True
    assert abandonado not in found


# 7
def test_activo_sin_verificar_usa_la_app(client, sin_key):  # noqa: F811
    pid = active_user(client)
    for url in [
        f"/home/my-day?profile_id={pid}&date=2026-10-12",
        f"/home/my-day/detail?profile_id={pid}&date=2026-10-12",
        f"/profiles/{pid}/natal/dimensions",
        f"/profiles/{pid}/style",
        f"/profiles/{pid}/astrochat",
        f"/discover?viewer_id={pid}",
    ]:
        assert client.get(url).status_code == 200, url


# 8
def test_pasar_a_whatsapp_exige_verificar(new_client):
    a, b = new_client(), new_client()
    ana = active_user(a, name="Ana")
    beto = verified_user(b, "5492222222222", name="Beto")
    match = b.post("/matches", json={"profile_a_id": beto, "profile_b_id": ana}).json()
    a.post(f"/matches/{match['id']}/accept", json={"profile_id": ana})
    r = a.post(f"/matches/{match['id']}/whatsapp", json={"profile_id": ana})
    assert r.status_code == 409 and "verific" in r.json()["detail"].lower()


# 9
def test_aceptar_invitacion_sin_verificar(new_client):
    a, b = new_client(), new_client()
    inviter = verified_user(a, "5491111111111", name="Ana")
    ref = a.post(
        "/invitations", json={"inviter_id": inviter, "friend_name": "Beto", "friend_sun_sign": "Leo"}
    ).json()["ref_id"]
    active_user(b, name="Beto")
    assert b.post(f"/invitations/{ref}/accept").status_code == 200


# 10
def test_frecuencia_cuenta_activos(new_client):
    a, b = new_client(), new_client()
    viewer = active_user(a, name="Vera")
    active_user(b, name="Beto")
    assert a.get("/home/frequency-count", params={"profile_id": viewer}).json()["count"] == 1
