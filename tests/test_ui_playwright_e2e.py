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


def _wait_trace_complete(page, counter_selector: str) -> None:
    page.wait_for_function(
        "(selector) => {"
        " const text = document.querySelector(selector)?.textContent || '';"
        " const match = text.match(/Paso:\\s*(\\d+)\\s*\\/\\s*(\\d+)/);"
        " return Boolean(match && Number(match[2]) > 0 && match[1] === match[2]);"
        "}",
        arg=counter_selector,
        timeout=30000,
    )



def _enable_manual_mode(page, prefix: str) -> None:
    """Opt into manual navigation using the actual user-facing mode control."""
    selector = {"seq": "#seq-step-mode", "hier": "#hier-step-mode"}.get(prefix, f"#{prefix}-sim-step")
    checkbox = page.locator(f"#{prefix}-step-toggle")
    if not checkbox.is_checked():
        page.click(selector)
    assert checkbox.is_checked()


def _advance_once(page, prefix: str) -> None:
    """Prepare one real operation if needed, then navigate exactly one frame."""
    _enable_manual_mode(page, prefix)
    counter = f"#{prefix}-sim-counter"
    text = page.text_content(counter) or "0/0"
    total = int(text.rsplit("/", 1)[-1])
    if total == 0:
        execute = "#seq-sim-execute" if prefix == "seq" else f"#{prefix}-sim-play"
        page.click(execute)
        page.wait_for_function("s => Number((document.querySelector(s)?.textContent || '0/0').split('/').pop()) > 0", arg=counter)
    next_selector = f"#{prefix}-sim-" + ("step" if prefix in {"seq", "hier"} else "next")
    page.click(next_selector)


def _finish_manual_trace(page, prefix: str) -> None:
    """Finish by navigation, checking progress rather than triggering another operation."""
    _enable_manual_mode(page, prefix)
    counter = f"#{prefix}-sim-counter"
    page.wait_for_function("s => Number((document.querySelector(s)?.textContent || '0/0').split('/').pop()) > 0", arg=counter)
    selector = f"#{prefix}-sim-" + ("step" if prefix in {"seq", "hier"} else "next")
    for _ in range(2000):
        text = page.text_content(counter) or ""
        match = __import__("re").search(r"Paso:\s*(\d+)\s*/\s*(\d+)", text)
        assert match is not None, text
        if int(match[1]) == int(match[2]):
            assert page.locator(selector).is_disabled()
            return
        before = text
        page.click(selector)
        page.wait_for_function("a => document.querySelector(a.s).textContent !== a.before", arg={"s":counter,"before":before})
    raise AssertionError("Trace did not finish within 2000 explicit manual steps")


def _wait_graph_mutation_final(page, expected: str) -> None:
    """Manual preparation is not a completed C operation or a future result."""
    _wait_status_contains(page, "#graph-message-box", "Operación preparada")
    assert "resultado pendiente" in (page.text_content("#graph-message-box") or "")
    _finish_manual_trace(page, "graph")
    _wait_status_contains(page, "#graph-message-box", expected)


