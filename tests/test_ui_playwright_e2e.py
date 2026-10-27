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
from scripts.e2e_diagnostics import checkpoint


pytestmark = pytest.mark.e2e


@contextmanager
def _live_server_url():
    """Run Flask app in-process and yield base URL."""
    checkpoint("server_create_start")
    app = create_app()
    app.config.update(TESTING=False, SECRET_KEY="e2e-secret")

    @app.before_request
    def _diagnostic_request_start():
        from flask import request
        checkpoint("http_start", method=request.method, path=request.path)

    @app.after_request
    def _diagnostic_request_end(response):
        from flask import request
        checkpoint("http_end", method=request.method, path=request.path, status=response.status_code)
        return response

    server = make_server("127.0.0.1", 0, app)
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    checkpoint("server_ready", port=port)
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        checkpoint("server_shutdown_start")
        server.shutdown()
        checkpoint("server_shutdown_end")
        thread.join(timeout=5)
        checkpoint("server_thread_join_end", alive=thread.is_alive())


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
    checkpoint("manual_prepare_start", module=prefix)
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


def _finish_manual_trace(page, prefix: str, observe=None) -> None:
    """Finish by navigation, checking progress rather than triggering another operation."""
    checkpoint("manual_prepare_start", module=prefix)
    _enable_manual_mode(page, prefix)
    counter = f"#{prefix}-sim-counter"
    page.wait_for_function("s => Number((document.querySelector(s)?.textContent || '0/0').split('/').pop()) > 0", arg=counter)
    selector = f"#{prefix}-sim-" + ("step" if prefix in {"seq", "hier"} else "next")
    checkpoint("manual_finish_start", module=prefix)
    initial = __import__("re").search(r"Paso:\s*(\d+)\s*/\s*(\d+)", page.text_content(counter) or "")
    assert initial is not None and int(initial[2]) > 0
    # The canonical book emits every real helper/allocator instruction. Traverse
    # the declared finite trace, rather than the old observer's 2,000-frame cap.
    total = int(initial[2])
    for navigation_index in range(total + 1):
        text = page.text_content(counter) or ""
        match = __import__("re").search(r"Paso:\s*(\d+)\s*/\s*(\d+)", text)
        assert match is not None, text
        if observe is not None:
            observe(int(match[1]), int(match[2]))
        if int(match[1]) == int(match[2]):
            assert page.locator(selector).is_disabled()
            checkpoint("manual_finish_end", module=prefix, counter=text)
            return
        if navigation_index % 25 == 0:
            checkpoint("manual_navigation", module=prefix, navigation_index=navigation_index, counter=text)
        before = text
        page.click(selector)
        page.wait_for_function("a => document.querySelector(a.s).textContent !== a.before", arg={"s":counter,"before":before})
    raise AssertionError(f"Trace did not finish within its {total} declared manual steps")


def _wait_graph_mutation_final(page, expected: str) -> None:
    """Manual preparation is not a completed C operation or a future result."""
    _wait_status_contains(page, "#graph-message-box", "Operación preparada")
    assert "resultado pendiente" in (page.text_content("#graph-message-box") or "")
    _finish_manual_trace(page, "graph")
    # The book contract reports the executed C function, rather than the
    # superseded presentation message ("arista insertada").
    symbol = {"vertice": "grafo_insertar_vertice", "arista": "grafo_insertar_arco"}.get(expected, expected)
    _wait_status_contains(page, "#graph-message-box", symbol)


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
            assert "Código C canónico del libro" in code_title
            assert "tad_grafo.c" in code_title

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

            page.once("dialog", lambda dialog: dialog.accept())
            with page.expect_response(lambda response: response.request.method == "POST"
                                      and response.url.split("?", 1)[0].endswith("/hash/hash_table/reset")) as reset:
                page.click("#hash-reset-button")
            assert reset.value.status == 200
            reset_body = reset.value.json()
            assert reset_body["success"] is True and reset_body["history"] == []
            _wait_status_contains(page, "#hash-sim-status", "Tabla restablecida. Prepara una operación.")

            _advance_once(page, "hash")
            _wait_status_contains(page, "#hash-sim-counter", "Paso: 1/")

            page.click("#hash-sim-prev")
            _wait_status_contains(page, "#hash-sim-counter", "Paso: 0/")

            browser.close()


