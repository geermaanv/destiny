import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ProfilePhoto

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("/{photo_id}")
def get_photo(photo_id: uuid.UUID, db: Session = Depends(get_db)) -> FileResponse:
    """Una foto del perfil (spec A11). Son públicas dentro de Descubrir; el id no se adivina."""
    photo = db.get(ProfilePhoto, photo_id)
    if photo is None or not Path(photo.path).exists():
        raise HTTPException(status_code=404, detail="Photo not found")
    return FileResponse(photo.path)
