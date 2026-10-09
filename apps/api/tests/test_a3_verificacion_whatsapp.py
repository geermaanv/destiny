"""Spec A3-verificacion-identidad v1: verificación por WhatsApp "al revés"."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import update

from app.database import SessionLocal
from app.models import PhoneVerificationCode
from tests.helpers import create_profile, send_whatsapp, verified_user


def _status(client, profile_id):
    return client.get(f"/profiles/{profile_id}/verification").json()["status"]


def test_codigo_valido_verifica_y_guarda_el_telefono(client):
    pid = create_profile(client)
    code = client.post(f"/profiles/{pid}/verification/whatsapp").json()
    assert len(code["code"]) == 6 and code["wa_link"].startswith("https://wa.me/15550000000?text=")
    send_whatsapp(client, "5491111111111", f"Mi código Destiny: {code['code']}")
    assert _status(client, pid) == "verificado"


def test_mensaje_sin_codigo_o_con_codigo_inexistente_no_cambia_nada(client):
    pid = create_profile(client)
    client.post(f"/profiles/{pid}/verification/whatsapp")
    send_whatsapp(client, "5491111111111", "hola")
    send_whatsapp(client, "5491111111111", "Mi código Destiny: 000000")
    assert _status(client, pid) == "pendiente"


def test_codigo_vencido_no_verifica(client):
    pid = create_profile(client)
    code = client.post(f"/profiles/{pid}/verification/whatsapp").json()["code"]
    with SessionLocal() as db:
        db.execute(
            update(PhoneVerificationCode)
            .where(PhoneVerificationCode.code == code)
            .values(expires_at=datetime.now(timezone.utc) - timedelta(minutes=1))
        )
        db.commit()
    send_whatsapp(client, "5491111111111", code)
    assert _status(client, pid) == "pendiente"


def test_pedir_otro_codigo_invalida_el_anterior(client):
    pid = create_profile(client)
    viejo = client.post(f"/profiles/{pid}/verification/whatsapp").json()["code"]
    nuevo = client.post(f"/profiles/{pid}/verification/whatsapp").json()["code"]
    send_whatsapp(client, "5491111111111", viejo)
    assert _status(client, pid) == "pendiente"
    send_whatsapp(client, "5491111111111", nuevo)
    assert _status(client, pid) == "verificado"


def test_codigo_no_se_puede_reusar_desde_otro_numero(new_client):
    a, b = new_client(), new_client()
    pid = create_profile(a)
    code = a.post(f"/profiles/{pid}/verification/whatsapp").json()["code"]
    send_whatsapp(a, "5491111111111", code)
    pid_b = create_profile(b)
    send_whatsapp(b, "5492222222222", code)
    assert _status(b, pid_b) == "pendiente"


def test_numero_ya_verificado_en_otra_cuenta_da_duplicado(new_client):
    a, b = new_client(), new_client()
    verified_user(a, "5491111111111")
    pid = create_profile(b)
    code = b.post(f"/profiles/{pid}/verification/whatsapp").json()["code"]
    send_whatsapp(b, "5491111111111", code)
    assert _status(b, pid) == "duplicado_detectado"


def test_duplicado_seguir_con_mi_cuenta_entra_a_la_existente_y_borra_la_nueva(new_client):
    a, b = new_client(), new_client()
    existente = verified_user(a, "5491111111111")
    nueva = create_profile(b)
    code = b.post(f"/profiles/{nueva}/verification/whatsapp").json()
    send_whatsapp(b, "5491111111111", code["code"])
    r = b.post(f"/profiles/{nueva}/verification/continue-existing", json={"claim_token": code["claim_token"]})
    assert r.status_code == 200 and r.json()["profile_id"] == existente
    assert b.get("/me").json()["id"] == existente
    assert b.get(f"/profiles/{nueva}").status_code == 404


def test_duplicado_seguir_con_mi_cuenta_exige_el_comprobante(new_client):
    a, b = new_client(), new_client()
    verified_user(a, "5491111111111")
    nueva = create_profile(b)
    code = b.post(f"/profiles/{nueva}/verification/whatsapp").json()
    send_whatsapp(b, "5491111111111", code["code"])
    r = b.post(f"/profiles/{nueva}/verification/continue-existing", json={"claim_token": "falso"})
    assert r.status_code == 403


def test_duplicado_usar_otro_numero_vuelve_a_pendiente(new_client):
    a, b = new_client(), new_client()
    verified_user(a, "5491111111111")
    pid = create_profile(b)
    send_whatsapp(b, "5491111111111", b.post(f"/profiles/{pid}/verification/whatsapp").json()["code"])
    assert _status(b, pid) == "duplicado_detectado"
    otro = b.post(f"/profiles/{pid}/verification/whatsapp").json()["code"]
    assert _status(b, pid) == "pendiente"
    send_whatsapp(b, "5493333333333", otro)
    assert _status(b, pid) == "verificado"


def test_sin_datos_natales_no_se_puede_pedir_codigo(client):
    pid = client.post("/profiles").json()["id"]
    assert client.post(f"/profiles/{pid}/verification/whatsapp").status_code == 409


def test_webhook_rechaza_mensajes_sin_firma_o_con_firma_falsa(client):
    pid = create_profile(client)
    code = client.post(f"/profiles/{pid}/verification/whatsapp").json()["code"]
    assert client.post("/webhooks/whatsapp", json={"entry": []}).status_code == 403
    assert send_whatsapp(client, "5491111111111", code, secret="otro-secreto").status_code == 403
    assert _status(client, pid) == "pendiente"


def test_handshake_de_meta(client):
    ok = client.get(
        "/webhooks/whatsapp",
        params={"hub.mode": "subscribe", "hub.verify_token": "test-verify-token", "hub.challenge": "42"},
    )
    assert ok.status_code == 200 and ok.text == "42"
    mal = client.get(
        "/webhooks/whatsapp", params={"hub.mode": "subscribe", "hub.verify_token": "x", "hub.challenge": "42"}
    )
    assert mal.status_code == 403


def test_el_telefono_nunca_se_expone(new_client):
    a, b = new_client(), new_client()
    pid_a = verified_user(a, "5491111111111", name="Ana")
    pid_b = verified_user(b, "5492222222222", name="Beto")
    assert "549111" not in a.get(f"/profiles/{pid_a}").text
    assert "549111" not in b.get("/discover", params={"viewer_id": pid_b}).text
