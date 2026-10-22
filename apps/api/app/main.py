from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import (
    calendar,
    discover,
    geocoding,
    home,
    invitations,
    matches,
    personality,
    photos,
    profiles,
    sessions,
    style,
    natal,
    share,
    astrochat,
    whatsapp,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Destiny API", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Spec R1: el 422 no repite el valor recibido (un NaN no se puede devolver en JSON y daba 500)."""
    errors = [{k: v for k, v in e.items() if k in ("type", "loc", "msg")} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": errors})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles.router)
app.include_router(photos.router)
app.include_router(home.router)
app.include_router(home.mood_router)
app.include_router(discover.router)
app.include_router(calendar.router)
app.include_router(matches.router)
app.include_router(invitations.router)
app.include_router(whatsapp.router)
app.include_router(geocoding.router)
app.include_router(sessions.router)
app.include_router(personality.router)
app.include_router(style.router)
app.include_router(natal.router)
app.include_router(share.router)
app.include_router(astrochat.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
