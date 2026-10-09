"""Infraestructura de tests de la API (regla: spec → casos de prueba → código).

- Base de datos separada `destiny_test`: nunca toca los datos de desarrollo.
- Configuración fija para tests (se setea antes de importar la app): WhatsApp
  "real" (con App Secret, así se prueba la firma de Meta), sin Claude API
  (adapters mock), y cookies Secure (por eso el cliente usa https://testserver).
"""

import os

os.environ.update(
    {
        "DATABASE_URL": "postgresql+psycopg://destiny:destiny@localhost:5432/destiny_test",
        "ENVIRONMENT": "test",
        "WHATSAPP_APP_SECRET": "test-app-secret",
        "WHATSAPP_VERIFY_TOKEN": "test-verify-token",
        "WHATSAPP_BUSINESS_NUMBER": "15550000000",
        "ANTHROPIC_API_KEY": "",
        "WEB_BASE_URL": "https://destiny.test",
        "UPLOADS_DIR": "/tmp/destiny-test-uploads",
    }
)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.geocoding import Place, get_geocoder  # noqa: E402
from app.main import app  # noqa: E402


class FakeGeocoder:
    """Sin llamadas a Open-Meteo en los tests."""

    def search(self, query: str) -> list[Place]:
        if "rosario" in query.lower():
            return [Place("Rosario, Provincia de Santa Fe, Argentina", -32.9468, -60.6393, "America/Argentina/Cordoba")]
        return [Place("Buenos Aires, Ciudad Autónoma de Buenos Aires, Argentina", -34.6131, -58.3772, "America/Argentina/Buenos_Aires")]


@pytest.fixture(scope="session", autouse=True)
def _schema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_geocoder] = lambda: FakeGeocoder()
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _clean_db():
    """Cada test arranca con la base vacía."""
    tables = ", ".join(t.name for t in Base.metadata.sorted_tables)
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture
def new_client():
    """Fábrica de clientes: cada uno es un navegador distinto (sus propias cookies)."""
    clients = []

    def make() -> TestClient:
        c = TestClient(app, base_url="https://testserver")
        c.__enter__()
        clients.append(c)
        return c

    yield make
    for c in clients:
        c.__exit__(None, None, None)


@pytest.fixture
def client(new_client) -> TestClient:
    return new_client()
