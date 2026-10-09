"""Spec A5-sesion: la verificación por WhatsApp funciona como login."""

from tests.helpers import create_profile, send_whatsapp, verified_user


def test_sin_sesion_me_da_401(client):
    assert client.get("/me").status_code == 401


def test_verificarse_deja_la_sesion_iniciada(client):
    pid = verified_user(client, "5491111111111")
    assert client.get("/me").json()["id"] == pid


def test_no_se_toma_la_sesion_antes_de_que_llegue_el_mensaje(client):
    pid = create_profile(client)
    code = client.post(f"/profiles/{pid}/verification/whatsapp").json()
    assert client.post("/sessions/claim", json={"claim_token": code["claim_token"]}).status_code == 409


def test_comprobante_falso_no_sirve(client):
    assert client.post("/sessions/claim", json={"claim_token": "falso"}).status_code == 409


def test_comprobante_se_usa_una_sola_vez(new_client):
    a, b = new_client(), new_client()
    pid = create_profile(a)
    code = a.post(f"/profiles/{pid}/verification/whatsapp").json()
    send_whatsapp(a, "5491111111111", code["code"])
    assert a.post("/sessions/claim", json={"claim_token": code["claim_token"]}).status_code == 204
    assert b.post("/sessions/claim", json={"claim_token": code["claim_token"]}).status_code == 409


def test_saber_el_profile_id_no_alcanza_para_actuar_como_otro(new_client):
    a, intruso = new_client(), new_client()
    pid = verified_user(a, "5491111111111")
    assert intruso.get(f"/profiles/{pid}").status_code == 401
    assert intruso.post(f"/profiles/{pid}/basic-info", json={"display_name": "hack"}).status_code == 401
    otro = verified_user(intruso, "5492222222222")
    assert intruso.get(f"/profiles/{pid}").status_code == 403
    assert intruso.get("/discover", params={"viewer_id": pid}).status_code == 403
    assert otro


def test_ya_tengo_cuenta_entra_con_el_numero_verificado(new_client):
    a, otro_navegador = new_client(), new_client()
    pid = verified_user(a, "5491111111111")
    login = otro_navegador.post("/sessions/login").json()
    assert otro_navegador.get(f"/sessions/login/{login['login_id']}").json()["status"] == "pendiente"
    send_whatsapp(otro_navegador, "5491111111111", login["code"])
    assert otro_navegador.get(f"/sessions/login/{login['login_id']}").json()["status"] == "listo"
    assert otro_navegador.post("/sessions/claim", json={"claim_token": login["claim_token"]}).status_code == 204
    assert otro_navegador.get("/me").json()["id"] == pid


def test_ya_tengo_cuenta_con_numero_sin_cuenta(client):
    login = client.post("/sessions/login").json()
    send_whatsapp(client, "5499999999999", login["code"])
    assert client.get(f"/sessions/login/{login['login_id']}").json()["status"] == "sin_cuenta"
    assert client.post("/sessions/claim", json={"claim_token": login["claim_token"]}).status_code == 409


def test_cerrar_sesion(client):
    verified_user(client, "5491111111111")
    assert client.post("/sessions/logout").status_code == 204
    assert client.get("/me").status_code == 401


def test_onboarding_funciona_sin_sesion_hasta_verificarse(client):
    pid = create_profile(client)
    assert client.get(f"/profiles/{pid}").status_code == 200
    assert client.post(f"/profiles/{pid}/basic-info", json={"display_name": "Ana"}).status_code == 200
