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

            page.once("dialog", lambda dialog: dialog.accept())
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


def test_playwright_graph_guided_level_and_mobile_context() -> None:
    """Guided graph examples and presentation changes preserve the trace context."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            page=browser.new_page(viewport={"width":1280,"height":900})
            page.goto(f"{base_url}/graph/graph/recorridos",wait_until="networkidle")
            page.check("#didactic-mode-switch")
            _wait_didactic_mode(page,"full")
            page.select_option("#graph-guided-example","single")
            page.click("#graph-load-example")
            page.wait_for_function("() => (document.querySelector('#graph-visual-state')?.textContent || '').includes('1')")
            assert page.input_value("#graph-algorithm-select")=="run_bfs"
            assert page.input_value("#g-alg-field-start")=="1"
            page.click("#graph-sim-step")
            _wait_status_contains(page,"#graph-sim-counter","Paso: 1/")
            cursor=page.text_content("#graph-sim-counter")
            page.select_option("#graph-learning-level","advanced")
            assert page.text_content("#graph-sim-counter")==cursor
            assert "función" in (page.text_content("#graph-pedagogy-summary") or "").lower()
            page.set_viewport_size({"width":390,"height":844})
            page.click('[data-graph-tab="code"]')
            assert page.is_visible("#graph-code-region")
            page.click('[data-graph-tab="visual"]')
            assert page.is_visible("#graph-visual-region")
            assert page.text_content("#graph-sim-counter")==cursor
            browser.close()


def test_playwright_graph_mst_practice_comparison_keyboard_and_responsive() -> None:
    """Graph active-learning controls stay synchronized across interaction modes."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
            page.goto(f"{base_url}/graph/graph/expansion-minima", wait_until="networkidle")
            page.check("#didactic-mode-switch")
            _wait_didactic_mode(page, "full")
            page.select_option("#graph-guided-example", "equal-mst")
            page.click("#graph-load-example")
            page.wait_for_function("() => (document.querySelector('#graph-visual-state')?.textContent || '').includes('4')")
            page.check("#graph-practice-mode")
            page.click("#graph-sim-step")
            page.wait_for_selector("#graph-practice-cover:not([hidden])")
            page.click("#graph-skip-prediction")
            assert page.locator("#graph-practice-cover").is_hidden()
            page.keyboard.press("Alt+ArrowRight")
            _wait_status_contains(page, "#graph-sim-counter", "Paso: 2/")
            page.select_option("#graph-compare-kind", "prim-kruskal")
            page.click("#graph-compare-run")
            page.wait_for_selector(".hier-compare-card")
            assert page.locator(".hier-compare-card").count() == 2
            assert "Entrada inmutable" in (page.text_content("#graph-compare-input") or "")
            page.set_viewport_size({"width": 390, "height": 844})
            assert page.is_visible("#graph-compare-grid")
            assert page.get_attribute("#graph-export-summary", "aria-label")
            browser.close()


