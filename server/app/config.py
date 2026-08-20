"""
SpamGuard AI — Application configuration.

All secrets and environment-specific settings are read from environment
variables / a `.env` file (never hardcoded). See `.env.example` for the full
list of supported variables.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
import os
# server/app/config.py -> server/ directory (2 levels up)
BASE_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Mistral AI ---
    mistral_api_key: str = ""
    mistral_model: str = "mistral-small-latest"
    mistral_base_url: str = "https://api.mistral.ai/v1"
    mistral_timeout_seconds: float = 30.0

    # --- Database ---
    mongodb_uri: str = "mongodb://localhost:27017/spamguard"
    mongodb_db_name: str = "spamguard"

    # --- Server ---
    port: int = int(os.getenv("PORT", "8000"))   
    client_url: str = "http://localhost:5173"
    host: str = "0.0.0.0"

    # --- Uploads ---
    max_file_size_mb: int = 5

    # --- ML ---
    model_dir: str = str(BASE_DIR / "ml" / "saved_models")

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def mistral_enabled(self) -> bool:
        return bool(self.mistral_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