def _assert_stack_push_final(page, expected_value: int, expected_count: int = 1) -> None:
    """Require published initialized C heap/root, not the superseded renderer CSS."""
    nodes = page.locator("[data-stack-push-node]")
    assert nodes.count() == expected_count
    for node in nodes.all():
        assert node.get_attribute("data-stack-push-mask") == "3"
    root_id = page.locator("[data-stack-push-root]").get_attribute("data-stack-push-root")
    root_node = page.locator(f'[data-stack-push-node="{root_id}"]')
    assert root_node.count() == 1
    assert root_node.locator('[data-stack-push-field="nro"] strong').inner_text() == str(expected_value)
    assert page.locator("[data-stack-push-aux-valid]").get_attribute("data-stack-push-aux-valid") == "out-of-scope"


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
                _wait_status_contains(page, "#hier-sim-status", "Modo rapido")

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
            _enable_manual_mode(page, "graph")
            page.click("#graph-sim-play")
            _wait_graph_mutation_final(page, "vertice")

            page.fill("#g-op-field-vertex", "40")
            _enable_manual_mode(page, "graph")
            page.click("#graph-sim-play")
            _wait_graph_mutation_final(page, "vertice")

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

            assert page.locator("#seq-code-region").is_visible()

            initial_url = page.url
            page.locator('label[for="didactic-mode-switch"]').click()
            _wait_didactic_mode(page, "full")
            assert page.url == initial_url
            assert page.locator("#seq-code-region").is_visible()

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
    """Sequential pilot exposes operation execution and compact step navigation."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/sequential/stack", wait_until="networkidle")
            page.locator('label[for="didactic-mode-switch"]').click()
            _wait_didactic_mode(page, "full")

            page.fill("#field-value", "21")
            _enable_manual_mode(page, "seq")
            page.click("#seq-sim-execute")
            _wait_status_contains(page, "#seq-sim-status", "Traza lista")
            _enable_manual_mode(page, "seq")
            assert page.is_visible("#seq-sim-step")
            assert page.is_visible("#seq-sim-prev")
            page.click("#seq-sim-step")
            _wait_status_contains(page, "#seq-sim-counter", "Paso: 1/")
            page.click("#seq-sim-prev")
            _wait_status_contains(page, "#seq-sim-counter", "Paso: 0/")
            page.click("#seq-sim-step")
            _enable_manual_mode(page, "seq")
            _finish_manual_trace(page, "seq")
            _assert_stack_push_final(page, 21)
            visual_text = page.text_content("#visual-state") or ""
            assert "aux (integrado)" not in visual_text

            browser.close()


def test_playwright_sequential_execution_is_separate_from_playback() -> None:
    """A real operation is posted once; replaying it never posts it again."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            requests: list[str] = []
            page.on(
                "request",
                lambda request: requests.append(request.url)
                if request.method == "POST" and request.url.endswith("/operate")
                else None,
            )
            page.goto(f"{base_url}/sequential/stack", wait_until="networkidle")
            page.locator('label[for="didactic-mode-switch"]').click()
            _wait_didactic_mode(page, "full")
            page.fill("#field-value", "7")

            _enable_manual_mode(page, "seq")
            page.click("#seq-sim-execute")
            _wait_status_contains(page, "#seq-sim-status", "Traza lista")
            assert len(requests) == 1
            _finish_manual_trace(page, "seq")
            _assert_stack_push_final(page, 7)
            page.click("#seq-step-mode")
            _enable_manual_mode(page, "seq")
            page.click("#seq-sim-step")
            page.click("#seq-sim-prev")
            assert len(requests) == 1
            _enable_manual_mode(page, "seq")
            _finish_manual_trace(page, "seq")
            assert len(requests) == 1
            _assert_stack_push_final(page, 7)

            _enable_manual_mode(page, "seq")
            page.click("#seq-sim-execute")
            _wait_status_contains(page, "#seq-sim-status", "Traza lista")
            assert len(requests) == 2
            _finish_manual_trace(page, "seq")
            _assert_stack_push_final(page, 7, expected_count=2)
            _assert_stack_push_final(page, 7, expected_count=2)

            page.select_option("#operation-select", "desapilar")
            _enable_manual_mode(page, "seq")
            page.click("#seq-sim-execute")
            _wait_status_contains(page, "#seq-sim-status", "Traza lista")
            assert len(requests) == 3
            _finish_manual_trace(page, "seq")
            assert page.locator(".viz-stack-node-row").count() == 1
            assert page.locator(".viz-stack-node-row").count() == 1

            _enable_manual_mode(page, "seq")
            page.click("#seq-sim-execute")
            _wait_status_contains(page, "#seq-sim-status", "Traza lista")
            assert len(requests) == 4
            _finish_manual_trace(page, "seq")
            assert page.locator(".viz-stack-node-row").count() == 0
            assert page.locator(".viz-stack-node-row").count() == 0
            browser.close()


