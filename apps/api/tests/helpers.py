"""Helpers compartidos: crear perfiles, simular mensajes de WhatsApp firmados como Meta, etc."""

import hashlib
import hmac
import json

from fastapi.testclient import TestClient

APP_SECRET = "test-app-secret"

BUENOS_AIRES = {
    "query": "Buenos Aires, Ciudad Autónoma de Buenos Aires, Argentina",
    "lat": -34.6131,
    "lon": -58.3772,
    "timezone": "America/Argentina/Buenos_Aires",
}


def whatsapp_payload(sender: str, text: str) -> dict:
    return {
        "object": "whatsapp_business_account",
        "entry": [{"changes": [{"value": {"messages": [{"from": sender, "type": "text", "text": {"body": text}}]}}]}],
    }


def send_whatsapp(client: TestClient, sender: str, text: str, secret: str = APP_SECRET):
    """Simula el webhook de Meta, con la firma X-Hub-Signature-256 que manda Meta."""
    body = json.dumps(whatsapp_payload(sender, text)).encode()
    signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return client.post(
        "/webhooks/whatsapp",
        content=body,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": signature},
    )


def create_profile(
    client: TestClient,
    birth_date: str = "1990-05-20",
    birth_time: str | None = "14:30",
    place: dict | None = None,
    name: str | None = None,
) -> str:
    profile_id = client.post("/profiles").json()["id"]
    payload = {"birth_date": birth_date, "birth_place": place or BUENOS_AIRES}
    if birth_time:
        payload["birth_time"] = birth_time
    assert client.post(f"/profiles/{profile_id}/birth-data", json=payload).status_code == 200
    if name:
        assert client.post(f"/profiles/{profile_id}/basic-info", json={"display_name": name}).status_code == 200
    return profile_id


def verify(client: TestClient, profile_id: str, phone: str) -> dict:
    """Pide código, 'manda' el WhatsApp desde `phone` y toma la sesión con el comprobante."""
    code = client.post(f"/profiles/{profile_id}/verification/whatsapp").json()
    send_whatsapp(client, phone, f"Mi código Destiny: {code['code']}")
    client.post("/sessions/claim", json={"claim_token": code["claim_token"]})
    return code


def verified_user(client: TestClient, phone: str, name: str = "Test", **kwargs) -> str:
    """Usuario completo: datos natales + nombre + verificado + sesión iniciada en `client`."""
    profile_id = create_profile(client, name=name, **kwargs)
    verify(client, profile_id, phone)
    assert client.get("/me").status_code == 200
    return profile_id
