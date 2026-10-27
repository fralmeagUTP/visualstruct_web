"""Corrupt transport independently; the canonical consumer must fail closed."""
from copy import deepcopy
import pytest
from _book_frame_oracle import assert_book_body
from _graph_trace_contract import decode_graph_http_trace

@pytest.fixture
def canonical_body(client):
    response=client.post('/graph/graph/operate',json={'operation':'insert_vertex','payload':{'vertex':7}})
    assert response.status_code==200
    body=response.get_json();body['execution_trace']=decode_graph_http_trace(body['execution_trace'])
    assert_book_body(body)
    return body

@pytest.mark.parametrize('corruption',['source','ledger','state_continuity','memory','executed_line','final_state'])
def test_canonical_consumer_rejects_detached_source_state_or_event(canonical_body,corruption):
    body=deepcopy(canonical_body);trace=body['execution_trace']
    index=next(i for i,s in enumerate(trace['steps']) if s['pedagogy']['instruction_event']['C_executed'])
    step=trace['steps'][index]
    if corruption=='source':trace['source_code']+='\n'
    elif corruption=='ledger':trace['C_instruction_events'][0]['function']='invented_function'
    elif corruption=='state_continuity':step['state_snapshot']={}
    elif corruption=='memory':step['pedagogy']['memory_state']={}
    elif corruption=='executed_line':step['line_index']=0
    else:body['visual_state']={}
    with pytest.raises(AssertionError):assert_book_body(body)
