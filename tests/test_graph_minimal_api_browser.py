"""Local browser verification for the simplified caller and yellow MST rendering."""
import shutil
import threading
from pathlib import Path
import pytest
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright, expect

@pytest.mark.e2e
@pytest.mark.parametrize('algorithm', ['run_prim', 'run_kruskal'])
def test_mst_yellow_controls_and_download(app, tmp_path, algorithm):
    server = make_server('127.0.0.1', 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=shutil.which('chromium'), args=['--no-sandbox'])
            context = browser.new_context(viewport={'width': 1440, 'height': 1000})
            for op, payload in [('create_graph', {'directed': False}),
                                ('insert_edge', {'origin': 1, 'target': 2, 'weight': 1}),
                                ('insert_edge', {'origin': 2, 'target': 3, 'weight': 2}),
                                ('insert_edge', {'origin': 1, 'target': 3, 'weight': 5})]:
                response = context.request.post(base+'/graph/graph/operate', data={'operation': op, 'payload': payload, 'execution_mode': 'normal'})
                assert response.status == 200, response.text()
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(base+'/graph/graph/expansion-minima', wait_until='networkidle')
            page.locator('#graph-algorithm-select').select_option(algorithm)
            if algorithm == 'run_prim':
                page.locator('#g-alg-field-start').fill('1')
            with page.expect_response(lambda response: response.url.endswith('/operate')) as pending:
                page.locator('#graph-sim-play').click()
            assert pending.value.status == 200
            expect(page.locator('#graph-visual-state .viz-graph-edge.mst')).to_have_count(2)
            colors = page.locator('#graph-visual-state .viz-graph-edge').evaluate_all('(es)=>es.map(e=>({mst:e.classList.contains("mst"),stroke:getComputedStyle(e).stroke}))')
            assert all(e['stroke'] == ('rgb(242, 197, 0)' if e['mst'] else 'rgb(36, 95, 157)') for e in colors)
            expect(page.locator('.graph-mst-legend')).to_contain_text('amarillo')
            main = context.request.get(base+'/help/source/graph/main').text()
            assert 'GrafoEstado' not in main and '&estado' not in main
            assert ('grafo_prim(g, 1);' if algorithm == 'run_prim' else 'grafo_kruskal(g);') in main
            # A repeat click executes once more and retains the same result.
            with page.expect_response(lambda response: response.url.endswith('/operate')):
                page.locator('#graph-sim-play').click()
            expect(page.locator('#graph-visual-state .viz-graph-edge.mst')).to_have_count(2)
            # Enter a real trace and verify navigation does not issue another mutation.
            with page.expect_response(lambda response: response.url.endswith('/operate')) as traced:
                page.locator('#graph-sim-step').click()
            assert traced.value.status == 200, traced.value.text()
            expect(page.locator('#graph-sim-next')).to_be_visible()
            page.locator('#graph-sim-next').click()
            page.locator('#graph-sim-prev').click()
            page.locator('#graph-sim-play').click()
            expect(page.locator('#graph-visual-state .viz-graph-edge.mst')).to_have_count(2)
            page.locator('#graph-visual-region').screenshot(path=str(tmp_path/f'{algorithm}-yellow.png'))
            assert not errors
            context.close(); browser.close()
    finally:
        server.shutdown(); thread.join(timeout=5)
