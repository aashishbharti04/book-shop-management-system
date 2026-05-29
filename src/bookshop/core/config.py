"""Application configuration.

Settings are read once from the environment (with a ``.env`` file loaded if
present) into an immutable :class:`Settings` object. No credentials are ever
hard-coded in source — everything comes from the environment, falling back to a
zero-config local SQLite database so the app runs out of the box.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Load variables from a project-level .env file if one exists. Real environment
# variables always take precedence (override=False).
load_dotenv(override=False)

_TRUTHY = {"1", "true", "yes", "on"}
_VALID_THEMES = {"dark", "light", "system"}
_VALID_FONT_SCALES = {"small", "medium", "large"}


def project_root() -> Path:
    """Return the repository/project root directory.

    ``config.py`` lives at ``<root>/src/bookshop/core/config.py``; the root is
    therefore three parents up from the package directory.
    """

    return Path(__file__).resolve().parents[3]


def _default_database_url() -> str:
    db_path = (project_root() / "bookshop.db").as_posix()
    return f"sqlite:///{db_path}"


def _normalize_choice(value: str, valid: set[str], fallback: str) -> str:
    value = value.strip().lower()
    return value if value in valid else fallback


@dataclass(frozen=True, slots=True)
class Settings:
    """Immutable application settings."""

    app_name: str = "Book Shop Management"
    org_name: str = "BookShopOSS"
    database_url: str = ""
    log_level: str = "INFO"
    default_theme: str = "dark"
    font_scale: str = "medium"
    reduced_motion: bool = False
    currency_symbol: str = "$"
    low_stock_threshold: int = 5

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Build (and cache) settings from the current environment."""

    return Settings(
        app_name=os.getenv("APP_NAME", "Book Shop Management"),
        org_name=os.getenv("ORG_NAME", "BookShopOSS"),
        database_url=os.getenv("DATABASE_URL", "").strip() or _default_database_url(),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
        default_theme=_normalize_choice(os.getenv("BOOKSHOP_THEME", "dark"), _VALID_THEMES, "dark"),
        font_scale=_normalize_choice(
            os.getenv("BOOKSHOP_FONT_SCALE", "medium"), _VALID_FONT_SCALES, "medium"
        ),
        reduced_motion=os.getenv("BOOKSHOP_REDUCED_MOTION", "0").strip().lower() in _TRUTHY,
        currency_symbol=os.getenv("BOOKSHOP_CURRENCY", "$").strip() or "$",
        low_stock_threshold=_safe_int(os.getenv("BOOKSHOP_LOW_STOCK_THRESHOLD"), 5),
    )


def _safe_int(value: str | None, fallback: int) -> int:
    try:
        return int(value) if value is not None and value.strip() else fallback
    except ValueError:
        return fallback
