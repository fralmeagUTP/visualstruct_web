"""Actual Chromium console rendering: cursor prefixes and natural output."""
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
        page.set_content('<section class="classroom-output-panel" style="width:400px"><pre id="console" class="console-screen"></pre></section>')
        page.add_style_tag(content=(ROOT / 'static/css/styles.css').read_text(encoding='utf8'))
        page.add_style_tag(content=(ROOT / 'static/css/classroom_view.css').read_text(encoding='utf8'))
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
        def expect_natural_output():
            metrics = page.eval_on_selector('#console', """el=>{
              const css=getComputedStyle(el);
              return {height:el.clientHeight, scrollHeight:el.scrollHeight,
                width:el.clientWidth, scrollWidth:el.scrollWidth,
                overflowY:css.overflowY, whiteSpace:css.whiteSpace, maxHeight:css.maxHeight};
            }""")
            assert metrics['height'] > 0
            assert metrics['scrollHeight'] <= metrics['height'] + 1
            assert metrics['scrollWidth'] <= metrics['width'] + 1
            assert metrics['overflowY'] == 'visible'
            assert metrics['whiteSpace'] == 'pre-wrap'
            assert metrics['maxHeight'] == 'none'
            return metrics['height']

        # Long real printf fragments grow the page, not an internal scroll box.
        fragment = data['console_stdout']
        assert fragment, 'Presentation fixture requires authentic nonempty caller stdout'
        tail = data['execution_trace']['steps'][count-1]['pedagogy']['memory_state']['console_stdout']
        page.evaluate('(prefix)=>consoleProbe.setPrefix(prefix)', fragment * 80)
        assert render(count-1) == fragment * 80 + tail
        first_height = expect_natural_output()
        assert first_height > 600
        assert render(count-1) == fragment * 80 + tail
        assert expect_natural_output() == first_height
        page.evaluate('(prefix)=>consoleProbe.setPrefix(prefix)', fragment * 100)
        assert render(count-1) == fragment * 100 + tail
        assert expect_natural_output() > first_height
        long_line = data['console_stdout'].strip() * 20 + '\n'
        page.evaluate('(prefix)=>consoleProbe.setPrefix(prefix)', long_line)
        assert render(count-1) == long_line + tail
        expect_natural_output()
        assert page.locator('#console').text_content() == long_line + tail
        page.screenshot(path=str(tmp_path / 'console-natural-output.png'), full_page=True)
        page.evaluate('(stdout)=>consoleProbe.raw(stdout)', data['console_stdout'])
        assert render(-1).endswith(data['console_stdout'])
        browser.close()


def test_session_console_full_page_reload_and_replay(tmp_path):
    import shutil
    import subprocess
    compiler = shutil.which('gcc')
    assert compiler, 'Native C17 compiler is required for the stdout contract'
    for name in ['tad_grafo.c', 'tad_grafo.h']:
        shutil.copyfile(ROOT / 'docs/tads_C' / name, tmp_path / name)
    def native_stdout(main):
        caller = tmp_path / 'main.c'
        caller.write_text(main, encoding='utf8')
        exe = tmp_path / 'caller.exe'
        built = subprocess.run([compiler, '-std=c17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                                str(caller), str(tmp_path / 'tad_grafo.c'), '-o', str(exe)],
                               capture_output=True, text=True, timeout=30)
        assert built.returncode == 0, built.stderr
        run = subprocess.run([str(exe)], capture_output=True, text=True, timeout=15)
        assert run.returncode == 0, run.stderr
        return run.stdout
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
                setup = response.json()
                assert setup['success']
            page.goto(base + '/graph/graph/camino-minimo')
            page.wait_for_function("document.getElementById('graph-printf-console').dataset.consoleCopy !== undefined")
            console = page.locator('#graph-printf-console')
            initial = console.get_attribute('data-console-copy')
            assert initial == setup['console_prefix'] + setup['console_stdout']
            assert initial == native_stdout(setup['main_c']) == ''  # Insertions do not printf statuses.
            for name, value in [('start', '1'), ('end', '3')]:
                page.locator('#g-alg-field-' + name).fill(value)
            with page.expect_response('**/graph/graph/operate') as pending:
                page.locator('#graph-sim-play').dispatch_event('click')
            result = pending.value.json()
            assert result['success']
            expected = result['console_prefix'] + result['console_stdout']
            assert expected == native_stdout(result['main_c'])
            assert expected  # Dijkstra produces actual caller output.
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