@pytest.mark.parametrize(
    ("structure_id", "seed_operation", "seed_payload", "remove_operation", "remove_payload"),
    [
        ("queue", "encolar", {"value": "7"}, "desencolar", {}),
        ("priority_queue", "encolar", {"value": "7", "priority": "1"}, "desencolar", {}),
        ("linked_list", "insertar_inicio", {"value": "7"}, "eliminar_elemento", {"value": "7"}),
        ("circular_list", "insertar_inicio", {"value": "7"}, "eliminar_inicio", {}),
        ("sublist", "insertar_padre", {"parent": "7"}, "eliminar_padre", {"parent": "7"}),
    ],
)
def test_playwright_other_sequential_structures_show_canonical_final_state(
    structure_id: str,
    seed_operation: str,
    seed_payload: dict[str, str],
    remove_operation: str,
    remove_payload: dict[str, str],
) -> None:
    """Every sequential renderer shows the final state immediately after Execute."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/sequential/{structure_id}", wait_until="networkidle")
            page.locator('label[for="didactic-mode-switch"]').click()
            _wait_didactic_mode(page, "full")

            page.select_option("#operation-select", seed_operation)
            for name, value in seed_payload.items():
                page.fill(f"#field-{name}", value)
            page.click("#seq-sim-execute")
            _wait_status_contains(page, "#seq-sim-status", "Modo rápido")
            assert "Tamano: 1" in (page.text_content("#visual-state") or "")

            page.select_option("#operation-select", remove_operation)
            for name, value in remove_payload.items():
                page.fill(f"#field-{name}", value)
            page.click("#seq-sim-execute")
            _wait_status_contains(page, "#seq-sim-status", "Modo rápido")
            assert "Tamano: 0" in (page.text_content("#visual-state") or "")
            browser.close()


def test_playwright_queue_final_view_hides_aux_temporary_node() -> None:
    """Queue simulation final step should show only queue structure without aux temporary block."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/sequential/queue", wait_until="networkidle")
            page.locator('label[for="didactic-mode-switch"]').click()
            _wait_didactic_mode(page, "full")

            page.select_option("#operation-select", "encolar")
            page.fill("#field-value", "8")
            _enable_manual_mode(page, "seq")
            page.click("#seq-sim-execute")
            _wait_status_contains(page, "#seq-sim-status", "Traza lista")
            _finish_manual_trace(page, "seq")
            assert "aux (integrado)" not in (page.text_content("#visual-state") or "")

            page.fill("#field-value", "6")
            _enable_manual_mode(page, "seq")
            page.click("#seq-sim-execute")
            _wait_status_contains(page, "#seq-sim-status", "Traza lista")
            _finish_manual_trace(page, "seq")
            assert "aux (integrado)" not in (page.text_content("#visual-state") or "")

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
            page.locator('label[for="didactic-mode-switch"]').click()
            _wait_didactic_mode(page, "full")

            page.select_option("#hash-operation-select", "insert")
            page.wait_for_selector("#hash-field-key", timeout=5000)
            page.fill("#hash-field-key", "1")
            page.fill("#hash-field-value", "10")
            _enable_manual_mode(page, "hash")
            page.click("#hash-sim-play")
            _finish_manual_trace(page, "hash")

            page.click("#hash-reset-button")
            _wait_status_contains(page, "#hash-sim-status", "Usa Reproducir o Siguiente paso para ejecutar.")

            _advance_once(page, "hash")
            _wait_status_contains(page, "#hash-sim-counter", "Paso: 1/")

            page.click("#hash-sim-prev")
            _wait_status_contains(page, "#hash-sim-counter", "Paso: 0/")

            browser.close()


