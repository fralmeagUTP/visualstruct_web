"""Deterministic regressions for requests sharing a server-side session."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Event
import os

import pytest

from app import create_app
from app.config import Config
from app.services.hash_structure_service import HashStructureService
from app.services.session_service import SESSION_KEY


@pytest.fixture()
def concurrency_app(tmp_path):
    class TestConfig(Config):
        TESTING = True
        APP_ENV = 'testing'
        SECRET_KEY = 'concurrency-test-key'
        SESSION_TYPE = 'cachelib'
        SESSION_CACHE_DIR = str(tmp_path / 'sessions')
    app = create_app(TestConfig)
    if os.environ.get("VISUALSTRUCT_TEST_BASELINE"):
        app.session_interface = app.session_interface.backend
    return app


@pytest.mark.parametrize("capacity", [3, 128])
def test_slow_hash_keeps_array_created_in_other_tab(concurrency_app, monkeypatch, capacity):
    app = concurrency_app
    first = app.test_client()
    created = first.post('/hash/hash_table/operate', json={
        'operation': 'create_table', 'payload': {'capacity': capacity}})
    assert created.status_code == 200
    second = app.test_client()
    second.set_cookie(app.config['SESSION_COOKIE_NAME'],
                      first.get_cookie(app.config['SESSION_COOKIE_NAME']).value)
    entered, release = Event(), Event()
    execute = HashStructureService.execute_operation

    def paused(*args, **kwargs):
        if kwargs.get('operation_name') == 'items':
            entered.set()
            assert release.wait(20), 'release signal missing'
        return execute(*args, **kwargs)

    monkeypatch.setattr(HashStructureService, 'execute_operation', paused)
    with ThreadPoolExecutor(max_workers=2) as pool:
        listing = pool.submit(first.post, '/hash/hash_table/operate', json={
            'operation': 'items', 'payload': {}})
        try:
            assert entered.wait(20)
            array = second.post('/api/ordenamiento/create-array', json={'values': [3, 1, 2]})
            assert array.status_code == 200, array.get_json()
        finally:
            release.set()
        assert listing.result(timeout=120).status_code == 200
    result = second.post('/api/ordenamiento/run', json={
        'algorithm_id': 'burbuja', 'mode': 'fast'})
    assert result.status_code == 200, result.get_json()
    with second.session_transaction() as session:
        assert 'sorting::sorting_array' in session[SESSION_KEY]
        assert 'hash::hash_table' in session[SESSION_KEY]


def _seed(app, data):
    client = app.test_client()
    with client.session_transaction() as session:
        session.update(data)
    return client.get_cookie(app.config['SESSION_COOKIE_NAME']).value


def _snapshot(app, sid):
    from werkzeug.test import EnvironBuilder
    from flask import Request
    environ = EnvironBuilder(headers={'Cookie': f"{app.config['SESSION_COOKIE_NAME']}={sid}"}).get_environ()
    return app.session_interface.open_session(app, Request(environ))


def _save(app, session):
    response = app.response_class('{}', content_type='application/json')
    app.session_interface.save_session(app, session, response)
    return response


def test_stale_read_refresh_does_not_restore_deleted_record(concurrency_app):
    app = concurrency_app
    sid = _seed(app, {SESSION_KEY: {'hash': {'history': [1]}, 'sort': {'history': [2]}}})
    reader, reset = _snapshot(app, sid), _snapshot(app, sid)
    del reset[SESSION_KEY]['sort']
    reset.modified = True
    assert _save(app, reset).status_code == 200
    assert _save(app, reader).status_code == 200
    assert _snapshot(app, sid)[SESSION_KEY] == {'hash': {'history': [1]}}


def test_same_record_conflict_rejects_entire_write(concurrency_app):
    app = concurrency_app
    sid = _seed(app, {SESSION_KEY: {'sort': {'history': [1], 'checkpoint': None}}})
    first, second = _snapshot(app, sid), _snapshot(app, sid)
    first[SESSION_KEY]['sort']['history'].append(2)
    second[SESSION_KEY]['sort']['checkpoint'] = {'data': 'stale'}
    first.modified = second.modified = True
    second['unrelated_side_effect'] = True
    assert _save(app, first).status_code == 200
    conflict = _save(app, second)
    assert conflict.status_code == 409
    assert conflict.get_json()['session_conflict'] is True
    assert not conflict.headers.getlist('Set-Cookie')
    latest = _snapshot(app, sid)
    assert latest[SESSION_KEY]['sort'] == {'history': [1, 2], 'checkpoint': None}
    assert 'unrelated_side_effect' not in latest


def test_stale_reset_cannot_remove_newer_history(concurrency_app):
    app = concurrency_app
    sid = _seed(app, {SESSION_KEY: {'sort': {'history': [1]}}})
    first, reset = _snapshot(app, sid), _snapshot(app, sid)
    first[SESSION_KEY]['sort'] = {'history': [1, 2]}
    first.modified = True
    reset[SESSION_KEY] = {}
    assert _save(app, first).status_code == 200
    assert _save(app, reset).status_code == 409
    assert _snapshot(app, sid)[SESSION_KEY]['sort']['history'] == [1, 2]


def test_clear_conflicts_with_concurrent_addition(concurrency_app):
    app = concurrency_app
    sid = _seed(app, {'base': 1})
    first, clear = _snapshot(app, sid), _snapshot(app, sid)
    first['new'] = 2
    clear.clear()
    assert _save(app, first).status_code == 200
    assert _save(app, clear).status_code == 409
    assert _snapshot(app, sid)['new'] == 2


def test_stale_request_cannot_resurrect_cleared_session(concurrency_app):
    app = concurrency_app
    sid = _seed(app, {'base': 1})
    first, clear = _snapshot(app, sid), _snapshot(app, sid)
    clear.clear()
    assert _save(app, clear).status_code == 200
    first['late'] = 2
    assert _save(app, first).status_code == 409
    assert app.session_interface.backend._retrieve_session_data(
        app.session_interface.backend._get_store_id(sid)) is None


def test_identical_concurrent_appends_are_not_silently_deduplicated(concurrency_app):
    app = concurrency_app
    sid = _seed(app, {SESSION_KEY: {'stack': {'history': [1]}}})
    first, second = _snapshot(app, sid), _snapshot(app, sid)
    for session in (first, second):
        session[SESSION_KEY]['stack']['history'].append(2)
        session.modified = True
    assert _save(app, first).status_code == 200
    assert _save(app, second).status_code == 409


def test_many_independent_threads_preserve_all_records(concurrency_app):
    app = concurrency_app
    sid = _seed(app, {SESSION_KEY: {'base': {'history': []}}})
    snapshots = [_snapshot(app, sid) for _ in range(16)]
    for index, session in enumerate(snapshots):
        session[SESSION_KEY][str(index)] = {'history': [index]}
        session.modified = True
    with ThreadPoolExecutor(max_workers=8) as pool:
        statuses = list(pool.map(lambda session: _save(app, session).status_code, snapshots))
    assert statuses == [200] * 16
    assert len(_snapshot(app, sid)[SESSION_KEY]) == 17


def _process_write(app, sid, key, barrier, results):
    try:
        session = _snapshot(app, sid)
        session[SESSION_KEY][key] = {'history': [key]}
        session.modified = True
        barrier.wait(15)
        results.put(_save(app, session).status_code)
    except BaseException as error:
        results.put(repr(error))
        raise


@pytest.mark.skipif(os.name == 'nt', reason='fork probe is specific to POSIX workers')
def test_shared_cache_preserves_records_from_separate_processes(concurrency_app):
    import multiprocessing
    app = concurrency_app
    sid = _seed(app, {SESSION_KEY: {}})
    context = multiprocessing.get_context('fork')
    barrier, results = context.Barrier(2), context.Queue()
    children = [context.Process(target=_process_write,
                                args=(app, sid, key, barrier, results)) for key in ('a', 'b')]
    for child in children:
        child.start()
    try:
        assert [results.get(timeout=20) for _ in children] == [200, 200]
    finally:
        for child in children:
            child.join(20)
            if child.is_alive():
                child.terminate()
                child.join()
            assert child.exitcode == 0
    assert set(_snapshot(app, sid)[SESSION_KEY]) == {'a', 'b'}


def test_signed_cookie_and_nonpermanent_session(concurrency_app):
    from flask_session.cachelib import CacheLibSessionInterface
    from app.services.concurrent_sessions import ConcurrentSessionInterface
    app = concurrency_app
    backend = CacheLibSessionInterface(app, client=app.session_interface.cache,
                                       use_signer=True, permanent=False)
    app.session_interface = ConcurrentSessionInterface(backend, app.config['SESSION_CACHE_DIR'])
    sid = _seed(app, {'base': 1})
    assert '.' in sid
    session = _snapshot(app, sid)
    session['value'] = 2
    saved = _save(app, session)
    assert saved.status_code == 200
    cookie = saved.headers['Set-Cookie']
    assert 'HttpOnly' in cookie and 'SameSite=Lax' in cookie
    assert 'Expires=' not in cookie
    assert _snapshot(app, sid)['value'] == 2


def test_regeneration_saves_new_sid_without_resurrecting_old(concurrency_app):
    app = concurrency_app
    sid = _seed(app, {'base': 1})
    old_request, rotating = _snapshot(app, sid), _snapshot(app, sid)
    with app.app_context():
        app.session_interface.regenerate(rotating)
    assert rotating.sid != sid
    rotating['new'] = 2
    assert _save(app, rotating).status_code == 200
    assert _snapshot(app, rotating.sid)['new'] == 2
    old_request['late'] = 3
    assert _save(app, old_request).status_code == 409


def test_regeneration_cannot_erase_concurrent_updates(concurrency_app):
    from werkzeug.exceptions import Conflict
    app = concurrency_app
    sid = _seed(app, {'base': 1})
    first, rotating = _snapshot(app, sid), _snapshot(app, sid)
    first['new'] = 2
    assert _save(app, first).status_code == 200
    with app.app_context(), pytest.raises(Conflict):
        app.session_interface.regenerate(rotating)
    assert _snapshot(app, sid)['new'] == 2


def test_mixed_case_backend_configuration(tmp_path):
    class TestConfig(Config):
        TESTING = True
        APP_ENV = 'testing'
        SESSION_TYPE = 'CacheLib'
        SESSION_CACHE_DIR = str(tmp_path / 'mixed-case')
    app = create_app(TestConfig)
    sid = _seed(app, {'base': 1})
    assert _snapshot(app, sid)['base'] == 1


def _counting_clients(app):
    first = app.test_client()
    assert first.post('/api/ordenamiento/create-array', json={'values': [2, 1]}).status_code == 200
    run = first.post('/api/ordenamiento/run', json={'algorithm_id': 'counting_sort', 'mode': 'step_by_step'})
    assert run.status_code == 200
    second = app.test_client()
    second.set_cookie(app.config['SESSION_COOKIE_NAME'], first.get_cookie(app.config['SESSION_COOKIE_NAME']).value)
    return first, second, run.get_json()['execution_trace']


def test_rejected_reset_cannot_revoke_winning_counting_trace(concurrency_app):
    from flask import request
    app = concurrency_app
    entered, release = Event(), Event()

    @app.before_request
    def pause_reset():
        if request.path == '/api/ordenamiento/reset':
            entered.set()
            assert release.wait(20)

    first, second, old_trace = _counting_clients(app)
    with ThreadPoolExecutor(max_workers=2) as pool:
        reset = pool.submit(second.post, '/api/ordenamiento/reset', json={})
        try:
            assert entered.wait(20)
            run = first.post('/api/ordenamiento/run', json={'algorithm_id': 'counting_sort', 'mode': 'step_by_step'})
            assert run.status_code == 200
            winner = run.get_json()['execution_trace']
            assert first.get(winner['page_url']).status_code == 200
        finally:
            release.set()
        assert reset.result(timeout=20).status_code == 409
    assert first.get(winner['page_url']).status_code == 200
    with first.session_transaction() as session:
        assert session['counting_latest']['trace_id'] == winner['trace_id']


def test_committed_reset_cleanup_does_not_revoke_later_trace(concurrency_app, monkeypatch):
    from app.services.counting_trace_service import get_counting_store
    app = concurrency_app
    first, second, old_trace = _counting_clients(app)
    with app.app_context():
        store = get_counting_store()
    entered, release = Event(), Event()
    revoke = store.revoke_keys

    def paused(owner, keys):
        entered.set()
        assert release.wait(20)
        revoke(owner, keys)

    monkeypatch.setattr(store, 'revoke_keys', paused)
    with ThreadPoolExecutor(max_workers=2) as pool:
        reset = pool.submit(second.post, '/api/ordenamiento/reset', json={})
        try:
            assert entered.wait(20)
            assert first.post('/api/ordenamiento/create-array', json={'values': [3, 1]}).status_code == 200
            pending_run = pool.submit(first.post, '/api/ordenamiento/run',
                                      json={'algorithm_id': 'counting_sort', 'mode': 'step_by_step'})
        finally:
            release.set()
        assert reset.result(timeout=20).status_code == 200
        run = pending_run.result(timeout=20)
        assert run.status_code == 200
        winner = run.get_json()['execution_trace']
    assert first.get(winner['page_url']).status_code == 200
    assert old_trace['trace_id'] not in store.entries


def test_new_session_can_clear_or_regenerate(concurrency_app):
    app = concurrency_app
    fresh = _snapshot(app, '')
    fresh.clear()
    assert _save(app, fresh).status_code == 200
    fresh = _snapshot(app, '')
    fresh['value'] = 1
    with app.app_context():
        app.session_interface.regenerate(fresh)
    assert _save(app, fresh).status_code == 200
    assert _snapshot(app, fresh.sid)['value'] == 1


def test_rejected_run_does_not_evict_winning_trace(concurrency_app, monkeypatch):
    from flask import request
    from app.services.counting_trace_service import get_counting_store
    app = concurrency_app
    entered, release = Event(), Event()

    @app.before_request
    def pause_losing_run():
        if request.headers.get('X-Pause'):
            entered.set()
            assert release.wait(20)

    first, second, _ = _counting_clients(app)
    with app.app_context():
        store = get_counting_store()
        store.max_traces = 1
    with ThreadPoolExecutor(max_workers=2) as pool:
        loser = pool.submit(second.post, '/api/ordenamiento/run',
                            json={'algorithm_id': 'counting_sort', 'mode': 'step_by_step'},
                            headers={'X-Pause': 'yes'})
        try:
            assert entered.wait(20)
            winner = first.post('/api/ordenamiento/run', json={'algorithm_id': 'counting_sort', 'mode': 'step_by_step'})
            assert winner.status_code == 200
            trace = winner.get_json()['execution_trace']
        finally:
            release.set()
        assert loser.result(timeout=20).status_code == 409
    assert first.get(trace['page_url']).status_code == 200
    assert list(store.entries) == [trace['trace_id']]


def test_trace_publication_runs_with_refresh_disabled_and_unchanged_owner(concurrency_app):
    app = concurrency_app
    app.config['SESSION_REFRESH_EACH_REQUEST'] = False
    first, _, _ = _counting_clients(app)
    response = first.post('/api/ordenamiento/compare', json={
        'values': [2, 1], 'left_algorithm': 'counting_sort', 'right_algorithm': 'counting_sort'})
    assert response.status_code == 200, response.get_json()
    for side in ('left', 'right'):
        assert first.get(response.get_json()[side]['trace']['page_url']).status_code == 200


def test_compare_cannot_publish_to_owner_revoked_by_concurrent_reset(concurrency_app):
    from flask import request
    app = concurrency_app
    entered, release = Event(), Event()

    @app.before_request
    def pause_compare():
        if request.path == '/api/ordenamiento/compare':
            entered.set()
            assert release.wait(20)

    first, second, _ = _counting_clients(app)
    with ThreadPoolExecutor(max_workers=2) as pool:
        comparison = pool.submit(second.post, '/api/ordenamiento/compare', json={
            'values': [2, 1], 'left_algorithm': 'counting_sort', 'right_algorithm': 'counting_sort'})
        try:
            assert entered.wait(20)
            assert first.post('/api/ordenamiento/reset', json={}).status_code == 200
        finally:
            release.set()
        assert comparison.result(timeout=20).status_code == 409
    assert not app.extensions['counting_trace_store'].entries
