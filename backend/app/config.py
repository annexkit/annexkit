"""Application configuration loaded from environment variables.

Pydantic-settings makes every knob:
    1. Type-checked (wrong types fail at boot, not at runtime).
    2. Documented in one place (this file).
    3. Loadable from `.env` (dev) or real env vars (prod).

Never read `os.environ` directly elsewhere — always go through `settings`.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings."""

    # --- Environment & metadata -------------------------------------------
    env: Literal["dev", "staging", "prod"] = Field(
        default="dev",
        description="Deployment environment. Drives logging and debug behaviour.",
    )
    app_name: str = "AnnexKit API"
    app_version: str = "0.1.0"

    # --- Database ---------------------------------------------------------
    database_url: str = Field(
        default="postgresql+asyncpg://annexkit:dev_password@db:5432/annexkit",
        description="Async SQLAlchemy DSN. Must use the asyncpg driver.",
    )

    # --- Security ---------------------------------------------------------
    # HMAC key used to hash tenant API keys at rest. JWT signing arrives
    # in M4 with SSO; until then this is the only secret that matters.
    secret_key: str = Field(
        default="dev-only-insecure-change-me-in-production",
        description="HMAC key for hashing tenant API keys. 32+ bytes in prod.",
    )

    # --- CORS -------------------------------------------------------------
    cors_origins: list[str] = ["http://localhost:3000"]

    # --- Document storage -------------------------------------------------
    document_storage_path: str = Field(
        default="/data/documents",
        description="Absolute directory for generated Annex IV PDFs.",
    )

    # --- LLM advisor (Mistral La Plateforme — EU-hosted) ------------------
    # The risk classifier is rules-driven and runs without this key. The
    # advisor is only invoked when the deterministic engine flags an
    # ambiguous case — it can suggest, never declassify.
    mistral_api_key: str | None = None
    mistral_embed_model: str = Field(
        default="mistral-embed",
        description="Mistral embedding model. Must return 1024-dim vectors.",
    )
    mistral_chat_model: str = Field(
        default="mistral-small-latest",
        description="Mistral chat model used by the risk advisor.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Use as a FastAPI dependency: `def route(s: Settings = Depends(get_settings))`.
    """
    return Settings()


# Module-level handle for non-dependency contexts (scripts, alembic env, etc.).
# Inside FastAPI routes prefer `Depends(get_settings)` so tests can override.
settings = get_settings()
