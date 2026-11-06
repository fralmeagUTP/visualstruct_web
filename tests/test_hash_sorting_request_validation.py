"""Malformed input must never change existing hash/sorting sessions."""
from copy import deepcopy
import pytest

ENDPOINTS = ['/hash/hash_table/operate', '/hash/compare-capacities'] + [
    '/api/ordenamiento/' + path for path in ('create-array', 'random-array', 'algorithm', 'run', 'step', 'compare')]

@pytest.mark.parametrize('endpoint', ENDPOINTS)
@pytest.mark.parametrize('body', ['[1]', '[]', '1', 'true', 'null', '"text"', '{bad', ''])
def test_non_object_json_is_rejected_without_session_changes(client, endpoint, body):
    client.post('/hash/hash_table/operate', json={'operation':'create_table','payload':{'capacity':3}})
    client.post('/api/ordenamiento/create-array', json={'values':[3,1,2]})
    with client.session_transaction() as session:
        before = deepcopy(dict(session))
    response = client.post(endpoint, data=body, content_type='application/json')
    assert response.status_code == 400
    assert response.get_json()['success'] is False
    with client.session_transaction() as session:
        assert dict(session) == before

@pytest.mark.parametrize('endpoint', ['run', 'step', 'algorithm'])
@pytest.mark.parametrize('algorithm', [['x'], {'x':1}, [], {}, 12, True, None])
def test_algorithm_id_type_is_rejected_without_session_changes(client, endpoint, algorithm):
    client.post('/api/ordenamiento/create-array', json={'values':[3,1,2]})
    with client.session_transaction() as session:
        before = deepcopy(dict(session))
    response = client.post('/api/ordenamiento/' + endpoint, json={'algorithm_id':algorithm})
    assert response.status_code == 400
    assert response.get_json()['success'] is False
    with client.session_transaction() as session:
        assert dict(session) == before

@pytest.mark.parametrize('module', ['hash', 'sorting'])
def test_capacity_rejection_preserves_entire_session_and_reload(client, app, module):
    app.config['SESSION_MAX_HISTORY'] = 3
    if module == 'hash':
        endpoint = '/hash/hash_table/operate'
        for operation, payload in [('create_table',{'capacity':3}), ('insert',{'key':1,'value':10}), ('insert',{'key':2,'value':20})]:
            assert client.post(endpoint,json={'operation':operation,'payload':payload}).status_code == 200
        next_payload = {'operation':'insert','payload':{'key':3,'value':30}}
        source = '/help/source/hash_table/main'
        before_source = client.get(source).data
    else:
        assert client.post('/api/ordenamiento/create-array',json={'values':[3,1,2]}).status_code == 200
        assert client.post('/api/ordenamiento/algorithm',json={'algorithm_id':'counting_sort'}).status_code == 200
        assert client.post('/api/ordenamiento/run',json={'algorithm_id':'counting_sort'}).status_code == 200
        endpoint = '/api/ordenamiento/run'
        next_payload = {'algorithm_id':'counting_sort'}
        source = '/api/ordenamiento/state'
        before_source = client.get(source).get_json()
    with client.session_transaction() as session:
        before = deepcopy(dict(session))
    response = client.post(endpoint,json=next_payload)
    assert response.status_code == 409
    data = response.get_json()
    assert data['success'] is False and data['preserve_session'] is True
    assert 'execution_trace' not in data
    with client.session_transaction() as session:
        assert dict(session) == before
    if module == 'hash':
        assert client.get(source).data == before_source
        assert client.get('/hash/hash_table').status_code == 200
    else:
        after_source = client.get(source).get_json()
        for field in ('history','visual_state','main_c','execution_trace'):
            assert after_source[field] == before_source[field]
        assert client.get('/api/ordenamiento/traces/' + before['counting_latest']['trace_id'] + '/page').status_code == 200