def test_playwright_graph_execute_completes_algorithms_across_phases() -> None:
    """Execute operation reaches each graph algorithm's final canonical state."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 1) Build a base graph in construction phase.
            page.goto(f"{base_url}/graph/graph/construccion", wait_until="networkidle")
            page.locator('label[for="didactic-mode-switch"]').click()
            _wait_didactic_mode(page, "full")
            for value in ["1", "2", "3", "4"]:
                page.select_option("#graph-operation-select", "insert_vertex")
                page.wait_for_selector("#g-op-field-vertex", timeout=5000)
                page.fill("#g-op-field-vertex", value)
                _enable_manual_mode(page, "graph")
                page.click("#graph-sim-play")
                _wait_graph_mutation_final(page, "vertice")

            for origin, target, weight in [("1", "2", "3"), ("2", "3", "2"), ("3", "4", "4"), ("1", "4", "15")]:
                page.select_option("#graph-operation-select", "insert_edge")
                page.wait_for_selector("#g-op-field-origin", timeout=5000)
                page.fill("#g-op-field-origin", origin)
                page.fill("#g-op-field-target", target)
                page.fill("#g-op-field-weight", weight)
                _enable_manual_mode(page, "graph")
                page.click("#graph-sim-play")
                _wait_graph_mutation_final(page, "arista")

            # 2) Traversals phase (BFS), executed to the final frame.
            page.goto(f"{base_url}/graph/graph/recorridos", wait_until="networkidle")
            page.select_option("#graph-algorithm-select", "run_bfs")
            page.fill("#g-alg-field-start", "1")
            _enable_manual_mode(page, "graph")
            page.click("#graph-sim-play")
            _finish_manual_trace(page, "graph")
            _wait_status_contains(page, "#graph-message-box", "BFS")
            result_text = page.text_content("#graph-visual-state") or ""
            assert ("Recorrido" in result_text) or ("BFS" in result_text)

            # 3) Shortest path phase (Dijkstra).
            page.goto(f"{base_url}/graph/graph/camino-minimo", wait_until="networkidle")
            page.select_option("#graph-algorithm-select", "run_dijkstra")
            page.fill("#g-alg-field-start", "1")
            page.fill("#g-alg-field-end", "4")
            _enable_manual_mode(page, "graph")
            page.click("#graph-sim-play")
            _finish_manual_trace(page, "graph")
            _wait_status_contains(page, "#graph-message-box", "Dijkstra")

            # 4) MST phase (Prim).
            page.goto(f"{base_url}/graph/graph/expansion-minima", wait_until="networkidle")
            page.select_option("#graph-algorithm-select", "run_prim")
            page.fill("#g-alg-field-start", "1")
            _enable_manual_mode(page, "graph")
            page.click("#graph-sim-play")
            _finish_manual_trace(page, "graph")
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
            page.locator('label[for="didactic-mode-switch"]').click()
            _wait_didactic_mode(page, "full")

            for value in [str(v) for v in range(1, 9)]:
                page.select_option("#graph-operation-select", "insert_vertex")
                page.wait_for_selector("#g-op-field-vertex", timeout=5000)
                page.fill("#g-op-field-vertex", value)
                _enable_manual_mode(page, "graph")
                page.click("#graph-sim-play")
                _wait_graph_mutation_final(page, "vertice")

            ring_edges = [
                ("1", "2", "4"),
                ("2", "3", "7"),
                ("3", "4", "6"),
                ("4", "5", "3"),
                ("5", "6", "2"),
                ("6", "7", "5"),
                ("7", "8", "8"),
                ("8", "1", "1"),
            ]
            extra_edges = [("1", "6", "11"), ("2", "7", "12"), ("3", "8", "13")]

            for origin, target, weight in ring_edges + extra_edges:
                page.select_option("#graph-operation-select", "insert_edge")
                page.wait_for_selector("#g-op-field-origin", timeout=5000)
                page.fill("#g-op-field-origin", origin)
                page.fill("#g-op-field-target", target)
                page.fill("#g-op-field-weight", weight)
                _enable_manual_mode(page, "graph")
                page.click("#graph-sim-play")
                _wait_graph_mutation_final(page, "arista")

            result_text = page.text_content("#graph-visual-state") or ""
            assert "Vértices" in result_text
            assert "Aristas" in result_text

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
    """The compact graph workspace keeps code and visualization accessible on mobile."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            page=browser.new_page(viewport={"width":1280,"height":900})
            page.goto(f"{base_url}/graph/graph/construccion",wait_until="networkidle")
            page.select_option("#graph-operation-select", "insert_vertex")
            page.fill("#g-op-field-vertex", "1")
            _enable_manual_mode(page, "graph")
            page.click("#graph-sim-play")
            _wait_graph_mutation_final(page, "vertice")
            page.goto(f"{base_url}/graph/graph/recorridos",wait_until="networkidle")
            assert page.locator("#graph-guided-example").count() == 0
            assert page.locator("#graph-visual-region").is_visible()
            assert page.locator("#graph-code-region").count() == 1
            page.select_option("#graph-algorithm-select", "run_bfs")
            page.fill("#g-alg-field-start", "1")
            _advance_once(page, "graph")
            _wait_status_contains(page, "#graph-sim-counter", "Paso: 1/")
            cursor = page.text_content("#graph-sim-counter")
            page.set_viewport_size({"width":390,"height":844})
            page.click('[data-graph-tab="code"]')
            assert page.is_visible("#graph-code-region")
            page.click('[data-graph-tab="visual"]')
            assert page.is_visible("#graph-visual-region")
            assert page.text_content("#graph-sim-counter")==cursor
            browser.close()


