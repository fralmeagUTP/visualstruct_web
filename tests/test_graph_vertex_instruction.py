"""Causal state and validation regression gates limited to vertex construction."""
from copy import deepcopy
import pytest
from app.services.graph_structure_service import GraphStructureService
from app.services.c_code_service import CCodeService
from app.domain.graph.vertex_instruction import build_graph_vertex_trace


def test_insert_allocation_fields_are_not_initialized_or_published_early():
    data=GraphStructureService.execute_operation("graph","insert_vertex",{"vertex":7},[])
    steps=data["execution_trace"]["steps"]
    allocation=next(s for s in steps if s["phase"]=="allocate")
    assert allocation["state_after"]["nodes"]==[]
    assert allocation["pedagogy"]["memory_state"]["heap_nodes"][0]["fields"]==dict(sig="sin inicializar",dato="sin inicializar",marcado="sin inicializar")
    published=next(s for s in steps if s["line_text"].strip()=="g.v = nuevo;")
    assert published["pedagogy"]["memory_state"]["heap_nodes"][0]["fields"]==dict(sig="NULL",dato=7,marcado=0)
    assert len(published["state_after"]["nodes"])==1
    assert all(s["state_after"]["last_result"] is None for s in steps[:-1])
    assert steps[0]["pedagogy"]["initial_frame"]["memory_state"]["frames"]==[]
    receipt=steps[-1]["pedagogy"]
    assert receipt["instruction_state_before"]["frames"] and receipt["instruction_state_after"]["frames"]==[]
    assert all(v["value"]=="fuera de ambito" for v in receipt["variables"])

@pytest.mark.parametrize("operation,payload",[("insert_vertex",{"vertex":"bad"}),("remove_vertex",{"vertex":7})])
def test_api_rejection_is_not_an_invocation_of_raw_c(operation,payload):
    data=GraphStructureService.execute_operation("graph",operation,payload,[])
    assert data["success"] is False
    trace=data["execution_trace"]
    assert trace["C_instruction_events"]==[] and trace["execution_started"] is False
    assert all(s["pedagogy"]["instruction_event"]["C_executed"] is False for s in trace["steps"])


def test_unknown_c_body_is_rejected_instead_of_synthetic_fallback():
    source=CCodeService.get_structure_data("graph")["operations"]["insert_vertex"]
    with pytest.raises(ValueError,match="C body changed"):
        build_graph_vertex_trace(operation_name="insert_vertex",payload={"vertex":7},source_code=source.replace("nuevo->dato = x;","nuevo->dato = x + 1;"),
            code_title="C",before_state={},after_state={},success=True,message="fixture")
