"""The no-trace hint identifies execution, not disabled trace navigation."""
import pytest
from playwright.sync_api import expect
from test_controls40_real_flows import controls40_page
from test_residual58_focal_cases import residual58_app

GUIDANCE = 'Pulsa Ejecutar operación para preparar la traza; después usa Siguiente paso o Paso anterior para recorrerla.'

@pytest.mark.e2e
def test_graph_guidance_distinguishes_execution_from_navigation(controls40_page):
    page, context, base = controls40_page
    created = context.request.post(base + '/graph/graph/operate', data={'operation':'create_graph', 'payload':{'directed':True}})
    assert created.status == 200 and created.json()['success']
    posts, errors = [], []
    page.on('request', lambda req: posts.append(req.url) if req.method == 'POST' else None)
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(base + '/graph/graph/construccion', wait_until='networkidle')
    status = page.locator('#graph-sim-status')
    expect(status).to_have_text(GUIDANCE)
    expect(page.locator('.graph-control-explanation')).to_have_text('Ejecutar operación inicia la llamada seleccionada. Para revisar instrucción a instrucción, activa Paso a paso antes de ejecutarla. Después, Paso anterior y Siguiente paso recorren esa misma llamada sin volver a ejecutarla.')
    page.select_option('#graph-operation-select', 'insert_vertex')
    page.locator('#g-op-field-vertex').fill('22')
    page.click('#graph-sim-step')
    expect(page.locator('#graph-step-toggle')).to_be_checked()
    expect(page.locator('#graph-sim-next')).to_be_disabled()
    expect(status).to_have_text('Entradas de operación cambiadas. Ejecuta nuevamente.')
    assert not posts
    with page.expect_response(lambda response: response.url.endswith('/graph/graph/operate') and response.request.method == 'POST') as response:
        page.click('#graph-sim-play')
    assert response.value.status == 200 and response.value.json()['success']
    expect(page.locator('#graph-sim-next')).to_be_enabled()
    assert len(posts) == 1
    total = len(response.value.json()['execution_trace']['steps'])
    assert total > 0
    counter = page.locator('#graph-sim-counter')
    expect(counter).to_have_text(f'Paso: 0/{total}')
    page.click('#graph-sim-next')
    expect(page.locator('#graph-sim-prev')).to_be_enabled()
    expect(counter).to_have_text(f'Paso: 1/{total}')
    page.click('#graph-sim-prev')
    expect(counter).to_have_text(f'Paso: 0/{total}')
    expect(status).to_have_text(f'Paso 0/{total}')
    assert len(posts) == 1
    page.locator('#g-op-field-vertex').fill('23')
    expect(status).to_have_text('Entradas de operación cambiadas. Ejecuta nuevamente.')
    expect(page.locator('#graph-sim-next')).to_be_disabled()
    assert len(posts) == 1
    assert not errors
