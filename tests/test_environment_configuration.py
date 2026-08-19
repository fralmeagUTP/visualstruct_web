"""Validation tests for APP_ENV and common application settings."""

from __future__ import annotations

from datetime import timedelta

import pytest

from app import create_app
from app.config import Config, ConfigurationError, validate_configuration


def _valid_config(**overrides):
    config = {
        "APP_ENV": "development",
        "SECRET_KEY": "a-production-secret-with-enough-entropy",
        "FLASK_HOST": "127.0.0.1",
        "FLASK_PORT": 5050,
        "SESSION_TYPE": "cachelib",
        "ENABLE_PROXY_FIX": False,
        "TRUSTED_PROXY_COUNT": None,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": True,
        "ALLOW_INSECURE_COOKIES_IN_PRODUCTION": False,
        "PERMANENT_SESSION_LIFETIME": timedelta(minutes=240),
        "SESSION_MAX_HISTORY": 300,
        "DEBUG": False,
        "TESTING": False,
    }
    config.update(overrides)
    return config


def test_default_environment_and_server_address_are_explicit() -> None:
    assert Config.APP_ENV == "development"
    assert Config.FLASK_HOST == "127.0.0.1"
    assert Config.FLASK_PORT == 5050
    validate_configuration(_valid_config())


@pytest.mark.parametrize("app_env", ["development", "testing", "production"])
def test_supported_application_environments(app_env: str) -> None:
    validate_configuration(_valid_config(APP_ENV=app_env))


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"APP_ENV": "staging"}, "APP_ENV"),
        ({"FLASK_HOST": "  "}, "FLASK_HOST"),
        ({"FLASK_PORT": 0}, "FLASK_PORT"),
        ({"FLASK_PORT": True}, "FLASK_PORT"),
        ({"SESSION_TYPE": "filesystem"}, "SESSION_TYPE"),
        ({"ENABLE_PROXY_FIX": "false"}, "ENABLE_PROXY_FIX"),
        ({"TRUSTED_PROXY_COUNT": 0}, "TRUSTED_PROXY_COUNT"),
        ({"SESSION_COOKIE_SAMESITE": "invalid"}, "SESSION_COOKIE_SAMESITE"),
        ({"SESSION_COOKIE_SECURE": "true"}, "SESSION_COOKIE_SECURE"),
        (
            {"ALLOW_INSECURE_COOKIES_IN_PRODUCTION": "false"},
            "ALLOW_INSECURE_COOKIES_IN_PRODUCTION",
        ),
        ({"PERMANENT_SESSION_LIFETIME": timedelta(0)}, "SESSION_LIFETIME_MINUTES"),
        ({"SESSION_MAX_HISTORY": 0}, "SESSION_MAX_HISTORY"),
    ],
)
def test_common_configuration_rejects_invalid_values(override, message: str) -> None:
    with pytest.raises(ConfigurationError, match=message):
        validate_configuration(_valid_config(**override))


@pytest.mark.parametrize("unsafe_flag", ["DEBUG", "TESTING"])
def test_production_rejects_debug_and_testing_modes(unsafe_flag: str) -> None:
    with pytest.raises(ConfigurationError, match="deben estar desactivados"):
        validate_configuration(
            _valid_config(APP_ENV="production", **{unsafe_flag: True})
        )


def test_application_factory_registers_validated_environment() -> None:
    class _TestingConfig(Config):
        APP_ENV = "testing"
        TESTING = True

    app = create_app(_TestingConfig)
    assert app.config["APP_ENV"] == "testing"
    assert app.config["TESTING"] is True


@pytest.mark.parametrize("secret", [None, "", "dev-secret-key-change-me"])
def test_production_rejects_missing_or_development_secret(secret) -> None:
    with pytest.raises(ConfigurationError, match="FLASK_SECRET_KEY") as captured:
        validate_configuration(_valid_config(APP_ENV="production", SECRET_KEY=secret))
    if secret:
        assert str(secret) not in str(captured.value)


def test_production_rejects_insecure_cookie_without_explicit_override() -> None:
    with pytest.raises(ConfigurationError, match="SESSION_COOKIE_SECURE"):
        validate_configuration(
            _valid_config(APP_ENV="production", SESSION_COOKIE_SECURE=False)
        )


def test_production_allows_documented_insecure_cookie_override() -> None:
    validate_configuration(
        _valid_config(
            APP_ENV="production",
            SESSION_COOKIE_SECURE=False,
            ALLOW_INSECURE_COOKIES_IN_PRODUCTION=True,
        )
    )


def test_development_default_logs_warning_without_secret_value(caplog) -> None:
    class _DevelopmentConfig(Config):
        APP_ENV = "development"
        SECRET_KEY = "dev-secret-key-change-me"

    create_app(_DevelopmentConfig)
    assert "Configure FLASK_SECRET_KEY" in caplog.text
    assert "dev-secret-key-change-me" not in caplog.text


def test_proxy_fix_requires_explicit_positive_trust_count() -> None:
    with pytest.raises(ConfigurationError, match="TRUSTED_PROXY_COUNT"):
        validate_configuration(_valid_config(ENABLE_PROXY_FIX=True))
    validate_configuration(
        _valid_config(ENABLE_PROXY_FIX=True, TRUSTED_PROXY_COUNT=1)
    )


def test_proxy_fix_uses_exact_configured_hop_count() -> None:
    class _ProxyConfig(Config):
        TESTING = True
        ENABLE_PROXY_FIX = True
        TRUSTED_PROXY_COUNT = 2

    app = create_app(_ProxyConfig)
    response = app.test_client().get(
        "/healthz",
        headers={
            "X-Forwarded-For": "198.51.100.10, 10.0.0.2",
            "X-Forwarded-Proto": "https, http",
            "X-Forwarded-Host": "public.example, internal.local",
            "X-Forwarded-Port": "443, 8080",
        },
    )
    assert response.status_code == 200
    assert app.wsgi_app.x_for == 2
    assert app.wsgi_app.x_proto == 2
    assert app.wsgi_app.x_host == 2
    assert app.wsgi_app.x_port == 2
