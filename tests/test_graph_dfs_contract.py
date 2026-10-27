"""Finite native DFS status/order/marks and explicit canonical command replay."""
from _book_traversal_oracle import CASES,native_cases,compare_native
from app.domain.graph.book_c_subset import BookSession,NULL
from app.services.graph_structure_service import GraphStructureService as S
from app.adapters.graph_adapter import GraphAdapter

def test_dfs_downloaded_native_contract(tmp_path):
    report=native_cases('dfs',tmp_path/'native',initial_mark=7)
    assert len(report['rows'])==11
    for case,record in enumerate(CASES):
        marks={vertex:7 for vertex in record['vertices']}
        arcs=[(a,b,1) for a,b in record['edges']]
        for run in range(record.get('repeat',1)):
            session=BookSession(record['vertices'],arcs,marks)
            result=session.call('grafo_dfs',[record['start']])
            compare_native(result,report['rows'][case,run])
            marks=result['graph_after']['marks']
            assert session.free_result(result['returned'],result['return_type'])==NULL
            assert len(session.machine.heap)==len(record['vertices'])+len(arcs)

def test_dfs_history_rebuild_replays_only_explicit_canonical_commands(monkeypatch):
    history=[{'operation':'insert_vertex','payload':{'vertex':-1},'source_contract':'graph-book/v1'}]
    for _ in range(2):
        data=S.execute_operation('graph','run_dfs',{'start':-1},history,execution_mode='normal')
        assert data['success'];history=data['history']
    failed=S.execute_operation('graph','run_dfs',{'start':999},history,execution_mode='normal')
    assert failed['c_status']==2 and failed['history'][:-1]==history
    calls=[];original=GraphAdapter.execute
    def spy(self,operation,payload):calls.append(operation);return original(self,operation,payload)
    monkeypatch.setattr(GraphAdapter,'execute',spy)
    for _ in range(2):assert S.get_view_model('graph',history)['history']==history
    assert calls==['insert_vertex','run_dfs','run_dfs']*2
    assert [entry['operation'] for entry in history]==['insert_vertex','run_dfs','run_dfs']
