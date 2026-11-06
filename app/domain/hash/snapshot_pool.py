"""Lossless Hash snapshot transport; references are immutable JSON, not C pointers."""
from __future__ import annotations
from typing import Any
from app.domain.graph.snapshot_pool import SnapshotPool

CODEC = 'hash-snapshot-pool/v1'
REFERENCE = '$hash_ref'
# Deterministic work estimate; small teaching traces retain their legacy shape.
COMPACT_CELL_STEPS = 12_000

class HashSnapshotPool(SnapshotPool):
    """Reuse typed structural interning with a separate Hash wire protocol."""
    def encode(self, value):
        if isinstance(value, (dict, list, tuple)):
            return {REFERENCE: self.identities[id(value)]}
        return value

    def pack(self, trace):
        steps = [{key: self.encode(self.intern(value)) if isinstance(value, (dict, list)) and key != 'console' else value
                  for key, value in step.items()} for step in trace['steps']]
        return {**trace, 'steps': steps, 'hash_snapshot_codec': CODEC,
                'hash_snapshot_pool': list(self.records),
                'hash_snapshot_stats': {'compound_nodes': len(self.records), 'steps': len(steps), 'sampling': False}}


def compact_hash_trace(trace: dict[str, Any]) -> dict[str, Any]:
    """Pack large traces exactly; never remove instructions, state fields or stdout."""
    if trace.get('hash_snapshot_codec'):
        return trace
    steps = trace.get('steps', [])
    capacity = max(trace.get('final_state', {}).get('metadata', {}).get('capacity', 0),
                   steps[0].get('state_snapshot', {}).get('metadata', {}).get('capacity', 0) if steps else 0)
    if len(steps) * max(capacity, 1) <= COMPACT_CELL_STEPS:
        return trace
    return HashSnapshotPool().pack(trace)


def expand_hash_trace(trace: dict[str, Any]) -> dict[str, Any]:
    """Decode a validated backward-reference table without rerunning the TAD."""
    if 'hash_snapshot_codec' not in trace:
        return trace
    if trace['hash_snapshot_codec'] != CODEC:
        raise ValueError('Unknown Hash snapshot codec')
    objects = []
    def decode(value):
        if isinstance(value, dict):
            if set(value) != {REFERENCE}:
                raise ValueError('Malformed Hash reference')
            index = value[REFERENCE]
            if type(index) is not int or not 0 <= index < len(objects):
                raise ValueError('Invalid or forward Hash reference')
            return objects[index]
        if isinstance(value, list):
            raise ValueError('Unexpected nested Hash record')
        return value
    for record in trace['hash_snapshot_pool']:
        if not isinstance(record, list) or len(record) != 2 or type(record[0]) is not int or record[0] not in (0, 1) or not isinstance(record[1], list):
            raise ValueError('Malformed Hash record')
        if record[0] == 0:
            if any(not isinstance(pair, list) or len(pair) != 2 or not isinstance(pair[0], str) for pair in record[1]):
                raise ValueError('Malformed Hash dictionary')
            keys = [pair[0] for pair in record[1]]
            if len(set(keys)) != len(keys):
                raise ValueError('Duplicate Hash dictionary key')
            value = {key: decode(child) for key, child in record[1]}
        else:
            value = [decode(child) for child in record[1]]
        objects.append(value)
    result = {key: value for key, value in trace.items() if key not in {'hash_snapshot_codec', 'hash_snapshot_pool', 'hash_snapshot_stats'}}
    result['steps'] = [{key: decode(value) if isinstance(value, dict) and REFERENCE in value else value
                        for key, value in step.items()} for step in trace['steps']]
    return result
