"""Helpers compartidos: crear perfiles, simular mensajes de WhatsApp firmados como Meta, etc."""

import hashlib
import hmac
import json
import struct
import zlib

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
    privacy: bool = True,
) -> str:
    profile_id = client.post("/profiles").json()["id"]
    if privacy:  # en la app la casilla del aviso es obligatoria en el primer paso (specs A12 y R2)
        client.post(f"/profiles/{profile_id}/privacy", json={"version": "privacidad_v1", "contexto": "registro"})
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


def png() -> bytes:
    """PNG válido de 1x1 para subir como foto."""

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00"))
        + chunk(b"IEND", b"")
    )


def add_photo(client: TestClient, profile_id: str):
    """Sube una foto (spec A11: sin foto no se aparece en Descubrir)."""
    return client.post(f"/profiles/{profile_id}/photos", files={"photo": ("p.png", png(), "image/png")})


def accept_privacy(client: TestClient, profile_id: str) -> None:
    """Acepta los avisos de privacidad del registro y del test (spec A12), como cualquier persona registrada."""
    for contexto in ("registro", "test"):
        r = client.post(f"/profiles/{profile_id}/privacy", json={"version": "privacidad_v1", "contexto": contexto})
        assert r.status_code == 200, r.text


def verified_user(client: TestClient, phone: str, name: str = "Test", photo: bool = True, **kwargs) -> str:
    """Usuario completo: datos natales + nombre + avisos aceptados + verificado + sesión en `client` + foto."""
    profile_id = create_profile(client, name=name, **kwargs)
    accept_privacy(client, profile_id)
    verify(client, profile_id, phone)
    assert client.get("/me").status_code == 200
    if photo:
        add_photo(client, profile_id)
    return profile_id


def complete_personality(client: TestClient, profile_id: str, choice: int = 2) -> None:
    """Responde las 32 preguntas del test de personalidad de Pablo con la misma opción."""
    from app.personality.engine import load_config

    answers = {q["id"]: [choice] for q in load_config()["questions"]}
    assert client.put(f"/profiles/{profile_id}/personality", json={"answers": answers}).status_code == 200
