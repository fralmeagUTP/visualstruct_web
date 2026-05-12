"""Pytest fixtures for Flask app tests."""

from __future__ import annotations

import pytest

from app import create_app


@pytest.fixture()
def app():
    """Create app fixture with test config."""
    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
    )
    return flask_app


@pytest.fixture()
def client(app):
    """Return Flask test client."""
    return app.test_client()
