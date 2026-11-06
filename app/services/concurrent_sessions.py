"""Atomic, conflict-aware persistence for Flask-Session's supported backends.

Flask-Session otherwise writes the entire request snapshot, including on a
read-only refresh. Merge only changed records, never histories or checkpoints
inside a record. A stale write to the same record fails instead of losing data.
"""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
from copy import deepcopy
import hashlib
import os
from pathlib import Path
from typing import Any, Iterator

from flask import Flask, Request, Response, current_app, session as flask_session
from flask.sessions import SessionInterface
from itsdangerous import BadSignature
from werkzeug.exceptions import Conflict, HTTPException

_MISSING = object()
_PUBLIC_SESSIONLESS_ENDPOINTS = frozenset({'static', 'main.asset_file', 'main.healthz'})
_RECORD_MAPS = frozenset({'sequential_histories', 'hash_execution_journals'})


class SessionConflict(RuntimeError):
    """The request would overwrite a change accepted after it began."""


def _merge_map(before: dict, proposed: dict, latest: dict) -> dict:
    result = deepcopy(latest)
    for key in before.keys() | proposed.keys():
        old, new = before.get(key, _MISSING), proposed.get(key, _MISSING)
        if old == new:
            continue
        if latest.get(key, _MISSING) != old:
            raise SessionConflict('Concurrent session record change')
        if new is _MISSING:
            result.pop(key, None)
        else:
            result[key] = deepcopy(new)
    return result


def merge_session(before: dict, proposed: dict, latest: dict) -> dict:
    """Merge independent records; reject all changes on any conflicting unit."""
    before, proposed, latest = dict(before), dict(proposed), dict(latest)
    maps = {}
    for key in _RECORD_MAPS:
        # Treat a namespace as a map only when it remains a valid map. Clearing
        # the entire session is deliberately a whole-session operation below.
        if key in proposed and all(isinstance(value.get(key, {}), dict)
                                   for value in (before, proposed, latest)):
            maps[key] = _merge_map(before.pop(key, {}), proposed.pop(key, {}),
                                   latest.pop(key, {}))
    result = _merge_map(before, proposed, latest)
    result.update(maps)
    return result


@contextmanager
def _file_lock(directory: Path, store_id: str) -> Iterator[None]:
    """Use bounded lock files, shared by threads and processes on one host.

    Locks are outside FileSystemCache so its pruning cannot unlink active locks.
    Never unlink these files: another worker may already hold the same inode.
    """
    directory.mkdir(parents=True, exist_ok=True)
    stripe = hashlib.sha256(store_id.encode()).digest()[0] % 64
    fd = os.open(directory / f'{stripe:02x}.lock', os.O_CREAT | os.O_RDWR, 0o600)
    try:
        if os.name == 'nt':  # pragma: no cover - exercised on Windows hosts
            import msvcrt
            if os.fstat(fd).st_size == 0:
                os.write(fd, b'\0')
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            yield
        finally:
            if os.name == 'nt':  # pragma: no cover
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


