from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import calendar, discover, home, invitations, matches, profiles, whatsapp


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Destiny API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles.router)
app.include_router(home.router)
app.include_router(home.mood_router)
app.include_router(discover.router)
app.include_router(calendar.router)
app.include_router(matches.router)
app.include_router(invitations.router)
app.include_router(whatsapp.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