def test_playwright_hierarchical_guided_level_and_mobile_context() -> None:
    """Guided AVL case and level changes must retain the canonical trace cursor."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(f"{base_url}/hierarchical/avl", wait_until="networkidle")
            page.check("#didactic-mode-switch")
            _wait_didactic_mode(page, "full")
            page.select_option("#hier-guided-example", "ll")
            page.click("#hier-load-example")
            page.wait_for_function("() => (document.querySelector('#visual-state')?.textContent || '').includes('30')")
            assert page.input_value("#operation-select") == "insertar"
            assert page.input_value("#h-field-value") == "10"
            page.click("#hier-sim-step")
            _wait_status_contains(page, "#hier-sim-counter", "Paso: 1/")
            cursor = page.text_content("#hier-sim-counter")
            page.select_option("#hier-learning-level", "advanced")
            assert page.text_content("#hier-sim-counter") == cursor
            assert "funci" in (page.text_content("#hier-pedagogy-summary") or "").lower()
            page.set_viewport_size({"width": 390, "height": 844})
            page.click('[data-hier-tab="code"]')
            assert page.is_visible("#hier-code-region") is True
            page.click('[data-hier-tab="visual"]')
            assert page.is_visible("#hier-visual-region") is True
            assert page.text_content("#hier-sim-counter") == cursor
            browser.close()


def test_playwright_hierarchical_comparison_practice_keyboard_and_accessibility() -> None:
    """Comparison, concealed practice and keyboard navigation remain synchronized."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
            page.goto(f"{base_url}/hierarchical/avl", wait_until="networkidle")
            page.check("#didactic-mode-switch")
            _wait_didactic_mode(page, "full")
            page.fill("#hier-compare-values", "10, 20, 30, 40, 50")
            page.select_option("#hier-compare-kind", "abb-avl")
            page.click("#hier-compare-run")
            page.wait_for_selector(".hier-compare-card")
            assert "Entrada inmutable" in (page.text_content("#hier-compare-input") or "")
            assert "rotaciones" in (page.text_content("#hier-compare-conclusion") or "")
            assert page.locator(".hier-compare-card").count() == 2
            page.fill("#h-field-value", "25")
            page.check("#hier-practice-mode")
            page.click("#hier-prepare")
            page.click("#hier-sim-step")
            assert page.locator("#visual-state").evaluate("el => el.classList.contains('hier-practice-hidden')")
            page.click("#hier-skip-prediction")
            assert not page.locator("#visual-state").evaluate("el => el.classList.contains('hier-practice-hidden')")
            before=page.text_content("#hier-sim-counter")
            page.locator("body").press("ArrowRight")
            assert page.text_content("#hier-sim-counter") != before
            page.locator("body").press("Home")
            assert "Paso: 0/" in (page.text_content("#hier-sim-counter") or "")
            assert page.input_value("#hier-speed-slider") == "-2"
            browser.close()


def test_playwright_sequential_level_and_guided_example_preserve_trace() -> None:
    """Changing explanation level keeps the same cursor and guided LIFO state."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/sequential/stack", wait_until="networkidle")
            page.check("#didactic-mode-switch")
            _wait_didactic_mode(page, "full")
            page.select_option("#seq-guided-example", "lifo")
            page.click("#seq-load-example")
            page.wait_for_function("() => (document.querySelector('#visual-state')?.textContent || '').includes('30')")
            assert "último insertado" in (page.text_content("#seq-example-lesson") or "")
            assert "30" in (page.text_content("#visual-state") or "")
            assert page.input_value("#operation-select") == "desapilar"
            page.click("#seq-sim-step")
            _wait_status_contains(page, "#seq-sim-counter", "Paso: 1/")
            cursor_before = page.text_content("#seq-sim-counter")
            page.select_option("#seq-learning-level", "advanced")
            assert page.text_content("#seq-sim-counter") == cursor_before
            assert "Semántica C" in (page.text_content("#seq-pedagogy-summary") or "")
            browser.close()


def test_playwright_sequential_prediction_progress_and_navigation() -> None:
    """Practice mode predicts a real frame and exposes complete navigation."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/sequential/stack", wait_until="networkidle")
            page.check("#didactic-mode-switch")
            _wait_didactic_mode(page, "full")
            page.fill("#field-value", "17")
            page.check("#seq-practice-mode")
            page.click("#seq-sim-prepare")
            _wait_status_contains(page, "#seq-sim-status", "Traza preparada")
            assert page.is_disabled("#seq-progress-slider") is False
            for _index in range(12):
                page.click("#seq-sim-step")
                if page.is_visible("#seq-prediction-panel"):
                    break
            assert page.is_visible("#seq-prediction-panel") is True
            page.click("#seq-prediction-hint")
            assert (page.text_content("#seq-prediction-feedback") or "").strip()
            page.click("#seq-prediction-choices button")
            page.wait_for_function("() => (document.querySelector('#seq-concept-progress')?.textContent || '').includes('/1')")
            assert page.is_visible(".seq-semantic-strip") is True
            page.click("#seq-sim-end")
            page.wait_for_function("() => document.querySelector('#seq-progress-slider').value === document.querySelector('#seq-progress-slider').max")
            page.click("#seq-sim-start")
            assert page.input_value("#seq-progress-slider") == "0"
            browser.close()