def _assert_graph_fixture(state, history, vertices, edges, expected_history, unmarked=False):
    """Check public logical state and chronological calls, not cached model output."""
    assert state["structure"] == "graph" and state["directed"] is False
    assert [node["id"] for node in state["nodes"]] == list(vertices)
    assert [node["label"] for node in state["nodes"]] == list(vertices)
    assert [node["value"] for node in state["nodes"]] == list(vertices)
    assert all(type(edge["weight"]) in (int, float) for edge in state["edges"])
    assert [(edge["source"], edge["target"], edge["weight"]) for edge in state["edges"]] == [
        (origin, target, float(weight)) for origin, target, weight in edges
    ]
    assert state["weighted"] is any(float(weight) != 1.0 for _, _, weight in edges)
    assert state["metadata"]["vertices_count"] == len(vertices)
    assert state["metadata"]["edges_count"] == len(edges)
    assert state["metadata"]["is_empty"] is (not vertices)
    if unmarked:
        assert all(node["marked"] == 0 for node in state["nodes"])
    assert len(history) == len(expected_history)
    assert [{"operation": step["operation"], "payload": step["payload"]} for step in history] == expected_history


def _seed_graph_via_public_api(page, base_url, vertices, edges):
    """Same browser session, same calls/data/order; construction UI clicks are not tested."""
    initial = page.evaluate("() => window.GRAPH_VIEW_MODEL")
    _assert_graph_fixture(initial["visual_state"], initial["history"], [], [], [], unmarked=True)
    history, inserted_vertices, inserted_edges = [], [], []
    operations = [("insert_vertex", {"vertex": vertex}) for vertex in vertices]
    operations += [("insert_edge", {"origin": origin, "target": target, "weight": weight})
                   for origin, target, weight in edges]
    for operation, payload in operations:
        # page.request shares the BrowserContext cookie jar; no private model/session injection.
        response = page.request.post(base_url + "/graph/graph/operate",
                                     data={"operation": operation, "payload": payload})
        assert response.status == 200
        data = response.json()
        assert data["success"] is True
        history.append({"operation": operation, "payload": dict(payload)})
        if operation == "insert_vertex":
            inserted_vertices.append(payload["vertex"])
        else:
            inserted_edges.append((payload["origin"], payload["target"], payload["weight"]))
        _assert_graph_fixture(data["visual_state"], data["history"],
                              inserted_vertices, inserted_edges, history, unmarked=True)
        response.dispose()
    assert len(operations) == len(vertices) + len(edges)
    page.reload(wait_until="networkidle")
    restored = page.evaluate("() => window.GRAPH_VIEW_MODEL")
    _assert_graph_fixture(restored["visual_state"], restored["history"], vertices, edges, history, unmarked=True)
    _wait_didactic_mode(page, "full")
    return history


def _graph_operate_response(response):
    return response.request.method == "POST" and response.url.split("?", 1)[0].endswith("/graph/graph/operate")


def _sorting_frame_observation(page):
    """Observe rendered frame and live/released views without changing the cursor."""
    return page.evaluate("""() => ({
      text: document.querySelector('#sorting-strategy-view')?.textContent || '',
      stack: document.querySelector('#sorting-call-stack')?.textContent || '',
      variables: Array.from(document.querySelectorAll('#sorting-variable-table tr td:first-child'),
                            node => node.textContent.trim()),
      countLive: !!document.querySelector('#sorting-strategy-view [data-count-live="true"]'),
      countReleased: !!document.querySelector('#sorting-strategy-view [data-count-live="false"]'),
      countCells: document.querySelectorAll('#sorting-strategy-view [data-count-index]').length,
      heapChildren: !!document.querySelector('#sorting-strategy-view [data-children]:not([data-children=""])'),
      heapN: document.querySelector('#sorting-strategy-view [data-heap-n]')?.getAttribute('data-heap-n'),
      suffixCount: document.querySelectorAll('#sorting-strategy-view [data-suffix-index]').length,
      radixLive: !!document.querySelector('#sorting-strategy-view [data-radix-buffer][data-live="true"]'),
      radixCells: document.querySelectorAll('#sorting-strategy-view [data-radix-index]').length,
      radixCounts: !!document.querySelector('#sorting-strategy-view [data-radix-counts]')
    })""")


