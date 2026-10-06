"""Contract tests for the opt-in C audit event channel."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.check_c_conformance import CHECKS, _canonical_outputs, _printf_outputs, _qa_events, run_checks


ROOT = Path(__file__).resolve().parents[1]


def test_all_thirteen_harnesses_opt_into_the_qa_channel() -> None:
    manifest = json.loads(
        (ROOT / "tests/conformance/c_harnesses/manifest.json").read_text(encoding="utf-8")
    )["structures"]
    for structure_id, filename in manifest.items():
        source = (ROOT / "tests/conformance/c_harnesses" / filename).read_text(encoding="utf-8")
        assert f'harness_qa_begin("{structure_id}"' in source
        assert "harness_qa_end();" in source
    assert len(CHECKS) == 13


def test_parser_accepts_only_versioned_ndjson_events() -> None:
    stderr = "diagnostic\n" + (
        '{"schema":"didactic-c-event/v1","sequence":0,"structure_id":"stack",'
        '"event":"lifecycle","phase":"begin","detail":"harness invocation"}\n'
    )
    assert _qa_events(stderr) == [{
        "schema": "didactic-c-event/v1", "sequence": 0, "structure_id": "stack",
        "event": "lifecycle", "phase": "begin", "detail": "harness invocation",
    }]


def test_instrumented_stack_executes_with_strict_c17() -> None:
    run_checks(compiler="gcc", sanitizers=False, only={"stack"}, qa_events=True)


def test_all_representative_runs_report_dynamic_allocation() -> None:
    run_checks(compiler="gcc", sanitizers=False, qa_events=True)


def test_canonical_snapshot_parser_preserves_causal_order() -> None:
    stdout = "\n".join([
        '{"schema":"canonical-state/v1","structure_id":"stack","state":{"values":[1]}}',
        "non-json diagnostic",
        '{"schema":"canonical-state/v1","structure_id":"stack","state":{"values":[2,1]}}',
    ])
    assert [item["state"] for item in _canonical_outputs(stdout)] == [
        {"values": [1]}, {"values": [2, 1]}
    ]


def test_printf_capture_excludes_canonical_transport() -> None:
    stdout = 'insertado 10\n{"schema":"canonical-state/v1","state":{}}\n'
    assert _printf_outputs(stdout) == ["insertado 10"]


def test_hash_lookup_update_collision_and_remove_execute_under_c17() -> None:
    run_checks(compiler="gcc", sanitizers=False, only={"hash_table"}, qa_events=True)
