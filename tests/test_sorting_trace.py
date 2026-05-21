"""Trace contract tests for sorting interpreter output."""

from __future__ import annotations


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

