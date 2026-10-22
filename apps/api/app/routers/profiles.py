import uuid
from datetime import date, datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.adapters.kyc import IdentityVerificationAdapter, get_kyc_adapter
from app.auth import hash_token, new_token, require_owner_if_active, session_profile_id, set_device_cookie, start_session
from app.config import settings
from app.public_profile import sun_sign
from app.database import get_db
from app import photos
from app.models import PhoneVerificationCode, Profile, ProfilePhoto
from app.schemas import (
    PERIOD_MIDPOINTS,
    UNKNOWN_TIME,
    BasicInfoIn,
    ClaimIn,
    BirthDataIn,
    ContinueExistingOut,
    NotificationPreferenceIn,
    PhotoOut,
    PhotosOut,
    LookingForIn,
    PreferencesIn,
    PrivacyIn,
    ResidenceIn,
    ProfileOut,
    VerificationOut,
    WhatsappCodeOut,
)
from app.whatsapp import build_wa_link, is_mock_mode, issue_code

router = APIRouter(prefix="/profiles", tags=["profiles"])
MAX_RESIDENCE_CHANGES = 3  # por día (spec P2)


@router.post("", response_model=ProfileOut, status_code=201)
def create_profile(response: Response, db: Session = Depends(get_db)) -> Profile:
    # Spec A10: prueba de que este navegador creó el perfil (para iniciar sesión sin WhatsApp).
    device_token = new_token()
    profile = Profile(device_token_hash=hash_token(device_token))
    set_device_cookie(response, device_token)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{profile_id}", response_model=ProfileOut)
