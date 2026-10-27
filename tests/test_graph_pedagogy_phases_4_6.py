"""Acceptance coverage for graph pedagogy phases 4 through 6."""
from _book_frame_oracle import assert_book_body
from pathlib import Path
from _graph_trace_contract import decode_graph_http_trace

from app.domain.graph.pedagogy import build_graph_frame, validate_graph_frame
from app.adapters.graph_adapter import GraphAdapter


def _operate(client, operation, payload, status=200):
    response = client.post(
        "/graph/graph/operate",
        json={"operation": operation, "payload": payload},
    )
    assert response.status_code == status
    body = response.get_json()
    body["execution_trace"] = decode_graph_http_trace(body["execution_trace"])
    return body


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
    for operation in ('run_bfs','run_dfs'):
        body=_operate(client,operation,{'start':1})
        assert body['success'] and body['c_status']==0
        assert sorted(body['result'])==[1,2,3] and len(body['result'])==3
        assert {n['id']:n['marked'] for n in body['visual_state']['nodes']}=={'1':1,'2':1,'3':1,'4':0}
        assert_book_body(body)
        steps=body['execution_trace']['steps']
        events=[step['pedagogy']['instruction_event'] for step in steps]
        assert any(e['function']=='preparar' and e['phase']=='enter' for e in events)
        assert any(e['function']=='publicar_marcas' and e['phase']=='enter' for e in events)
        assert any(e['function']=='grafo_liberar_vertices' and e['phase']=='enter' for e in events)
        assert any(e['phase']=='allocate' for e in events) and any(e['phase']=='free' for e in events)
        assert not steps[-1]['pedagogy']['memory_state']['frames']
        if operation=='run_bfs':
            assert sum(e['function']=='grafo_bfs' and e['phase']=='write' and e.get('name','').startswith('t.prev[') for e in events)==3
            assert any('t.prev[' in step['line_text'] and '++' in step['line_text'] for step in steps)
            assert not any((e['function'] or '').startswith('cola_') for e in events)
        else:
            assert any(e['function']=='grafo_dfs_recursivo' and e['phase']=='enter' for e in events)
            assert any(sum(f['function']=='grafo_dfs_recursivo' for f in step['pedagogy']['memory_state']['frames'])>=2 for step in steps)


def test_dijkstra_frames_show_index_selection_relaxation_and_path(client):
    _prepare_weighted_graph(client)
    data=_operate(client,'run_dijkstra',{'start':1,'end':3})
    assert data['result']['path']==[1,2,3] and data['result']['path_arcs']==[[1,2,2],[2,3,1]]
    assert data['result']['distance_to_destination']==3 and type(data['result']['distance_to_destination']) is int
    assert_book_body(data)
    steps=data['execution_trace']['steps'];events=[step['pedagogy']['instruction_event'] for step in steps]
    for function in ('preparar','sumar_seguro','reconstruir','liberar_trabajo','grafo_liberar_arcos'):
        assert any(e['function']==function and e['phase']=='enter' for e in events)
    assert any('t.alcanzable[j]' in step['line_text'] and step['phase']=='condition' for step in steps)
    assert not steps[-1]['pedagogy']['memory_state']['frames']


def test_bellman_ford_distinguishes_unreachable_and_reachable_negative_cycle(client):
    _prepare_weighted_graph(client)
    unreachable=_operate(client,'run_bellman_ford',{'start':1,'end':4},status=400)
    assert unreachable['c_status']==2 and unreachable['result']['reachable'] is False
    assert unreachable['result']['path']==[] and unreachable['result']['distance_to_destination'] is None
    assert_book_body(unreachable)
    assert unreachable['history'][-1]['operation']=='run_bellman_ford'
    _operate(client,'create_graph',{'directed':True})
    for origin,target,weight in ((1,2,1),(2,3,-3),(3,2,1)):
        prepared=_operate(client,'insert_edge',{'origin':origin,'target':target,'weight':weight})
    negative=_operate(client,'run_bellman_ford',{'start':1,'end':3},status=400)
    assert negative['c_status']==4 and negative['result']['has_negative_cycle'] is True
    assert negative['history'][:-1]==prepared['history']
    assert negative['result']['path_arcs']==[] and negative['result']['distance_to_destination'] is None
    assert_book_body(negative)
    assert any('e = GRAFO_CICLO_NEGATIVO' in step['line_text'] and step['phase']=='write' for step in negative['execution_trace']['steps'])


def test_ui_exposes_representation_traversal_relaxation_and_immutable_replay(client):
    html = client.get("/graph/graph/recorridos").get_data(as_text=True)
    for element_id in ("graph-representation-view", "graph-traversal-view", "graph-relaxation-view"):
        assert f'id="{element_id}"' in html
    assert "BFS:" in html and "no ponderados" in html
    source = (Path(__file__).parents[1] / "static/js/graph.js").read_text(encoding="utf-8")
    assert "pageState.traceSelectionKey === selectionKey" in source
    assert "no cambia al reproducir" in source
