import secrets
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.astro import ZODIAC_SIGNS
from app.auth import require_self, session_profile_id
from app.database import get_db
from app.models import Profile, ShareLink
from app.natal.dimensions import natal_dimensions
from app.personalization.style import style_for
from app.routers.natal import dimension_synthesis
from app.schemas import PublicCartaOut, ShareStatusOut

# Compartir mi carta con un link público (spec A9). Destiny decide qué se muestra:
# nada de fecha, hora o lugar de nacimiento, grados exactos, teléfono ni foto.
router = APIRouter(tags=["share"])

WHEEL_POINTS = ("sol", "luna", "mercurio", "venus", "marte", "jupiter", "saturno", "urano", "neptuno", "pluton", "asc")


def _active(db: Session, profile_id: uuid.UUID) -> ShareLink | None:
    return db.scalar(select(ShareLink).where(ShareLink.profile_id == profile_id, ShareLink.revoked_at.is_(None)))


def _own(profile_id: uuid.UUID, current: uuid.UUID | None, db: Session) -> Profile:
    require_self(profile_id, current)
    profile = db.get(Profile, profile_id)
    if profile is None or profile.birth_date is None:
        raise HTTPException(status_code=409, detail="Perfil sin datos natales")
    return profile


@router.post("/profiles/{profile_id}/share", response_model=ShareStatusOut)
def create_share(
    profile_id: uuid.UUID, db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> ShareStatusOut:
    _own(profile_id, current, db)
    link = _active(db, profile_id)
    if link is None:
        link = ShareLink(token=secrets.token_urlsafe(18), profile_id=profile_id)
        db.add(link)
        db.commit()
        db.refresh(link)
    return ShareStatusOut(activo=True, token=link.token, vistas=link.views)


@router.get("/profiles/{profile_id}/share", response_model=ShareStatusOut)
def get_share(
    profile_id: uuid.UUID, db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> ShareStatusOut:
    require_self(profile_id, current)
    link = _active(db, profile_id)
    return ShareStatusOut(activo=True, token=link.token, vistas=link.views) if link else ShareStatusOut(activo=False)


@router.delete("/profiles/{profile_id}/share", status_code=204)
def delete_share(
    profile_id: uuid.UUID, db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> Response:
    require_self(profile_id, current)
    if (link := _active(db, profile_id)) is not None:
        link.revoked_at = datetime.now(timezone.utc)
        db.commit()
    return Response(status_code=204)


def _public_sky(cielo: list[dict]) -> list[dict]:
    """Cada planeta en el medio de su signo (repartidos si hay varios): sin grados exactos."""
    by_sign: dict[int, list[dict]] = {}
    for p in cielo:
        if p["punto"] in WHEEL_POINTS:
            by_sign.setdefault(int(p["lon"] // 30), []).append(p)
    out = []
    for sign, points in by_sign.items():
        points.sort(key=lambda p: p["lon"])
        n = len(points)
        for i, p in enumerate(points):
            offset = max(-12.0, min(12.0, (i - (n - 1) / 2) * 5.0))
            out.append({"punto": p["punto"], "lon": sign * 30 + 15 + offset})
    return out


@router.get("/public/carta/{token}", response_model=PublicCartaOut)
def public_carta(token: str, db: Session = Depends(get_db)) -> PublicCartaOut:
    link = db.get(ShareLink, token)
    if link is None or link.revoked_at is not None:
        raise HTTPException(status_code=404, detail="Link inexistente")
    profile = db.get(Profile, link.profile_id)
    if profile is None or profile.birth_date is None:
        raise HTTPException(status_code=404, detail="Link inexistente")
    link.views += 1
    db.commit()

    style = style_for(profile)
    lon = {p["punto"]: p["lon"] for p in style["cielo"]}
    signos = {p: ZODIAC_SIGNS[int(lon[p] // 30)] for p in ("sol", "luna", "asc") if p in lon}
    result = natal_dimensions(profile)
    dimensiones = [
        {
            "clave": d["clave"],
            "nombre": d["nombre"],
            "pregunta": d["pregunta"],
            "sintesis": dimension_synthesis(db, profile, d, result["aproximado"], style)[0],
        }
        for d in result["dimensiones"]
    ]
    return PublicCartaOut(
        nombre=profile.display_name or "Alguien",
        signos=signos,
        cielo=_public_sky(style["cielo"]),
        dimensiones=dimensiones,
        paleta=style["paleta"],
        tipografia=style["tipografia"],
        fondo=style["fondo"],
        elementos=style["elementos"],
    )
