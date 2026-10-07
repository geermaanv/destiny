from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://destiny:destiny@localhost:5432/destiny"
    environment: str = "development"
    anthropic_api_key: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
