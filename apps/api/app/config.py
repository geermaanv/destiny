from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://destiny:destiny@localhost:5432/destiny"
    environment: str = "development"
    anthropic_api_key: str | None = None
    web_base_url: str = "http://localhost:3000"
    # Verificación por WhatsApp (spec A3 v1, ADR 0008). Sin estas variables y
    # con environment=development, el webhook corre en modo mock.
    whatsapp_business_number: str | None = None
    whatsapp_verify_token: str | None = None
    whatsapp_app_secret: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
