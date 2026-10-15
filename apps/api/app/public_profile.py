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


GENDER_LABELS = {"mujer": "mujer", "hombre": "hombre", "no_binario": "no binario"}


def gender_label(profile: Profile) -> str | None:
    """Spec B8: el género se muestra solo si la persona lo elige; su texto libre si lo escribió."""
    if not profile.show_gender or profile.gender is None:
        return None
    return profile.gender_detail or GENDER_LABELS[profile.gender]


def public_fields(profile: Profile) -> dict:
    return {
        "display_name": profile.display_name,
        "age": age(profile.birth_date),
        "sun_sign": sun_sign(profile),
        "photo_url": f"/profiles/{profile.id}/photo" if profile.photo_path else None,
        # La principal por su URL de siempre (avatar en chats y listas); el resto por id (spec A11).
        "photos": [f"/profiles/{profile.id}/photo" if p.position == 0 else f"/photos/{p.id}" for p in profile.photos],
        "gender_label": gender_label(profile),
        "avatar": profile.avatar,
        "energy_period": profile.energy_period,
        "interests": profile.interests or [],
        "bio": profile.bio,
        "neighborhood": profile.neighborhood,
    }
