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


def _wait_status_contains(page, selector: str, expected: str, timeout_ms: int = 15000) -> None:
    page.wait_for_function(
        "(args) => (document.querySelector(args.sel)?.textContent || '').includes(args.txt)",
        arg={"sel": selector, "txt": expected},
        timeout=timeout_ms,
    )


def test_playwright_hierarchical_red_black_null_and_history_sync() -> None:
    """Hierarchical page should render NULL leaves and synchronized C main history."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/hierarchical/red_black", wait_until="networkidle")

            for value in ["10", "5", "15"]:
                page.fill("#h-field-value", value)
                page.click("#hier-sim-play")
                _wait_status_contains(page, "#hier-sim-status", "Simulacion completada")

            page.wait_for_selector(".viz-tree-svg", timeout=5000)

            null_count = page.evaluate("() => document.querySelectorAll('.viz-tree-text.nil').length")
            assert int(null_count) > 0

            nil_class_ok = page.evaluate(
                "() => !!document.querySelector('.viz-tree-node.nil.black')",
            )
            assert bool(nil_class_ok) is True

            code_text = page.text_content("#op-pseudocode") or ""
            assert "rbt_insertar" in code_text

            history_text = page.text_content("#action-history") or ""
            assert "Programa principal (main)" in history_text
            assert "rbt_insertar(&arbol, 15);" in history_text

            tad_record_ok = page.evaluate(
                "() => { const el = document.querySelector('#tad-record'); return !!el && (el.textContent || '').trim().length > 20; }",
            )
            assert bool(tad_record_ok) is True

            browser.close()


def test_playwright_graph_code_panel_scroll_and_history_sync() -> None:
    """Graph page should keep code panel and C history synchronized after operations."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/graph/graph", wait_until="networkidle")

            page.select_option("#graph-operation-select", "insert_vertex")
            page.wait_for_selector("#g-op-field-vertex", timeout=5000)
            page.fill("#g-op-field-vertex", "30")
            page.click("#graph-sim-play")
            _wait_status_contains(page, "#graph-message-box", "vertice")

            page.fill("#g-op-field-vertex", "40")
            page.click("#graph-sim-play")
            _wait_status_contains(page, "#graph-message-box", "vertice")

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


def test_playwright_sequential_interpreter_controls_workflow() -> None:
    """Sequential page should support play/pause/step/reset interpreter controls."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/sequential/stack", wait_until="networkidle")

            page.fill("#field-value", "21")
            page.click("#seq-sim-play")
            _wait_status_contains(page, "#seq-sim-status", "Simulacion completada")

            page.click("#reset-button")
            _wait_status_contains(page, "#seq-sim-status", "Usa Reproducir o Siguiente paso para ejecutar.")

            page.click("#seq-sim-step")
            _wait_status_contains(page, "#seq-sim-counter", "Paso: 1/")

            page.click("#seq-sim-prev")
            _wait_status_contains(page, "#seq-sim-counter", "Paso: 0/")

            browser.close()


def test_playwright_hash_interpreter_controls_workflow() -> None:
    """Hash page should support play/pause/step/reset interpreter controls."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/hash/hash_table", wait_until="networkidle")

            page.select_option("#hash-operation-select", "insert")
            page.wait_for_selector("#hash-field-key", timeout=5000)
            page.fill("#hash-field-key", "K1")
            page.fill("#hash-field-value", "V1")
            page.click("#hash-sim-play")
            _wait_status_contains(page, "#hash-sim-status", "Simulacion completada")

            page.click("#hash-reset-button")
            _wait_status_contains(page, "#hash-sim-status", "Usa Reproducir o Siguiente paso para ejecutar.")

            page.click("#hash-sim-step")
            _wait_status_contains(page, "#hash-sim-counter", "Paso: 1/")

            page.click("#hash-sim-prev")
            _wait_status_contains(page, "#hash-sim-counter", "Paso: 0/")

            browser.close()


def test_playwright_graph_fast_mode_executes_algorithms_without_step_trace() -> None:
    """Graph fast mode (step toggle off) must apply final result on algorithm phases."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 1) Build a base graph in construction phase.
            page.goto(f"{base_url}/graph/graph/construccion", wait_until="networkidle")
            for value in ["1", "2", "3", "4"]:
                page.select_option("#graph-operation-select", "insert_vertex")
                page.wait_for_selector("#g-op-field-vertex", timeout=5000)
                page.fill("#g-op-field-vertex", value)
                page.click("#graph-sim-play")
                _wait_status_contains(page, "#graph-message-box", "vertice")

            for origin, target, weight in [("1", "2", "3"), ("2", "3", "2"), ("3", "4", "4"), ("1", "4", "15")]:
                page.select_option("#graph-operation-select", "insert_edge")
                page.wait_for_selector("#g-op-field-origin", timeout=5000)
                page.fill("#g-op-field-origin", origin)
                page.fill("#g-op-field-target", target)
                page.fill("#g-op-field-weight", weight)
                page.click("#graph-sim-play")
                _wait_status_contains(page, "#graph-message-box", "arista")

            # 2) Traversals phase (BFS) in fast mode.
            page.goto(f"{base_url}/graph/graph/recorridos", wait_until="networkidle")
            page.uncheck("#graph-step-toggle")
            page.select_option("#graph-algorithm-select", "run_bfs")
            page.fill("#g-alg-field-start", "1")
            page.click("#graph-sim-play")
            _wait_status_contains(page, "#graph-sim-status", "Modo rapido")
            _wait_status_contains(page, "#graph-message-box", "BFS")
            result_text = page.text_content("#graph-visual-state") or ""
            assert ("Recorrido" in result_text) or ("BFS" in result_text)

            # 3) Shortest path phase (Dijkstra) in fast mode.
            page.goto(f"{base_url}/graph/graph/camino-minimo", wait_until="networkidle")
            page.uncheck("#graph-step-toggle")
            page.select_option("#graph-algorithm-select", "run_dijkstra")
            page.fill("#g-alg-field-start", "1")
            page.fill("#g-alg-field-end", "4")
            page.click("#graph-sim-play")
            _wait_status_contains(page, "#graph-sim-status", "Modo rapido")
            _wait_status_contains(page, "#graph-message-box", "Dijkstra")

            # 4) MST phase (Prim) in fast mode.
            page.goto(f"{base_url}/graph/graph/expansion-minima", wait_until="networkidle")
            page.uncheck("#graph-step-toggle")
            page.select_option("#graph-algorithm-select", "run_prim")
            page.fill("#g-alg-field-start", "1")
            page.click("#graph-sim-play")
            _wait_status_contains(page, "#graph-sim-status", "Modo rapido")
            _wait_status_contains(page, "#graph-message-box", "Prim")

            browser.close()