def get_profile(
    profile_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> ProfileOut:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    require_owner_if_active(profile, current)
    return ProfileOut.model_validate(profile).model_copy(update={"sun_sign": sun_sign(profile)})


@router.post("/{profile_id}/birth-data", response_model=ProfileOut)
def set_birth_data(
    profile_id: uuid.UUID,
    payload: BirthDataIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    require_owner_if_active(profile, current)

    profile.birth_date = payload.birth_date
    if payload.birth_time is None:
        # "No sé mi hora exacta" -> punto medio de la franja si la recuerda
        # (5 franjas de Pablo, spec A7), si no 12:30 (mediodía); flag de estimada. Derivado
        # server-side: no se confía en un flag de estimada mandado por el cliente.
        profile.birth_time = PERIOD_MIDPOINTS.get(payload.birth_time_period or "", UNKNOWN_TIME)
        profile.birth_time_estimated = True
    else:
        profile.birth_time = payload.birth_time
        profile.birth_time_estimated = False

    profile.birth_place_query = payload.birth_place.query
    profile.birth_place_lat = payload.birth_place.lat
    profile.birth_place_lon = payload.birth_place.lon
    profile.birth_place_timezone = payload.birth_place.timezone

    db.commit()
    db.refresh(profile)
    return profile


@router.post("/{profile_id}/notification-preference", response_model=ProfileOut)
def set_notification_preference(
    profile_id: uuid.UUID,
    payload: NotificationPreferenceIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    require_owner_if_active(profile, current)

    profile.notification_rhythm = payload.rhythm

    db.commit()
    db.refresh(profile)
    return profile


@router.post("/{profile_id}/verification", response_model=VerificationOut)
async def start_verification(
    profile_id: uuid.UUID,
    media: UploadFile = File(...),
    db: Session = Depends(get_db),
    adapter: IdentityVerificationAdapter = Depends(get_kyc_adapter),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> VerificationOut:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    require_owner_if_active(profile, current)

    media_bytes = await media.read()
    result = adapter.start_verification(str(profile_id), media_bytes)

    profile.verification_id = result.verification_id
    profile.verification_status = result.status
    profile.verification_method = "kyc_video"
    db.commit()

    return VerificationOut(verification_id=result.verification_id, status=result.status, method="kyc_video")


@router.post("/{profile_id}/verification/whatsapp", response_model=WhatsappCodeOut)
def start_whatsapp_verification(
    profile_id: uuid.UUID, db: Session = Depends(get_db), current: uuid.UUID | None = Depends(session_profile_id)
) -> WhatsappCodeOut:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    # Spec A10: una cuenta activa solo la verifica su dueño (si no, otro la verificaría con su teléfono).
    require_owner_if_active(profile, current)
    if profile.verification_status == "verificado":
        raise HTTPException(status_code=409, detail="Profile already verified")
    if profile.birth_date is None:
        # La verificación cierra el onboarding: sin datos natales no hay Descubrir posible.
        raise HTTPException(status_code=409, detail="Profile has no birth data")

    entry, claim_token = issue_code(db, profile)
    return WhatsappCodeOut(
        code=entry.code,
        wa_link=build_wa_link(entry.code),
        expires_at=entry.expires_at,
        mock=is_mock_mode(),
        claim_token=claim_token,
    )


@router.get("/{profile_id}/verification", response_model=VerificationOut)
def get_verification(profile_id: uuid.UUID, db: Session = Depends(get_db)) -> VerificationOut:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return VerificationOut(
        verification_id=profile.verification_id,
        status=profile.verification_status,
        method=profile.verification_method,
    )


@router.post("/{profile_id}/verification/continue-existing", response_model=ContinueExistingOut)
def continue_with_existing_profile(
    profile_id: uuid.UUID, payload: ClaimIn, response: Response, db: Session = Depends(get_db)
) -> ContinueExistingOut:
    """Tras duplicado_detectado: seguir con la cuenta que ya tiene ese número.

    El perfil nuevo (todavía sin verificar) se descarta y se inicia sesión en el
    existente. Requiere el comprobante del navegador que mandó el código (spec A5).
    """
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.verification_status != "duplicado_detectado" or profile.duplicate_of_id is None:
        raise HTTPException(status_code=409, detail="Profile is not a detected duplicate")

    existing = db.get(Profile, profile.duplicate_of_id)
    if existing is None or existing.verification_status != "verificado":
        raise HTTPException(status_code=409, detail="Existing profile not available")

    proof = db.scalar(
        select(PhoneVerificationCode).where(
            PhoneVerificationCode.profile_id == profile.id,
            PhoneVerificationCode.claim_token_hash == hash_token(payload.claim_token),
            PhoneVerificationCode.used_at.is_not(None),
        )
    )
    if proof is None:
        raise HTTPException(status_code=403, detail="Comprobante inválido")

    db.execute(delete(PhoneVerificationCode).where(PhoneVerificationCode.profile_id == profile.id))
    db.delete(profile)
    db.commit()
    start_session(db, response, existing.id)
    return ContinueExistingOut(profile_id=existing.id)


# Perfil liviano (spec A4); las fotos son de la spec A11.


@router.post("/{profile_id}/basic-info", response_model=ProfileOut)
def set_basic_info(
    profile_id: uuid.UUID,
    payload: BasicInfoIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    require_owner_if_active(profile, current)

    profile.display_name = payload.display_name
    profile.energy_period = payload.energy_period
    profile.interests = list(dict.fromkeys(payload.interests))
    profile.bio = payload.bio
    profile.neighborhood = payload.neighborhood
    profile.avatar = payload.avatar
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/{profile_id}/preferences", response_model=ProfileOut)
def set_preferences(
    profile_id: uuid.UUID,
    payload: PreferencesIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> Profile:
    """Spec B8: género y a quién ver en Descubrir ("pareja")."""
    profile = _owned(profile_id, db, current)
    profile.gender = payload.gender
    profile.gender_detail = payload.gender_detail
    profile.show_me = list(dict.fromkeys(payload.show_me))
    profile.appear_in = list(dict.fromkeys(payload.appear_in)) if payload.gender == "no_binario" else []
    profile.show_gender = payload.show_gender
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/{profile_id}/privacy", response_model=ProfileOut)
def accept_privacy(
    profile_id: uuid.UUID,
    payload: PrivacyIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> Profile:
    """Spec A12: se guarda qué versión del aviso aceptó y cuándo (registro o test)."""
    profile = _owned(profile_id, db, current)
    now = datetime.now(timezone.utc)
    if payload.contexto == "registro":
        profile.privacy_version, profile.privacy_accepted_at = payload.version, now
    else:
        profile.test_privacy_version, profile.test_privacy_accepted_at = payload.version, now
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/{profile_id}/looking-for", response_model=ProfileOut)
def set_looking_for(
    profile_id: uuid.UUID,
    payload: LookingForIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> Profile:
    """Spec A12: lo último que eligió en "¿Qué buscás?" de Círculo; ordena el test."""
    profile = _owned(profile_id, db, current)
    profile.looking_for = payload.looking_for
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/{profile_id}/residence", response_model=ProfileOut)
def set_residence(
    profile_id: uuid.UUID,
    payload: ResidenceIn,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> Profile:
    """Spec B9: dónde vive, para el filtro de distancia. Solo lo ve su dueño."""
    profile = _owned(profile_id, db, current)
    # Spec P2: hasta 3 cambios por día y coordenadas a ~1 km (contra la triangulación).
    today = date.today()
    if profile.residence_changed_on != today:
        profile.residence_changed_on, profile.residence_changes = today, 0
    if profile.residence_changes >= MAX_RESIDENCE_CHANGES:
        raise HTTPException(status_code=429, detail="Podés volver a cambiar dónde vivís mañana")
    profile.residence_changes += 1
    profile.residence_label = payload.query
    profile.residence_lat = round(payload.lat, 2)
    profile.residence_lon = round(payload.lon, 2)
    db.commit()
    db.refresh(profile)
    return profile


def _owned(profile_id: uuid.UUID, db: Session, current: uuid.UUID | None) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    require_owner_if_active(profile, current)
    return profile


def _photos_out(profile: Profile) -> PhotosOut:
    return PhotosOut(
        photos=[
            PhotoOut(
                id=p.id,
                url=f"/profiles/{profile.id}/photo" if p.position == 0 else f"/photos/{p.id}",
                principal=p.position == 0,
            )
            for p in profile.photos
        ],
        max=photos.load_config()["max"],
    )


def _save_order(db: Session, profile: Profile, ordered: list[ProfilePhoto]) -> PhotosOut:
    """Renumera (0 = principal) y deja `photo_path` apuntando a la principal."""
    for position, photo in enumerate(ordered):
        photo.position = position
    profile.photo_path = ordered[0].path if ordered else None
    db.commit()
    db.refresh(profile)
    return _photos_out(profile)


@router.get("/{profile_id}/photos", response_model=PhotosOut)
def list_photos(
    profile_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> PhotosOut:
    profile = _owned(profile_id, db, current)
    if current != profile.id:  # sus fotos solo las lista el dueño (las públicas van por Descubrir)
        raise HTTPException(status_code=401, detail="Iniciá sesión")
    return _photos_out(profile)


@router.post("/{profile_id}/photos", response_model=PhotosOut, status_code=201)
async def upload_photo(
    profile_id: uuid.UUID,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> PhotosOut:
    profile = _owned(profile_id, db, current)
    cfg = photos.load_config()
    if len(profile.photos) >= cfg["max"]:
        raise HTTPException(status_code=409, detail=f"Podés tener hasta {cfg['max']} fotos")
    content_type = photo.content_type or ""
    extension = cfg["tipos"].get(content_type)
    if extension is None:
        raise HTTPException(status_code=415, detail="La foto tiene que ser JPG, PNG o WebP")
    content = await photo.read(cfg["max_bytes"] + 1)
    if len(content) > cfg["max_bytes"]:
        raise HTTPException(status_code=413, detail="La foto no puede pesar más de 5 MB")
    if not photos.is_image(content):  # spec R1: el contenido, no solo el tipo declarado
        raise HTTPException(status_code=415, detail="La foto tiene que ser JPG, PNG o WebP")

    # Chequeo automático (ADR 0013): a la IA va solo la imagen.
    verdict = photos.check(content, content_type)
    if not verdict.apta:
        raise HTTPException(status_code=422, detail=photos.rejection_message(verdict))
    if not profile.photos and verdict.persona is False:
        raise HTTPException(status_code=422, detail=cfg["sin_persona"])

    uploads = Path(settings.uploads_dir)
    uploads.mkdir(parents=True, exist_ok=True)
    photo_id = uuid.uuid4()
    path = uploads / f"{profile.id}-{photo_id}{extension}"
    path.write_bytes(content)
    new = ProfilePhoto(
        id=photo_id,
        profile_id=profile.id,
        path=str(path),
        position=len(profile.photos),
        persona=verdict.persona,
        moderacion="aprobada" if verdict.revisada else "sin_revisar",
    )
    db.add(new)
    return _save_order(db, profile, [*profile.photos, new])


def _find_photo(profile: Profile, photo_id: uuid.UUID) -> ProfilePhoto:
    for p in profile.photos:
        if p.id == photo_id:
            return p
    raise HTTPException(status_code=404, detail="Photo not found")


@router.delete("/{profile_id}/photos/{photo_id}", response_model=PhotosOut)
def delete_photo(
    profile_id: uuid.UUID,
    photo_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> PhotosOut:
    profile = _owned(profile_id, db, current)
    target = _find_photo(profile, photo_id)
    Path(target.path).unlink(missing_ok=True)
    rest = [p for p in profile.photos if p.id != photo_id]
    db.delete(target)
    return _save_order(db, profile, rest)


@router.post("/{profile_id}/photos/{photo_id}/principal", response_model=PhotosOut)
def set_principal(
    profile_id: uuid.UUID,
    photo_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: uuid.UUID | None = Depends(session_profile_id),
) -> PhotosOut:
    profile = _owned(profile_id, db, current)
    target = _find_photo(profile, photo_id)
    if target.persona is False:
        raise HTTPException(status_code=409, detail=photos.load_config()["sin_persona"])
    return _save_order(db, profile, [target, *(p for p in profile.photos if p.id != photo_id)])


@router.get("/{profile_id}/photo")
def get_photo(profile_id: uuid.UUID, db: Session = Depends(get_db)) -> FileResponse:
    profile = db.get(Profile, profile_id)
    if profile is None or not profile.photo_path or not Path(profile.photo_path).exists():
        raise HTTPException(status_code=404, detail="Photo not found")
    return FileResponse(profile.photo_path, headers={"Cache-Control": "no-cache", "X-Content-Type-Options": "nosniff"})
