"""Acceptance coverage for graph pedagogy phases 4 through 6."""
from pathlib import Path

from app.domain.graph.pedagogy import build_graph_frame, validate_graph_frame
from app.adapters.graph_adapter import GraphAdapter


def _operate(client, operation, payload):
    response = client.post(
        "/graph/graph/operate",
        json={"operation": operation, "payload": payload},
    )
    assert response.status_code == 200
    return response.get_json()


def _prepare_weighted_graph(client, *, directed=True):
    _operate(client, "create_graph", {"directed": directed})
    for vertex in ("1", "2", "3", "4"):
        assert _operate(client, "insert_vertex", {"vertex": vertex})["success"]
    for origin, target, weight in (("1", "2", 2), ("1", "3", 9), ("2", "3", 1), ("2", "1", 5)):
        assert _operate(client, "insert_edge", {"origin": origin, "target": target, "weight": weight})["success"]


def test_representation_degrees_and_logical_memory_are_canonical():
    before = {"nodes": [{"id": "A"}], "edges": [], "directed": True, "validation": True}
    after = {
        "nodes": [{"id": "A"}, {"id": "B"}],
        "edges": [{"source": "A", "target": "B", "weight": 3}, {"source": "B", "target": "B", "weight": 1}],
        "directed": True,
        "validation": True,
    }
    line = "nuevo = malloc(sizeof(struct Vertice));"
    frame = build_graph_frame(
        operation_name="insert_vertex",
        payload={"vertex": "B"},
        step={"line_index": 0, "line_text": line, "state_snapshot": before, "state_after": after, "debug": {"stage": "allocation"}},
        source_lines=[line],
        success=True,
    )
    validate_graph_frame(frame, source_code=line)
    assert frame["representation"]["adjacency"]["A"] == [{"vertex": "B", "weight": 3}]
    degrees = {item["vertex"]: item for item in frame["representation"]["degrees"]}
    assert degrees["A"]["out_degree"] == 1 and degrees["A"]["in_degree"] == 0
    assert degrees["B"]["out_degree"] == 1 and degrees["B"]["in_degree"] == 2
    assert "0xVERT-B" in {item["address"] for item in frame["memory"]["allocated"]}
    assert frame["memory"]["dangling_references"] == []


def test_undirected_self_loop_counts_twice_in_degree():
    state = {"nodes": [{"id": "A"}], "edges": [{"source": "A", "target": "A", "weight": 1}], "directed": False, "validation": True}
    line = "insertar_arista(g, origen, destino, peso);"
    frame = build_graph_frame(operation_name="insert_edge", payload={}, step={"line_index": 0, "line_text": line, "state_snapshot": state, "state_after": state, "debug": {}}, source_lines=[line], success=True)
    assert frame["representation"]["degrees"][0]["degree"] == 2


def test_vertex_removal_reports_incident_edges_and_freed_objects():
    before = {"nodes": [{"id": "A"}, {"id": "B"}, {"id": "C"}], "edges": [{"source": "A", "target": "B", "weight": 1}, {"source": "B", "target": "C", "weight": 2}], "directed": True, "validation": True}
    after = {"nodes": [{"id": "A"}, {"id": "C"}], "edges": [], "directed": True, "validation": True}
    line = "free(vertice);"
    frame = build_graph_frame(operation_name="remove_vertex", payload={"vertex": "B"}, step={"line_index": 0, "line_text": line, "state_snapshot": before, "state_after": after, "debug": {"note": "Se desconectan todas las aristas incidentes antes de liberar."}}, source_lines=[line], success=True)
    freed = {item["id"] for item in frame["memory"]["freed"]}
    assert {"B", "A->B", "B->C"} <= freed
    assert frame["representation"]["adjacency"] == {"A": [], "C": []}


