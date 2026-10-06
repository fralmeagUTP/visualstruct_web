"""Keep the last completed C dequeue trace, bound to history and source bytes."""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json
from typing import Any
from flask import session

_KEY='queue_dequeue_prepared_v1'

def _digest(history: list[dict[str, Any]]) -> str:
    return hashlib.sha256(json.dumps(history,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')).hexdigest()

def remember_dequeue(result: dict[str, Any]) -> None:
    """Save a completed dequeue, including its genuine native empty guard trace."""
    trace=result.get('execution_trace') or {}
    memory=((trace.get('steps') or [{}])[0].get('pedagogy') or {}).get('dequeue_memory')
    if trace.get('structure_id')=='queue' and trace.get('operation_name')=='desencolar' and memory:
        session[_KEY]={'history_digest':_digest(result['history']),'trace':deepcopy(trace)}
        session.modified=True
    elif result.get('success'):
        forget_dequeue()

def prepared_dequeue(history: list[dict[str, Any]], *, source_code: str) -> dict[str, Any] | None:
    """Reuse the exact stored trace without building or appending an operation."""
    record=session.get(_KEY)
    if not isinstance(record,dict) or record.get('history_digest')!=_digest(history):return None
    trace=record.get('trace')
    if not isinstance(trace,dict) or trace.get('structure_id')!='queue' or trace.get('operation_name')!='desencolar' or trace.get('source_code')!=source_code:return None
    return deepcopy(trace)

def forget_dequeue() -> None:
    """Invalidate only this prepared record, preserving other structure namespaces."""
    session.pop(_KEY,None)
