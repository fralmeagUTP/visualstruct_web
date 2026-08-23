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


pytestmark = pytest.mark.e2e


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


def _wait_didactic_mode(page, mode: str, timeout_ms: int = 15000) -> None:
    page.wait_for_function(
        "(expected) => document.documentElement.getAttribute('data-didactic-mode') === expected",
        arg=mode,
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


def test_playwright_global_didactic_switch_visual_default_and_persistence() -> None:
    """Global didactic switch should default to visual and persist across navigation/reload."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/sequential/stack", wait_until="networkidle")

            _wait_didactic_mode(page, "visual")
            assert page.is_checked("#didactic-mode-switch") is False

            hidden_on_visual = page.evaluate(
                "() => {"
                " const blocks = Array.from(document.querySelectorAll('.didactic-technical'));"
                " if (!blocks.length) return false;"
                " return blocks.every((el) => {"
                "   const s = window.getComputedStyle(el);"
                "   return s.maxHeight === '0px' && s.opacity === '0';"
                " });"
                "}",
            )
            assert bool(hidden_on_visual) is True

            initial_url = page.url
            page.check("#didactic-mode-switch")
            _wait_didactic_mode(page, "full")
            assert page.url == initial_url
            page.wait_for_function(
                "() => {"
                " const el = document.querySelector('.didactic-technical');"
                " if (!el) return false;"
                " const s = window.getComputedStyle(el);"
                " return s.maxHeight !== '0px' && s.opacity !== '0';"
                "}",
                timeout=15000,
            )

            visible_on_full = page.evaluate(
                "() => {"
                " const blocks = Array.from(document.querySelectorAll('.didactic-technical'));"
                " if (!blocks.length) return false;"
                " return blocks.every((el) => {"
                "   const s = window.getComputedStyle(el);"
                "   return s.maxHeight !== '0px' && s.opacity !== '0';"
                " });"
                "}",
            )
            assert bool(visible_on_full) is True

            page.goto(f"{base_url}/hash/hash_table", wait_until='networkidle')
            _wait_didactic_mode(page, "full")
            assert page.is_checked("#didactic-mode-switch") is True

            page.reload(wait_until="networkidle")
            _wait_didactic_mode(page, "full")
            assert page.is_checked("#didactic-mode-switch") is True

            browser.close()


def test_playwright_export_controls_hidden_when_page_has_no_visual_target() -> None:
    """Export JPG controls should hide on pages without an exportable visual panel."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(f"{base_url}/", wait_until="networkidle")
            export_hidden = page.evaluate(
                "() => {"
                " const box = document.querySelector('#export-jpg-controls');"
                " if (!box) return false;"
                " return window.getComputedStyle(box).display === 'none';"
                "}",
            )
            assert bool(export_hidden) is True

            page.goto(f"{base_url}/sequential/stack", wait_until="networkidle")
            export_visible = page.evaluate(
                "() => {"
                " const box = document.querySelector('#export-jpg-controls');"
                " if (!box) return false;"
                " return window.getComputedStyle(box).display !== 'none';"
                "}",
            )
            assert bool(export_visible) is True

            browser.close()


def test_playwright_sequential_interpreter_controls_workflow() -> None:
    """Sequential page should support play/pause/step/reset interpreter controls."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/sequential/stack", wait_until="networkidle")
            page.check("#didactic-mode-switch")
            _wait_didactic_mode(page, "full")

            page.fill("#field-value", "21")
            page.uncheck("#seq-step-toggle")
            assert page.is_disabled("#seq-sim-prev") is True
            assert page.is_disabled("#seq-sim-step") is True

            page.check("#seq-step-toggle")
            assert page.is_disabled("#seq-sim-step") is False
            page.click("#seq-sim-play")
            _wait_status_contains(page, "#seq-sim-status", "Simulacion completada")
            visual_text = page.text_content("#visual-state") or ""
            assert "aux (integrado)" not in visual_text

            page.click("#reset-button")
            _wait_status_contains(page, "#seq-sim-status", "Usa Reproducir o Siguiente paso para ejecutar.")

            page.click("#seq-sim-step")
            _wait_status_contains(page, "#seq-sim-counter", "Paso: 1/")

            page.click("#seq-sim-prev")
            _wait_status_contains(page, "#seq-sim-counter", "Paso: 0/")

            browser.close()


def test_playwright_queue_final_view_hides_aux_temporary_node() -> None:
    """Queue simulation final step should show only queue structure without aux temporary block."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/sequential/queue", wait_until="networkidle")
            page.check("#didactic-mode-switch")
            _wait_didactic_mode(page, "full")

            page.select_option("#operation-select", "encolar")
            page.fill("#field-value", "8")
            page.click("#seq-sim-play")
            _wait_status_contains(page, "#seq-sim-status", "Simulacion completada")

            page.fill("#field-value", "6")
            page.click("#seq-sim-play")
            _wait_status_contains(page, "#seq-sim-status", "Simulacion completada")

            visual_text = page.text_content("#visual-state") or ""
            assert "aux (integrado)" not in visual_text

            browser.close()


