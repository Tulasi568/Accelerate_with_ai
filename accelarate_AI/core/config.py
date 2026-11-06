"""Centralized, environment-driven configuration.

Follows 12-factor config principles: all settings are read from
environment variables (optionally loaded from a local .env file),
never hardcoded. No secrets are logged or embedded in source.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"
STTM_DIR = DATA_DIR / "sttm"
PROFILES_DIR = DATA_DIR / "profiles"
REPORTS_DIR = DATA_DIR / "reports"
TRACES_DIR = DATA_DIR / "traces"

ALL_DATA_DIRS = (
    BRONZE_DIR,
    SILVER_DIR,
    GOLD_DIR,
    STTM_DIR,
    PROFILES_DIR,
    REPORTS_DIR,
    TRACES_DIR,
)


@dataclass(frozen=True)
class Settings:
    """Immutable application settings sourced from environment variables."""

    llm_provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "anthropic"))
    anthropic_api_key: str | None = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    anthropic_model: str = field(
        default_factory=lambda: os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
    )
    llm_max_tokens: int = field(
        default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "4096"))
    )

    def validate(self) -> None:
        """Raise a clear error if required secrets are missing.

        Never includes the secret value itself in the error message.
        """
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is not set. Create a .env file "
                "(see .env.example) with your API key."
            )


def get_settings() -> Settings:
    """Factory returning a fresh Settings instance (re-reads env each call)."""
    return Settings()


def ensure_data_dirs() -> None:
    """Create all required data directories if they do not already exist."""
    for directory in ALL_DATA_DIRS:
        directory.mkdir(parents=True, exist_ok=True)
