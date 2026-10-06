"""Acceptance tests for MST, active learning, comparison and graph QA closure."""
from app.domain.graph.snapshot_pool import expand_graph_trace
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
    assert {(min(a,b), max(a,b), weight) for a,b,weight in result["mst_edges"]} == {(1,2,1),(2,3,2)}
    trace = expand_graph_trace(data["execution_trace"])
    steps = trace["steps"]
    source = trace["source_code"].splitlines()
    assert all(source[step["line_index"]] == step["line_text"] for step in steps if step.get("line_index") is not None)
    finds = [step for step in steps if _C_event(step).get("function") == "grafo_encontrar_conjunto" and _C_event(step)["phase"] == "enter"]
    unions = [step for step in steps if _C_event(step).get("function") == "grafo_unir_conjuntos" and _C_event(step)["phase"] == "enter"]
    assert finds and len(unions) == 2
    first = finds[0]["pedagogy"]["memory_state"]
    variables = _C_vars(first, "grafo_kruskal")
    assert _live_int_buffer(first, variables["conjuntos"]["padre"], 3) == [0,1,2]
    decisions = [step for step in steps if _C_event(step).get("function") == "grafo_kruskal" and _C_event(step)["phase"] == "condition" and "grafo_encontrar_conjunto(&conjuntos" in step["line_text"]]
    assert len(decisions) == 6
    assert sum(bool(_C_event(step)["value"]) for step in decisions) == 2
    assert sum(not bool(_C_event(step)["value"]) for step in decisions) == 4
    for step in decisions:
        assert _C_event(step)["C_executed"]
        memory = step["pedagogy"]["memory_state"]
        variables = _C_vars(memory, "grafo_kruskal")
        parents = _live_int_buffer(memory, variables["conjuntos"]["padre"], 3)
        roots_differ = _C_root(parents, variables["u"]) != _C_root(parents, variables["v"])
        assert roots_differ == bool(_C_event(step)["value"])
        if not roots_differ:
            # The actual false C guard and equal live roots identify rejection;
            # learners must receive its cycle reason, not only a generic phase.
            narration = step["pedagogy"]["narration"]["basic"].lower()
            assert "ciclo" in narration and any(word in narration for word in ("rechaz", "descart", "exclu", "no se", "no agregar", "no añadir")), (
                f"Rechazo C con raices iguales ({_C_root(parents, variables['u'])}); "
                f"la narracion debe explicar el descarte por ciclo: {narration!r}"
            )
    writes = [step for step in steps if _C_event(step).get("function") == "grafo_unir_conjuntos" and _C_event(step)["phase"] == "write" and _C_event(step)["name"] == "c->padre[ry]"]
    assert len(writes) == 2
    assert any(_C_event(step).get("function") == "grafo_kruskal" and _C_event(step)["phase"] == "return" for step in steps)


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
    assert data["result"]["total_weight"] == 3
    assert {(min(a,b), max(a,b), weight) for a,b,weight in data["result"]["mst_edges"]} == {(1,2,1),(3,4,2)}
    trace = expand_graph_trace(data["execution_trace"])
    steps = trace["steps"]
    source = trace["source_code"].splitlines()
    assert all(source[step["line_index"]] == step["line_text"] for step in steps if step.get("line_index") is not None)
    restarts = [(i,step) for i,step in enumerate(steps) if _C_event(step).get("function") == "grafo_prim" and _C_event(step)["phase"] == "condition" and step["line_text"].strip() == "if (u == -1) {" and _C_event(step)["value"] == 1]
    assert len(restarts) == 1
    index, restart = restarts[0]
    memory = restart["pedagogy"]["memory_state"]
    variables = _C_vars(memory, "grafo_prim")
    assert variables["u"] == -1 and _C_event(restart)["C_executed"]
    visited = _live_int_buffer(memory, variables["visitado"], 4)
    candidates = _live_int_buffer(memory, variables["candidato"], 4)
    assert any(not flag for flag in visited)
    assert not any(not visited[j] and candidates[j] for j in range(4))
    selected = next(step for step in steps[index+1:] if _C_event(step).get("function") == "grafo_prim" and _C_event(step)["phase"] == "write" and _C_event(step)["name"] == "u" and "if (!visitado[j])" in step["line_text"])
    chosen = _C_event(selected)["value"]
    assert 0 <= chosen < 4 and not visited[chosen]
    zeroed = next(step for step in steps[index+1:] if _C_event(step).get("function") == "grafo_prim" and _C_event(step)["phase"] == "write" and _C_event(step)["name"] == "costo[u]" and "if (!visitado[j])" in step["line_text"])
    assert _C_event(zeroed)["value"] == 0
    after = zeroed["pedagogy"]["memory_state"]
    variables_after = _C_vars(after, "grafo_prim")
    assert variables_after["u"] == chosen
    assert _live_int_buffer(after, variables_after["costo"], 4)[chosen] == 0
    assert any(_C_event(step).get("function") == "grafo_prim" and _C_event(step)["phase"] == "return" for step in steps)


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
    for element_id in ("graph-controls", "graph-sim-play", "graph-sim-step", "graph-step-navigation", "graph-sim-counter", "graph-step-metadata", "graph-visual-region", "graph-code-region", "graph-export-image", "graph-export-summary", "graph-accessible-announcer", "graph-printf-console", "action-history", "tad-record"):
        assert f'id="{element_id}"' in html


def test_help_glossary_teacher_keyboard_and_frontend_restoration_contract(client):
    help_html = client.get("/help/graph/graph").get_data(as_text=True)
    for text in ("Guía de aprendizaje", "Invariantes", "Complejidad", "Errores frecuentes", "Glosario", "Guía docente", "Alt+→"):
        assert text in help_html
    source = (Path(__file__).parents[1] / "static/js/graph.js").read_text(encoding="utf-8")
    for token in ("tracePlayer.seek", "refreshGraphPrintfConsole(cursor)", "renderGraphPedagogy", "graph-practice-hidden", "exportVisualStateAsJpg", "Entrada inmutable"):
        assert token in source

def _C_event(step):
    return step["pedagogy"]["instruction_event"]

def _C_vars(memory, function):
    frame = next(frame for frame in memory["frames"] if frame["function"] == function)
    return {name: cell["value"] for scope in frame["scopes"] for name, cell in scope["variables"].items()}

def _live_int_buffer(memory, identity, size):
    node = next(node for node in memory["heap_nodes"] if node["id"] == identity)
    assert node["alive"] and node["kind"] == "int" and node["element_type"] == "int"
    assert len(node["items"]) == size and all(type(value) is int for value in node["items"])
    return node["items"]

def _C_root(parents, index):
    seen = set()
    while True:
        assert 0 <= index < len(parents) and index not in seen
        seen.add(index)
        if parents[index] == index:
            return index
        index = parents[index]
