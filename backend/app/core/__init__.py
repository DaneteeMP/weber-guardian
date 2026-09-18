"""Config centralizada. Lee .env. Todo setting pasa por aquí, nada de os.getenv suelto."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/weberguardian"


settings = Settings()
