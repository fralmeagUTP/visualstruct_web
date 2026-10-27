"""Causal state and validation regression gates limited to vertex construction."""
from copy import deepcopy
import pytest
from app.services.graph_structure_service import GraphStructureService
from app.services.c_code_service import CCodeService
from app.domain.graph.book_c_subset import Program
from app.domain.graph.book_source import canonical_source


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
    assert receipt["instruction_state_before"]["frames"]==receipt["instruction_state_after"]["frames"]==[]
    assert receipt['call_stack']==[]
    assert any(s['pedagogy']['completed_call_stack'] for s in steps[:-1])

@pytest.mark.parametrize("operation,payload",[("insert_vertex",{"vertex":"bad"}),("remove_vertex",{"vertex":7})])
def test_host_rejection_is_distinct_from_C_noop_removal(operation,payload):
    data=GraphStructureService.execute_operation("graph",operation,payload,[])
    trace=data["execution_trace"]
    if operation=='remove_vertex':
        assert data['success'] is True and data['visual_state']['nodes']==[]
        assert trace['execution_started'] and trace['C_instruction_events']
        assert all(not s['pedagogy']['memory_state']['heap_nodes'] for s in trace['steps'])
        return
    assert data["success"] is False
    assert trace["C_instruction_events"]==[] and trace["execution_started"] is False
    assert all(s["pedagogy"]["instruction_event"]["C_executed"] is False for s in trace["steps"])


def test_unknown_c_body_is_rejected_instead_of_synthetic_fallback():
    source=canonical_source()
    mutated=source.replace('{x, g.v, 0}', '{x + 1, g.v, 0}')
    assert mutated!=source
    with pytest.raises(ValueError,match="byte-exact"):
        Program(mutated)