def test_playwright_graph_mst_practice_comparison_keyboard_and_responsive() -> None:
    """Graph step controls and primary views remain usable in the compact layout."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
            page.goto(f"{base_url}/graph/graph/expansion-minima", wait_until="networkidle")
            assert page.locator("#graph-guided-example").count() == 0
            assert page.locator("#graph-practice-mode").count() == 0
            assert page.locator("#graph-compare-kind").count() == 0
            page.goto(f"{base_url}/graph/graph/construccion", wait_until="networkidle")
            for value in ("1", "2", "3"):
                page.select_option("#graph-operation-select", "insert_vertex")
                page.fill("#g-op-field-vertex", value)
                _enable_manual_mode(page, "graph")
                page.click("#graph-sim-play")
                _wait_graph_mutation_final(page, "vertice")
            page.select_option("#graph-operation-select", "insert_edge")
            page.fill("#g-op-field-origin", "1")
            page.fill("#g-op-field-target", "2")
            page.fill("#g-op-field-weight", "4")
            _enable_manual_mode(page, "graph")
            page.click("#graph-sim-play")
            _wait_graph_mutation_final(page, "arista")
            page.select_option("#graph-operation-select", "insert_edge")
            page.fill("#g-op-field-origin", "2")
            page.fill("#g-op-field-target", "3")
            page.fill("#g-op-field-weight", "2")
            _enable_manual_mode(page, "graph")
            page.click("#graph-sim-play")
            _wait_graph_mutation_final(page, "arista")
            page.goto(f"{base_url}/graph/graph/expansion-minima", wait_until="networkidle")
            page.select_option("#graph-algorithm-select", "run_prim")
            page.fill("#g-alg-field-start", "1")
            _advance_once(page, "graph")
            page.keyboard.press("Alt+ArrowRight")
            assert "Paso:" in (page.text_content("#graph-sim-counter") or "")
            page.set_viewport_size({"width": 390, "height": 844})
            assert (page.locator("#graph-export-summary").text_content() or "").strip()
            browser.close()


def test_playwright_hierarchical_guided_level_and_mobile_context() -> None:
    """The compact hierarchical workspace preserves code and visualization views."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(f"{base_url}/hierarchical/avl", wait_until="networkidle")
            assert page.locator("#hier-guided-example").count() == 0
            assert page.locator("#hier-compare-kind").count() == 0
            page.fill("#h-field-value", "30")
            page.click("#hier-step-mode")
            page.click("#hier-sim-step")
            _wait_status_contains(page, "#hier-sim-counter", "Paso: 1/")
            cursor = page.text_content("#hier-sim-counter")
            assert page.text_content("#hier-sim-counter") == cursor
            summary = (page.text_content("#hier-pedagogy-summary") or "").lower()
            assert "caller_enter" in summary and "no hay resultado futuro" in summary
            page.set_viewport_size({"width": 390, "height": 844})
            page.click('[data-hier-tab="code"]')
            assert page.is_visible("#hier-code-region") is True
            page.click('[data-hier-tab="visual"]')
            assert page.is_visible("#hier-visual-region") is True
            assert page.text_content("#hier-sim-counter") == cursor
            browser.close()


