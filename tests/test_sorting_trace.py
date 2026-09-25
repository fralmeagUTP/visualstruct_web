"""Trace contract tests for sorting interpreter output."""

from __future__ import annotations

import pytest

from app.adapters.sorting_adapter import SortingAdapter
from app.services.trace import TraceEngine, TraceStrategyRegistry


def test_sorting_trace_contains_visual_snapshots(client) -> None:
    """Run should produce trace steps with snapshot/after states."""
    client.post("/api/ordenamiento/create-array", json={"values": "4,2,3,1"})
    client.post("/api/ordenamiento/algorithm", json={"algorithm_id": "seleccion"})
    response = client.post("/api/ordenamiento/run", json={"mode": "step_by_step", "algorithm_id": "seleccion"})
    assert response.status_code == 200
    data = response.get_json()
    steps = data["execution_trace"]["steps"]
    assert steps, "Expected non-empty execution trace."
    first = steps[0]
    assert "state_snapshot" in first
    assert "state_after" in first
    assert "line_index" in first
    assert "metrics" in first["state_after"]
    assert "trace_token" in first["state_after"]
    assert "trace_action" in first["state_after"]
    trace = data["execution_trace"]
    assert trace["steps"][-1]["state_after"] == trace["final_state"]
    assert TraceStrategyRegistry.resolve(trace["structure_id"]).family == "sorting"
    semantic_steps = TraceEngine.validate_legacy_trace(trace)
    assert semantic_steps[-1].after_state == data["visual_state"]


@pytest.mark.parametrize(
    "algorithm_id",
    [
        "intercambio",
        "seleccion",
        "insercion",
        "burbuja",
        "shell",
        "quicksort",
        "mergesort",
        "heapsort",
        "counting_sort",
        "binsort",
        "radixsort",
    ],
)
def test_all_sorting_algorithms_satisfy_common_trace_contract(algorithm_id: str) -> None:
    adapter = SortingAdapter()
    adapter.execute("create_array", {"values": "5,1,4,2,3"})
    adapter.execute("select_algorithm", {"algorithm_id": algorithm_id})
    result = adapter.execute("run", {"mode": "step_by_step", "source_code": ""})
    trace = result["execution_trace"]
    semantic_steps = TraceEngine.validate_legacy_trace(trace)
    assert semantic_steps
    assert semantic_steps[-1].after_state == result["visual_state"]
    assert result["visual_state"]["items"] == [1, 2, 3, 4, 5]
