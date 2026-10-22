"""Centralized config. Reads .env. All settings go through here, no stray os.getenv."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/weberguardian"
    # Local-only identity mock (X-Dev-User header). Always False in prod:
    # with it off, header identities are ignored and callers get 401.
    dev_auth_enabled: bool = False

    # Browser origins allowed to call the API, comma-separated. Local dev
    # default; in the demo deploy this is the Vercel URL.
    allowed_origins: str = "http://localhost:5173"

    # Shared gate in front of the demo. Empty (the default) means no gate,
    # which is what local dev and the test suite rely on. Set BOTH values in
    # the hosting environment to require HTTP Basic auth on every route
    # except /health, so the API cannot be read by anyone who finds its URL.
    basic_auth_user: str = ""
    basic_auth_password: str = ""

    @property
    def cors_origins(self) -> list[str]:
        """Parsed origin list, ignoring blanks and stray spaces."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def basic_auth_enabled(self) -> bool:
        return bool(self.basic_auth_user and self.basic_auth_password)


settings = Settings()
