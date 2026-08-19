"""Low-cardinality operational metrics and structured JSON logging."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
import logging
from functools import wraps
from threading import Lock
from time import perf_counter
from typing import Any


LOGGER = logging.getLogger("visualstruct.operations")


class OperationalMetrics:
    """Thread-safe process metrics without user-controlled labels."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: Counter[str] = Counter()
        self._durations: dict[str, dict[str, float]] = {}

    def record(self, event: str, *, outcome: str, duration_ms: float) -> None:
        with self._lock:
            self._counters[f"{event}.total"] += 1
            self._counters[f"{event}.{outcome}"] += 1
            duration = self._durations.setdefault(
                event, {"count": 0.0, "sum_ms": 0.0, "max_ms": 0.0}
            )
            duration["count"] += 1
            duration["sum_ms"] += duration_ms
            duration["max_ms"] = max(duration["max_ms"], duration_ms)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "counters": dict(self._counters),
                "durations": deepcopy(self._durations),
            }

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()
            self._durations.clear()


operational_metrics = OperationalMetrics()


def emit_operational_event(
    event: str,
    *,
    outcome: str,
    duration_ms: float,
    **fields: str | int | float | bool | None,
) -> None:
    """Record metrics and emit one deterministic, payload-free JSON event."""
    operational_metrics.record(event, outcome=outcome, duration_ms=duration_ms)
    document = {
        "event": event,
        "outcome": outcome,
        "duration_ms": round(duration_ms, 3),
        **fields,
    }
    LOGGER.info(json.dumps(document, ensure_ascii=False, sort_keys=True))


def observe_replay(function):
    """Measure a ``_rebuild_adapter(structure_id, history)`` boundary."""
    @wraps(function)
    def wrapped(structure_id, history):
        started = perf_counter()
        try:
            result = function(structure_id, history)
        except Exception as error:
            emit_operational_event(
                "history_replay",
                outcome="error",
                duration_ms=(perf_counter() - started) * 1000,
                structure_id=structure_id,
                replay_operations=len(history) if isinstance(history, list) else 0,
                valid_operations=0,
                error_type=type(error).__name__,
            )
            raise
        valid_history = result[1]
        emit_operational_event(
            "history_replay",
            outcome="success",
            duration_ms=(perf_counter() - started) * 1000,
            structure_id=structure_id,
            replay_operations=len(history) if isinstance(history, list) else 0,
            valid_operations=len(valid_history),
        )
        return result

    return wrapped
