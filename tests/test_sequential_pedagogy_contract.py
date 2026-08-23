"""Pedagogical contract tests for sequential structures."""

from __future__ import annotations

import json
from pathlib import Path

from app.domain.sequential.pedagogy import (
    SEQUENTIAL_FRAME_SCHEMA_VERSION,
    SEQUENTIAL_LEARNING_CATALOG,
    SEQUENTIAL_GUIDED_EXAMPLES,
    SEQUENTIAL_STRUCTURES,
    build_sequential_frame,
    sequential_frame_schema,
    validate_sequential_frame,
)


def _step(line: str) -> dict:
    return {"line_index": 0, "line_text": line, "state_snapshot": {"kind": "linear", "values": [1]}, "state_after": {"kind": "linear", "values": [1, 8]}, "condition_result": False}


def test_learning_catalog_and_schema_cover_six_tads() -> None:
    assert set(SEQUENTIAL_LEARNING_CATALOG) == SEQUENTIAL_STRUCTURES
    assert sequential_frame_schema()["version"] == SEQUENTIAL_FRAME_SCHEMA_VERSION
    assert sequential_frame_schema()["$id"].endswith("/v2")
    assert sequential_frame_schema()["levels"] == ["basic", "intermediate", "advanced"]
    for profile in SEQUENTIAL_LEARNING_CATALOG.values():
        assert profile["objective"] and profile["prior"] and profile["mastery"]


def test_golden_memory_and_control_flow_events_are_classified() -> None:
    fixtures = json.loads((Path(__file__).parent / "golden" / "sequential_pedagogical_frames_v1.json").read_text(encoding="utf-8"))["fixtures"]
    expected = {"call": "call", "return": "return", "malloc": "allocation", "allocation_failure": "condition", "link": "link", "branch": "condition", "loop": "condition", "free": "free"}
    for name, line in fixtures.items():
        frame = build_sequential_frame(structure_id="stack", operation_name="apilar", payload={"value": 8}, step=_step(line), success=True)
        validate_sequential_frame(frame, source_code=line)
        assert frame["concept"] == expected[name]


def test_real_sequential_trace_exposes_complete_canonical_frames(client) -> None:
    response = client.post("/sequential/stack/operate", json={"operation": "apilar", "payload": {"value": "42"}})
    assert response.status_code == 200
    trace = response.get_json()["execution_trace"]
    assert trace["pedagogy_schema_version"] == SEQUENTIAL_FRAME_SCHEMA_VERSION
    assert trace["learning_profile"]["objective"]
    for step in trace["steps"]:
        validate_sequential_frame(step["pedagogy"], source_code=trace["source_code"])
        assert step["pedagogy"]["invariant"]["holds"] is True
        assert step["pedagogy"]["invariant"]["symbol"] == "✓"
        assert "nodos=" in step["pedagogy"]["invariant"]["evidence"]
        assert set(step["pedagogy"]["narration"]) == {"basic", "intermediate", "advanced"}
        assert step["pedagogy"]["heap_transition"]["dangling_references"] == []


def test_guided_examples_cover_limits_and_specific_sequences() -> None:
    assert set(SEQUENTIAL_GUIDED_EXAMPLES) == SEQUENTIAL_STRUCTURES
    kinds = {example["kind"] for examples in SEQUENTIAL_GUIDED_EXAMPLES.values() for example in examples}
    assert {"empty", "one", "several", "repeated", "invalid", "extremes", "not_found"} <= kinds
    ids = {example["id"] for examples in SEQUENTIAL_GUIDED_EXAMPLES.values() for example in examples}
    assert {"lifo", "fifo", "tie", "circularity", "isolation"} <= ids


def test_trace_boundaries_are_exactly_reversible(client) -> None:
    trace = client.post("/sequential/stack/operate", json={"operation": "apilar", "payload": {"value": "42"}}).get_json()["execution_trace"]
    for previous, current in zip(trace["steps"], trace["steps"][1:]):
        assert previous["state_after"] == current["state_snapshot"]


def test_sequential_page_exposes_learning_regions_and_mobile_workspace(client) -> None:
    html = client.get("/sequential/stack").get_data(as_text=True)
    for label in ("Preparar", "Predecir", "Controlar la ejecución", "Comprender", "Relacionar con C", "Reflexionar"):
        assert label in html
    assert 'id="seq-visual-region"' in html
    assert 'id="seq-code-region"' in html
    assert 'data-seq-tab="visual"' in html and 'data-seq-tab="code"' in html
    assert 'id="seq-hide-comments"' in html and 'id="seq-function-list"' in html
    assert 'id="seq-restart-execution"' in html
    for element_id in ("seq-learning-level", "seq-guided-example", "seq-condition-view", "seq-variable-view", "seq-pointer-view", "seq-heap-view", "seq-call-view", "seq-sim-prepare", "seq-sim-pause", "seq-sim-start", "seq-sim-end", "seq-sim-repeat", "seq-progress-slider", "seq-prediction-panel", "seq-practice-mode", "seq-reset-learning"):
        assert f'id="{element_id}"' in html


def test_priority_help_describes_arrival_order_and_selection(client) -> None:
    html = client.get("/help/sequential/priority_queue").get_data(as_text=True)
    assert "orden de llegada" in html
    assert "selecciona" in html


def test_sequential_javascript_exposes_per_tad_semantics_and_active_learning() -> None:
    source = (Path(__file__).parents[1] / "static" / "js" / "sequential.js").read_text(encoding="utf-8")
    for marker in ("Regla: LIFO", "Regla: FIFO", "empate → gana quien llegó antes", "TAIL.next → HEAD ↻", "ramas no activas: sin cambios"):
        assert marker in source
    for marker in ("requestPrediction", "learningProgressKey", "tracePlayer.seek", "seq-practice-hidden"):
        assert marker in source
