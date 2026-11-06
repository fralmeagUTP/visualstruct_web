"""Public resources never deserialize, lock, renew, or overwrite user sessions."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import pytest
from flask import session

from app import create_app
from app.config import Config


@pytest.fixture()
def resource_app(tmp_path):
    class ResourceConfig(Config):
        TESTING = True
        APP_ENV = 'testing'
        SESSION_CACHE_DIR = str(tmp_path / 'sessions')
    app = create_app(ResourceConfig)

    @app.get('/static/private-state')
    @app.get('/assets/private-state')
    def private_state():
        session['dynamic_counter'] = session.get('dynamic_counter', 0) + 1
        return {'value': session['dynamic_counter']}

    return app


def forbid(*args, **kwargs):
    pytest.fail('A public resource must not access session storage')


@pytest.mark.parametrize('path', ['/static/js/hash.js', '/static/css/styles.css',
                                 '/assets/logo_UTP.jpg', '/healthz'])
@pytest.mark.parametrize('method', ['GET', 'HEAD'])
def test_public_routes_skip_all_session_io(resource_app, monkeypatch, path, method):
    app = resource_app
    backend = app.session_interface.backend
    monkeypatch.setattr(backend, 'open_session', forbid)
    monkeypatch.setattr(backend, '_retrieve_session_data', forbid)
    monkeypatch.setattr(app.session_interface, '_commit', forbid)
    client = app.test_client()
    client.set_cookie(app.config['SESSION_COOKIE_NAME'], 'existing-cookie')
    response = client.open(path, method=method)
    assert response.status_code == 200
    assert not response.headers.getlist('Set-Cookie')
    assert 'Cookie' not in response.vary


def test_conditional_assets_and_missing_files_skip_session_io(resource_app, monkeypatch):
    app = resource_app
    client = app.test_client()
    initial = client.get('/static/js/hash.js')
    monkeypatch.setattr(app.session_interface.backend, 'open_session', forbid)
    client.set_cookie(app.config['SESSION_COOKIE_NAME'], 'existing-cookie')
    response = client.get('/static/js/hash.js?v=anything', headers={'If-None-Match': initial.headers['ETag']})
    assert response.status_code == 304
    assert not response.headers.getlist('Set-Cookie')
    assert client.get('/static/nonexistent.js').status_code == 404
    assert client.get('/assets/../README.md').status_code == 404


def test_dynamic_routes_under_public_prefix_keep_sessions(resource_app):
    app = resource_app
    client = app.test_client()
    assert client.get('/static/private-state').get_json() == {'value': 1}
    assert client.get('/assets/private-state').get_json() == {'value': 2}
    with client.session_transaction() as stored:
        assert stored['dynamic_counter'] == 2


def test_public_requests_do_not_change_storage_or_ttl(resource_app, monkeypatch):
    app = resource_app
    client = app.test_client()
    client.get('/assets/private-state')
    sid = client.get_cookie(app.config['SESSION_COOKIE_NAME']).value
    backend = app.session_interface.backend
    key = backend._get_store_id(sid)
    path = backend.cache._get_filename(key)
    from pathlib import Path
    before = Path(path).read_bytes()
    mtime = Path(path).stat().st_mtime_ns
    monkeypatch.setattr(backend, 'open_session', forbid)

    def load(_):
        other = app.test_client()
        other.set_cookie(app.config['SESSION_COOKIE_NAME'], sid)
        return other.get('/static/js/hash.js').status_code

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert list(pool.map(load, range(24))) == [200] * 24
    assert Path(path).read_bytes() == before
    assert Path(path).stat().st_mtime_ns == mtime


def test_sessionless_routes_support_script_name_mount(resource_app, monkeypatch):
    app = resource_app
    monkeypatch.setattr(app.session_interface.backend, 'open_session', forbid)
    response = app.test_client().get('/static/js/hash.js', environ_overrides={'SCRIPT_NAME': '/visualstruct'})
    assert response.status_code == 200