def test_playwright_graph_execute_completes_algorithms_across_phases() -> None:
    """Execute operation reaches each graph algorithm's final canonical state."""
    playwright_mod = pytest.importorskip("playwright.sync_api")

    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Fixture only: the omitted construction clicks are not UI evidence.
            page.goto(f"{base_url}/graph/graph/construccion", wait_until="networkidle")
            page.locator('label[for="didactic-mode-switch"]').click()
            _wait_didactic_mode(page, "full")
            vertices = ["1", "2", "3", "4"]
            edges = [("1", "2", "3"), ("2", "3", "2"), ("3", "4", "4"), ("1", "4", "15")]
            expected_history = _seed_graph_via_public_api(page, base_url, vertices, edges)
            assert len(expected_history) == 8
            ui_requests = []

            def record_ui_operation(request):
                if request.method == "POST" and request.url.split("?", 1)[0].endswith("/graph/graph/operate"):
                    body = request.post_data_json
                    assert set(body) == {"operation", "payload", "execution_mode"}
                    assert body["execution_mode"] == "step"
                    ui_requests.append({key: body[key] for key in ("operation", "payload")})

            page.on("request", record_ui_operation)

            # 2) Traversals phase (BFS), executed to the final frame.
            page.goto(f"{base_url}/graph/graph/recorridos", wait_until="networkidle")
            page.select_option("#graph-algorithm-select", "run_bfs")
            page.fill("#g-alg-field-start", "1")
            _enable_manual_mode(page, "graph")
            with page.expect_response(_graph_operate_response) as operation_response:
                page.click("#graph-sim-play")
            _finish_manual_trace(page, "graph")
            result_response = operation_response.value
            assert result_response.status == 200
            result_data = result_response.json()
            assert result_data["success"] is True
            expected_history.append({'operation': 'run_bfs', 'payload': {'start': '1'}})
            assert ui_requests == expected_history[8:]
            _assert_graph_fixture(result_data["visual_state"], result_data["history"],
                                  vertices, edges, expected_history)
            _assert_graph_fixture(page.evaluate("() => window.GRAPH_VIEW_MODEL.visual_state"),
                                  result_data["history"], vertices, edges, expected_history)
            _wait_status_contains(page, "#graph-message-box", "grafo_bfs")
            result_text = page.text_content("#graph-visual-state") or ""
            assert ("Recorrido" in result_text) or ("BFS" in result_text)

            # 3) Shortest path phase (Dijkstra).
            page.goto(f"{base_url}/graph/graph/camino-minimo", wait_until="networkidle")
            page.select_option("#graph-algorithm-select", "run_dijkstra")
            page.fill("#g-alg-field-start", "1")
            page.fill("#g-alg-field-end", "4")
            _enable_manual_mode(page, "graph")
            with page.expect_response(_graph_operate_response) as operation_response:
                page.click("#graph-sim-play")
            _finish_manual_trace(page, "graph")
            result_response = operation_response.value
            assert result_response.status == 200
            result_data = result_response.json()
            assert result_data["success"] is True
            expected_history.append({'operation': 'run_dijkstra', 'payload': {'start': '1', 'end': '4'}})
            assert ui_requests == expected_history[8:]
            _assert_graph_fixture(result_data["visual_state"], result_data["history"],
                                  vertices, edges, expected_history)
            _assert_graph_fixture(page.evaluate("() => window.GRAPH_VIEW_MODEL.visual_state"),
                                  result_data["history"], vertices, edges, expected_history)
            _wait_status_contains(page, "#graph-message-box", "grafo_dijkstra")

            # 4) MST phase (Prim).
            page.goto(f"{base_url}/graph/graph/expansion-minima", wait_until="networkidle")
            page.select_option("#graph-algorithm-select", "run_prim")
            page.fill("#g-alg-field-start", "1")
            _enable_manual_mode(page, "graph")
            with page.expect_response(_graph_operate_response) as operation_response:
                page.click("#graph-sim-play")
            _finish_manual_trace(page, "graph")
            result_response = operation_response.value
            assert result_response.status == 200
            result_data = result_response.json()
            assert result_data["success"] is True
            expected_history.append({'operation': 'run_prim', 'payload': {'start': '1'}})
            assert ui_requests == expected_history[8:]
            _assert_graph_fixture(result_data["visual_state"], result_data["history"],
                                  vertices, edges, expected_history)
            _assert_graph_fixture(page.evaluate("() => window.GRAPH_VIEW_MODEL.visual_state"),
                                  result_data["history"], vertices, edges, expected_history)
            _wait_status_contains(page, "#graph-message-box", "grafo_prim")

            assert len(expected_history) == 11
            page.remove_listener("request", record_ui_operation)
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

            vertices = [str(v) for v in range(1, 9)]
            edges = ring_edges + extra_edges
            expected_history = _seed_graph_via_public_api(page, base_url, vertices, edges[:-1])
            assert len(expected_history) == 18
            ui_requests = []

            def record_ui_operation(request):
                if request.method == "POST" and request.url.split("?", 1)[0].endswith("/graph/graph/operate"):
                    body = request.post_data_json
                    assert set(body) == {"operation", "payload", "execution_mode"}
                    assert body["execution_mode"] == "step"
                    ui_requests.append({key: body[key] for key in ("operation", "payload")})

            page.on("request", record_ui_operation)
            origin, target, weight = edges[-1]
            page.select_option("#graph-operation-select", "insert_edge")
            page.wait_for_selector("#g-op-field-origin", timeout=5000)
            page.fill("#g-op-field-origin", origin)
            page.fill("#g-op-field-target", target)
            page.fill("#g-op-field-weight", weight)
            _enable_manual_mode(page, "graph")
            with page.expect_response(_graph_operate_response) as operation_response:
                page.click("#graph-sim-play")
            _wait_graph_mutation_final(page, "arista")
            result_response = operation_response.value
            assert result_response.status == 200
            result_data = result_response.json()
            assert result_data["success"] is True
            expected_history.append({"operation": "insert_edge", "payload": {
                "origin": origin, "target": target, "weight": weight}})
            assert len(expected_history) == 19
            assert ui_requests == expected_history[18:]
            _assert_graph_fixture(result_data["visual_state"], result_data["history"],
                                  vertices, edges, expected_history)
            _assert_graph_fixture(page.evaluate("() => window.GRAPH_VIEW_MODEL.visual_state"),
                                  result_data["history"], vertices, edges, expected_history)
            # JS export observes geometry/format/size, not the download button or pixel equality.

            result_text = page.text_content("#graph-visual-state") or ""
            assert "Vértices" in result_text
            assert "Aristas" in result_text

            # Classroom mode initially fits the graph. On a narrow viewport,
            # retain native 100% glyph size and verify export includes overflow.
            # Export deliberately normalizes live zoom; do not compare an image
            # at native scale with zoom-enlarged display pixels.
            page.set_viewport_size({"width": 390, "height": 900})
            page.locator(".graph-primary-workspace .classroom-view-tools").get_by_role("button", name="100%", exact=True).click()
            graph_target = page.locator("#graph-visual-state")
            page.wait_for_function("() => {const el=document.querySelector('#graph-visual-state');return el.scrollWidth > el.clientWidth;}")
            assert graph_target.evaluate("el => el.scrollWidth > el.clientWidth"), graph_target.evaluate("""el => ({
                width:el.clientWidth, scroll:el.scrollWidth,
                svg:[...el.querySelectorAll('svg')].map(n=>({viewBox:n.getAttribute('viewBox'),width:n.getBoundingClientRect().width,style:n.getAttribute('style')})),
                wrappers:[...el.querySelectorAll('.viz-canvas,.viz-stage,.viz-stage-center')].map(n=>({class:n.className,client:n.clientWidth,scroll:n.scrollWidth,overflow:getComputedStyle(n).overflow})),
                zoom:document.querySelector('.graph-primary-workspace .classroom-view-tools output')?.textContent
            })""")

            export_meta = page.evaluate(
                """
                async () => {
                  const target = document.querySelector('#graph-visual-state');
                  const before = {
                    clientWidth: target.clientWidth,
                    clientHeight: target.clientHeight,
                    scrollWidth: target.scrollWidth,
                    scrollHeight: target.scrollHeight,
                    nativeWidth: Math.max(...Array.from(target.querySelectorAll('svg'), svg => svg.viewBox.baseVal.width)),
                    nativeHeight: Math.max(...Array.from(target.querySelectorAll('svg'), svg => svg.viewBox.baseVal.height)),
                    resultText: target.querySelector('.graph-current-result').textContent,
                  };
                  // Observe the actual scene passed to the rasterizer, not an
                  // independently rebuilt expected graph or zoomed pixel size.
                  let serialized = '';
                  const originalSerialize = XMLSerializer.prototype.serializeToString;
                  let result;
                  try {
                    XMLSerializer.prototype.serializeToString = function(node) {
                      serialized = originalSerialize.call(this, node);
                      return serialized;
                    };
                    result = await window.InterpreterRuntime.exportVisualStateAsJpg({target, quality: 0.92, scale: 1});
                  } finally {
                    XMLSerializer.prototype.serializeToString = originalSerialize;
                  }
                  const scene = new DOMParser().parseFromString(serialized, 'application/xml');
                  const decoded = new Image();
                  await new Promise((resolve, reject) => {
                    decoded.onload = resolve;
                    decoded.onerror = reject;
                    decoded.src = result.dataUrl;
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
                      sceneNodes: scene.querySelectorAll('circle.viz-graph-node').length,
                      resultText: scene.querySelector('.graph-current-result')?.textContent,
                      sceneText: scene.documentElement.textContent,
                      decodedWidth: decoded.naturalWidth,
                      decodedHeight: decoded.naturalHeight,
                    },
                  };
                }
                """,
            )

            assert int(export_meta["before"]["scrollWidth"]) > int(export_meta["before"]["clientWidth"])
            assert int(export_meta["exported"]["width"]) >= int(export_meta["before"]["nativeWidth"]) > 0
            assert int(export_meta["exported"]["height"]) >= int(export_meta["before"]["nativeHeight"]) > 0
            assert export_meta["exported"]["sceneNodes"] == len(vertices)
            assert export_meta["exported"]["resultText"] == export_meta["before"]["resultText"]
            assert "Vértices" in export_meta["exported"]["sceneText"] and "Aristas" in export_meta["exported"]["sceneText"]
            assert export_meta["exported"]["decodedWidth"] == export_meta["exported"]["width"]
            assert export_meta["exported"]["decodedHeight"] == export_meta["exported"]["height"]
            assert str(export_meta["exported"]["dataPrefix"]).startswith("data:image/jpeg;base64,")
            assert int(export_meta["exported"]["dataLength"]) > 5000

            page.remove_listener("request", record_ui_operation)
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
    """Restored education keeps one guided/comparison control and responsive code views."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(f"{base_url}/hierarchical/avl", wait_until="networkidle")
            assert page.locator("#hier-guided-example").count() == 1
            assert page.locator("#hier-compare-kind").count() == 1
            page.fill("#h-field-value", "30")
            page.click("#hier-step-mode")
            with page.expect_response(lambda response: response.request.method == "POST"
                                      and response.url.split("?", 1)[0].endswith("/hierarchical/avl/operate")) as prepared:
                page.click("#hier-sim-step")
            assert prepared.value.status == 200
            first_frame = prepared.value.json()["execution_trace"]["steps"][0]["pedagogy"]
            assert first_frame["instruction_event"]["phase"] == "caller_enter"
            _wait_status_contains(page, "#hier-sim-counter", "Paso: 1/")
            cursor = page.text_content("#hier-sim-counter")
            assert page.text_content("#hier-sim-counter") == cursor
            summary = (page.text_content("#hier-pedagogy-summary") or "").lower()
            assert "llamador equivalente" in summary and "no hay resultado futuro" in summary
            page.set_viewport_size({"width": 390, "height": 844})
            page.click('[data-hier-tab="code"]')
            assert page.is_visible("#hier-code-region") is True
            page.click('[data-hier-tab="visual"]')
            assert page.is_visible("#hier-visual-region") is True
            assert page.text_content("#hier-sim-counter") == cursor
            browser.close()


def test_playwright_hierarchical_comparison_practice_keyboard_and_accessibility() -> None:
    """Restored comparison/practice coexist with keyboard navigation of cached steps."""
    import re

    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
            page.goto(f"{base_url}/hierarchical/avl", wait_until="networkidle")
            assert page.locator("#hier-compare-kind").count() == 1
            assert page.locator("#hier-practice-mode").count() == 1
            page.fill("#h-field-value", "25")
            page.click("#hier-step-mode")
            checkpoint("manual_prepare_start", module="hier")
            with page.expect_response(lambda response: response.request.method == "POST"
                                      and response.url.split("?", 1)[0].endswith("/hierarchical/avl/operate")) as prepared:
                page.click("#hier-sim-step")
            assert prepared.value.status == 200
            assert prepared.value.json().get("success") is True
            page.wait_for_function(r"""() => {
                const match = document.querySelector('#hier-sim-counter')?.textContent.trim().match(/^Paso:\s*(\d+)\s*\/\s*(\d+)$/);
                return match && Number(match[1]) > 0 && Number(match[1]) < Number(match[2])
                    && !document.querySelector('#hier-sim-step')?.disabled;
            }""")
            before = page.text_content("#hier-sim-counter") or ""
            match = re.fullmatch(r"Paso:\s*(\d+)\s*/\s*(\d+)", before.strip())
            assert match is not None
            current, total = map(int, match.groups())
            checkpoint("manual_navigation", module="hier", navigation_index=0, counter=before)
            page.locator("body").press("ArrowRight")
            page.wait_for_function(r"""([expected, total]) => {
                const match = document.querySelector('#hier-sim-counter')?.textContent.trim().match(/^Paso:\s*(\d+)\s*\/\s*(\d+)$/);
                return match && Number(match[1]) === expected && Number(match[2]) === total;
            }""", arg=[current + 1, total])
            after = page.text_content("#hier-sim-counter") or ""
            checkpoint("manual_navigation", module="hier", navigation_index=1, counter=after)
            assert page.text_content("#hier-sim-counter") != before
            assert re.fullmatch(r"Paso:\s*(\d+)\s*/\s*(\d+)", after.strip()).groups() == (str(current + 1), str(total))
            page.locator("body").press("Home")
            page.wait_for_function(r"""total => {
                const match = document.querySelector('#hier-sim-counter')?.textContent.trim().match(/^Paso:\s*(\d+)\s*\/\s*(\d+)$/);
                return match && Number(match[1]) === 0 && Number(match[2]) === total;
            }""", arg=total)
            checkpoint("manual_navigation", module="hier", navigation_index=2, counter=page.text_content("#hier-sim-counter") or "")
            assert "Paso: 0/" in (page.text_content("#hier-sim-counter") or "")
            assert page.locator("#hier-sim-prev").is_visible()
            assert page.locator("#hier-sim-step").is_visible()
            checkpoint("manual_finish_end", module="hier", counter=page.text_content("#hier-sim-counter") or "")
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
            assert page.locator(".seq-execute").evaluate("el => el.classList.contains('classroom-execution-controls') && el.nextElementSibling.classList.contains('sequential-primary-workspace')")
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
    """Observe distinct real C families while live, then enforce ended scopes."""
    playwright_mod = pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base_url:
        with playwright_mod.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(f"{base_url}/sorting/visualizador", wait_until="networkidle")
            expected = {
                "seleccion": "Mínimo provisional",
                "insercion": "Clave:",
                "burbuja": "Pasada:",
                "shell": "Intervalo:",
                "quicksort": "Pivote local:",
                "mergesort": "Division/fusion activa",
                "heapsort": "hijos:",
                "counting_sort": "Frecuencias",
                "binsort": "Frecuencias",  # The real C wrapper delegates Counting; no invented urnas.
                "radixsort": "Magnitudes uint32_t",
            }
            local_names = {
                "seleccion": {"i", "j", "indice_menor"},
                "insercion": {"i", "j", "clave"},
                "burbuja": {"i", "j", "hubo_intercambio"},
                "shell": {"intervalo", "i", "j", "temporal"},
                "quicksort": {"primero", "ultimo", "i", "j", "pivote"},
                "mergesort": {"izquierda", "medio", "derecha", "i", "j", "k"},
                "heapsort": {"i", "raiz", "mayor", "izquierdo", "derecho"},
                "counting_sort": {"minimo", "maximo", "rango", "i", "indice"},
                "binsort": {"minimo", "maximo", "rango", "i", "indice"},
                "radixsort": {"i", "indice", "maximo", "exp", "magnitud", "valor", "digito"},
            }
            assert len(expected) == 10
            for algorithm, marker in expected.items():
                # Every family receives the original mixed input, not its predecessor's sorted array.
                page.fill("#sorting-manual-values", "5,-3,0,2,1")
                page.click("#sorting-create-array")
                _wait_status_contains(page, "#sorting-message-box", "Arreglo creado")
                assert page.locator(".sorting-zero-axis").count() == 5
                assert page.locator(".sorting-item-bar.is-negative").count() == 1
                assert page.locator(".sorting-item-bar.is-zero").count() == 1
                assert [int(text.split("]", 1)[1]) for text in page.locator(".sorting-item-label").all_text_contents()] == [5, -3, 0, 2, 1]
                page.select_option("#sorting-algorithm", algorithm)
                _enable_manual_mode(page, "sorting")
                seen = {"family": False, "active_scope": False, "countLive": False,
                        "heapChildren": False, "radixLive": False, "radixCounts": False,
                        "cursor": None, "total": None}

                def observe_frame(current, total):
                    if seen["cursor"] is None:
                        assert current == 0
                        seen["total"] = total
                    else:
                        assert current == seen["cursor"] + 1 and total == seen["total"]
                    seen["cursor"] = current
                    frame = _sorting_frame_observation(page)
                    active = bool(frame["stack"].strip()) and "Sin llamadas activas." not in frame["stack"]
                    seen["active_scope"] |= active
                    seen["family"] |= active and marker in frame["text"]
                    for field in ("countLive", "heapChildren", "radixLive", "radixCounts"):
                        seen[field] |= active and frame[field]

                page.click("#sorting-sim-play")
                _finish_manual_trace(page, "sorting", observe=observe_frame)
                assert seen["cursor"] == seen["total"]
                assert seen["active_scope"] and seen["family"], algorithm
                page.wait_for_function("() => (document.querySelector('#sorting-call-stack')?.textContent || '').includes('Sin llamadas activas.')")
                final = _sorting_frame_observation(page)
                assert "Sin llamadas activas." in final["stack"]
                assert not (set(final["variables"]) & local_names[algorithm]), algorithm
                assert [int(text.split("]", 1)[1]) for text in page.locator(".sorting-item-label").all_text_contents()] == [-3, 0, 1, 2, 5]
                assert page.locator(".sorting-zero-axis").count() == 5
                assert page.locator(".sorting-item-bar.is-negative").count() == 1
                assert page.locator(".sorting-item-bar.is-zero").count() == 1
                if algorithm == "burbuja":
                    strategy = page.text_content("#sorting-strategy-view") or ""
                    assert "Retorno void al caller" in strategy
                    assert "j: —" in strategy and "hubo_intercambio: —" in strategy
                elif algorithm == "heapsort":
                    assert seen["heapChildren"]
                    assert final["heapN"] == "0" and final["suffixCount"] == 5
                elif algorithm in {"counting_sort", "binsort"}:
                    assert seen["countLive"]
                    assert not final["countLive"] and final["countReleased"] and final["countCells"] == 0
                    assert "Conteo liberado; sin lectura de memoria." in final["text"]
                elif algorithm == "radixsort":
                    assert seen["radixLive"] and seen["radixCounts"]
                    assert not final["radixLive"] and final["radixCells"] == 0 and not final["radixCounts"]
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
            results = page.locator("#sorting-export-summary").locator("xpath=ancestor::details")
            for panel in results.all():
                if panel.get_attribute("open") is None:
                    panel.locator(":scope > summary").click()
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
            results = page.locator("#hash-export-summary").locator("xpath=ancestor::details")
            for panel in results.all():
                if panel.get_attribute("open") is None:
                    panel.locator(":scope > summary").click()
            with page.expect_download() as download_info:
                page.click("#hash-export-summary")
            assert download_info.value.suggested_filename.endswith(".json")
            browser.close()

