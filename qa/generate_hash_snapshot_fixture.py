"""Generate fresh wire data for Node codec/runtime QA from the local checkout.

Usage from repository root:
  python -m qa.generate_hash_snapshot_fixture --capacity 128 --output <temporary-file>
  node qa/hash_snapshot_codec_check.js <temporary-file>
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from app.services.hash_structure_service import HashStructureService
from app.domain.hash.snapshot_pool import HashSnapshotPool


def make_fixture(capacity: int) -> dict:
    """Return a complete trace, not a sampled or archived fixture."""
    history = [{'operation':'create_table','payload':{'capacity':capacity}},
               {'operation':'insert','payload':{'key':1,'value':10}}]
    logical = HashStructureService.execute_operation('hash_table','keys',{},history)['execution_trace']
    fixture = {'wire':HashSnapshotPool().pack(logical)}
    if capacity <= 3:
        fixture['logical'] = logical
    else:
        fixture.update(events=[step['event_type'] for step in logical['steps']], final_state=logical['final_state'])
    return fixture


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capacity', type=int, choices=[3,64,128], default=3)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(make_fixture(args.capacity)), encoding='utf-8')
