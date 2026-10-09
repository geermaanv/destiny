"""Spec B7 v2: conexión mutua, chat con rompehielos y paso a WhatsApp."""

import pytest

from tests.helpers import verified_user


@pytest.fixture
def pareja(new_client):
    a, b = new_client(), new_client()
    pid_a = verified_user(a, "5491111111111", name="Ana")
    pid_b = verified_user(b, "5492222222222", name="Beto")
    return a, pid_a, b, pid_b


def _conectar(a, pid_a, pid_b):
    return a.post("/matches", json={"profile_a_id": pid_a, "profile_b_id": pid_b}).json()


def test_conectar_crea_solicitud_pendiente_sin_chat(pareja):
    a, pid_a, b, pid_b = pareja
    m = _conectar(a, pid_a, pid_b)
    assert m["status"] == "pendiente"
    assert a.get(f"/chats/{m['id']}/messages").json() == []
    r = a.post(f"/chats/{m['id']}/messages", json={"profile_id": pid_a, "text": "hola"})
    assert r.status_code == 409


def test_la_otra_persona_ve_la_solicitud_recibida(pareja):
    a, pid_a, b, pid_b = pareja
    _conectar(a, pid_a, pid_b)
    conexiones = b.get("/connections", params={"profile_id": pid_b}).json()
    assert [(c["direction"], c["status"], c["other"]["display_name"]) for c in conexiones] == [
        ("recibida", "pendiente", "Ana")
    ]


def test_solo_quien_recibe_puede_aceptar(pareja):
    a, pid_a, b, pid_b = pareja
    m = _conectar(a, pid_a, pid_b)
    assert a.post(f"/matches/{m['id']}/accept", json={"profile_id": pid_a}).status_code == 409
    assert b.post(f"/matches/{m['id']}/accept", json={"profile_id": pid_b}).json()["status"] == "aceptada"


def test_si_los_dos_se_piden_conexion_se_acepta_sola(pareja):
    a, pid_a, b, pid_b = pareja
    _conectar(a, pid_a, pid_b)
    assert _conectar(b, pid_b, pid_a)["status"] == "aceptada"


def test_chat_arranca_con_rompehielos_y_se_puede_escribir(pareja):
    a, pid_a, b, pid_b = pareja
    m = _conectar(a, pid_a, pid_b)
    b.post(f"/matches/{m['id']}/accept", json={"profile_id": pid_b})
    a.post(f"/chats/{m['id']}/messages", json={"profile_id": pid_a, "text": "Hola Beto"})
    msgs = b.get(f"/chats/{m['id']}/messages").json()
    assert msgs[0]["sender"] == "system_icebreaker" and msgs[0]["text"]
    assert msgs[1]["text"] == "Hola Beto"


def test_un_tercero_no_puede_leer_el_chat(pareja, new_client):
    a, pid_a, b, pid_b = pareja
    m = _conectar(a, pid_a, pid_b)
    tercero = new_client()
    assert tercero.get(f"/chats/{m['id']}/messages").status_code == 401
    verified_user(tercero, "5493333333333", name="Caro")
    assert tercero.get(f"/chats/{m['id']}/messages").status_code == 403


def test_el_numero_aparece_solo_cuando_los_dos_aceptan_whatsapp(pareja):
    a, pid_a, b, pid_b = pareja
    m = _conectar(a, pid_a, pid_b)
    b.post(f"/matches/{m['id']}/accept", json={"profile_id": pid_b})
    uno = a.post(f"/matches/{m['id']}/whatsapp", json={"profile_id": pid_a}).json()["whatsapp"]
    assert uno == {"me_ok": True, "other_ok": False, "link": None}
    dos = b.post(f"/matches/{m['id']}/whatsapp", json={"profile_id": pid_b}).json()["whatsapp"]
    assert dos["link"].startswith("https://wa.me/5491111111111?text=")
    assert a.get(f"/matches/{m['id']}").json()["whatsapp"]["link"].startswith("https://wa.me/5492222222222")


def test_no_se_puede_pasar_a_whatsapp_sin_conexion_aceptada(pareja):
    a, pid_a, b, pid_b = pareja
    m = _conectar(a, pid_a, pid_b)
    assert a.post(f"/matches/{m['id']}/whatsapp", json={"profile_id": pid_a}).status_code == 409


def test_bloquear_cierra_la_conexion_y_no_se_puede_volver_a_pedir(pareja):
    a, pid_a, b, pid_b = pareja
    m = _conectar(a, pid_a, pid_b)
    assert b.post(f"/matches/{m['id']}/block", json={"profile_id": pid_b}).json()["status"] == "bloqueada"
    r = a.post("/matches", json={"profile_a_id": pid_a, "profile_b_id": pid_b})
    assert r.status_code == 409
    assert b.get("/connections", params={"profile_id": pid_b}).json() == []


def test_no_se_puede_conectar_con_uno_mismo(pareja):
    a, pid_a, _, _ = pareja
    assert a.post("/matches", json={"profile_a_id": pid_a, "profile_b_id": pid_a}).status_code == 422


def test_conectar_en_nombre_de_otro_esta_prohibido(pareja):
    a, pid_a, b, pid_b = pareja
    assert a.post("/matches", json={"profile_a_id": pid_b, "profile_b_id": pid_a}).status_code == 403
