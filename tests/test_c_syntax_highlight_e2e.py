"""Finite browser evidence for all code readers, independent of title or updates."""
import json
import os
import threading
from pathlib import Path

import pytest
from werkzeug.serving import WSGIRequestHandler, make_server
from app import create_app

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def browser_env(tmp_path_factory):
    from playwright.sync_api import sync_playwright
    class Quiet(WSGIRequestHandler):
        def log_request(self, *args, **kwargs):
            pass
    app = create_app()
    app.config.update(TESTING=True, SECRET_KEY="syntax-test-only")
    server = make_server("127.0.0.1", 0, app, request_handler=Quiet)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    output = Path(os.environ.get("VISUALSTRUCT_SYNTAX_EVIDENCE_DIR", str(tmp_path_factory.mktemp("syntax"))))
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        yield browser, f"http://127.0.0.1:{server.server_port}", output
        browser.close()
    server.shutdown()
    thread.join(timeout=5)


def _page(browser, base):
    context = browser.new_context(viewport={"width": 1440, "height": 1000})
    context.grant_permissions(["clipboard-read", "clipboard-write"], origin=base)
    context.add_init_script("localStorage.setItem('didactic-mode','full')")
    context.add_init_script("""const original=navigator.clipboard.writeText.bind(navigator.clipboard);
      navigator.clipboard.writeText=text=>{window.__copiedSource=text;return original(text);};""")
    page = context.new_page()
    return context, page


def _readers(page):
    return page.evaluate("""() => [...document.querySelectorAll('pre.didactic-code,pre.didactic-history-main')].map(p=>({
      id:p.id,classes:p.className,syntax:p.dataset.cSyntax,
      tokens:p.querySelectorAll('[class^="code-"]:not(.code-line)').length,
      text:ClassroomView.sourceText(p),raw:p.dataset.rawCode,
      colors:[...new Set([...p.querySelectorAll('.code-type,.code-keyword,.code-function')].map(n=>getComputedStyle(n).color))]
    }))""")


def _assert_readers(page):
    page.wait_for_function("() => window.CSyntax && [...document.querySelectorAll('pre.didactic-code,pre.didactic-history-main')].every(p=>p.dataset.cSyntax==='c')")
    rows = _readers(page)
    assert rows
    for row in rows:
        if row["text"].strip():
            assert row["tokens"] > 0, row
        if row["raw"] is not None:
            assert row["text"] == row["raw"].replace("\r\n", "\n"), row["id"]
    return rows