def test_playwright_hash_interpreter_controls_workflow() -> None:
    """Hash page should support play/pause/step/reset interpreter controls."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/hash/hash_table", wait_until="networkidle")
            page.check("#didactic-mode-switch")
            _wait_didactic_mode(page, "full")

            page.select_option("#hash-operation-select", "insert")
            page.wait_for_selector("#hash-field-key", timeout=5000)
            page.fill("#hash-field-key", "1")
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
            page.check("#didactic-mode-switch")
            _wait_didactic_mode(page, "full")
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


def test_playwright_graph_export_jpg_captures_full_canvas_and_result_block() -> None:
    """Graph JPG export should include full scrollable canvas and algorithm result summary."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(f"{base_url}/graph/graph/construccion", wait_until="networkidle")
            page.check("#didactic-mode-switch")
            _wait_didactic_mode(page, "full")

            for value in [str(v) for v in range(1, 11)]:
                page.select_option("#graph-operation-select", "insert_vertex")
                page.wait_for_selector("#g-op-field-vertex", timeout=5000)
                page.fill("#g-op-field-vertex", value)
                page.click("#graph-sim-play")
                _wait_status_contains(page, "#graph-message-box", "vertice")

            ring_edges = [
                ("1", "2", "4"),
                ("2", "3", "7"),
                ("3", "4", "6"),
                ("4", "5", "3"),
                ("5", "6", "2"),
                ("6", "7", "5"),
                ("7", "8", "8"),
                ("8", "9", "1"),
                ("9", "10", "9"),
                ("10", "1", "10"),
            ]
            extra_edges = [("1", "6", "11"), ("2", "7", "12"), ("3", "8", "13"), ("4", "9", "14")]

            for origin, target, weight in ring_edges + extra_edges:
                page.select_option("#graph-operation-select", "insert_edge")
                page.wait_for_selector("#g-op-field-origin", timeout=5000)
                page.fill("#g-op-field-origin", origin)
                page.fill("#g-op-field-target", target)
                page.fill("#g-op-field-weight", weight)
                page.click("#graph-sim-play")
                _wait_status_contains(page, "#graph-message-box", "arista")

            page.goto(f"{base_url}/graph/graph/expansion-minima", wait_until="networkidle")
            page.uncheck("#graph-step-toggle")
            page.select_option("#graph-algorithm-select", "run_prim")
            page.fill("#g-alg-field-start", "1")
            page.click("#graph-sim-play")
            _wait_status_contains(page, "#graph-sim-status", "Modo rapido")

            result_text = page.text_content("#graph-visual-state") or ""
            assert "MST por Prim" in result_text
            assert "Peso total" in result_text

            export_meta = page.evaluate(
                """
                async () => {
                  const target = document.querySelector('#graph-visual-state');
                  const before = {
                    clientWidth: target.clientWidth,
                    clientHeight: target.clientHeight,
                    scrollWidth: target.scrollWidth,
                    scrollHeight: target.scrollHeight,
                  };
                  const result = await window.InterpreterRuntime.exportVisualStateAsJpg({
                    target,
                    quality: 0.92,
                    scale: 1,
                  });
                  return {
                    before,
                    exported: {
                      width: result.width,
                      height: result.height,
                      scale: result.scale,
                      quality: result.quality,
                      dataPrefix: String(result.dataUrl || '').slice(0, 32),
                      dataLength: String(result.dataUrl || '').length,
                    },
                  };
                }
                """,
            )

            assert int(export_meta["before"]["scrollWidth"]) > int(export_meta["before"]["clientWidth"])
            assert int(export_meta["exported"]["width"]) >= int(export_meta["before"]["scrollWidth"])
            assert int(export_meta["exported"]["height"]) >= int(export_meta["before"]["scrollHeight"])
            assert str(export_meta["exported"]["dataPrefix"]).startswith("data:image/jpeg;base64,")
            assert int(export_meta["exported"]["dataLength"]) > 5000

            browser.close()

