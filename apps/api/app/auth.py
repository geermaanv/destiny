"""Sesión con WhatsApp (spec A5).

La verificación por WhatsApp funciona como login: cuando llega el mensaje con
el código, el navegador que lo pidió presenta su comprobante (claim token) y
recibe una cookie de sesión. Saber el profile_id no alcanza para actuar como
esa persona.
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Profile, UserSession

COOKIE_NAME = "destiny_session"
SESSION_TTL = timedelta(days=90)
# Ventana para tomar la sesión después de que llegó el mensaje de WhatsApp.
CLAIM_WINDOW = timedelta(minutes=30)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def new_token() -> str:
    return secrets.token_urlsafe(32)


def start_session(db: Session, response: Response, profile_id: uuid.UUID) -> None:
    token = new_token()
    db.add(
        UserSession(
            token_hash=hash_token(token),
            profile_id=profile_id,
            expires_at=datetime.now(timezone.utc) + SESSION_TTL,
        )
    )
    db.commit()
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=int(SESSION_TTL.total_seconds()),
        httponly=True,
        samesite="lax",
        secure=settings.environment != "development",
        path="/",
    )


def end_session(db: Session, request: Request, response: Response) -> None:
    token = request.cookies.get(COOKIE_NAME)
    if token:
        db.execute(delete(UserSession).where(UserSession.token_hash == hash_token(token)))
        db.commit()
    response.delete_cookie(COOKIE_NAME, path="/")


def session_profile_id(request: Request, db: Session = Depends(get_db)) -> uuid.UUID | None:
    """Perfil de la sesión actual, o None si no hay sesión válida."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    session = db.scalar(
        select(UserSession).where(
            UserSession.token_hash == hash_token(token),
            UserSession.expires_at > datetime.now(timezone.utc),
        )
    )
    return session.profile_id if session else None


def require_self(profile_id: uuid.UUID, current: uuid.UUID | None) -> None:
    """Para las pantallas de la app (post-verificación): el perfil tiene que ser el de la sesión."""
    if current is None:
        raise HTTPException(status_code=401, detail="Necesitás iniciar sesión")
    if current != profile_id:
        raise HTTPException(status_code=403, detail="No podés actuar en nombre de otro perfil")


def require_owner_if_verified(profile: Profile, current: uuid.UUID | None) -> None:
    """El onboarding (antes de verificar) funciona sin sesión; un perfil verificado solo lo toca su dueño."""
    if profile.verification_status == "verificado":
        require_self(profile.id, current)
