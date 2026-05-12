"""Application configuration module."""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    """Parse a boolean environment variable."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    """Default Flask configuration with production-safe session settings."""

    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")
    TEMPLATES_AUTO_RELOAD = _env_bool("TEMPLATES_AUTO_RELOAD", True)

    ENABLE_PROXY_FIX = _env_bool("ENABLE_PROXY_FIX", True)

    SESSION_COOKIE_NAME = os.environ.get("SESSION_COOKIE_NAME", "visualstruct_session")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE", False)
    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=int(os.environ.get("SESSION_LIFETIME_MINUTES", "240"))
    )
    SESSION_PERMANENT = _env_bool("SESSION_PERMANENT", True)
    SESSION_REFRESH_EACH_REQUEST = _env_bool("SESSION_REFRESH_EACH_REQUEST", True)

    SESSION_TYPE = os.environ.get("SESSION_TYPE", "cachelib")
    SESSION_KEY_PREFIX = os.environ.get("SESSION_KEY_PREFIX", "wved:")
    SESSION_CACHE_DIR = os.environ.get(
        "SESSION_CACHE_DIR",
        str((Path(__file__).resolve().parent.parent / ".flask_session").resolve()),
    )
    SESSION_CACHE_THRESHOLD = int(os.environ.get("SESSION_CACHE_THRESHOLD", "10000"))
    SESSION_CACHE_MODE = int(os.environ.get("SESSION_CACHE_MODE", "384"))
    SESSION_REDIS_URL = os.environ.get("SESSION_REDIS_URL")

    SESSION_MAX_HISTORY = int(os.environ.get("SESSION_MAX_HISTORY", "300"))
