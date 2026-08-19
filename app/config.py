"""Application configuration module."""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path
from typing import Any, Mapping


VALID_APP_ENVS = frozenset({"development", "testing", "production"})
DEVELOPMENT_SECRET_KEY = "dev-secret-key-change-me"


class ConfigurationError(ValueError):
    """Raised when application configuration is unsafe or inconsistent."""


def _env_bool(name: str, default: bool) -> bool:
    """Parse a boolean environment variable."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_optional_int(name: str) -> int | None:
    """Parse an optional integer while preserving whether it was configured."""
    raw = os.environ.get(name)
    return None if raw is None or not raw.strip() else int(raw)


class Config:
    """Default Flask configuration with production-safe session settings."""

    APP_ENV = os.environ.get("APP_ENV", "development").strip().lower()
    FLASK_HOST = os.environ.get("FLASK_HOST", "127.0.0.1").strip()
    FLASK_PORT = int(os.environ.get("FLASK_PORT", "5050"))

    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", DEVELOPMENT_SECRET_KEY)
    TEMPLATES_AUTO_RELOAD = _env_bool("TEMPLATES_AUTO_RELOAD", True)

    ENABLE_PROXY_FIX = _env_bool("ENABLE_PROXY_FIX", False)
    TRUSTED_PROXY_COUNT = _env_optional_int("TRUSTED_PROXY_COUNT")

    SESSION_COOKIE_NAME = os.environ.get("SESSION_COOKIE_NAME", "visualstruct_session")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE", False)
    ALLOW_INSECURE_COOKIES_IN_PRODUCTION = _env_bool(
        "ALLOW_INSECURE_COOKIES_IN_PRODUCTION", False
    )
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

    # Checkpoints remain opt-in until every adapter supports state import/export.
    ENABLE_CHECKPOINTS = _env_bool("ENABLE_CHECKPOINTS", False)
    CHECKPOINT_INTERVAL = int(os.environ.get("CHECKPOINT_INTERVAL", "50"))
    CHECKPOINT_MAX_PER_STRUCTURE = int(
        os.environ.get("CHECKPOINT_MAX_PER_STRUCTURE", "1")
    )


def validate_configuration(config: Mapping[str, Any]) -> None:
    """Validate environment-independent and production-mode invariants."""
    app_env = config.get("APP_ENV")
    if app_env not in VALID_APP_ENVS:
        allowed = ", ".join(sorted(VALID_APP_ENVS))
        raise ConfigurationError(f"APP_ENV debe ser uno de: {allowed}.")

    host = config.get("FLASK_HOST")
    if not isinstance(host, str) or not host.strip():
        raise ConfigurationError("FLASK_HOST no puede estar vacio.")
    port = config.get("FLASK_PORT")
    if type(port) is not int or not 1 <= port <= 65535:
        raise ConfigurationError("FLASK_PORT debe ser un entero entre 1 y 65535.")

    session_type = str(config.get("SESSION_TYPE", "")).lower()
    if session_type not in {"cachelib", "redis"}:
        raise ConfigurationError("SESSION_TYPE debe ser 'cachelib' o 'redis'.")

    enable_proxy_fix = config.get("ENABLE_PROXY_FIX")
    trusted_proxy_count = config.get("TRUSTED_PROXY_COUNT")
    if type(enable_proxy_fix) is not bool:
        raise ConfigurationError("ENABLE_PROXY_FIX debe ser un valor booleano.")
    if trusted_proxy_count is not None and (
        type(trusted_proxy_count) is not int or trusted_proxy_count <= 0
    ):
        raise ConfigurationError("TRUSTED_PROXY_COUNT debe ser un entero mayor que cero.")
    if enable_proxy_fix and trusted_proxy_count is None:
        raise ConfigurationError(
            "TRUSTED_PROXY_COUNT debe configurarse cuando ENABLE_PROXY_FIX=true."
        )
    same_site = config.get("SESSION_COOKIE_SAMESITE")
    if same_site not in {"Lax", "Strict", "None"}:
        raise ConfigurationError(
            "SESSION_COOKIE_SAMESITE debe ser 'Lax', 'Strict' o 'None'."
        )
    cookie_secure = config.get("SESSION_COOKIE_SECURE")
    insecure_cookie_override = config.get("ALLOW_INSECURE_COOKIES_IN_PRODUCTION", False)
    if type(cookie_secure) is not bool:
        raise ConfigurationError("SESSION_COOKIE_SECURE debe ser un valor booleano.")
    if type(insecure_cookie_override) is not bool:
        raise ConfigurationError(
            "ALLOW_INSECURE_COOKIES_IN_PRODUCTION debe ser un valor booleano."
        )

    lifetime = config.get("PERMANENT_SESSION_LIFETIME")
    if not isinstance(lifetime, timedelta) or lifetime.total_seconds() <= 0:
        raise ConfigurationError("SESSION_LIFETIME_MINUTES debe ser mayor que cero.")
    max_history = config.get("SESSION_MAX_HISTORY")
    if type(max_history) is not int or max_history <= 0:
        raise ConfigurationError("SESSION_MAX_HISTORY debe ser un entero mayor que cero.")

    if app_env == "production" and (
        bool(config.get("DEBUG")) or bool(config.get("TESTING"))
    ):
        raise ConfigurationError(
            "DEBUG y TESTING deben estar desactivados cuando APP_ENV=production."
        )
    if app_env == "production":
        secret_key = config.get("SECRET_KEY")
        if (
            not isinstance(secret_key, str)
            or not secret_key.strip()
            or secret_key == DEVELOPMENT_SECRET_KEY
        ):
            raise ConfigurationError(
                "FLASK_SECRET_KEY debe configurarse con un secreto propio en produccion."
            )
        if not cookie_secure and not insecure_cookie_override:
            raise ConfigurationError(
                "SESSION_COOKIE_SECURE debe ser true en produccion; "
                "solo entornos HTTP controlados pueden usar "
                "ALLOW_INSECURE_COOKIES_IN_PRODUCTION=true."
            )
