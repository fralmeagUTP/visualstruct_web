"""Prepared dequeue lifetime for successful calls and completed native guard failures."""
from __future__ import annotations
from unittest.mock import patch
from app.services.queue_dequeue_session_service import prepared_dequeue

def seed(client,value=-1):
    assert client.post('/sequential/queue/operate',json={'operation':'encolar','payload':{'value':value}}).status_code==200

def dequeue(client):return client.post('/sequential/queue/operate',json={'operation':'desencolar','payload':{}}).get_json()

def test_GET_reuses_exact_dequeue_trace_without_builder_or_new_history(client):
    seed(client);d=dequeue(client)
    with patch('app.services.execution_trace_service.ExecutionTraceService.build_trace',side_effect=AssertionError('GET may not rebuild prepared trace')):
        response=client.get('/sequential/queue')
    assert response.status_code==200
    with client.session_transaction() as s:assert s['queue_dequeue_prepared_v1']['trace']==d['execution_trace']
    import json
    text=response.data.decode('utf-8');model=json.JSONDecoder().raw_decode(text.split('window.SEQ_VIEW_MODEL =',1)[1].lstrip())[0];assert model['history']==d['history'] and model['prepared_dequeue_trace']==d['execution_trace']

def test_changed_source_or_history_rejects_stale_dequeue_record(client):
    seed(client);d=dequeue(client);source=d['execution_trace']['source_code']
    with client.application.test_request_context():
        from flask import session
        from app.services.queue_dequeue_session_service import remember_dequeue
        remember_dequeue(d);assert prepared_dequeue(d['history'],source_code=source)==d['execution_trace'];assert prepared_dequeue(d['history'],source_code=source+'\n') is None;assert prepared_dequeue([],source_code=source) is None

def test_invalid_payload_preserves_record_later_success_invalidates_only_dequeue(client):
    seed(client);d=dequeue(client)
    assert client.post('/sequential/queue/operate',json={'operation':'desencolar','payload':[]}).status_code==400
    with client.session_transaction() as s:
        assert s['queue_dequeue_prepared_v1']['trace']==d['execution_trace'];s['stack_push_prepared_v1']={'sentinel':True}
    seed(client,7)
    with client.session_transaction() as s:assert 'queue_dequeue_prepared_v1' not in s and s['stack_push_prepared_v1']=={'sentinel':True}

def test_completed_empty_C_guard_is_prepared_without_history_append_and_reset_isolated(client):
    seed(client);first=dequeue(client);empty=dequeue(client);assert not empty['success'] and empty['history']==first['history'];assert empty['execution_trace']['steps'][-1]['debug']['result']==-1
    with client.session_transaction() as s:
        assert s['queue_dequeue_prepared_v1']['trace']==empty['execution_trace'];s['priority_queue_enqueue_prepared_v1']={'sentinel':True}
    assert client.post('/sequential/queue/reset').status_code==200
    with client.session_transaction() as s:assert 'queue_dequeue_prepared_v1' not in s and s['priority_queue_enqueue_prepared_v1']=={'sentinel':True}
