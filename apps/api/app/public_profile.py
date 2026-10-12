"""Datos públicos de un perfil (spec A4): lo que ven otros usuarios.

Nunca incluye teléfono ni fecha/hora/lugar de nacimiento exactos.
"""

from datetime import date

from app.astro import natal_sun_longitude, zodiac_sign
from app.models import Profile


def age(birth_date: date | None) -> int | None:
    if birth_date is None:
        return None
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def sun_sign(profile: Profile) -> str | None:
    if profile.birth_date is None:
        return None
    return zodiac_sign(natal_sun_longitude(profile))


def public_fields(profile: Profile) -> dict:
    return {
        "display_name": profile.display_name,
        "age": age(profile.birth_date),
        "sun_sign": sun_sign(profile),
        "photo_url": f"/profiles/{profile.id}/photo" if profile.photo_path else None,
        "avatar": profile.avatar,
        "energy_period": profile.energy_period,
        "interests": profile.interests or [],
        "bio": profile.bio,
        "neighborhood": profile.neighborhood,
    }
