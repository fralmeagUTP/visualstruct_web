"""Acceptance tests for graph pedagogy phases 1-3."""
import json
from pathlib import Path

from app.domain.graph.pedagogy import GRAPH_EDGE_POLICY, GRAPH_FRAME_SCHEMA_VERSION, GRAPH_GUIDED_EXAMPLES, GRAPH_LEARNING_CATALOG, build_graph_frame, graph_frame_schema, validate_graph_frame
from app.adapters.graph_adapter import GraphAdapter


def _step(line,stage):
    state={"nodes":[{"id":"1"},{"id":"2"}],"edges":[{"source":"1","target":"2","weight":4}],"directed":True,"validation":True}
    return {"line_index":0,"line_text":line,"state_snapshot":state,"state_after":state,"debug":{"stage":stage,"note":"evento canónico","graph_progress":{"nodes":["1"],"edges":[["1","2"]],"distances":{"1":0,"2":4},"previous":{"1":None,"2":"1"},"visited":["1"],"selected":"1","candidates":["2"]}}}


def test_schema_catalog_and_examples_cover_learning_scope():
    assert graph_frame_schema()["version"]==GRAPH_FRAME_SCHEMA_VERSION
    assert set(graph_frame_schema()["levels"])=={"basic","intermediate","advanced"}
    assert {"run_bfs","run_dfs","run_dijkstra","run_bellman_ford","run_prim","run_kruskal"} <= set(GRAPH_LEARNING_CATALOG)
    ids={example["id"] for example in GRAPH_GUIDED_EXAMPLES}
    assert {"empty","single","isolated","disconnected","cycle","dag","complete","cheap-detour","unreachable","negative","negative-cycle","negative-cycle-unreachable","equal-mst"} <= ids


def test_golden_graph_concepts_are_stable():
    fixtures=json.loads((Path(__file__).parent/"golden/graph_pedagogical_frames_v1.json").read_text(encoding="utf-8"))["fixtures"]
    for fixture in fixtures.values():
        frame=build_graph_frame(operation_name="run_dijkstra",payload={"start":1,"end":2},step=_step(fixture["line"],fixture["stage"]),source_lines=[fixture["line"]],success=True)
        validate_graph_frame(frame,source_code=fixture["line"])
        assert frame["concept"]==fixture["concept"]


def test_real_graph_trace_exposes_canonical_frames(client):
    history=[]
    for operation,payload in (("create_graph",{"directed":False}),("insert_vertex",{"vertex":1}),("insert_vertex",{"vertex":2}),("insert_edge",{"origin":1,"target":2,"weight":4})):
        response=client.post("/graph/graph/operate",json={"operation":operation,"payload":payload})
        assert response.status_code==200
    trace=client.post("/graph/graph/operate",json={"operation":"run_bfs","payload":{"start":1}}).get_json()["execution_trace"]
    assert trace["pedagogy_schema_version"]==GRAPH_FRAME_SCHEMA_VERSION
    for step in trace["steps"]:
        frame=step["pedagogy"];validate_graph_frame(frame,source_code=trace["source_code"])
        assert frame["state_before"]==step["state_snapshot"]
        assert frame["state_after"]==step["state_after"]


def test_page_exposes_learning_regions_and_no_active_frontend_inference(client):
    html=client.get("/graph/graph/recorridos").get_data(as_text=True)
    for label in ("Preparar","Predecir","Ejecutar y visualizar","Comprender","Relacionar con C","Comparar","Reflexionar"):
        assert label in html
    for element_id in ("graph-learning-level","graph-guided-example","graph-load-example","graph-visual-region","graph-code-region","graph-function-list","graph-hide-comments","graph-restart-execution","graph-reset-button","graph-state-legend","graph-pedagogy-summary"):
        assert f'id="{element_id}"' in html or (element_id=="graph-state-legend" and 'class="graph-state-legend"' in html)
    source=(Path(__file__).parents[1]/"static/js/graph.js").read_text(encoding="utf-8")
    assert source.count("buildSimulationFromState(")==1


def test_edge_policy_matches_adapter_behavior():
    adapter=GraphAdapter();adapter.execute("create_graph",{"directed":True})
    adapter.execute("insert_edge",{"origin":1,"target":1,"weight":3})
    adapter.execute("insert_edge",{"origin":1,"target":2,"weight":8})
    adapter.execute("insert_edge",{"origin":1,"target":2,"weight":5})
    state=adapter.to_visual_state()
    assert GRAPH_EDGE_POLICY=={"self_loops":"allowed","parallel_edges":"update_existing_weight","neighbor_order":"vertex/edge insertion order"}
    edges={(edge["source"],edge["target"]):edge["weight"] for edge in state["edges"]}
    assert edges[("1","1")]==3 and edges[("1","2")]==5
