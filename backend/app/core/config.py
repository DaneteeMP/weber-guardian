"""Centralized config. Reads .env. All settings go through here, no stray os.getenv."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/weberguardian"
    # Local-only identity mock (X-Dev-User header). Always False in prod:
    # with it off, header identities are ignored and callers get 401.
    dev_auth_enabled: bool = False


settings = Settings()