def test_playwright_sequential_comparison_keyboard_and_responsive_accessibility() -> None:
    """Comparison remains isolated/readable and keyboard navigation works on mobile."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 390, "height": 844})
            page.goto(f"{base_url}/sequential/queue", wait_until="networkidle")
            page.check("#didactic-mode-switch")
            _wait_didactic_mode(page, "full")
            page.select_option("#seq-compare-kind", "queue-priority")
            page.click("#seq-compare-run")
            assert page.locator(".seq-compare-card").count() == 2
            assert "conserva llegada" in (page.text_content("#seq-compare-conclusion") or "")
            page.fill("#field-value", "8")
            page.click("#seq-sim-prepare")
            _wait_status_contains(page, "#seq-sim-status", "Traza preparada")
            page.keyboard.press("Alt+ArrowRight")
            _wait_status_contains(page, "#seq-sim-counter", "Paso: 1/")
            page.keyboard.press("Alt+Home")
            assert page.input_value("#seq-progress-slider") == "0"
            assert page.get_attribute("#seq-export-image", "aria-label")
            columns = page.evaluate("() => getComputedStyle(document.querySelector('#seq-compare-grid')).gridTemplateColumns.split(' ').length")
            assert int(columns) == 1
            browser.close()


def test_playwright_sorting_all_algorithms_and_playback_controls() -> None:
    """Every sorting option should render its C and reach the expected visual state."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    algorithms = [
        "intercambio", "seleccion", "insercion", "burbuja", "shell", "quicksort",
        "mergesort", "heapsort", "counting_sort", "binsort", "radixsort",
    ]

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/sorting/visualizador", wait_until="networkidle")
            page.fill("#sorting-manual-values", "5,-1,3,3,0")
            page.click("#sorting-create-array")
            _wait_status_contains(page, "#sorting-message-box", "Arreglo creado")
            page.evaluate("() => { const el = document.querySelector('#sorting-step-toggle'); el.checked = false; el.dispatchEvent(new Event('change', {bubbles: true})); }")

            for algorithm in algorithms:
                page.select_option("#sorting-algorithm", algorithm)
                page.click("#sorting-sim-play")
                _wait_status_contains(page, "#sorting-sim-status", "Modo rapido")
                labels = page.locator(".sorting-item-label").all_text_contents()
                assert [int(label.split("]", 1)[1].strip()) for label in labels] == [-1, 0, 3, 3, 5]
                code = page.text_content("#sorting-code") or ""
                assert f"ordenar_{algorithm}" in code

            page.evaluate("() => { const el = document.querySelector('#sorting-step-toggle'); el.checked = true; el.dispatchEvent(new Event('change', {bubbles: true})); }")
            page.select_option("#sorting-algorithm", "quicksort")
            page.click("#sorting-sim-play")
            _wait_status_contains(page, "#sorting-sim-status", "Simulacion completada", timeout_ms=30000)
            completed_counter = page.text_content("#sorting-sim-counter") or ""
            page.evaluate("() => document.querySelector('#sorting-sim-prev').click()")
            page.wait_for_function("(completed) => (document.querySelector('#sorting-sim-counter')?.textContent || '') !== completed", arg=completed_counter)
            counter_after_previous = page.text_content("#sorting-sim-counter") or ""
            page.evaluate("() => document.querySelector('#sorting-sim-step').click()")
            page.wait_for_function("(previous) => (document.querySelector('#sorting-sim-counter')?.textContent || '') !== previous", arg=counter_after_previous)
            counter_after_next = page.text_content("#sorting-sim-counter") or ""
            assert counter_after_previous != counter_after_next
            browser.close()


