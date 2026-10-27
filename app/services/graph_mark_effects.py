"""Validated BFS/DFS historical mark effects; never redispatch a query.

Snapshots are applied at their chronological history position. Subsequent
mutations operate on restored marks normally: surviving vertices keep marks,
new vertices start at zero and removed vertices cannot be revived by a cache.
"""
from __future__ import annotations
from copy import deepcopy
import hashlib
import hmac
import json
import re
from typing import Any
from flask import current_app, has_app_context, has_request_context, session
from app.config import Config
from app.domain.graph.tad_grafo import _sync_graph_lists

_FIELDS = frozenset({"schema_version", "operation", "start", "topology", "prefix", "marks", "signature"})

def _bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")

def _digest(value: Any) -> str:
    return hashlib.sha256(_bytes(value)).hexdigest()

def _scope() -> str:
    """Bind effects to the current server-side session; detached services have their own scope."""
    if has_request_context():
        sid = getattr(session, "sid", None)
        if not isinstance(sid, str) or not sid:
            # Preserve isolation with Flask's ordinary cookie session in tests.
            from secrets import token_urlsafe
            sid = session.get("_graph_mark_effect_scope")
            if not isinstance(sid, str) or not sid:
                sid = token_urlsafe(24)
                session["_graph_mark_effect_scope"] = sid
        return "graph-session:" + sid
    return "detached-graph-service"

def _signature(body: dict[str, Any]) -> str:
    key = current_app.config["SECRET_KEY"] if has_app_context() else Config.SECRET_KEY
    if isinstance(key, str):
        key = key.encode("utf-8")
    if not isinstance(key, bytes) or not key:
        raise ValueError("Graph mark snapshots require a configured signing key")
    return hmac.new(key, _scope().encode("utf-8") + b"\0graph-marks-v1\0" + _bytes(body), hashlib.sha256).hexdigest()

def _topology(adapter: Any) -> str:
    graph = adapter.graph._g
    return _digest({"directed": adapter.graph.dirigido, "vertices": list(graph._vertices), "arcs": [list(a) for a in graph._arcos]})

def capture_mark_effect(adapter: Any, operation: str, start: int, prefix: list[dict[str, Any]]) -> dict[str, Any]:
    """Capture detached marks only after an actual successful BFS/DFS call."""
    graph = adapter.graph._g
    body = {"schema_version": 1, "operation": operation, "start": start,
            "topology": _topology(adapter), "prefix": _digest(prefix),
            "marks": [[v, graph._marcas[v]] for v in graph._vertices]}
    body["signature"] = _signature(body)
    return deepcopy(body)

def restore_mark_effect(adapter: Any, operation: str, start: int, prefix: list[dict[str, Any]], raw: Any) -> dict[str, Any] | None:
    """Validate the complete effect before changing anything; invalid data is discarded.

    Legacy successful entries remain in caller history without invented effects.
    Missing snapshots cannot establish old mark values; no query is rerun to
    manufacture them. A new actual traversal records a fresh validated effect.
    """
    if not isinstance(raw, dict) or set(raw) != _FIELDS:
        return None
    try:
        body = deepcopy(raw)
        signature = body.pop("signature")
        if not isinstance(signature, str) or re.fullmatch(r"[0-9a-f]{64}", signature) is None:
            return None
        if type(body["schema_version"]) is not int or body["schema_version"] != 1:
            return None
        if body["operation"] != operation or type(body["start"]) is not int or body["start"] != start:
            return None
        if body["topology"] != _topology(adapter) or body["prefix"] != _digest(prefix):
            return None
        graph = adapter.graph._g
        marks = body["marks"]
        if not isinstance(marks, list) or len(marks) != len(graph._vertices):
            return None
        values = {}
        for row in marks:
            if not isinstance(row, list) or len(row) != 2:
                return None
            vertex, mark = row
            if type(vertex) is not int or type(mark) is not int or mark not in (0, 1) or vertex in values:
                return None
            values[vertex] = mark
        if list(values) != list(graph._vertices) or start not in values or values[start] != 1:
            return None
        if not hmac.compare_digest(signature, _signature(body)):
            return None
    except (KeyError, TypeError, ValueError, OverflowError):
        return None
    graph._marcas = values
    _sync_graph_lists(graph)
    return deepcopy(raw)
