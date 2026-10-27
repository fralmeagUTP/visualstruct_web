"""Acceptance tests for MST, active learning, comparison and graph QA closure."""
from app.domain.graph.snapshot_pool import expand_graph_trace
from pathlib import Path
from _book_frame_oracle import assert_book_body

from app.services.graph_structure_service import GraphStructureService


def _operate(client, operation, payload, status=200):
    response = client.post("/graph/graph/operate", json={"operation": operation, "payload": payload})
    assert response.status_code == status, response.get_data(as_text=True)
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
    data['execution_trace']=trace
    assert_book_body(data)
    first = finds[0]["pedagogy"]["memory_state"]
    variables = _C_vars(first, "grafo_kruskal")
    assert _live_int_buffer(first, variables["c"]["padre"], 3) == [0,1,2]
    decisions = [step for step in steps if _C_event(step).get("function") == "grafo_kruskal" and _C_event(step)["phase"] == "condition" and "grafo_encontrar_conjunto(&c" in step["line_text"]]
    assert len(decisions) == 6
    assert sum(bool(_C_event(step)["value"]) for step in decisions) == 4
    assert sum(not bool(_C_event(step)["value"]) for step in decisions) == 2
    for step in decisions:
        assert _C_event(step)["C_executed"]
        memory = step["pedagogy"]["memory_state"]
        variables = _C_vars(memory, "grafo_kruskal")
        parents = _live_int_buffer(memory, variables["c"]["padre"], 3)
        roots_equal = _C_root(parents, variables['u']) == _C_root(parents, variables['v'])
        assert roots_equal == bool(_C_event(step)['value'])
    # Equal live roots execute continue, so only the two distinct-root edges
    # allocate result arcs and invoke the real union helper.
    writes = [step for step in steps if _C_event(step).get("function") == "grafo_unir_conjuntos" and _C_event(step)["phase"] == "write" and _C_event(step)["name"] == "c->padre[b]"]
    assert len(writes) == 2
    assert any(_C_event(step).get("function") == "grafo_kruskal" and _C_event(step)["phase"] == "return" for step in steps)


def test_prim_distinguishes_mst_from_disconnected_failure(client):
    _operate(client,'create_graph',{'directed':False})
    for vertex in (1,2,3,4):_operate(client,'insert_vertex',{'vertex':vertex})
    _operate(client,'insert_edge',{'origin':1,'target':2,'weight':1})
    _operate(client,'insert_edge',{'origin':3,'target':4,'weight':2})
    data=_operate(client,'run_prim',{'start':1},status=400)
    assert data['c_status']==5 and data['result']=={'start':1,'kind':'error','connected':False,'mst_edges':[],'total_weight':None}
    trace=expand_graph_trace(data['execution_trace']);data['execution_trace']=trace
    assert_book_body(data);steps=trace['steps']
    guards=[step for step in steps if _C_event(step)['function']=='grafo_prim' and step['phase']=='condition' and 'if (u < 0)' in step['line_text'] and _C_event(step)['value']]
    assert len(guards)==1
    memory=guards[0]['pedagogy']['memory_state'];variables=_C_vars(memory,'grafo_prim')
    assert variables['u']==-1
    used=_live_int_buffer(memory,variables['t']['usado'],4)
    reachable=_live_int_buffer(memory,variables['t']['alcanzable'],4)
    assert sum(bool(v) for v in used)==2 and not any(not used[j] and reachable[j] for j in range(4))
    assert any('e = GRAFO_DESCONECTADO' in step['line_text'] and step['phase']=='write' for step in steps)
    assert any(_C_event(step)['function']=='liberar_trabajo' and step['phase']=='enter' for step in steps)
    assert not steps[-1]['pedagogy']['memory_state']['frames']


def test_mst_algorithms_reject_directed_graph(client):
    _operate(client, "create_graph", {"directed": True})
    _operate(client, "insert_edge", {"origin": 1, "target": 2, "weight": 1})
    for operation, payload in (("run_prim", {"start": 1}), ("run_kruskal", {})):
        response = client.post("/graph/graph/operate", json={"operation": operation, "payload": payload})
        assert response.status_code == 400
        body=response.get_json();assert body['c_status']==6 and 'GRAFO_ARGUMENTO' in body['message']
        assert body['history'][-1]['operation']==operation
        body['execution_trace']=expand_graph_trace(body['execution_trace']);assert_book_body(body)


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
    for text in ('Manual','GrafoEstado','Dijkstra','Prim','Kruskal'):
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
