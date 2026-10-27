"""Actual Chromium console rendering: cursor prefixes and manual scroll."""
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright
from app.services.graph_structure_service import GraphStructureService as Service
from test_caller_console_history import history
from app import create_app
from threading import Thread
from werkzeug.serving import make_server

pytestmark = pytest.mark.e2e
ROOT = Path(__file__).resolve().parents[1]


def test_console_cursor_replay_and_scroll(tmp_path):
    data = Service.execute_operation('graph', 'run_dijkstra', {'start': 1, 'end': 3},
                                     history([(1, 2, 2), (2, 3, 3)]))
    source = (ROOT / 'static/js/graph.js').read_text(encoding='utf8')
    functions = source[source.index('  function collectGraphPrintfLines('):source.index('  function parseJsonArray(')]
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 800, 'height': 600})
        page.set_content('<pre id="console" class="console-screen" style="width:400px"></pre>')
        page.add_style_tag(content=(ROOT / 'static/css/styles.css').read_text(encoding='utf8'))
        page.evaluate('''([functions, trace, prefix]) => {
          const printfConsole = document.getElementById('console');
          const pageState = {consoleTrace:trace, consolePrefix:prefix, consoleRawStdout:null};
          eval(functions + `\nwindow.consoleProbe = {render:refreshGraphPrintfConsole,
            setPrefix(value){pageState.consolePrefix=value;},
            raw(value){pageState.consoleTrace=null;pageState.consoleRawStdout=value;}};`);
        }''', [functions, data['execution_trace'], data['console_prefix']])
        count = len(data['execution_trace']['steps'])
        def render(cursor):
            page.evaluate('(cursor)=>consoleProbe.render(cursor)', cursor)
            return page.locator('#console').get_attribute('data-console-copy')
        assert render(-1) == data['console_prefix']
        for cursor in [0, count-1, count//2, 0, count-1, count-1]:
            expected = data['console_prefix'] + data['execution_trace']['steps'][cursor]['pedagogy']['memory_state']['console_stdout']
            assert render(cursor) == expected
        # Long presentation fixture exercises both scrollbars with real printf
        # fragments; no synthetic fragment is added by the renderer itself.
        page.evaluate('(prefix)=>consoleProbe.setPrefix(prefix)', data['console_prefix'] * 80)
        render(count-1)
        assert page.eval_on_selector('#console', 'el=>el.scrollHeight>el.clientHeight')
        page.eval_on_selector('#console', 'el=>{el.scrollTop=30;}')
        render(count-1)
        assert page.eval_on_selector('#console', 'el=>el.scrollTop') == 30
        page.eval_on_selector('#console', 'el=>{el.scrollTop=el.scrollHeight;}')
        page.evaluate('(prefix)=>consoleProbe.setPrefix(prefix)', data['console_prefix'] * 100)
        render(count-1)
        assert page.eval_on_selector('#console', 'el=>el.scrollHeight-el.clientHeight-el.scrollTop') <= 4
        page.evaluate('(prefix)=>consoleProbe.setPrefix(prefix)', data['console_stdout'].strip() * 20 + '\n')
        render(count-1)
        assert page.eval_on_selector('#console', 'el=>el.scrollWidth>el.clientWidth')
        page.screenshot(path=str(tmp_path / 'console-scroll.png'))
        page.evaluate('(stdout)=>consoleProbe.raw(stdout)', data['console_stdout'])
        assert render(-1).endswith(data['console_stdout'])
        browser.close()


def test_session_console_full_page_reload_and_replay(tmp_path):
    app = create_app()
    app.config.update(TESTING=True, SECRET_KEY='isolated-console-test')
    server = make_server('127.0.0.1', 0, app, threaded=True)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            base = f'http://127.0.0.1:{server.server_port}'
            for entry in history([(1, 2, 2), (2, 3, 3)]):
                response = page.request.post(base + '/graph/graph/operate', data={
                    'operation': entry['operation'], 'payload': entry['payload'], 'execution_mode': 'normal'})
                assert response.ok
            page.goto(base + '/graph/graph/camino-minimo')
            page.wait_for_function("document.getElementById('graph-printf-console').dataset.consoleCopy !== undefined")
            console = page.locator('#graph-printf-console')
            initial = console.get_attribute('data-console-copy')
            assert initial.count('insert_vertex: estado=0\n') == 3
            for name, value in [('start', '1'), ('end', '3')]:
                page.locator('#g-alg-field-' + name).fill(value)
            with page.expect_response('**/graph/graph/operate') as pending:
                page.locator('#graph-sim-play').dispatch_event('click')
            result = pending.value.json()
            expected = result['console_prefix'] + result['console_stdout']
            page.wait_for_function('(s)=>document.getElementById("graph-printf-console").dataset.consoleCopy===s', arg=expected)
            posts = []
            page.on('request', lambda request: posts.append(request.url) if request.method == 'POST' else None)
            # Switching the real control replays this response instead of POSTing.
            page.locator('#graph-step-toggle').evaluate("el=>{el.checked=true;el.dispatchEvent(new Event('change'));}")
            assert console.get_attribute('data-console-copy') == result['console_prefix']
            page.locator('#graph-sim-next').dispatch_event('click')
            assert console.get_attribute('data-console-copy') == result['console_prefix']
            page.locator('#graph-sim-prev').dispatch_event('click')
            assert console.get_attribute('data-console-copy') == result['console_prefix']
            page.locator('#graph-step-toggle').evaluate("el=>{el.checked=false;el.dispatchEvent(new Event('change'));}")
            assert console.get_attribute('data-console-copy') == expected
            page.locator('#graph-step-toggle').evaluate("el=>{el.checked=true;el.dispatchEvent(new Event('change'));}")
            assert console.get_attribute('data-console-copy') == result['console_prefix']
            page.locator('#graph-step-toggle').evaluate("el=>{el.checked=false;el.dispatchEvent(new Event('change'));}")
            assert console.get_attribute('data-console-copy') == expected
            assert posts == []
            page.reload()
            page.wait_for_function('(s)=>document.getElementById("graph-printf-console").dataset.consoleCopy===s', arg=expected)
            assert not errors
            page.screenshot(path=str(tmp_path / 'full-session-console.png'), full_page=True)
            browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=5)
