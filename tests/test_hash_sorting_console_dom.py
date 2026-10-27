"""Finite full-page Chromium checks for real Hash and Sorting caller stdout."""
from contextlib import contextmanager
from threading import Thread
import pytest
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server
from app import create_app
from app.config import Config

pytestmark = pytest.mark.e2e


@contextmanager
def _server(tmp_path):
    class LocalConfig(Config):
        TESTING = True
        SECRET_KEY = "isolated-hash-sorting-console-test"
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


def _exercise(page, tmp_path, base, family, run_path, reset_path):
    console_id = f"{family}-printf-console"
    console = page.locator("#" + console_id)
    page.wait_for_function("id=>document.getElementById(id)?.dataset.consoleCopy!==undefined", arg=console_id)
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))

    def expect_text(expected):
        try:
            page.wait_for_function("([id,s])=>document.getElementById(id).dataset.consoleCopy===s", arg=[console_id, expected], timeout=5000)
        except Exception:
            page.screenshot(path=str(tmp_path / f"{family}-failure.png"), full_page=True)
            pytest.fail(f"{family}: expected={expected!r}; actual={console.get_attribute('data-console-copy')!r}; errors={errors!r}")
        if expected:
            assert console.text_content() == expected

    results = []
    for _ in range(2):
        with page.expect_response("**" + run_path, timeout=10000) as pending:
            page.locator(f"#{family}-sim-play").dispatch_event("click")
        data = pending.value.json()
        assert data["success"]
        assert isinstance(data.get("console_output"), str) and data["console_output"]
        expect_text(data["console_output"])
        results.append(data)
    first, second = results
    assert second["console_output"].startswith(first["console_output"])
    assert len(second["console_output"]) > len(first["console_output"])
    trace = second["execution_trace"]
    prefix = trace["console_prefix"]
    assert isinstance(prefix, str)
    assert all(isinstance(step.get("console_stdout"), str) for step in trace["steps"])
    assert prefix + trace["steps"][-1]["console_stdout"] == second["console_output"]
    posts = []
    page.on("request", lambda request: posts.append(request.url) if request.method == "POST" else None)

    # Constrain only presentation height; every displayed byte still comes from
    # these real API operations. Do not manufacture repeated output for scroll.
    console.evaluate("el=>{el.style.height='32px';el.style.minHeight='0';el.style.maxHeight='32px';}")
    assert console.evaluate("el=>el.scrollHeight>el.clientHeight+5")
    console.evaluate("el=>{el.scrollTop=1;}")
    page.locator(f"#{family}-sim-step").dispatch_event("click")
    expect_text(prefix)
    assert console.evaluate("el=>el.scrollTop") == 1

    # Walk the real current trace: stdout at every cursor is exact, not a
    # fabricated query/result message. No navigation may execute a new caller.
    for cursor, step in enumerate(trace["steps"]):
        page.locator(f"#{family}-sim-next").dispatch_event("click")
        expect_text(prefix + step["console_stdout"])
    assert console.evaluate("el=>el.scrollTop") == 1
    for cursor in range(len(trace["steps"]) - 2, -2, -1):
        page.locator(f"#{family}-sim-prev").dispatch_event("click")
        expect_text(prefix + (trace["steps"][cursor]["console_stdout"] if cursor >= 0 else ""))

    # Replay with the existing manual controls, preserving the historical
    # prefix and legitimate repeats without adding another POST.
    for step in trace["steps"]:
        page.locator(f"#{family}-sim-next").dispatch_event("click")
        expect_text(prefix + step["console_stdout"])
    assert posts == []
    page.locator(f"#{family}-sim-step").dispatch_event("click")
    expect_text(second["console_output"])
    page.locator(f"#{family}-sim-step").dispatch_event("click")
    expect_text(prefix)
    console.evaluate("el=>{el.scrollTop=el.scrollHeight;}")
    page.locator(f"#{family}-sim-step").dispatch_event("click")
    expect_text(second["console_output"])
    assert console.evaluate("el=>el.scrollHeight-el.clientHeight-el.scrollTop") <= 4
    assert posts == []

    # Backend reconstruction must survive removing the optional observed cache.
    page.evaluate("sessionStorage.clear()")
    page.reload()
    expect_text(second["console_output"])
    if family == "hash":
        # A missing key still executes the authentic caller: success=False
        # must not suppress its initialized found-flag stdout or read output.
        page.locator("#hash-field-key").fill("99")
        with page.expect_response("**" + run_path, timeout=10000) as pending:
            page.locator("#hash-sim-play").dispatch_event("click")
        missing = pending.value.json()
        assert missing["execution_trace"]["steps"]
        assert missing["console_output"].startswith(second["console_output"])
        assert missing["console_output"].endswith("get:99:0\n")
        expect_text(missing["console_output"])
        page.evaluate("sessionStorage.clear()")
        page.reload()
        expect_text(missing["console_output"])
    page.screenshot(path=str(tmp_path / f"{family}-console-history.png"), full_page=True)
    page.on("dialog", lambda dialog: dialog.accept())
    with page.expect_response("**" + reset_path, timeout=10000) as pending:
        page.locator("#hash-reset-button" if family == "hash" else "#sorting-reset").dispatch_event("click")
    assert pending.value.json()["success"]
    expect_text("")
    page.reload()
    expect_text("")
    assert not errors


def test_hash_real_caller_console_dom(tmp_path):
    with _server(tmp_path) as base, sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        path = "/hash/hash_table/operate"
        for operation, payload in [("create_table", {"capacity": 3}), ("insert", {"key": "1", "value": "10"})]:
            response = page.request.post(base + path, data={"operation": operation, "payload": payload})
            assert response.ok and response.json()["success"]
        page.goto(base + "/hash/hash_table")
        page.locator("#hash-operation-select").select_option("get")
        page.locator("#hash-field-key").fill("1")
        _exercise(page, tmp_path, base, "hash", path, "/hash/hash_table/reset")
        browser.close()


def test_sorting_real_caller_console_dom(tmp_path):
    with _server(tmp_path) as base, sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        response = page.request.post(base + "/api/ordenamiento/create-array", data={"values": "2,1"})
        assert response.ok and response.json()["success"]
        page.goto(base + "/sorting/visualizador")
        assert page.locator("#sorting-algorithm").input_value() == "burbuja"
        _exercise(page, tmp_path, base, "sorting", "/api/ordenamiento/run", "/api/ordenamiento/reset")
        browser.close()
