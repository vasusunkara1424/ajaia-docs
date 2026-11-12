"""Application settings, loaded from environment variables (or a local .env file)."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Ajaia Docs"
    environment: str = "development"

    # SQLite for local dev; set to a Postgres URL in production.
    database_url: str = "sqlite:///./ajaia_docs.db"

    # Token signing. MUST be overridden in production.
    secret_key: str = "dev-only-insecure-secret-change-me-in-production"
    token_ttl_minutes: int = 60 * 12

    # Upload limits
    max_upload_bytes: int = 2 * 1024 * 1024  # 2 MB
    max_content_bytes: int = 1024 * 1024  # 1 MB of HTML per document

    # Seed demo users on startup (safe to leave on: it is idempotent).
    seed_demo_users: bool = True

    # Where the built frontend lives (served by FastAPI in production).
    frontend_dist: Path = Path(__file__).resolve().parents[3] / "frontend" / "dist"

    # Comma-separated origins allowed in dev (Vite dev server).
    cors_origins: str = "http://localhost:5173"

    @property
    def sqlalchemy_url(self) -> str:
        # Render/Neon hand out postgres:// URLs; SQLAlchemy + psycopg3 needs the explicit driver.
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
