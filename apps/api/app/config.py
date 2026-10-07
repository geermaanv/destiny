from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://destiny:destiny@localhost:5432/destiny"
    environment: str = "development"
    anthropic_api_key: str | None = None
    web_base_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