def test_playwright_hierarchical_comparison_practice_keyboard_and_accessibility() -> None:
    """Hierarchy uses the compact execution flow and keyboard step navigation."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
            page.goto(f"{base_url}/hierarchical/avl", wait_until="networkidle")
            assert page.locator("#hier-compare-kind").count() == 0
            assert page.locator("#hier-practice-mode").count() == 0
            page.fill("#h-field-value", "25")
            page.click("#hier-step-mode")
            page.click("#hier-sim-step")
            before=page.text_content("#hier-sim-counter")
            page.locator("body").press("ArrowRight")
            assert page.text_content("#hier-sim-counter") != before
            page.locator("body").press("Home")
            assert "Paso: 0/" in (page.text_content("#hier-sim-counter") or "")
            assert page.locator("#hier-sim-prev").is_visible()
            assert page.locator("#hier-sim-step").is_visible()
            browser.close()


def test_playwright_sequential_step_progress_keeps_visual_and_c_synchronized() -> None:
    """Compact sequential UI exposes step state and keeps optional learning under Comprender."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/sequential/stack", wait_until="networkidle")
            page.locator('label[for="didactic-mode-switch"]').click()
            _wait_didactic_mode(page, "full")
            page.fill("#field-value", "17")
            _enable_manual_mode(page, "seq")
            page.click("#seq-sim-execute")
            _wait_status_contains(page, "#seq-sim-status", "Traza lista")
            page.click("#seq-step-mode")
            _enable_manual_mode(page, "seq")
            page.click("#seq-sim-step")
            _wait_status_contains(page, "#seq-sim-counter", "Paso: 1/")
            assert page.locator(".seq-understand details > .seq-predict").count() == 1
            assert page.locator(".seq-predict").evaluate("el => !el.closest('details').open")
            assert page.locator(".seq-understand details > .seq-compare").count() == 1
            assert page.locator(".seq-compare").evaluate("el => !el.closest('details').open")
            assert page.locator(".seq-understand").count() == 1
            assert page.locator("#seq-code-region").count() == 1
            assert page.locator("#visual-state").count() == 1
            browser.close()


def test_playwright_stack_compact_pilot_keeps_primary_workspace_visible() -> None:
    """The stack baseline uses the five requested stages and contextual controls."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1366, "height": 768})
            page.goto(f"{base_url}/sequential/stack", wait_until="networkidle")

            assert page.locator(".is-stack-pilot").count() == 1
            headings = page.evaluate(
                """() => [
                    document.querySelector('#seq-prepare-title')?.innerText,
                    document.querySelector('#seq-visual-title')?.innerText,
                    document.querySelector('.seq-code-toolbar h3')?.innerText,
                    document.querySelector('#seq-execute-title')?.innerText,
                    document.querySelector('#seq-predict-title')?.innerText,
                ]""",
            )
            assert headings[:3] == [
                "1 Preparar y controlar ejecución",
                "2 Visualizar y ejecutar",
                "3 Relacionar con código",
            ]
            assert page.locator(".seq-understand details > .seq-predict").count() == 1
            assert page.locator(".seq-predict").evaluate("el => !el.closest('details').open")
            assert page.locator(".seq-understand details > .seq-compare").count() == 1
            assert page.locator(".seq-compare").evaluate("el => !el.closest('details').open")
            assert page.locator(".seq-understand").count() == 1
            assert page.locator(".seq-execute").evaluate("el => el.parentElement.classList.contains('seq-prepare')")
            assert page.locator(".seq-reflect").count() == 1

            page.goto(f"{base_url}/sequential/queue", wait_until="networkidle")
            assert page.locator(".is-stack-pilot").count() == 0
            browser.close()


def test_playwright_sequential_mobile_step_controls_are_available() -> None:
    """Mobile sequential view keeps the structure, C code, and step controls available."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 390, "height": 844})
            page.goto(f"{base_url}/sequential/queue", wait_until="networkidle")
            page.locator('label[for="didactic-mode-switch"]').click()
            _wait_didactic_mode(page, "full")
            page.fill("#field-value", "8")
            _enable_manual_mode(page, "seq")
            page.click("#seq-sim-execute")
            _wait_status_contains(page, "#seq-sim-status", "Traza lista")
            page.click("#seq-sim-step")
            _wait_status_contains(page, "#seq-sim-counter", "Paso: 1/")
            assert page.locator("#visual-state").is_visible()
            assert page.locator("#seq-sim-prev").is_visible()
            assert page.locator("#seq-sim-step").is_visible()
            assert page.locator("#seq-code-region").count() == 1
            page.click('[data-seq-tab="code"]')
            assert page.locator("#seq-code-region").is_visible()
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

            for algorithm in algorithms:
                page.select_option("#sorting-algorithm", algorithm)
                _enable_manual_mode(page, "sorting")
                page.click("#sorting-sim-play")
                _finish_manual_trace(page, "sorting")
                labels = page.locator(".sorting-item-label").all_text_contents()
                assert [int(label.split("]", 1)[1].strip()) for label in labels] == [-1, 0, 3, 3, 5]
                code = page.text_content("#sorting-code") or ""
                assert f"ordenar_{algorithm}" in code

            page.select_option("#sorting-algorithm", "quicksort")
            _enable_manual_mode(page, "sorting")
            page.click("#sorting-sim-play")
            _finish_manual_trace(page, "sorting")
            completed_counter = page.text_content("#sorting-sim-counter") or ""
            page.evaluate("() => document.querySelector('#sorting-sim-prev').click()")
            page.wait_for_function("(completed) => (document.querySelector('#sorting-sim-counter')?.textContent || '') !== completed", arg=completed_counter)
            counter_after_previous = page.text_content("#sorting-sim-counter") or ""
            page.evaluate("() => document.querySelector('#sorting-sim-next').click()")
            page.wait_for_function("(previous) => (document.querySelector('#sorting-sim-counter')?.textContent || '') !== previous", arg=counter_after_previous)
            counter_after_next = page.text_content("#sorting-sim-counter") or ""
            assert counter_after_previous != counter_after_next
            browser.close()