def test_initial_inventory_help_and_safe_dynamic_readers(browser_env):
    browser, base, output = browser_env
    context, page = _page(browser, base)
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    inventory = []
    groups = {"sequential": ["stack", "queue", "priority_queue", "linked_list", "circular_list", "sublist"],
              "hierarchical": ["abb", "avl", "red_black", "binary_heap"], "graph": ["graph"], "hash": ["hash_table"]}
    routes = [(f"/{group}/{name}", f"/help/{group}/{name}") for group, names in groups.items() for name in names]
    routes.append(("/sorting/visualizador", "/help/sorting/sorting_array"))
    for structure, help_page in routes:
        for url in (structure, help_page):
            response = page.goto(base + url, wait_until="networkidle")
            assert response.status == 200, url
            rows = _assert_readers(page)
            inventory.append({"url": url, "readers": [{k: v for k, v in row.items() if k not in {"text", "raw"}} for row in rows]})
    page.goto(base + "/help/manual", wait_until="networkidle")
    _assert_readers(page)
    page.screenshot(path=str(output / "syntax-help.png"), full_page=True)
    # Hostile source stays literal; CRLF/tabs, rows/listeners/classes and scroll survive.
    source = '#include <stdio.h>\r\nint main(void) {\r\n\tprintf("<img src=x onerror=window.__unsafe=1>"); /* safe */\r\n}\r\n'
    page.evaluate("""source => {
      const p=document.createElement('pre');p.id='syntax-probe';p.className='didactic-code';p.style.cssText='width:260px;height:80px;overflow:auto;white-space:pre';
      p.dataset.rawCode=source;p.textContent=source;document.body.append(p);
      const q=document.createElement('pre');q.id='syntax-lines';q.className='didactic-code';
      const line=document.createElement('span');line.className='code-line sim-active';line.dataset.line='7';line.setAttribute('aria-label','instruction');
      line.textContent='\treturn 42;';line.addEventListener('click',()=>window.__rowClicked=true);q.append(line);document.body.append(q);window.__originalLine=line;
    }""", source)
    page.wait_for_function("() => document.querySelector('#syntax-probe .code-type') && document.querySelector('#syntax-lines .code-keyword')")
    assert page.locator("#syntax-probe").text_content() == source
    assert page.locator("#syntax-probe img").count() == 0
    assert page.evaluate("() => !window.__unsafe && document.querySelector('#syntax-probe').dataset.rawCode") == source
    assert page.evaluate("() => document.querySelector('#syntax-lines .code-line')===window.__originalLine && window.__originalLine.classList.contains('sim-active') && window.__originalLine.dataset.line==='7'")
    page.locator("#syntax-lines .code-keyword").click()
    assert page.evaluate("() => window.__rowClicked")
    # Replace existing source with the same text: it must recolor again, without loops.
    page.evaluate("""() => {const p=document.querySelector('#syntax-probe');p.scrollLeft=80;window.__scroll=p.scrollLeft;p.textContent=p.dataset.rawCode;
      window.__changes=0;new MutationObserver(()=>window.__changes++).observe(p,{childList:true,subtree:true});}""")
    page.wait_for_function("() => document.querySelector('#syntax-probe .code-type')")
    page.evaluate("() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))")
    count = page.evaluate("() => window.__changes")
    page.evaluate("() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))")
    assert page.evaluate("() => window.__changes") == count
    assert page.evaluate("() => document.querySelector('#syntax-probe').scrollLeft===window.__scroll")
    assert not errors, errors
    (output / "inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    context.close()


@pytest.mark.parametrize("family", ["seq", "hier", "graph", "hash", "sorting"])
def test_real_operations_navigation_tabs_copy_and_enlargement(browser_env, family):
    browser, base, output = browser_env
    context, page = _page(browser, base)
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    route = {"seq": "/sequential/stack", "hier": "/hierarchical/abb", "graph": "/graph/graph", "hash": "/hash/hash_table", "sorting": "/sorting/visualizador"}[family]
    page.goto(base + route, wait_until="networkidle")
    if family == "sorting":
        assert page.request.post(base + "/api/ordenamiento/create-array", data={"values": "3,1,2"}).status == 200
        page.reload(wait_until="networkidle")
        page.select_option("#sorting-algorithm", "quicksort")
    elif family == "hash":
        page.select_option("#hash-operation-select", "create_table")
        page.locator("#hash-field-capacity").fill("5")
    elif family == "graph":
        page.select_option("#graph-operation-select", "insert_vertex")
        page.locator('input[id$="-vertex"]').fill("7")
    else:
        page.select_option("#operation-select", "apilar" if family == "seq" else "insertar")
        page.fill("#field-value" if family == "seq" else "#h-field-value", "7")
    _assert_readers(page)
    toggle = f"#{family}-step-mode" if family in {"seq", "hier"} else f"#{family}-sim-step"
    page.click(toggle)
    execute = "#seq-sim-execute" if family == "seq" else f"#{family}-sim-play"
    with page.expect_response(lambda response: response.request.method == "POST" and ("/operate" in response.url or "/ordenamiento/run" in response.url)) as observed:
        page.click(execute)
    assert observed.value.status == 200
    assert observed.value.json()["success"] is True
    counter = f"#{family}-sim-counter"
    page.wait_for_function("s=>Number((document.querySelector(s).textContent||'0/0').split('/').pop())>0", arg=counter)
    panel = "#sorting-code" if family == "sorting" else "#op-pseudocode"
    _assert_readers(page)
    page.evaluate("s=>window.__sourceRows=[...document.querySelector(s).querySelectorAll('.code-line')]", panel)
    next_button = f"#{family}-sim-step" if family in {"seq", "hier"} else f"#{family}-sim-next"
    before = page.locator(counter).inner_text()
    page.click(next_button)
    page.wait_for_function("o=>document.querySelector(o.s).textContent!==o.before", arg={"s": counter, "before": before})
    _assert_readers(page)
    page.click(f"#{family}-sim-prev")
    _assert_readers(page)
    assert page.evaluate("s=>[...document.querySelector(s).querySelectorAll('.code-line')].every((n,i)=>n===window.__sourceRows[i])", panel)
    # Existing user-facing copy and enlarged reader retain the actual source.
    source = page.evaluate("s=>ClassroomView.sourceText(document.querySelector(s))", panel)
    actions = page.locator(panel).locator("..").locator(".classroom-code-actions").first
    actions.get_by_role("button", name="Copiar C", exact=True).click()
    assert page.evaluate("() => window.__copiedSource") == source
    # The Windows clipboard platform converts LF to CRLF; the application input
    # to writeText above must still be byte-for-byte unchanged.
    assert page.evaluate("() => navigator.clipboard.readText()").replace("\r\n", "\n") == source.replace("\r\n", "\n")
    actions.get_by_role("button", name="Ampliar", exact=True).click()
    assert page.locator("dialog " + panel).is_visible()
    _assert_readers(page)
    page.screenshot(path=str(output / f"syntax-{family}-expanded.png"))
    page.get_by_role("button", name="Cerrar ampliación", exact=True).click()
    page.locator("dialog").wait_for(state="detached")
    assert page.locator("dialog").count() == 0
    page.get_by_role("tab", name="main.c del historial", exact=True).click()
    _assert_readers(page)
    page.wait_for_function("() => document.querySelector('pre.didactic-history-main')?.closest('[data-raw-code]')?.dataset.rawCode.includes('main')")
    main_source = page.evaluate("() => document.querySelector('pre.didactic-history-main').closest('[data-raw-code]').dataset.rawCode")
    structure = {"seq": "stack", "hier": "abb", "graph": "graph", "hash": "hash_table", "sorting": "sorting_array"}[family]
    main_panel = page.locator('[role="tabpanel"]').filter(has=page.locator("pre.didactic-history-main")).first
    main_panel.get_by_role("button", name="Copiar C", exact=True).click()
    assert page.evaluate("() => window.__copiedSource") == main_source
    # Hierarchical main is an existing copy-only caller; there is no /abb/main
    # download route. Verify its real TAD download instead of inventing a URL.
    download = page.request.get(base + f"/help/source/{structure}/" + ("source" if family == "hier" else "main"))
    assert download.status == 200
    expected = (Path(__file__).resolve().parents[1] / "docs/tads_C/tad_abb.c").read_bytes() if family == "hier" else main_source.encode("utf-8")
    assert download.body() == expected
    page.get_by_role("tab", name="Estructura del TAD", exact=True).click()
    _assert_readers(page)
    mains = page.locator("pre.didactic-history-main")
    if mains.count():
        assert mains.first.locator(".code-type,.code-directive").count() > 0
    # A real operation switch redraws readers; reset must not leave stale tokens.
    select = page.locator("#sorting-algorithm" if family == "sorting" else "#hash-operation-select" if family == "hash" else "#graph-operation-select" if family == "graph" else "#operation-select")
    options = select.locator("option").evaluate_all("nodes=>nodes.map(n=>n.value)")
    alternative = next(value for value in options if value != select.input_value())
    select.select_option(alternative)
    _assert_readers(page)
    page.on("dialog", lambda dialog: dialog.accept())
    reset = "#sorting-reset" if family == "sorting" else "#reset-button" if family in {"seq", "hier"} else f"#{family}-reset-button"
    with page.expect_response(lambda response: response.request.method == "POST" and "reset" in response.url):
        page.click(reset)
    _assert_readers(page)
    assert not errors, errors
    context.close()


def test_baseline_and_fixed_sorting_main_screenshots(browser_env):
    browser, base, output = browser_env
    context, page = _page(browser, base)
    context.route("**/js/c_syntax_highlight.js*", lambda route: route.abort())
    assert page.request.post(base + "/api/ordenamiento/create-array", data={"values": "3,1,2"}).status == 200
    page.goto(base + "/sorting/visualizador", wait_until="networkidle")
    page.get_by_role("tab", name="main.c del historial", exact=True).click()
    before = page.locator("pre.didactic-history-main").locator(".code-type,.code-keyword,.code-function").count()
    raw = page.evaluate("() => ClassroomView.sourceText(document.querySelector('pre.didactic-history-main'))")
    page.locator("pre.didactic-history-main").screenshot(path=str(output / "syntax-sorting-main-before.png"))
    context.unroute("**/js/c_syntax_highlight.js*")
    page.reload(wait_until="networkidle")
    page.get_by_role("tab", name="main.c del historial", exact=True).click()
    _assert_readers(page)
    after = page.locator("pre.didactic-history-main").locator(".code-type,.code-keyword,.code-function").count()
    assert before == 0 and after > 0, (before, after)
    assert page.evaluate("() => ClassroomView.sourceText(document.querySelector('pre.didactic-history-main'))") == raw
    page.locator("pre.didactic-history-main").screenshot(path=str(output / "syntax-sorting-main-after.png"))
    (output / "before-after.json").write_text(json.dumps({"sorting_main_tokens_before": before, "after": after, "source_unchanged": True}), encoding="utf-8")
    context.close()


def test_accented_title_dynamic_renderer_and_plain_stdout(browser_env):
    browser, base, _ = browser_env
    context, page = _page(browser, base)
    page.goto(base + "/sequential/queue", wait_until="networkidle")
    source = 'int value = 7;\nreturn value;\n'
    before = page.evaluate("""source => {
      const p=document.createElement('pre');p.id='title-probe';p.className='didactic-code';document.body.append(p);
      InterpreterRuntime.renderCode(p,source,'Código C: título con acento');
      window.__titleRows=[...p.querySelectorAll('.code-line')];
      const out=document.createElement('pre');out.id='stdout-probe';out.className='console-screen';
      const code=document.createElement('code');code.textContent=source;out.append(code);document.body.append(out);
      return p.querySelectorAll('.code-type,.code-keyword').length;
    }""", source)
    assert before == 0  # Existing title-gated producer; common reader fixes it.
    page.wait_for_function("() => document.querySelector('#title-probe .code-type')")
    assert page.locator('#title-probe').locator('.code-line').all_text_contents() == source.split('\n')
    assert page.evaluate("() => document.querySelector('#title-probe').dataset.rawCode") == source
    assert page.evaluate("() => [...document.querySelectorAll('#title-probe .code-line')].every((n,i)=>n===window.__titleRows[i])")
    assert page.locator('#stdout-probe').text_content() == source
    assert page.locator('#stdout-probe span').count() == 0
    context.close()
