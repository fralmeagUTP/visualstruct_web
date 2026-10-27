"""Real full-page Chromium checks for observed List/ABB stdout history."""
from threading import Thread
import pytest
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server
from app import create_app
from app.config import Config

pytestmark = pytest.mark.e2e


def _stdout(trace, cursor):
    if cursor < 0:
        return ""
    step = trace["steps"][cursor]
    if isinstance(step.get("console_stdout"), str):
        return step["console_stdout"]
    memory = (step.get("pedagogy") or {}).get("memory_state") or {}
    if isinstance(memory.get("console_stdout"), str):
        return memory["console_stdout"]
    if trace.get("console_mode") == "snapshot":
        return "\n".join(step.get("console") or [])
    return "\n".join(line for row in trace["steps"][:cursor + 1] for line in row.get("console") or [])


@pytest.mark.parametrize("family,structure,seed,query,prefix,alternate", [
    ("sequential", "linked_list", "insertar_final", "buscar_elemento", "seq", "insertar_final"),
    ("hierarchical", "abb", "insertar", "inorden", "hier", "insertar"),
])
def test_observed_console_real_page_history(tmp_path, family, structure, seed, query, prefix, alternate):
    class LocalConfig(Config):
        TESTING = True
        SECRET_KEY = "isolated-family-console-test"
        SESSION_CACHE_DIR = str(tmp_path / "sessions")
    app = create_app(LocalConfig)
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            base = f"http://127.0.0.1:{server.server_port}"
            url = f"/{family}/{structure}"
            seed_response = page.request.post(base + url + "/operate", data={"operation": seed, "payload": {"value": 7}})
            assert seed_response.ok and seed_response.json()["success"]
            page.goto(base + url)
            console = page.locator(f"#{prefix}-printf-console")
            page.wait_for_function("(id)=>document.getElementById(id)?.dataset.consoleCopy !== undefined", arg=f"{prefix}-printf-console")
            select = page.locator("#operation-select")
            select.select_option(query)
            if family == "sequential":
                page.locator("#field-value").fill("7")
            toggle = page.locator(f"#{prefix}-step-toggle")
            def mode(active):
                toggle.evaluate("(el,on)=>{el.checked=on;el.dispatchEvent(new Event('change'));}", active)
            def expect_stdout(value):
                try:
                    page.wait_for_function("([id,s])=>document.getElementById(id).dataset.consoleCopy===s", arg=[f"{prefix}-printf-console", value], timeout=3000)
                except Exception:
                    page.screenshot(path=str(tmp_path / f"{prefix}-failure.png"), full_page=True)
                    pytest.fail(f"expected={value!r}; actual={console.get_attribute('data-console-copy')!r}; errors={errors!r}; toggle={toggle.is_checked()}")
                assert console.text_content() == value if value else console.get_attribute("data-console-copy") == ""
            def execute():
                with page.expect_response("**" + url + "/operate") as pending:
                    page.locator("#operation-form").dispatch_event("submit")
                data = pending.value.json()
                assert data["success"]
                return data["execution_trace"]
            mode(False)
            first = execute()
            output = _stdout(first, len(first["steps"]) - 1)
            assert output == ("\n Encontrado en la posicion 1\n" if family == "sequential" else "7 ")
            expect_stdout(output)
            # A second normal request has a separate identity even if its
            # emitted text and trace are identical.
            second = execute()
            assert _stdout(second, len(second["steps"]) - 1) == output
            expect_stdout(output + output)
            page.reload()
            expect_stdout(output + output)
            page.on("dialog", lambda dialog: dialog.accept())
            with page.expect_response("**" + url + "/reset") as pending:
                page.locator("#reset-button").dispatch_event("click")
            assert pending.value.json()["success"]
            expect_stdout("")
            assert page.request.post(base + url + "/operate", data={"operation": seed, "payload": {"value": 7}}).json()["success"]
            page.reload()
            expect_stdout("")
            select.select_option(query)
            if family == "sequential":
                page.locator("#field-value").fill("7")
            # Manual mode starts with a newly prepared trace. Fast mode does
            # not promise to retain its frames for a later mode switch.
            mode(True)
            def prepare():
                with page.expect_response("**" + url + "/operate", timeout=5000) as pending:
                    page.locator("#operation-form" if family == "sequential" else f"#{prefix}-sim-step").dispatch_event("submit" if family == "sequential" else "click")
                data = pending.value.json()
                assert data["success"]
                return data["execution_trace"]
            active_trace = prepare()
            def finish():
                if family == "sequential":
                    page.locator("#seq-sim-end").dispatch_event("click")
                else:
                    for _ in active_trace["steps"]:
                        page.locator("#hier-sim-step").dispatch_event("click")
            def rewind():
                if family == "sequential":
                    page.locator("#seq-sim-start").dispatch_event("click")
                else:
                    for _ in active_trace["steps"]:
                        page.locator("#hier-sim-prev").dispatch_event("click")
            expect_stdout("")
            finish()
            expect_stdout(output)
            rewind()
            expect_stdout("")
            select.select_option(alternate)
            select.select_option(query)
            if family == "sequential":
                page.locator("#field-value").fill("7")
            active_trace = prepare()
            expect_stdout(output)
            finish()
            expect_stdout(output + output)
            posts = []
            page.on("request", lambda request: posts.append(request.url) if request.method == "POST" else None)
            mode(True)
            expect_stdout(output)
            page.locator(f"#{prefix}-sim-step").dispatch_event("click")
            expect_stdout(output)
            page.locator(f"#{prefix}-sim-prev").dispatch_event("click")
            expect_stdout(output)
            finish()
            expect_stdout(output + output)
            if family == "sequential":
                page.locator("#seq-sim-repeat").dispatch_event("click")
                expect_stdout(output)
                page.locator("#seq-sim-pause").dispatch_event("click")
            else:
                rewind()
                expect_stdout(output)
            finish()
            expect_stdout(output + output)
            assert posts == []
            page.reload()
            expect_stdout(output + output)
            page.screenshot(path=str(tmp_path / f"{prefix}-console-history.png"), full_page=True)
            with page.expect_response("**" + url + "/reset") as pending:
                page.locator("#reset-button").dispatch_event("click")
            assert pending.value.json()["success"]
            expect_stdout("")
            page.reload()
            expect_stdout("")
            assert not errors
            browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=5)