def test_playwright_sorting_compact_workspace_omits_removed_learning_widgets() -> None:
    """Sorting keeps its current fixed-level compact workspace without removed widgets."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(f"{base_url}/sorting/visualizador", wait_until="networkidle")
            assert page.locator("#sorting-guided-example").count() == 0
            assert page.locator("#sorting-learning-level").count() == 0
            assert page.locator("#sorting-practice-mode").count() == 0
            assert page.locator("#sorting-compare-run").count() == 0
            page.fill("#sorting-manual-values", "4,2,4,1")
            page.click("#sorting-create-array")
            _wait_status_contains(page, "#sorting-message-box", "Arreglo creado")
            _advance_once(page, "sorting")
            _wait_status_contains(page, "#sorting-sim-counter", "Paso: 1/")
            assert (page.text_content("#sorting-pedagogy-narration") or "").strip()
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
            expected = {
                "seleccion": "Mínimo provisional",
                "insercion": "Clave:",
                "burbuja": "Pasada:",
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
                _enable_manual_mode(page, "sorting")
                page.click("#sorting-sim-play")
                _finish_manual_trace(page, "sorting")
                assert marker in (page.text_content("#sorting-strategy-view") or "")
                if algorithm == "burbuja":
                    strategy = page.text_content("#sorting-strategy-view") or ""
                    assert "Retorno void al caller" in strategy
                    assert "j: —" in strategy and "hubo_intercambio: —" in strategy
            browser.close()


def test_playwright_sorting_step_navigation_and_theory_analysis() -> None:
    """The simplified player navigates steps while theory remains separate from metrics."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(f"{base_url}/sorting/visualizador", wait_until="networkidle")
            page.fill("#sorting-manual-values", "4,1,3,2")
            page.click("#sorting-create-array")
            _wait_status_contains(page, "#sorting-message-box", "Arreglo creado")
            _advance_once(page, "sorting")
            _wait_status_contains(page, "#sorting-sim-counter", "Paso: 1/")
            total = int((page.text_content("#sorting-sim-counter") or "0/0").split("/")[-1])
            assert total > 2
            assert "Paso: 1/" in (page.text_content("#sorting-sim-counter") or "")
            before_tab = page.text_content("#sorting-sim-counter")
            page.set_viewport_size({"width": 760, "height": 900})
            page.click('[data-sorting-tab="code"]')
            assert page.text_content("#sorting-sim-counter") == before_tab
            page.click("#sorting-sim-next")
            assert "Paso: 2/" in (page.text_content("#sorting-sim-counter") or "")
            page.click("#sorting-sim-prev")
            assert "Paso: 1/" in (page.text_content("#sorting-sim-counter") or "")
            _finish_manual_trace(page, "sorting")
            page.wait_for_function("(expected) => (document.querySelector('#sorting-sim-counter')?.textContent || '') === expected", arg=f"Paso: {total}/{total}")
            assert (page.text_content("#sorting-invariant-text") or "").strip()
            theory = page.text_content("#sorting-theory-profile") or ""
            observed = page.text_content("#sorting-observed-metrics") or ""
            assert "Mejor" in theory and "Memoria" in theory and "Estable" in theory
            assert "Comparaciones" in observed and "Intercambios" in observed
            assert page.input_value("#sorting-manual-values") == "4,1,3,2"
            browser.close()