class ConcurrentSessionInterface(SessionInterface):
    """Preserve Flask-Session cookies and serializers with atomic commits."""

    def __init__(self, backend: Any, cache_dir: str | None = None) -> None:
        self.backend = backend
        self.lock_dir = Path(str(cache_dir) + '.locks') if cache_dir else None

    def __getattr__(self, name: str) -> Any:
        return getattr(self.backend, name)

    def open_session(self, app: Flask, request: Request) -> Any:
        """Load state only for routes that can use it, before any mutation."""
        # Flask opens sessions before its normal URL matching. Resolve the exact
        # endpoint, not a path prefix that might also contain a dynamic route.
        # This app uses only Flask's built-in, session-independent converters.
        try:
            adapter = app.create_url_adapter(request)
            endpoint, _ = adapter.match() if adapter is not None else (None, {})
        except HTTPException:
            endpoint = None
        if endpoint in _PUBLIC_SESSIONLESS_ENDPOINTS:
            # Public files/health never depend on a user's state. A NullSession
            # also makes accidental future writes fail instead of being lost.
            return self.make_null_session(app)
        session = self.backend.open_session(app, request)
        session._concurrent_baseline = deepcopy(dict(session))
        sid = request.cookies.get(app.config['SESSION_COOKIE_NAME'])
        if sid and self.backend.use_signer:
            try:
                sid = self.backend._unsign(app, sid)
            except BadSignature:
                sid = None
        session._concurrent_existing = sid == session.sid
        return session

    def regenerate(self, session: Any) -> None:
        """Rotate the SID and its baseline without deleting concurrent changes."""
        if not session:
            return
        deletion = self.backend.session_class(sid=session.sid)
        deletion._concurrent_baseline = session._concurrent_baseline
        deletion._concurrent_existing = session._concurrent_existing
        try:
            self._commit(current_app, deletion, self.backend._get_store_id(session.sid))
        except SessionConflict as error:
            raise Conflict('La sesión cambió en otra pestaña. Recarga la página.') from error
        session.sid = self.backend._generate_sid(self.backend.sid_length)
        session._concurrent_baseline = {}
        session._concurrent_existing = False
        session.modified = True

    def _merged(self, session: Any, latest: dict | None) -> dict:
        before = session._concurrent_baseline
        if latest is None and session._concurrent_existing:
            raise SessionConflict('Session expired or was cleared')
        latest = latest or {}
        for path in getattr(session, '_concurrent_dependencies', ()):
            if _lookup(before, path) != _lookup(latest, path):
                raise SessionConflict('Session dependency changed')
        proposed = dict(session)
        if not session._concurrent_existing:
            before = {}
        if not session:
            if latest != before:
                raise SessionConflict('Concurrent session clear')
            return {}
        return merge_session(before, proposed, latest)

    def _commit(self, app: Flask, session: Any, store_id: str) -> dict:
        ttl = max(1, int(app.permanent_session_lifetime.total_seconds()))
        if self.lock_dir is not None:
            with _file_lock(self.lock_dir, store_id):
                latest = self.backend._retrieve_session_data(store_id)
                merged = self._merged(session, latest)
                if merged:
                    if not self.backend.cache.set(store_id, merged, timeout=ttl):
                        raise OSError('Failed to persist session')
                elif latest is not None and not self.backend.cache.delete(store_id):
                    raise OSError('Failed to clear session')
                return merged
        # Redis WATCH detects other processes/hosts as well as threads; retries
        # re-read storage, but never re-run the user's operation or side effects.
        from redis.exceptions import WatchError

        for _ in range(16):
            with self.backend.client.pipeline() as pipe:
                try:
                    pipe.watch(store_id)
                    raw = pipe.get(store_id)
                    latest = self.backend.serializer.decode(raw) if raw else None
                    merged = self._merged(session, latest)
                    pipe.multi()
                    if merged:
                        pipe.set(store_id, self.backend.serializer.encode(merged), ex=ttl)
                    else:
                        pipe.delete(store_id)
                    pipe.execute()
                    return merged
                except WatchError:
                    continue
        raise SessionConflict('Session changed too frequently')

    def save_session(self, app: Flask, session: Any, response: Response) -> None:
        """Commit before advertising success or renewing the session cookie."""
        if session.accessed:
            response.vary.add('Cookie')
        if not session and not session.modified:
            return
        if (session and not self.backend.should_set_storage(app, session)
                and not getattr(session, '_concurrent_after_commit', ())):
            return
        try:
            with ExitStack() as stack:
                for lock in getattr(session, '_concurrent_commit_locks', ()):
                    stack.enter_context(lock)
                merged = self._commit(app, session, self.backend._get_store_id(session.sid))
                for callback in getattr(session, '_concurrent_after_commit', ()):
                    callback()
        except SessionConflict:
            response.status_code = 409
            response.set_data(app.json.dumps({
                'success': False, 'preserve_session': True,
                'session_conflict': True,
                'message': 'La sesión cambió en otra pestaña. Recarga la página y vuelve a intentar la operación.',
            }))
            response.content_type = 'application/json'
            response.headers.pop('Content-Disposition', None)
            response.headers['Cache-Control'] = 'no-store'
            return
        if not merged:
            response.delete_cookie(key=self.backend.get_cookie_name(app),
                                   domain=self.backend.get_cookie_domain(app),
                                   path=self.backend.get_cookie_path(app))
            response.vary.add('Cookie')
            return
        if not self.backend.should_set_cookie(app, session):
            return
        value = self.backend._sign(app, session.sid) if self.backend.use_signer else session.sid
        response.set_cookie(
            key=self.backend.get_cookie_name(app), value=value,
            expires=self.backend.get_expiration_time(app, session),
            httponly=self.backend.get_cookie_httponly(app),
            secure=self.backend.get_cookie_secure(app),
            samesite=self.backend.get_cookie_samesite(app),
            domain=self.backend.get_cookie_domain(app),
            path=self.backend.get_cookie_path(app),
        )
        response.vary.add('Cookie')


def install_concurrent_sessions(app: Flask) -> None:
    """Wrap the configured cachelib or Redis interface without changing its SID."""
    directory = app.config['SESSION_CACHE_DIR'] if str(app.config['SESSION_TYPE']).lower() == 'cachelib' else None
    app.session_interface = ConcurrentSessionInterface(app.session_interface, directory)


def after_session_commit(callback: Any, *, lock: Any = None) -> None:
    """Defer local cleanup until storage accepts the request's session changes."""
    if isinstance(current_app.session_interface, ConcurrentSessionInterface):
        callbacks = getattr(flask_session, '_concurrent_after_commit', None)
        if callbacks is None:
            callbacks = []
            flask_session._concurrent_after_commit = callbacks
        callbacks.append(callback)
        if lock is not None:
            locks = getattr(flask_session, '_concurrent_commit_locks', None)
            if locks is None:
                locks = []
                flask_session._concurrent_commit_locks = locks
            if all(held is not lock for held in locks):
                locks.append(lock)
    else:  # Minimal installation with Flask's signed-cookie fallback.
        callback()


def _lookup(data: dict, path: tuple[str, ...]) -> Any:
    value = data
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return _MISSING
        value = value[key]
    return value


def require_session_unchanged(*path: str) -> None:
    """Guard a read dependency used by a deferred trace or unchanged result."""
    if isinstance(current_app.session_interface, ConcurrentSessionInterface):
        paths = getattr(flask_session, '_concurrent_dependencies', None)
        if paths is None:
            paths = []
            flask_session._concurrent_dependencies = paths
        if path not in paths:
            paths.append(path)
