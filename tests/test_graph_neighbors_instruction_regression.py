"""Unclosed Graph neighbors raw/caller ownership paths, including rejected input."""
from copy import deepcopy
import pytest
from app.services.graph_structure_service import GraphStructureService
CASES=[('existing-no-arcs',[{'operation':'insert_vertex','payload':{'vertex':7}}],7,[]),('existing-no-outgoing',[{'operation':'insert_edge','payload':{'origin':o,'target':t,'weight':w}} for o,t,w in [(1,2,3),(1,3,5),(2,3,7)]],3,[]),('multiple-successors',[{'operation':'insert_edge','payload':{'origin':1,'target':t,'weight':w}} for t,w in [(2,3),(3,5)]],1,[2,3]),('self-loop-and-successor',[{'operation':'insert_edge','payload':{'origin':1,'target':t,'weight':5}} for t in [1,2]],1,[1,2])]
@pytest.mark.parametrize('case_id,mutations,vertex,expected',CASES,ids=[c[0] for c in CASES])
def test_neighbors_executes_real_guards_and_caller_owns_result(case_id,mutations,vertex,expected):
    history=[{'operation':'create_graph','payload':{'directed':True}}]+mutations
    r=GraphStructureService.execute_operation('graph','neighbors',{'vertex':vertex},history)
    assert r['success'] and r['result']==expected
    trace=r['execution_trace'];assert trace.get('neighbor_instruction_model')
    events=trace['C_instruction_events']
    assert sum(e['phase']=='allocate' for e in events)==len(expected)
    assert sum(e['phase']=='free' for e in events)==len(expected)
    if not expected:assert not any('malloc' in s['line_text'] or 'nuevo->' in s['line_text'] for s in trace['steps'])
    first=trace['steps'][0]['pedagogy']['initial_frame']['memory_state']
    borrowed={n['id']:n for n in first['heap_nodes']}
    for s in trace['steps']:
        state=s['pedagogy']['memory_state']
        assert state['graph']==first['graph']
        assert {n['id']:n for n in state['heap_nodes'] if n['borrowed']}==borrowed
    final=trace['steps'][-1]['pedagogy']['memory_state']
    assert final['heap_nodes']==first['heap_nodes'] and not final['frames']
    assert len(final['retired_objects'])==len(expected)
    assert trace['steps'][-1]['state_after']==r['visual_state']
    assert r['history']==history

def test_rejected_neighbor_query_has_no_C_events_or_frames():
    r=GraphStructureService.execute_operation('graph','neighbors',{'vertex':99},[])
    assert not r['success']
    t=r['execution_trace'];assert t.get('neighbor_instruction_model')
    assert not t['execution_started'] and not t['C_instruction_events']
    assert len(t['steps'])==1 and not t['steps'][0]['pedagogy']['call_stack']