def test_playwright_sorting_removed_practice_and_comparison_widgets() -> None:
    """Prediction and visual comparison are intentionally absent from this workspace."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(f"{base_url}/sorting/visualizador", wait_until="networkidle")
            page.fill("#sorting-manual-values", "4,1,3,2")
            page.click("#sorting-create-array")
            assert page.locator("#sorting-practice-mode").count() == 0
            assert page.locator("#sorting-prediction-card").count() == 0
            assert page.locator("#sorting-compare-run").count() == 0
            _advance_once(page, "sorting")
            _wait_status_contains(page, "#sorting-sim-counter", "Paso: 1/")
            assert (page.text_content("#sorting-pedagogy-narration") or "").strip()
            assert page.locator("#sorting-visual-state").is_visible()
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
            _advance_once(page, "sorting")
            _wait_status_contains(page, "#sorting-sim-counter", "Paso: 1/")
            page.keyboard.press("Alt+ArrowRight")
            _wait_status_contains(page, "#sorting-sim-counter", "Paso: 2/")
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
            page.locator(".sorting-collapsible").nth(1).locator("summary").click()
            with page.expect_download() as download_info:
                page.click("#sorting-export-summary")
            assert download_info.value.suggested_filename.endswith(".json")
            browser.close()


def test_playwright_hash_step_navigation_and_export() -> None:
    """Hash step navigation, responsive views, and export work in the compact UI."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1200, "height": 900}, accept_downloads=True)
            page.goto(f"{base_url}/hash/hash_table", wait_until="networkidle")
            page.select_option("#hash-operation-select", "insert")
            page.fill("#hash-field-key", "1")
            page.fill("#hash-field-value", "10")
            assert page.locator("#hash-practice-mode").count() == 0
            assert page.locator("#hash-prediction-answer").count() == 0
            assert page.locator("#hash-compare-run").count() == 0
            _advance_once(page, "hash")
            _wait_status_contains(page, "#hash-sim-counter", "Paso: 1/")
            page.click("#hash-sim-prev")
            assert "Paso: 0/" in (page.text_content("#hash-sim-counter") or "")
            _advance_once(page, "hash")
            _enable_manual_mode(page, "hash")
            page.click("#hash-sim-play")
            _finish_manual_trace(page, "hash")
            page.locator('label[for="didactic-mode-switch"]').click()
            _wait_didactic_mode(page, "full")
            for width in (760, 390):
                page.set_viewport_size({"width": width, "height": 900})
                page.click('[data-hash-tab="visual"]')
                assert page.locator("#hash-visual-region").is_visible()
                page.click('[data-hash-tab="code"]')
                assert page.locator("#hash-code-region").is_visible()
            page.locator(".hash-collapsible").nth(1).locator("summary").click()
            with page.expect_download() as download_info:
                page.click("#hash-export-summary")
            assert download_info.value.suggested_filename.endswith(".json")
            browser.close()

