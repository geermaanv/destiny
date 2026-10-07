import uuid
from datetime import date, time

from pydantic import BaseModel


class BirthPlaceIn(BaseModel):
    query: str
    lat: float | None = None
    lon: float | None = None
    timezone: str | None = None


class BirthDataIn(BaseModel):
    birth_date: date
    birth_time: time | None = None
    birth_place: BirthPlaceIn


class ProfileOut(BaseModel):
    id: uuid.UUID
    birth_date: date | None
    birth_time: time | None
    birth_time_estimated: bool
    birth_place_query: str | None
    birth_place_lat: float | None
    birth_place_lon: float | None
    birth_place_timezone: str | None

    class Config:
        from_attributes = True
