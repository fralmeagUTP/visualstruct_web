"""Enqueue prepared trace lifetime independent of other sequential namespaces."""
from unittest.mock import patch
import json
import re
from app.services.priority_queue_enqueue_session_service import prepared_enqueue

def enqueue(client,value=9):
    response=client.post('/sequential/priority_queue/operate',json={'operation':'encolar','payload':{'value':value,'priority':2}})
    assert response.status_code==200
    return response.get_json()

def test_GET_keeps_exact_trace_without_execution_trace_builder(client):
    data=enqueue(client)
    with patch('app.services.execution_trace_service.ExecutionTraceService.build_trace',side_effect=AssertionError('GET must not build enqueue trace')):
        response=client.get('/sequential/priority_queue')
    assert response.status_code==200
    html=response.get_data(as_text=True)
    match=re.search(r"window\.SEQ_VIEW_MODEL\s*=\s*",html)
    assert match is not None
    model=json.JSONDecoder().raw_decode(html[match.end():])[0]
    assert model["prepared_enqueue_trace"]==data["execution_trace"]
    with client.session_transaction() as s:
        assert s['priority_queue_enqueue_prepared_v1']['trace']==data['execution_trace']

def test_failed_input_preserves_last_trace_and_next_success_replaces_it(client):
    first=enqueue(client)
    assert client.post('/sequential/priority_queue/operate',json={'operation':'encolar','payload':{'value':'invalid','priority':2}}).status_code==400
    with client.session_transaction() as s:
        assert s['priority_queue_enqueue_prepared_v1']['trace']==first['execution_trace']
    second=enqueue(client,-1)
    with client.session_transaction() as s:
        assert s['priority_queue_enqueue_prepared_v1']['trace']==second['execution_trace']
        assert s['priority_queue_enqueue_prepared_v1']['trace']!=first['execution_trace']

def test_other_success_or_reset_invalidates_only_enqueue_record(client):
    enqueue(client)
    with client.session_transaction() as s:
        s['stack_push_prepared_v1']={'sentinel':True}
    assert client.post('/sequential/priority_queue/operate',json={'operation':'desencolar','payload':{}}).status_code==200
    with client.session_transaction() as s:
        assert 'priority_queue_enqueue_prepared_v1' not in s
        assert s['stack_push_prepared_v1']=={'sentinel':True}
    enqueue(client)
    assert client.post('/sequential/priority_queue/reset').status_code==200
    with client.session_transaction() as s:
        assert 'priority_queue_enqueue_prepared_v1' not in s
        assert s['stack_push_prepared_v1']=={'sentinel':True}


def test_changed_source_or_history_rejects_stale_prepared_trace(app,client):
    from app.services.priority_queue_enqueue_session_service import prepared_enqueue, remember_enqueue
    data=enqueue(client)
    with app.test_request_context():
        remember_enqueue(data)
        assert prepared_enqueue(data['history'], source_code=data['execution_trace']['source_code']) == data['execution_trace']
        assert prepared_enqueue(data['history'], source_code='different C') is None
        assert prepared_enqueue([]) is None
