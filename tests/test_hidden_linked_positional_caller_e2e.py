"""Actual browser hidden callers preserve all twelve native/reload case contracts."""
import threading

import pytest
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

from app import create_app
from app.config import Config
from _hidden_linked_caller_contract import CASES, HIDDEN, SEED, verify_native_caller

pytestmark = pytest.mark.e2e


@pytest.fixture(scope='module')
def hidden_caller_browser(tmp_path_factory):
    target = tmp_path_factory.mktemp('hidden-caller-browser')

    class PrivateConfig(Config):
        TESTING = True
        SECRET_KEY = 'hidden-caller-private-test'
        SESSION_CACHE_DIR = str(target / 'cache')
        SESSION_CACHE_THRESHOLD = 0

    app = create_app(PrivateConfig)
    server = make_server('127.0.0.1', 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                yield app, f'http://127.0.0.1:{server.server_port}', browser
            finally:
                browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=5)


@pytest.mark.parametrize('case_id,operation,payload', CASES, ids=[row[0] for row in CASES])
def test_hidden_caller_actual_DOM_native_and_reload(hidden_caller_browser, tmp_path, case_id, operation, payload):
    app, base, browser = hidden_caller_browser
    context = browser.new_context()
    try:
        for value in SEED:
            response = context.request.post(base + '/sequential/linked_list/operate', data={
                'operation': 'insertar_final', 'payload': {'value': value}})
            assert response.status == 200 and response.json()['success']
        response = context.request.post(base + '/sequential/linked_list/operate', data={
            'operation': operation, 'payload': payload})
        assert response.status == 200
        data = response.json()
        assert data['success']
        expected = [item['value'] for item in data['visual_state']['items']]
        page = context.new_page()
        errors = []
        posts = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: posts.append(request.url) if request.method == 'POST' else None)
        page.goto(base + '/sequential/linked_list', wait_until='networkidle')
        page.wait_for_function("document.querySelector('#action-history')?.dataset.rawCode?.includes('int main(void)')")
        assert not HIDDEN.intersection(page.locator('#operation-select option').evaluate_all('nodes => nodes.map(n => n.value)'))
        main = '\n'.join(page.locator('#action-history .code-line').all_text_contents())
        # Only API supplies these legacy operations. No hidden selector is invented.
        assert len(page.evaluate('window.SEQ_VIEW_MODEL.history')) == len(SEED) + 1
        for _ in range(2):
            page.reload(wait_until='networkidle')
            page.wait_for_function("document.querySelector('#action-history')?.dataset.rawCode?.includes('int main(void)')")
            assert '\n'.join(page.locator('#action-history .code-line').all_text_contents()) == main
            assert not HIDDEN.intersection(page.locator('#operation-select option').evaluate_all('nodes => nodes.map(n => n.value)'))
            assert page.evaluate('window.SEQ_VIEW_MODEL.visual_state.items.map(item => item.value)') == expected
        assert not posts and not errors
        # Compile exactly the displayed browser C and check it against the HTTP state.
        verify_native_caller(main, expected, tmp_path, app.test_client())
    finally:
        context.close()