def test_random_graph_seed_reproduces_a_stable_prepared_input():
    first = GraphAdapter(); second = GraphAdapter()
    first.execute("generate_random_graph", {"vertices_count": 8, "seed": 90210})
    second.execute("generate_random_graph", {"vertices_count": 8, "seed": 90210})
    assert first.to_visual_state()["nodes"] == second.to_visual_state()["nodes"]
    assert first.to_visual_state()["edges"] == second.to_visual_state()["edges"]


def test_bfs_and_dfs_frames_expose_real_auxiliary_and_tree(client):
    _prepare_weighted_graph(client, directed=False)
    bfs = _operate(client, "run_bfs", {"start": "1"})["execution_trace"]
    bfs_frames = [step["pedagogy"] for step in bfs["steps"]]
    assert all(frame["auxiliary"]["kind"] == "queue" for frame in bfs_frames)
    assert any(frame["traversal"]["tree_edges"] for frame in bfs_frames)
    assert all(len(frame["traversal"]["discovery_order"]) == len(set(frame["traversal"]["discovery_order"])) for frame in bfs_frames)
    assert any(frame["table"]["previous"] for frame in bfs_frames)

    dfs = _operate(client, "run_dfs", {"start": "1"})["execution_trace"]
    dfs_frames = [step["pedagogy"] for step in dfs["steps"]]
    assert all(frame["auxiliary"]["kind"] == "recursive_stack" for frame in dfs_frames)
    assert any(frame["auxiliary"]["items"] for frame in dfs_frames)
    assert any(frame["traversal"]["tree_edges"] for frame in dfs_frames)


def test_dijkstra_frames_show_priority_queue_relaxation_and_path(client):
    _prepare_weighted_graph(client)
    data = _operate(client, "run_dijkstra", {"start": "1", "end": "3"})
    assert data["result"]["path"] == [1, 2, 3]
    assert data["result"]["distance_to_destination"] == 3.0
    frames = [step["pedagogy"] for step in data["execution_trace"]["steps"]]
    assert all(frame["auxiliary"]["kind"] == "priority_queue" for frame in frames)
    relaxation_frames = [frame for frame in frames if frame["relaxation"]]
    assert relaxation_frames
    assert any(frame["relaxation"]["candidate"] is not None for frame in relaxation_frames)
    assert any(frame["relaxation"]["success"] is False for frame in relaxation_frames)
    assert any(frame["auxiliary"]["iteration"] is not None for frame in relaxation_frames)
    assert frames[-1]["table"]["previous"]["3"] == "2"


def test_bellman_ford_distinguishes_unreachable_and_reachable_negative_cycle(client):
    _prepare_weighted_graph(client)
    unreachable = _operate(client, "run_bellman_ford", {"start": "1", "end": "4"})
    assert unreachable["result"]["reachable"] is False
    stages = {step["debug"].get("stage") for step in unreachable["execution_trace"]["steps"]}
    assert "detect_unreachable" in stages

    _operate(client, "create_graph", {"directed": True})
    for origin, target, weight in (("1", "2", 1), ("2", "3", -3), ("3", "2", 1)):
        _operate(client, "insert_edge", {"origin": origin, "target": target, "weight": weight})
    negative = _operate(client, "run_bellman_ford", {"start": "1", "end": "3"})
    assert negative["result"]["has_negative_cycle"] is True
    detection = [step["pedagogy"] for step in negative["execution_trace"]["steps"] if step["debug"].get("stage") == "detect_negative_cycle"]
    assert detection and detection[0]["auxiliary"]["iteration"] is not None


def test_ui_exposes_representation_traversal_relaxation_and_immutable_replay(client):
    html = client.get("/graph/graph/recorridos").get_data(as_text=True)
    for element_id in ("graph-representation-view", "graph-traversal-view", "graph-relaxation-view"):
        assert f'id="{element_id}"' in html
    assert "BFS:" in html and "no ponderados" in html
    source = (Path(__file__).parents[1] / "static/js/graph.js").read_text(encoding="utf-8")
    assert "pageState.traceSelectionKey === selectionKey" in source
    assert "no cambia al reproducir" in source
