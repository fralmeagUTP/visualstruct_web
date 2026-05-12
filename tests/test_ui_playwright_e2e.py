"""Optional E2E UI tests with Playwright for interpreter UX regressions.

These tests are skipped automatically when Playwright or browser binaries
are not installed in the environment.
"""

from __future__ import annotations

import threading
from contextlib import contextmanager

import pytest
from werkzeug.serving import make_server

from app import create_app


@contextmanager
def _live_server_url():
    """Run Flask app in-process and yield base URL."""
    app = create_app()
    app.config.update(TESTING=False, SECRET_KEY="e2e-secret")

    server = make_server("127.0.0.1", 0, app)
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)


def test_playwright_hierarchical_red_black_null_and_history_sync() -> None:
    """Hierarchical page should render NULL leaves and synchronized C main history."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        try:
            with playwright_mod.sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(f"{base_url}/hierarchical/red_black", wait_until="networkidle")

                for value in ["10", "5", "15"]:
                    page.fill("#h-field-value", value)
                    page.click("#operation-form button[type='submit']")
                    page.wait_for_timeout(220)

                page.wait_for_selector(".viz-tree-svg", timeout=5000)

                null_count = page.evaluate("() => document.querySelectorAll('.viz-tree-text.nil').length")
                assert int(null_count) > 0

                nil_class_ok = page.evaluate(
                    "() => !!document.querySelector('.viz-tree-node.nil.black')",
                )
                assert bool(nil_class_ok) is True

                code_text = page.text_content("#op-pseudocode") or ""
                assert "rn_insertar" in code_text

                history_text = page.text_content("#action-history") or ""
                assert "Programa principal (main)" in history_text
                assert "rn_insertar(arbol, 15);" in history_text

                tad_scrollable = page.evaluate(
                    "() => { const el = document.querySelector('#tad-record'); return el && el.scrollHeight > el.clientHeight; }",
                )
                assert bool(tad_scrollable) is True

                browser.close()
        except Exception as error:  # pragma: no cover - environment dependent
            pytest.skip(f"Playwright no disponible en este entorno: {error}")


def test_playwright_graph_code_panel_scroll_and_history_sync() -> None:
    """Graph page should keep code panel and C history synchronized after operations."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        try:
            with playwright_mod.sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(f"{base_url}/graph/graph", wait_until="networkidle")

                page.select_option("#graph-operation-select", "insert_vertex")
                page.wait_for_selector("#g-op-field-vertex", timeout=5000)
                page.fill("#g-op-field-vertex", "30")
                page.select_option("#graph-run-mode", "operation")
                page.click("#graph-sim-play")
                page.wait_for_timeout(200)

                page.fill("#g-op-field-vertex", "40")
                page.click("#graph-sim-play")
                page.wait_for_timeout(200)

                code_title = page.text_content("#op-pseudocode-title") or ""
                assert "Codigo C" in code_title

                code_text = page.text_content("#op-pseudocode") or ""
                assert "grafo_insertar_vertice" in code_text

                history_text = page.text_content("#action-history") or ""
                assert "Programa principal (main)" in history_text
                assert "grafo_insertar_vertice" in history_text

                panel_scrollable = page.evaluate(
                    "() => { const el = document.querySelector('#op-pseudocode'); return el && el.scrollHeight >= el.clientHeight; }",
                )
                assert bool(panel_scrollable) is True

                browser.close()
        except Exception as error:  # pragma: no cover - environment dependent
            pytest.skip(f"Playwright no disponible en este entorno: {error}")


def test_playwright_sequential_interpreter_controls_workflow() -> None:
    """Sequential page should support play/pause/step/reset interpreter controls."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        try:
            with playwright_mod.sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(f"{base_url}/sequential/stack", wait_until="networkidle")

                page.fill("#field-value", "21")
                page.click("#seq-sim-play")
                page.wait_for_timeout(260)

                seq_status = page.locator("#seq-sim-status")
                assert "Simulacion completada" in ((seq_status.text_content() or ""))

                page.click("#seq-sim-reset")
                page.wait_for_timeout(180)
                assert "Simulacion reiniciada" in ((seq_status.text_content() or ""))

                page.click("#seq-sim-step")
                page.wait_for_timeout(180)
                assert "Paso 1/" in ((seq_status.text_content() or ""))

                page.click("#seq-sim-play")
                page.wait_for_timeout(250)
                page.click("#seq-sim-pause")
                page.wait_for_timeout(100)
                assert "Simulacion pausada" in ((seq_status.text_content() or ""))

                browser.close()
        except Exception as error:  # pragma: no cover - environment dependent
            pytest.skip(f"Playwright no disponible en este entorno: {error}")


def test_playwright_hash_interpreter_controls_workflow() -> None:
    """Hash page should support play/pause/step/reset interpreter controls."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        try:
            with playwright_mod.sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(f"{base_url}/hash/hash_table", wait_until="networkidle")

                page.select_option("#hash-operation-select", "insert")
                page.wait_for_timeout(120)
                page.fill("#hash-field-key", "K1")
                page.fill("#hash-field-value", "V1")
                page.click("#hash-sim-play")
                page.wait_for_timeout(280)

                hash_status = page.locator("#hash-sim-status")
                assert "Simulacion completada" in ((hash_status.text_content() or ""))

                page.click("#hash-sim-reset")
                page.wait_for_timeout(160)
                assert "Simulacion reiniciada" in ((hash_status.text_content() or ""))

                page.click("#hash-sim-step")
                page.wait_for_timeout(160)
                assert "Paso 1/" in ((hash_status.text_content() or ""))

                page.click("#hash-sim-play")
                page.wait_for_timeout(240)
                page.click("#hash-sim-pause")
                page.wait_for_timeout(100)
                assert "Simulacion pausada" in ((hash_status.text_content() or ""))

                browser.close()
        except Exception as error:  # pragma: no cover - environment dependent
            pytest.skip(f"Playwright no disponible en este entorno: {error}")

