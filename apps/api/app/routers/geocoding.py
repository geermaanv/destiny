from fastapi import APIRouter, Depends, HTTPException, Query

from app.geocoding import Geocoder, GeocodingUnavailable, get_geocoder
from app.schemas import PlaceOut

router = APIRouter(prefix="/geocoding", tags=["geocoding"])


@router.get("/search", response_model=list[PlaceOut])
def search_places(q: str = Query(min_length=2, max_length=100), geocoder: Geocoder = Depends(get_geocoder)):
    try:
        return geocoder.search(q)
    except GeocodingUnavailable:
        raise HTTPException(status_code=503, detail="Geocoding unavailable")
