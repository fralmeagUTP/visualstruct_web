"""Characterization tests that freeze representative trace behavior."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.services.graph_structure_service import GraphStructureService
from app.services.hash_structure_service import HashStructureService
from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.services.sorting_structure_service import SortingStructureService
from app.services.structure_service import StructureService
from app.services.trace import LegacyTraceAdapter


GOLDEN = json.loads(
    (Path(__file__).parent / "golden" / "traces_v1.json").read_text(encoding="utf-8")
)["cases"]


def _execute(service: Any, structure_id: str, operations: list[tuple[str, dict[str, Any]]]) -> dict[str, Any]:
    history: list[dict[str, Any]] = []
    response: dict[str, Any] = {}
    for operation, payload in operations:
        response = service.execute_operation(
            structure_id=structure_id,
            operation_name=operation,
            payload=payload,
            history=history,
        )
        assert response["success"] is True
        history = response["history"]
    return response


def _assert_trace(case: str, response: dict[str, Any]) -> None:
    expected = GOLDEN[case]
    steps = response["execution_trace"]["steps"]
    lines = [step.get("line_text") for step in steps]
    assert len(steps) == expected["step_count"]
    if "line_texts" in expected:
        assert lines == expected["line_texts"]
    for line in expected.get("required_lines", []):
        assert line in lines
    assert response["execution_trace"]["final_state"] == response["visual_state"]
    assert LegacyTraceAdapter.round_trip(steps) == steps


def test_sequential_trace_golden() -> None:
    response = _execute(StructureService, "stack", [("apilar", {"value": 7})])
    _assert_trace("sequential", response)
    state = response["visual_state"]
    assert {"size": state["size"], "values": [item["value"] for item in state["items"]]} == GOLDEN["sequential"]["final"]


def test_tree_trace_golden() -> None:
    response = _execute(HierarchicalStructureService, "avl", [("insertar", {"value": value}) for value in (30, 20, 10)])
    _assert_trace("tree", response)
    state = response["visual_state"]
    actual = {"size": state["size"], "root": state["root"]["value"], "inorder": state["traversals"]["inorden"]}
    assert actual == GOLDEN["tree"]["final"]


def test_graph_trace_golden() -> None:
    response = _execute(GraphStructureService, "graph", [
        ("create_graph", {"directed": False}),
        ("insert_vertex", {"vertex": 1}),
        ("insert_vertex", {"vertex": 2}),
        ("insert_edge", {"origin": 1, "target": 2, "weight": 3}),
    ])
    _assert_trace("graph", response)
    state = response["visual_state"]
    edge = state["edges"][0]
    actual = {"vertices": state["metadata"]["vertices_count"], "edges": state["metadata"]["edges_count"], "edge": [edge["source"], edge["target"], edge["weight"]]}
    assert actual == GOLDEN["graph"]["final"]


def test_hash_trace_golden() -> None:
    response = _execute(HashStructureService, "hash_table", [
        ("create_table", {"capacity": 5}),
        ("insert", {"key": "1", "value": "1"}),
    ])
    _assert_trace("hash", response)
    state = response["visual_state"]
    items = [[entry["key"], entry["value"]] for bucket in state["buckets"] for entry in bucket["entries"]]
    actual = {"size": state["metadata"]["size"], "capacity": state["metadata"]["capacity"], "items": items}
    assert actual == GOLDEN["hash"]["final"]


def test_sorting_trace_golden() -> None:
    response = _execute(SortingStructureService, "sorting_array", [
        ("create_array", {"values": "3,1,2"}),
        ("select_algorithm", {"algorithm_id": "burbuja"}),
        ("run", {"mode": "fast"}),
    ])
    _assert_trace("sorting", response)
    state = response["visual_state"]
    assert {"items": state["items"], "algorithm": state["algorithm"]} == GOLDEN["sorting"]["final"]
