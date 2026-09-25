"""Acceptance tests for MST, active learning, comparison and graph QA closure."""
from pathlib import Path

from app.services.graph_structure_service import GraphStructureService


def _operate(client, operation, payload):
    response = client.post("/graph/graph/operate", json={"operation": operation, "payload": payload})
    assert response.status_code == 200, response.get_data(as_text=True)
    return response.get_json()


def _triangle(client):
    _operate(client, "create_graph", {"directed": False})
    for vertex in (1, 2, 3):
        _operate(client, "insert_vertex", {"vertex": vertex})
    for origin, target, weight in ((1, 2, 1), (2, 3, 2), (1, 3, 5)):
        _operate(client, "insert_edge", {"origin": origin, "target": target, "weight": weight})


def test_kruskal_frames_expose_find_union_rejection_and_valid_weight(client):
    _triangle(client)
    data = _operate(client, "run_kruskal", {})
    result = data["result"]
    assert result["kind"] == "mst" and result["total_weight"] == 3.0
    assert len(result["mst_edges"]) == 2
    frames = [step["pedagogy"] for step in data["execution_trace"]["steps"]]
    stages = {frame["case"] for frame in frames}
    assert {"find", "union", "accept_edge", "reject_edge", "complete"} <= stages
    union_frames = [frame for frame in frames if frame["case"] in {"find", "union"}]
    assert union_frames and any(frame["auxiliary"]["items"] for frame in union_frames)
    rejected = next(frame for frame in frames if frame["case"] == "reject_edge")
    assert "ciclo" in rejected["narration"]["basic"].lower()


def test_prim_distinguishes_mst_from_disconnected_forest(client):
    _operate(client, "create_graph", {"directed": False})
    for vertex in (1, 2, 3, 4):
        _operate(client, "insert_vertex", {"vertex": vertex})
    _operate(client, "insert_edge", {"origin": 1, "target": 2, "weight": 1})
    _operate(client, "insert_edge", {"origin": 3, "target": 4, "weight": 2})
    data = _operate(client, "run_prim", {"start": 1})
    assert data["result"]["kind"] == "minimum_spanning_forest"
    assert data["result"]["components_count"] == 2
    assert len(data["result"]["mst_edges"]) == 2
    assert any(step["pedagogy"]["case"] == "restart_component" for step in data["execution_trace"]["steps"])


def test_mst_algorithms_reject_directed_graph(client):
    _operate(client, "create_graph", {"directed": True})
    _operate(client, "insert_edge", {"origin": 1, "target": 2, "weight": 1})
    for operation, payload in (("run_prim", {"start": 1}), ("run_kruskal", {})):
        response = client.post("/graph/graph/operate", json={"operation": operation, "payload": payload})
        assert response.status_code == 400
        assert "no dirigido" in response.get_json()["message"]


def test_comparison_uses_isolated_copies_and_preserves_input():
    graph = {"directed": False, "nodes": [{"id": "1"}, {"id": "2"}, {"id": "3"}], "edges": [{"source": "1", "target": "2", "weight": 1}, {"source": "2", "target": "3", "weight": 2}]}
    original = {"directed": graph["directed"], "nodes": [dict(item) for item in graph["nodes"]], "edges": [dict(item) for item in graph["edges"]]}
    for kind in ("bfs-dfs", "dijkstra-bellman-ford", "prim-kruskal"):
        result = GraphStructureService.compare_algorithms(kind, graph, "1", "3")
        assert result["isolated"] is True
        assert result["left"]["algorithm"] != result["right"]["algorithm"]
    assert graph == original


def test_compare_route_and_learning_regions(client):
    _triangle(client)
    state = _operate(client, "list_edges", {})["visual_state"]
    response = client.post("/graph/compare", json={"kind": "prim-kruskal", "graph": state, "start": 1})
    assert response.status_code == 200 and response.get_json()["isolated"] is True
    html = client.get("/graph/graph/expansion-minima").get_data(as_text=True)
    for element_id in ("graph-prepare", "graph-sim-pause", "graph-sim-home", "graph-sim-end", "graph-sim-repeat", "graph-progress", "graph-step-metadata", "graph-prediction", "graph-practice-mode", "graph-compare-kind", "graph-compare-grid", "graph-export-image", "graph-export-summary", "graph-accessible-announcer"):
        assert f'id="{element_id}"' in html


def test_help_glossary_teacher_keyboard_and_frontend_restoration_contract(client):
    help_html = client.get("/help/graph/graph").get_data(as_text=True)
    for text in ("Guía de aprendizaje", "Invariantes", "Complejidad", "Errores frecuentes", "Glosario", "Guía docente", "Alt+→"):
        assert text in help_html
    source = (Path(__file__).parents[1] / "static/js/graph.js").read_text(encoding="utf-8")
    for token in ("tracePlayer.seek", "refreshGraphPrintfConsole(cursor)", "renderGraphPedagogy", "graph-practice-hidden", "exportVisualStateAsJpg", "Entrada inmutable"):
        assert token in source
