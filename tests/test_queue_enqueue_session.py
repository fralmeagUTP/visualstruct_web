"""Enqueue prepared trace lifetime independent of other sequential namespaces."""
from unittest.mock import patch
from app.services.queue_enqueue_session_service import prepared_enqueue

def enqueue(client,value=9):
    response=client.post('/sequential/queue/operate',json={'operation':'encolar','payload':{'value':value}})
    assert response.status_code==200
    return response.get_json()

def test_GET_keeps_exact_trace_without_execution_trace_builder(client):
    data=enqueue(client)
    with patch('app.services.execution_trace_service.ExecutionTraceService.build_trace',side_effect=AssertionError('GET must not build enqueue trace')):
        response=client.get('/sequential/queue')
    assert response.status_code==200
    with client.session_transaction() as s:
        assert s['queue_enqueue_prepared_v1']['trace']==data['execution_trace']

def test_failed_input_preserves_last_trace_and_next_success_replaces_it(client):
    first=enqueue(client)
    assert client.post('/sequential/queue/operate',json={'operation':'encolar','payload':{'value':'invalid'}}).status_code==400
    with client.session_transaction() as s:
        assert s['queue_enqueue_prepared_v1']['trace']==first['execution_trace']
    second=enqueue(client,-1)
    with client.session_transaction() as s:
        assert s['queue_enqueue_prepared_v1']['trace']==second['execution_trace']
        assert s['queue_enqueue_prepared_v1']['trace']!=first['execution_trace']

def test_other_success_or_reset_invalidates_only_enqueue_record(client):
    enqueue(client)
    with client.session_transaction() as s:
        s['stack_push_prepared_v1']={'sentinel':True}
    assert client.post('/sequential/queue/operate',json={'operation':'desencolar','payload':{}}).status_code==200
    with client.session_transaction() as s:
        assert 'queue_enqueue_prepared_v1' not in s
        assert s['stack_push_prepared_v1']=={'sentinel':True}
    enqueue(client)
    assert client.post('/sequential/queue/reset').status_code==200
    with client.session_transaction() as s:
        assert 'queue_enqueue_prepared_v1' not in s
        assert s['stack_push_prepared_v1']=={'sentinel':True}
