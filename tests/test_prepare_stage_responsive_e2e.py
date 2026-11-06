"""Responsive five-stage contract with screenshots of an isolated test app only."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import re
from threading import Thread
from urllib.parse import urlsplit

import pytest
from werkzeug.serving import make_server

from app import create_app
from app.config import Config
from ui_stage_contract import STAGES, assert_stage_contract

pytestmark = pytest.mark.e2e


def _numbered_stages(headings: list[str]) -> list[str]:
    """Apply the existing audit's exact stage-label contract."""
    return [
        re.sub(r"\s+", " ", heading).strip().replace("Mostrar", "").replace("Ocultar", "").strip()
        for heading in headings
        if re.match(r"\s*\d+\s", heading)
    ]


@contextmanager
def _isolated_test_app_url(tmp_path: Path):
    """Serve a fresh test application without reusing user session data."""
    class LocalConfig(Config):
        TESTING = True
        SECRET_KEY = "responsive-heading-test-only"
        SESSION_CACHE_DIR = str(tmp_path / "sessions")

    app = create_app(LocalConfig)
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


@pytest.mark.parametrize("width,height", [(1165, 757), (390, 844)], ids=["desktop", "narrow"])
@pytest.mark.parametrize("name,path,prefix,controls,workspace", [
    ("stack", "/sequential/stack", "seq", ".seq-execute", ".sequential-primary-workspace"),
    ("hash", "/hash/hash_table", "hash", ".hash-execution-controls", ".hash-primary-workspace"),
    ("sorting", "/sorting/visualizador", "sorting", ".sorting-execution-controls", ".sorting-primary-workspace"),
])
def test_prepare_title_and_five_stages_responsive(
    tmp_path: Path, width: int, height: int, name: str, path: str,
    prefix: str, controls: str, workspace: str,
) -> None:
    """Keep exact labels, original stage order and execution controls before views."""
    pw = pytest.importorskip("playwright.sync_api")
    with _isolated_test_app_url(tmp_path) as base, pw.sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": width, "height": height})
            errors: list[str] = []
            external_requests: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))

            def only_test_app(route):
                request_url = urlsplit(route.request.url)
                allowed = urlsplit(base)
                if (request_url.scheme, request_url.netloc) != (allowed.scheme, allowed.netloc):
                    external_requests.append(request_url.netloc)
                    route.abort()
                else:
                    route.continue_()

            page.route("**/*", only_test_app)
            page.goto(base + path, wait_until="networkidle")
            # Capture before assertions, so a broken stage label also has evidence.
            # No account, saved browser context, external page or user data is used.
            artifacts = Path("visual-safe-diagnostics")
            artifacts.mkdir(exist_ok=True)
            page.screenshot(
                path=str(artifacts / f"prepare-stages-{name}-{width}x{height}.png"),
                full_page=True,
                animations="disabled",
            )
            assert not external_requests, external_requests
            assert not errors, errors
            headings = page.locator("main h3, main summary").evaluate_all("""els => els.map(el => {
                const copy = el.cloneNode(true);
                copy.querySelectorAll('small').forEach(node => node.remove());
                return copy.textContent;
            })""")
            assert_stage_contract(_numbered_stages(headings), path)
            title = page.locator(f"#{prefix}-prepare-title")
            assert " ".join(title.text_content().split()) == STAGES[0]
            assert title.is_visible()
            bounds = title.evaluate("""el => {
                const rect = el.getBoundingClientRect();
                return {left: rect.left, right: rect.right, height: rect.height,
                        viewport: innerWidth, scroll: el.scrollWidth, client: el.clientWidth};
            }""")
            assert bounds["height"] > 0 and bounds["left"] >= -1
            assert bounds["right"] <= bounds["viewport"] + 1
            assert bounds["scroll"] <= bounds["client"] + 1, bounds
            assert page.evaluate("""([title, controls, workspace]) => {
                const first = document.querySelector(title);
                const execution = document.querySelector(controls);
                const views = document.querySelector(workspace);
                return Boolean(first && execution && views &&
                    (first.compareDocumentPosition(execution) & Node.DOCUMENT_POSITION_FOLLOWING) &&
                    (execution.compareDocumentPosition(views) & Node.DOCUMENT_POSITION_FOLLOWING));
            }""", [f"#{prefix}-prepare-title", controls, workspace])
        finally:
            browser.close()
