"""Centralized config. Reads .env. All settings go through here, no stray os.getenv."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/weberguardian"


settings = Settings()
