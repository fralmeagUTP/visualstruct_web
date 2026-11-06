"""Redis WATCH/MULTI protocol tests with an explicit in-memory test double.

These verify merge/serialization/retry behavior, not a real Redis deployment.
"""
from __future__ import annotations

from threading import RLock

import pytest
from redis import Redis
from redis.exceptions import WatchError

from app import create_app
from app.config import Config
from test_concurrent_session_persistence import _seed, _snapshot, _save


class RedisDouble:
    def __init__(self):
        self.data, self.versions = {}, {}
        self.lock = RLock()
        self.conflicts = 0
        self.executions = 0
        self.last_ttl = None

    def get(self, key):
        with self.lock:
            return self.data.get(key)

    def pipeline(self):
        return PipelineDouble(self)


class PipelineDouble:
    def __init__(self, client):
        self.client = client
        self.action = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def watch(self, key):
        self.key = key
        with self.client.lock:
            self.version = self.client.versions.get(key, 0)

    def get(self, key):
        return self.client.get(key)

    def multi(self):
        pass

    def set(self, key, value, ex):
        self.action = ('set', key, value, ex)

    def delete(self, key):
        self.action = ('delete', key)

    def execute(self):
        with self.client.lock:
            self.client.executions += 1
            if self.client.conflicts:
                self.client.conflicts -= 1
                raise WatchError()
            if self.client.versions.get(self.key, 0) != self.version:
                raise WatchError()
            if self.action[0] == 'set':
                self.client.data[self.key] = self.action[2]
                self.client.last_ttl = self.action[3]
            else:
                self.client.data.pop(self.key, None)
            self.client.versions[self.key] = self.version + 1
            return [True]


@pytest.fixture()
def redis_app():
    class RedisConfig(Config):
        TESTING = True
        APP_ENV = 'testing'
        SESSION_TYPE = 'redis'
        SESSION_REDIS_URL = None
        SESSION_REDIS = Redis()
    app = create_app(RedisConfig)
    app.session_interface.backend.client = RedisDouble()
    return app


def test_redis_protocol_merges_independent_writes_and_refresh(redis_app):
    app = redis_app
    sid = _seed(app, {'base': 1})
    first, second, reader = [_snapshot(app, sid) for _ in range(3)]
    first['a'], second['b'] = 2, 3
    assert _save(app, first).status_code == 200
    assert _save(app, second).status_code == 200
    assert _save(app, reader).status_code == 200
    assert dict(_snapshot(app, sid)) == {'_permanent': True, 'base': 1, 'a': 2, 'b': 3}
    assert app.session_interface.backend.client.last_ttl == 14400


def test_redis_protocol_retries_watch_without_reexecuting_operation(redis_app):
    app = redis_app
    sid = _seed(app, {'base': 1})
    session = _snapshot(app, sid)
    session['base'] = 2
    client = app.session_interface.backend.client
    before = client.executions
    client.conflicts = 2
    assert _save(app, session).status_code == 200
    assert client.executions == before + 3
    assert _snapshot(app, sid)['base'] == 2


def test_redis_protocol_conflict_and_retry_exhaustion_preserve_storage(redis_app):
    app = redis_app
    sid = _seed(app, {'base': 1})
    first, second = _snapshot(app, sid), _snapshot(app, sid)
    first['base'], second['base'] = 2, 3
    assert _save(app, first).status_code == 200
    assert _save(app, second).status_code == 409
    fresh = _snapshot(app, sid)
    fresh['new'] = 4
    app.session_interface.backend.client.conflicts = 16
    assert _save(app, fresh).status_code == 409
    assert 'new' not in _snapshot(app, sid)
    assert _snapshot(app, sid)['base'] == 2


def test_redis_protocol_clear_and_stale_revival(redis_app):
    app = redis_app
    sid = _seed(app, {'base': 1})
    clear, stale = _snapshot(app, sid), _snapshot(app, sid)
    clear.clear()
    assert _save(app, clear).status_code == 200
    stale['late'] = 2
    assert _save(app, stale).status_code == 409
    assert not app.session_interface.backend.client.data
