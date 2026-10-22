from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def advisory_lock(db, key: str) -> None:
    """Spec R2: serializa operaciones sobre la misma cosa (un par de personas, un perfil) hasta el
    fin de la transacción. Evita duplicados y límites pasados con pedidos simultáneos."""
    from sqlalchemy import text

    db.execute(text("SELECT pg_advisory_xact_lock(hashtext(:key))"), {"key": key})


def pair_key(a, b) -> str:
    return "par:" + ":".join(sorted([str(a), str(b)]))
