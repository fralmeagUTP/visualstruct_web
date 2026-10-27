"""Canonical DFS scopes/heap/source trace and independent native observations."""
import pytest
from _book_traversal_oracle import CASES,native_cases,recorded_call,compare_native,assert_recorded_instruction_contract

@pytest.fixture(scope='module')
def dfs_native(tmp_path_factory):
    return native_cases('dfs',tmp_path_factory.mktemp('canonical-dfs'))

def case_trace(case,marks=None,history=None):
    if history is not None:
        from app.services.graph_structure_service import GraphStructureService as S
        return S.execute_operation('graph','run_dfs',{'start':case['start']},history)['execution_trace']
    return recorded_call('dfs',case,marks)[1]

@pytest.mark.parametrize('case',range(10))
def test_dfs_native_instructions(dfs_native,case):
    record=CASES[case];marks=None
    for run in range(record.get('repeat',1)):
        result,trace=recorded_call('dfs',record,marks)
        compare_native(result,dfs_native['rows'][case,run])
        assert_recorded_instruction_contract(result,trace)
        assert trace['source_code']==dfs_native['source']
        if result['status']==0:
            recursive=[transition for transition in result['transitions'] if transition['event']['function']=='grafo_dfs_recursivo']
            assert recursive
            assert any(len(transition['after']['frames'])>1 for transition in recursive)
        marks=result['graph_after']['marks']
