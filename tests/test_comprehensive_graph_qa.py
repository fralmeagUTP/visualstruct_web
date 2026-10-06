"""Complete route-level QA matrix for construction and graph algorithms."""

from __future__ import annotations

from typing import Any

import pytest

from app.services.graph_structure_service import GraphStructureService


BASE = [
    ("create_graph", {"directed": "false"}),
    ("insert_vertex", {"vertex": "1"}),
    ("insert_vertex", {"vertex": "2"}),
    ("insert_vertex", {"vertex": "3"}),
    ("insert_edge", {"origin": "1", "target": "2", "weight": "1"}),
    ("insert_edge", {"origin": "2", "target": "3", "weight": "2"}),
    ("insert_edge", {"origin": "1", "target": "3", "weight": "5"}),
]
CASES: dict[str, tuple[list[tuple[str, dict[str, str]]], dict[str, str]]] = {
    "create_graph": ([], {"directed": "false"}),
    "generate_random_graph": ([], {"vertices_count": "5"}),
    "insert_vertex": ([("create_graph", {"directed": "false"})], {"vertex": "1"}),
    "remove_vertex": (BASE, {"vertex": "3"}),
    "insert_edge": (BASE[:4], {"origin": "1", "target": "2", "weight": "1"}),
    "remove_edge": (BASE, {"origin": "1", "target": "3"}),
    "exists_vertex": (BASE, {"vertex": "1"}),
    "exists_edge": (BASE, {"origin": "1", "target": "2"}),
    "list_vertices": (BASE, {}),
    "list_edges": (BASE, {}),
    "neighbors": (BASE, {"vertex": "1"}),
    "edge_weight": (BASE, {"origin": "1", "target": "2"}),
    "run_bfs": (BASE, {"start": "1"}),
    "run_dfs": (BASE, {"start": "1"}),
    "run_dijkstra": (BASE, {"start": "1", "end": "3"}),
    "run_bellman_ford": (BASE, {"start": "1", "end": "3"}),
    "run_prim": (BASE, {"start": "1"}),
    "run_kruskal": (BASE, {}),
    "clear_graph": (BASE, {}),
}


def _post(client: Any, operation: str, payload: dict[str, str]) -> Any:
    return client.post("/graph/graph/operate", json={"operation": operation, "payload": payload})


def test_graph_case_matrix_covers_every_registered_operation() -> None:
    operations = {entry["name"] for entry in GraphStructureService._new_adapter("graph").get_supported_operations()}
    assert set(CASES) == operations


@pytest.mark.parametrize("operation", sorted(CASES))
def test_every_graph_operation_returns_a_consistent_trace(client: Any, operation: str) -> None:
    setup, payload = CASES[operation]
    for setup_op, setup_payload in setup:
        assert _post(client, setup_op, setup_payload).status_code == 200
    response = _post(client, operation, payload)
    assert response.status_code == 200, response.get_json()
    body = response.get_json()
    assert body["execution_trace"]["steps"]
    assert body["execution_trace"]["steps"][-1]["state_after"] == body["visual_state"]
    assert all(step["pedagogy"]["invariant"]["holds"] for step in body["execution_trace"]["steps"])


def test_graph_algorithms_return_expected_traversal_shortest_path_and_mst(client: Any) -> None:
    for operation, payload in BASE:
        assert _post(client, operation, payload).status_code == 200
    bfs = _post(client, "run_bfs", {"start": "1"}).get_json()["result"]
    dijkstra = _post(client, "run_dijkstra", {"start": "1", "end": "3"}).get_json()["result"]
    prim = _post(client, "run_prim", {"start": "1"}).get_json()["result"]
    kruskal = _post(client, "run_kruskal", {}).get_json()["result"]
    assert bfs == [1, 2, 3]
    assert dijkstra["distance_to_destination"] == 3
    assert dijkstra["path"] == [1, 2, 3]
    assert prim["total_weight"] == kruskal["total_weight"] == 3


def test_graph_invalid_input_and_dijkstra_negative_weight_are_controlled(client: Any) -> None:
    invalid = _post(client, "insert_vertex", {"vertex": "not-an-int"})
    assert invalid.status_code == 400
    for operation, payload in [("create_graph", {"directed": "true"}), ("insert_vertex", {"vertex": "1"}), ("insert_vertex", {"vertex": "2"}), ("insert_edge", {"origin": "1", "target": "2", "weight": "-1"})]:
        assert _post(client, operation, payload).status_code == 200
    negative = _post(client, "run_dijkstra", {"start": "1", "end": "2"})
    assert negative.status_code == 400
    assert "Bellman-Ford" in negative.get_json()["message"]


@pytest.mark.parametrize("phase", ["construccion", "recorridos", "camino-minimo", "expansion-minima"])
def test_every_graph_learning_phase_renders(client: Any, phase: str) -> None:
    response = client.get(f"/graph/graph/{phase}")
    assert response.status_code == 200
    assert phase.encode() in response.data
