"""Opt-in numeric-only diagnostics for the existing reconstruction budget gate."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any


FAMILIES = ('sequential', 'tree', 'graph', 'hash', 'sorting')
COUNT_FIELDS = ('history_operations', 'replay_operations')
TIME_FIELDS = ('median_ms', 'p95_ms', 'budget_ms')
OUTPUT_NAME = 'checkpoint-reconstruction-result.json'


def _count(value: Any) -> int:
    if type(value) is not int or value < 0:
        raise ValueError('Invalid numeric diagnostic count')
    return value


def _time(value: Any) -> int | float:
    if type(value) not in (int, float) or value < 0 or (type(value) is float and not math.isfinite(value)):
        raise ValueError('Invalid numeric diagnostic time')
    return value


def write_checkpoint_diagnostics(report: dict[str, Any]) -> None:
    """Write only approved numeric metrics; never serialize the raw report.

    Environment metadata, timestamps, paths, fallback descriptions, unknown
    families and arbitrary extra fields are excluded by construction. Failures
    are not swallowed and the caller's benchmark/assertions remain unchanged.
    """
    destination = os.environ.get('VISUALSTRUCT_E2E_DIAGNOSTICS_DIR')
    if destination is None:
        return
    if not destination:
        raise ValueError('Numeric diagnostics directory must not be empty')
    safe = {
        'iterations': _count(report['iterations']),
        'budget_ms': _time(report['budget_ms']),
        'results': {},
    }
    for family in FAMILIES:
        result = report['results'][family]
        safe['results'][family] = {
            **{key: _count(result[key]) for key in COUNT_FIELDS},
            **{key: _time(result[key]) for key in TIME_FIELDS},
        }
    # Validate/serialize the whitelist fully before creating any output file.
    serialized = json.dumps(safe, allow_nan=False, sort_keys=True, indent=2) + '\n'
    folder = Path(destination)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / OUTPUT_NAME).write_text(serialized, encoding='utf-8')
