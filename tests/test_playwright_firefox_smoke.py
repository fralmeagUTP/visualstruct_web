"""Firefox compatibility smoke coverage for the student-facing modules."""

from __future__ import annotations

import threading
from contextlib import contextmanager

import pytest
from werkzeug.serving import make_server

from app import create_app


pytestmark = pytest.mark.e2e


@contextmanager
def _live_server_url():
    """Serve the Flask application on an ephemeral local port for Firefox."""
    application = create_app()
    application.config.update(TESTING=False, SECRET_KEY="firefox-e2e-secret")
    server = make_server("127.0.0.1", 0, application)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)


@pytest.mark.parametrize(
    "path",
    ["/sequential/stack", "/hierarchical/avl", "/graph/graph/recorridos", "/hash/hash_table", "/sorting/visualizador"],
)
def test_firefox_renders_each_learning_module_and_keyboard_target(path: str) -> None:
    """Firefox must render each primary learning screen and its didactic switch."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as playwright:
            try:
                browser = playwright.firefox.launch(headless=True)
            except Exception as error:  # Browser binaries are an infrastructure dependency.
                pytest.skip(f"Firefox Playwright no disponible: {error}")
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(f"{base_url}{path}", wait_until="networkidle")
            assert page.title()
            assert page.locator("#didactic-mode-switch").is_visible()
            page.locator("#didactic-mode-switch").focus()
            assert page.evaluate("() => document.activeElement?.id") == "didactic-mode-switch"
            browser.close()
