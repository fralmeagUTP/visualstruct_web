"""Persist only the last completed priority queue enqueue, bound to its replay history."""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json
from typing import Any
from flask import session

_KEY = 'priority_queue_enqueue_prepared_v1'


def _digest(history: list[dict[str, Any]]) -> str:
    return hashlib.sha256(json.dumps(history, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()


def remember_enqueue(result: dict[str, Any]) -> None:
    """Keep enqueue trace only; subsequent operations invalidate this record."""
    if not result.get('success'):
        return
    trace = result.get('execution_trace') or {}
    if trace.get('operation_name') == 'encolar':
        session[_KEY] = {'history_digest':_digest(result['history']), 'trace':deepcopy(trace)}
        session.modified = True
    else:
        forget_enqueue()


def prepared_enqueue(history: list[dict[str, Any]], *, source_code: str | None = None) -> dict[str, Any] | None:
    """Return a matching trace without dispatching an adapter operation."""
    record = session.get(_KEY)
    if not isinstance(record, dict) or record.get('history_digest') != _digest(history):
        return None
    trace = record.get('trace')
    if not isinstance(trace, dict) or trace.get('structure_id') != 'priority_queue' or trace.get('operation_name') != 'encolar':
        return None
    if source_code is not None and trace.get('source_code') != source_code:
        return None
    return deepcopy(trace)


def forget_enqueue() -> None:
    """Invalidate only this prepared trace; leave other structure records alone."""
    session.pop(_KEY, None)
