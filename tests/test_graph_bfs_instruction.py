"""Canonical BFS source/scope trace plus independent native endpoint/memory oracle."""
import pytest
from _book_traversal_oracle import CASES,native_cases,recorded_call,compare_native,assert_recorded_instruction_contract
from app.domain.graph.book_c_subset import BookSession,NULL
from app.services.graph_structure_service import GraphStructureService as S

@pytest.fixture(scope='module')
def bfs_native(tmp_path_factory):
    return native_cases('bfs',tmp_path_factory.mktemp('canonical-bfs'))

def case_trace(case,marks=None):
    return recorded_call('bfs',case,marks)[1]

@pytest.mark.parametrize('case',range(10))
def test_bfs_native_outer_instruction_projection(bfs_native,case):
    record=CASES[case];marks=None
    for run in range(record.get('repeat',1)):
        result,trace=recorded_call('bfs',record,marks)
        compare_native(result,bfs_native['rows'][case,run])
        assert_recorded_instruction_contract(result,trace)
        assert trace['source_code']==bfs_native['source']
        marks=result['graph_after']['marks']

def test_bfs_domain_marks_and_owned_result():
    vertices=[-1,2,3,99];arcs=[(-1,2,1),(-1,3,1),(2,3,1),(3,-1,1)]
    session=BookSession(vertices,arcs)
    for _ in range(2):
        result=session.call('grafo_bfs',[-1])
        assert result['status']==0 and result['result_items']==[-1,2,3]
        assert result['graph_after']['marks']=={-1:1,2:1,3:1,99:0}
        assert session.free_result(result['returned'],result['return_type'])==NULL
        assert len(session.machine.heap)==len(vertices)+len(arcs)
    absent=session.call('grafo_bfs',[101])
    assert absent['status']==2 and absent['returned']==NULL
    assert absent['graph_after']['marks']=={-1:1,2:1,3:1,99:0}

def test_bfs_history_rebuild_explicitly_replays_canonical_commands(monkeypatch):
    from app.adapters.graph_adapter import GraphAdapter
    history=[{'operation':'insert_vertex','payload':{'vertex':-1},'source_contract':'graph-book/v1'}]
    for _ in range(2):
        data=S.execute_operation('graph','run_bfs',{'start':-1},history,execution_mode='normal');assert data['success'];history=data['history']
    failed=S.execute_operation('graph','run_bfs',{'start':99},history,execution_mode='normal')
    assert failed['c_status']==2 and failed['history'][:-1]==history
    calls=[];old=GraphAdapter.execute
    def spy(self,operation,payload):calls.append(operation);return old(self,operation,payload)
    monkeypatch.setattr(GraphAdapter,'execute',spy)
    for _ in range(2):
        model=S.get_view_model('graph',history)
        assert model['history']==history and [n['id'] for n in model['visual_state']['nodes']]==['-1']
    assert calls==['insert_vertex','run_bfs','run_bfs']*2