def test_playwright_sorting_level_preserves_cursor_and_guided_examples() -> None:
    """Changing presentation level must not mutate the canonical execution."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(f"{base_url}/sorting/visualizador", wait_until="networkidle")
            page.select_option("#sorting-guided-example", "duplicates")
            page.click("#sorting-load-example")
            _wait_status_contains(page, "#sorting-message-box", "Arreglo creado")
            assert page.input_value("#sorting-manual-values") == "4, 2, 4, 1, 2, 4, 1"
            page.click("#sorting-sim-play")
            _wait_status_contains(page, "#sorting-sim-status", "Simulacion completada", timeout_ms=30000)
            page.evaluate("() => document.querySelector('#sorting-sim-prev').click()")
            page.wait_for_timeout(100)
            before = page.text_content("#sorting-sim-counter")
            page.select_option("#sorting-learning-level", "advanced")
            after = page.text_content("#sorting-sim-counter")
            assert after == before
            assert "Línea C" in (page.text_content("#sorting-pedagogy-narration") or "")
            assert (page.text_content("#sorting-call-stack") or "").strip()
            assert (page.text_content("#sorting-variable-table") or "").strip()
            assert page.locator("#sorting-code-region").is_visible()
            browser.close()


def test_playwright_sorting_specific_strategy_views_and_zero_axis() -> None:
    """Representative algorithm families must expose distinct visual strategies."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(f"{base_url}/sorting/visualizador", wait_until="networkidle")
            page.fill("#sorting-manual-values", "5,-3,0,2,1")
            page.click("#sorting-create-array")
            _wait_status_contains(page, "#sorting-message-box", "Arreglo creado")
            assert page.locator(".sorting-zero-axis").count() == 5
            assert page.locator(".sorting-item-bar.is-negative").count() == 1
            assert page.locator(".sorting-item-bar.is-zero").count() == 1
            page.evaluate("() => { const el = document.querySelector('#sorting-step-toggle'); el.checked = false; el.dispatchEvent(new Event('change', {bubbles: true})); }")
            expected = {
                "seleccion": "Mínimo provisional",
                "insercion": "Clave:",
                "burbuja": "Frontera:",
                "shell": "Intervalo (gap)",
                "quicksort": "Subproblema activo",
                "mergesort": "División/fusión activa",
                "heapsort": "hijos:",
                "counting_sort": "Frecuencias",
                "binsort": "Urnas",
                "radixsort": "Dígito activo",
            }
            for algorithm, marker in expected.items():
                page.select_option("#sorting-algorithm", algorithm)
                page.click("#sorting-sim-play")
                _wait_status_contains(page, "#sorting-sim-status", "Modo rapido")
                assert marker in (page.text_content("#sorting-strategy-view") or "")
            browser.close()


def test_playwright_sorting_navigable_player_and_theory_analysis() -> None:
    """The player must seek reversibly while theory remains separate from metrics."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(f"{base_url}/sorting/visualizador", wait_until="networkidle")
            page.fill("#sorting-manual-values", "4,1,3,2")
            page.click("#sorting-create-array")
            _wait_status_contains(page, "#sorting-message-box", "Arreglo creado")
            page.click("#sorting-sim-prepare")
            _wait_status_contains(page, "#sorting-sim-status", "Simulacion lista")
            total = int(page.get_attribute("#sorting-progress", "max") or "0")
            assert total > 2
            page.click("#sorting-sim-step")
            assert "Paso: 1/" in (page.text_content("#sorting-sim-counter") or "")
            before_tab = page.text_content("#sorting-sim-counter")
            page.set_viewport_size({"width": 760, "height": 900})
            page.click('[data-sorting-tab="code"]')
            assert page.text_content("#sorting-sim-counter") == before_tab
            page.locator("#sorting-progress").fill(str(total))
            assert f"Paso: {total}/{total}" == (page.text_content("#sorting-sim-counter") or "")
            assert (page.text_content("#sorting-invariant-text") or "").strip()
            theory = page.text_content("#sorting-theory-profile") or ""
            observed = page.text_content("#sorting-observed-metrics") or ""
            assert "Mejor" in theory and "Memoria" in theory and "Estable" in theory
            assert "Comparaciones" in observed and "Intercambios" in observed
            page.click("#sorting-restart-execution")
            assert "Paso: 0/" in (page.text_content("#sorting-sim-counter") or "")
            assert page.input_value("#sorting-manual-values") == "4,1,3,2"
            browser.close()


def test_playwright_sorting_practice_and_comparator() -> None:
    """Practice feedback and comparison must use the canonical immutable input."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(f"{base_url}/sorting/visualizador", wait_until="networkidle")
            page.fill("#sorting-manual-values", "4,1,3,2")
            page.click("#sorting-create-array")
            page.check("#sorting-practice-mode")
            page.click("#sorting-sim-prepare")
            _wait_status_contains(page, "#sorting-sim-status", "Simulacion lista")
            page.click("#sorting-sim-step")
            assert page.locator("#sorting-prediction-card").is_visible()
            assert "resultado permanece oculto" in (page.text_content("#sorting-prediction-feedback") or "")
            page.click('[data-prediction="true"]')
            assert "1 intentos" in (page.text_content("#sorting-concept-progress") or "")
            page.click("#sorting-progress-reset")
            assert "0 intentos" in (page.text_content("#sorting-concept-progress") or "")
            page.select_option("#sorting-compare-left", "burbuja")
            page.select_option("#sorting-compare-right", "insercion")
            page.click("#sorting-compare-run")
            page.wait_for_function("() => !document.querySelector('#sorting-compare-progress')?.disabled")
            assert "[4, 1, 3, 2]" in (page.text_content("#sorting-compare-input") or "")
            assert "Observado:" in (page.text_content("#sorting-compare-left-analysis") or "")
            assert "Teoría:" in (page.text_content("#sorting-compare-right-analysis") or "")
            page.select_option("#sorting-compare-sync", "concept")
            page.locator("#sorting-compare-progress").fill("2")
            assert "una sola entrada no demuestra" in (page.text_content("#sorting-compare-conclusion") or "").lower()
            assert page.input_value("#sorting-manual-values") == "4,1,3,2"
            browser.close()


