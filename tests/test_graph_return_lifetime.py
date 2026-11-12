"""Separate received TAD results from subsequent helper returns without futures."""
import pytest
from app.domain.graph.book_c_subset import BookSession, NULL, UNINIT
from app.services.graph_structure_service import GraphStructureService as S

EMPTY=[{'operation':'create_graph','payload':{'directed':True},'source_contract':'graph-book/v1'}]
EDGE=EMPTY+[{'operation':'insert_edge','payload':{'origin':11,'target':12,'weight':1},'source_contract':'graph-book/v1'}]


def receipt_frame(steps):
    index=next(i for i,step in enumerate(steps)
               if step['pedagogy']['instruction_event']['phase']=='caller_receipt')
    for step in steps[:index]:
        assert 'result' not in step['pedagogy']['memory_state']['external']
        assert step['state_after']['last_result'] is None
    return index,steps[index]['pedagogy']['memory_state']


@pytest.mark.parametrize('operation',['list_vertices','list_edges'])
def test_empty_borrowed_result_is_received_null_not_helper_void(operation):
    data=S.execute_operation('graph',operation,{},EMPTY)
    assert data['success']
    steps=data['execution_trace']['steps'];index,receipt=receipt_frame(steps)
    assert receipt['returned']==NULL
    assert receipt['external']['result']['value']==NULL
    for step in steps[index:]:
        memory=step['pedagogy']['memory_state']
        assert memory['external']['result']['value']==NULL
        assert memory['heap_nodes']==[]
        assert memory['allocations']==memory['frees']==0
    assert steps[-1]['pedagogy']['memory_state']['returned'] is None


@pytest.mark.parametrize('start',[11,99],ids=['owned-list','absent-start-null'])
def test_owned_result_receipt_survives_printf_then_cleanup_updates_holder(start):
    data=S.execute_operation('graph','run_bfs',{'start':start},EDGE)
    assert data['success']==(start==11)
    steps=data['execution_trace']['steps'];index,receipt=receipt_frame(steps)
    pointer=receipt['external']['result']['value']
    assert receipt['returned']==pointer
    assert (pointer!=NULL)==(start==11)
    graph_ids={n['id'] for n in steps[0]['pedagogy']['memory_state']['heap_nodes']}
    seen_cleanup=False;seen_output=False
    for step in steps[index+1:]:
        frame=step['pedagogy'];event=frame['instruction_event'];memory=frame['memory_state']
        if event.get('caller_C_executed'):
            seen_output=True
            assert memory['external']['result']['value']==pointer
        if event.get('function')=='grafo_liberar_vertices':
            seen_cleanup=True
        assert graph_ids.issubset({n['id'] for n in memory['heap_nodes']})
    assert seen_output and seen_cleanup
    final=steps[-1]['pedagogy']['memory_state']
    assert final['returned'] is None and final['external']['result']['value']==NULL
    assert {n['id'] for n in final['heap_nodes']}==graph_ids
    assert not graph_ids.intersection(n['id'] for n in final['retired_objects'])
    assert final['allocations']==final['frees']
    if pointer!=NULL:
        assert pointer in {n['id'] for n in final['retired_objects']}


def test_next_call_clears_previous_result_until_its_own_receipt():
    session=BookSession([11,12],[(11,12,1)],trace=True)
    first=session.call('grafo_vertices')
    previous=first['returned'];assert previous!=NULL
    second=session.call('grafo_arcos')
    transitions=second['transitions']
    assert transitions[0]['event']['phase']=='caller_prepare'
    assert transitions[0]['before']['external']['result']['value']==previous
    assert transitions[0]['after']['external']=={}
    assert transitions[0]['after']['returned']==UNINIT
    for transition in transitions[:-1]:
        assert 'result' not in transition['after']['external']
    last=transitions[-1]
    assert last['event']['phase']=='caller_receipt'
    assert last['after']['external']['result']['value']==second['returned']
    assert second['returned']!=previous
    assert second['memory']['allocations']==second['memory']['frees']==0
