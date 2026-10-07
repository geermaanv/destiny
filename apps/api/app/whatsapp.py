"""Verificación de identidad por WhatsApp "al revés" (spec A3 v1, ADR 0008).

El usuario envía un código prellenado al número de Destiny vía link wa.me;
Meta llama a /webhooks/whatsapp con el mensaje y acá se valida el código y
se toma el número del remitente como teléfono verificado. Una cuenta por número.
"""

import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import PhoneVerificationCode, Profile

CODE_TTL = timedelta(minutes=15)
CODE_PATTERN = re.compile(r"\b(\d{6})\b")


def is_mock_mode() -> bool:
    """Sin credenciales de WhatsApp en desarrollo: webhook sin firma + botón de simulación."""
    return settings.environment == "development" and not settings.whatsapp_app_secret


def _now() -> datetime:
    return datetime.now(timezone.utc)


def build_wa_link(code: str) -> str:
    message = quote(f"Mi código Destiny: {code}")
    number = (settings.whatsapp_business_number or "").lstrip("+")
    # Sin número configurado (mock), wa.me abre el selector de contactos.
    return f"https://wa.me/{number}?text={message}"


def issue_code(db: Session, profile: Profile) -> PhoneVerificationCode:
    """Genera un código nuevo e invalida los anteriores sin usar del mismo perfil.

    Un intento nuevo después de `duplicado_detectado` (ej. con otro número)
    vuelve el perfil a `pendiente`.
    """
    now = _now()
    if profile.verification_status == "duplicado_detectado":
        profile.verification_status = "pendiente"
        profile.duplicate_of_id = None
    for old in db.scalars(
        select(PhoneVerificationCode).where(
            PhoneVerificationCode.profile_id == profile.id, PhoneVerificationCode.used_at.is_(None)
        )
    ):
        db.delete(old)

    while True:
        code = f"{secrets.randbelow(1_000_000):06d}"
        clash = db.scalar(
            select(PhoneVerificationCode).where(
                PhoneVerificationCode.code == code,
                PhoneVerificationCode.used_at.is_(None),
                PhoneVerificationCode.expires_at > now,
            )
        )
        if clash is None:
            break

    entry = PhoneVerificationCode(profile_id=profile.id, code=code, expires_at=now + CODE_TTL)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def signature_is_valid(raw_body: bytes, header: str | None) -> bool:
    if not settings.whatsapp_app_secret or not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(settings.whatsapp_app_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.removeprefix("sha256="))


def extract_text_messages(payload: dict) -> list[tuple[str, str]]:
    """(remitente, texto) de cada mensaje de texto del payload de Meta. Ignora el resto."""
    messages = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            for message in change.get("value", {}).get("messages", []):
                if message.get("type") == "text" and message.get("from"):
                    messages.append((message["from"], message.get("text", {}).get("body", "")))
    return messages


def normalize_phone(wa_id: str) -> str:
    return "+" + re.sub(r"\D", "", wa_id)


def process_incoming(db: Session, sender: str, text: str) -> None:
    """Aplica un mensaje entrante. Sin código válido y vigente, no cambia nada."""
    match = CODE_PATTERN.search(text)
    if match is None:
        return

    now = _now()
    entry = db.scalar(
        select(PhoneVerificationCode).where(
            PhoneVerificationCode.code == match.group(1),
            PhoneVerificationCode.used_at.is_(None),
            PhoneVerificationCode.expires_at > now,
        )
    )
    if entry is None:
        return

    entry.used_at = now
    profile = db.get(Profile, entry.profile_id)
    if profile is None or profile.verification_status == "verificado":
        db.commit()
        return

    phone = normalize_phone(sender)
    owner = db.scalar(select(Profile).where(Profile.phone_e164 == phone, Profile.id != profile.id))
    profile.verification_method = "whatsapp"
    if owner is not None:
        # Quien mandó el código probó que tiene ese número: puede seguir con la
        # cuenta existente (POST /profiles/{id}/verification/continue-existing).
        profile.verification_status = "duplicado_detectado"
        profile.duplicate_of_id = owner.id
    else:
        profile.phone_e164 = phone
        profile.verification_status = "verificado"
    db.commit()
