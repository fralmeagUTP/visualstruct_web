"""Canonical traversal browser journey shared by BFS and DFS scenarios."""
import json
import threading
import pytest
from werkzeug.serving import make_server
from app import create_app
from app.config import Config
from _audit_graph_bfs_native_observer import CASES
from _book_graph_browser_contract import decoded_body, verify_player, main_text, compile_downloaded_main


def run_traversal_browser(tmp_path, case, algorithm):
    record = CASES[case]; operation = 'run_' + algorithm; function = 'grafo_' + algorithm
    class PrivateConfig(Config):
        TESTING = True
        SECRET_KEY = 'canonical-traversal-browser'
        SESSION_CACHE_DIR = str(tmp_path / 'sessions')
    app = create_app(PrivateConfig); server = make_server('127.0.0.1', 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    try:
        with pytest.importorskip('playwright.sync_api').sync_playwright() as driver:
            browser = driver.chromium.launch(); context = browser.new_context(viewport={'width': 1366, 'height': 1000})
            page = context.new_page(); posts = []; errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda request: posts.append(request.url) if request.method == 'POST' else None)
            def post(op, payload):
                return context.request.post(base + '/graph/graph/operate', data={'operation': op, 'payload': payload}).json()
            assert post('create_graph', {'directed': True})['success']
            for vertex in record['vertices']:
                assert post('insert_vertex', {'vertex': vertex})['success']
            for origin, target in record['edges']:
                assert post('insert_edge', {'origin': origin, 'target': target, 'weight': 1})['success']
            page.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const old=window.InterpreterRuntime.createTracePlayer;window.InterpreterRuntime.createTracePlayer=function(options){const player=old(options);window.auditGraphPlayer=player;return player;};});")
            page.goto(base + '/graph/graph/recorridos', wait_until='networkidle')
            page.select_option('#graph-algorithm-select', operation)
            page.locator('#g-alg-field-start').fill(str(record['start']))
            page.evaluate("()=>{const b=document.querySelector('#graph-step-toggle');b.checked=true;b.dispatchEvent(new Event('change'));}")
            with page.expect_response(lambda response: response.url.endswith('/graph/graph/operate') and response.request.method == 'POST') as response:
                page.click('#graph-sim-play')
            first = decoded_body(response.value.json()); assert first['success']
            report = verify_player(page, first, posts)
            second = post(operation, {'start': record['start']}); assert second['success']
            failure = post(operation, {'start': 999})
            assert not failure['success'] and failure['c_status_name'] == 'GRAFO_NO_EXISTE'
            assert failure['history'][:-1] == second['history']
            assert failure['history'][-1] == {'operation': operation, 'payload': {'start': 999}, 'source_contract': 'graph-book/v1'}
            assert failure['console_stdout'] == algorithm.upper() + ': estado=2\n'
            before = len(posts); programs = []
            for _ in range(2):
                page.reload(wait_until='networkidle'); programs.append(main_text(page))
                assert main_text(page).count('= ' + function + '(') == 3 and len(posts) == before
            assert programs[0] == programs[1]
            assert context.request.get(base + '/help/source/graph/main').body() == programs[0].encode('utf-8')
            stdout = compile_downloaded_main(context, base, tmp_path / 'three-calls', programs[0], failure['console_prefix'] + failure['console_stdout'])
            expected_success = algorithm.upper() + ': estado=0' + ''.join(' ' + str(v) for v in first['result'])
            assert stdout.splitlines().count(expected_success) == 2
            assert programs[0].count('grafo_liberar_vertices(&lista_') == 3
            if case == 1:
                # Missing start executes C and returns a status, rather than a host rejection.
                page.select_option('#graph-algorithm-select', operation)
                page.locator('#g-alg-field-start').fill('999')
                page.evaluate("()=>{const b=document.querySelector('#graph-step-toggle');b.checked=true;b.dispatchEvent(new Event('change'));}")
                with page.expect_response(lambda response: response.url.endswith('/graph/graph/operate') and response.request.method == 'POST') as response:
                    page.click('#graph-sim-play')
                rejected = decoded_body(response.value.json())
                assert not rejected['success'] and rejected['execution_trace']['C_instruction_events']
                assert rejected['history'][:-1] == failure['history'] and rejected['c_status'] == 2
                verify_player(page, rejected, posts)
                current = main_text(page); assert current.count('= ' + function + '(') == 4
                assert context.request.get(base + '/help/source/graph/main').body() == current.encode('utf-8')
                compile_downloaded_main(context, base, tmp_path / 'four-calls', current, rejected['console_prefix'] + rejected['console_stdout'])
            assert not errors
            (tmp_path / 'browser-report.json').write_text(json.dumps({'case': case, 'algorithm': algorithm,
                **report, 'successful_calls': 2, 'failed_C_calls_retained': 2 if case == 1 else 1,
                'reload_POSTs': 0, 'native_main_exact_stdout': True, 'errors': errors}, indent=2), encoding='utf-8')
            context.close(); browser.close()
    finally:
        server.shutdown(); thread.join(timeout=5)
