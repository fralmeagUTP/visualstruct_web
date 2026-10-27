"""Missing Graph instruction cells only; no closed Graph6/vertex/neighbors cases."""
import pytest
from app.services.graph_structure_service import GraphStructureService

EDGE=[{"operation":"create_graph","payload":{"directed":True}},{"operation":"insert_edge","payload":{"origin":1,"target":2,"weight":3}}]
EDGE=[dict(record,source_contract="graph-book/v1") for record in EDGE]

@pytest.mark.parametrize("operation,payload,history,forbidden",[
 ("exists_vertex",{"vertex":1},[],["k=k->sig;","return 1;"]),
 ("exists_edge",{"origin":1,"target":2},[],["k=k->sig;","return 1;"]),
 ("edge_weight",{"origin":1,"target":2},EDGE,["k=k->sig;","return -1;"]),
 ("insert_edge",{"origin":1,"target":2,"weight":4},EDGE,["malloc(sizeof(struct NodoA))","nuevo->origen = x;","g.a = nuevo;"]),
 ("remove_edge",{"origin":1,"target":2},EDGE,["free(p);","p=k->sig;"]),
],ids=["empty-vertex-scan","empty-arc-scan","cost-head-return","existing-arc-update","remove-arc-head"])
def test_only_executed_graph_branch_highlights(operation,payload,history,forbidden):
    data=GraphStructureService.execute_operation("graph",operation,payload,history)
    assert data["success"]
    lines=[s["line_text"].strip() for s in data["execution_trace"]["steps"]]
    assert not any(token in line for line in lines for token in forbidden),lines

@pytest.mark.parametrize("operation",["list_vertices","list_edges"])
def test_borrowed_list_return_has_explicit_pointer_memory(operation):
    data=GraphStructureService.execute_operation("graph",operation,{},EDGE)
    assert data["success"]
    frames=[s.get("pedagogy",{}).get("memory_state",{}) for s in data["execution_trace"]["steps"]]
    # These C methods return borrowed heads, not independently allocated result nodes.
    result=data["visual_state"]["last_result"]
    assert result["ownership"]=="borrowed" and result["c_return"]!="NULL"
    assert any(result["c_return"] in {node["id"] for node in frame.get("heap_nodes",[])} for frame in frames)
    assert all(frame.get("allocations",0)==0 and frame.get("frees",0)==0 for frame in frames)

@pytest.mark.parametrize("operation,payload",[("create_graph",{"directed":True}),("clear_graph",{})])
def test_replacing_nonempty_graph_explains_owning_caller_cleanup(operation,payload):
    data=GraphStructureService.execute_operation("graph",operation,payload,EDGE)
    assert data["success"] and not data["visual_state"]["nodes"]
    # Actual accepted generated main frees owned nodes before replacing graph by value.
    lines=[s["line_text"] for s in data["execution_trace"]["steps"]]
    assert any("free(" in line for line in lines),lines


def test_random_materialization_does_not_claim_single_vertex_C_is_whole_operation():
    data=GraphStructureService.execute_operation("graph","generate_random_graph",{"seed":42,"vertices_count":5},[])
    assert data["success"] and len(data["visual_state"]["nodes"])==5
    # No standalone C random generator exists: actual main materializes vertices/arcs.
    lines=[s["line_text"] for s in data["execution_trace"]["steps"]]
    assert any("grafo_insertar_arco" in line for line in lines),lines