def test_playwright_sorting_accessibility_keyboard_responsive_and_export() -> None:
    """Keyboard, responsive context and summary export must remain operable."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1366, "height": 900}, accept_downloads=True)
            page.goto(f"{base_url}/sorting/visualizador", wait_until="networkidle")
            page.fill("#sorting-manual-values", "3,-1,2,0")
            page.click("#sorting-create-array")
            page.click("#sorting-sim-prepare")
            _wait_status_contains(page, "#sorting-sim-status", "Simulacion lista")
            page.keyboard.press("Alt+ArrowRight")
            assert "Paso: 1/" in (page.text_content("#sorting-sim-counter") or "")
            assert page.get_attribute("#sorting-visual-state", "role") == "img"
            assert "Arreglo" in (page.get_attribute("#sorting-visual-state", "aria-label") or "")
            assert page.locator(".sorting-state-symbol").count() >= 0
            for width in (1024, 760, 390):
                page.set_viewport_size({"width": width, "height": 900})
                assert page.locator("#sorting-sim-counter").is_visible()
                if width <= 800:
                    page.click('[data-sorting-tab="visual"]')
                    assert page.locator("#sorting-visual-region").is_visible()
                    page.click('[data-sorting-tab="code"]')
                    assert page.locator("#sorting-code-region").is_visible()
            with page.expect_download() as download_info:
                page.click("#sorting-export-summary")
            assert download_info.value.suggested_filename.endswith(".json")
            browser.close()


def test_playwright_hash_replay_practice_comparison_and_export() -> None:
    """Hash playback, practice, comparison and keyboard stay operable together."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1200, "height": 900}, accept_downloads=True)
            page.goto(f"{base_url}/hash/hash_table", wait_until="networkidle")
            page.select_option("#hash-operation-select", "insert")
            page.fill("#hash-field-key", "1")
            page.fill("#hash-field-value", "10")
            page.click("#hash-sim-play")
            _wait_status_contains(page, "#hash-sim-status", "Simulacion completada")
            page.keyboard.press("Alt+ArrowLeft")
            assert "Paso:" in (page.text_content("#hash-sim-counter") or "")
            page.check("#hash-practice-mode")
            page.fill("#hash-prediction-answer", "1")
            page.click("#hash-check-prediction")
            assert (page.text_content("#hash-prediction-feedback") or "").strip()
            page.click("#hash-compare-run")
            page.wait_for_function("() => !document.querySelector('#hash-compare-progress')?.disabled")
            assert "Capacidad 3" in (page.text_content("#hash-compare-grid") or "")
            page.check("#didactic-mode-switch")
            _wait_didactic_mode(page, "full")
            for width in (760, 390):
                page.set_viewport_size({"width": width, "height": 900})
                page.click('[data-hash-tab="visual"]')
                assert page.locator("#hash-visual-region").is_visible()
                page.click('[data-hash-tab="code"]')
                assert page.locator("#hash-code-region").is_visible()
            with page.expect_download() as download_info:
                page.click("#hash-export-summary")
            assert download_info.value.suggested_filename.endswith(".json")
            browser.close()

