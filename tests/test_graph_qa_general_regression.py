"""Invalid requests are atomic; trace budget is a mode limit, not random failure."""
from copy import deepcopy
import pytest


def saved(client):
    with client.session_transaction() as session:
        return deepcopy(dict(session))


@pytest.mark.parametrize('endpoint', ['/graph/graph/operate', '/graph/compare'])
@pytest.mark.parametrize('body', [None, [], [1], 'text', 1, True, False])
def test_non_object_body_rejected_before_session_access(client, endpoint, body):
    before = saved(client)
    response = client.post(endpoint, json=body)
    assert response.status_code == 400
    assert response.get_json() == {'success': False, 'message': 'El cuerpo enviado debe ser un objeto JSON válido.'}
    assert saved(client) == before


@pytest.mark.parametrize('payload', [None, [], [1], 'x', 1, True])
def test_invalid_operation_payload_preserves_existing_history(client, payload):
    assert client.post('/graph/graph/operate', json={'operation':'insert_vertex', 'payload':{'vertex':9}}).status_code == 200
    before = saved(client)
    response = client.post('/graph/graph/operate', json={'operation':'insert_vertex', 'payload':payload})
    assert response.status_code == 400 and response.get_json()['success'] is False
    assert saved(client) == before


@pytest.mark.parametrize('graph', [
    {'nodes':1}, {'nodes':'bad'}, {'nodes':[1]}, {'nodes':None},
    {'nodes':[{'id':1}], 'edges':1}, {'nodes':[{'id':1}], 'edges':[1]},
    {'nodes':[{'id':1}], 'edges':{}}, {'nodes':[{'id':1}], 'edges':None},
])
def test_malformed_comparison_graph_is_400_and_read_only(client, graph):
    before = saved(client)
    response = client.post('/graph/compare', json={'kind':'bfs-dfs', 'graph':graph})
    assert response.status_code == 400 and response.get_json()['success'] is False
    assert saved(client) == before


def test_seed_two_step_budget_rejection_then_normal_complete_and_reset(client):
    assert client.post('/graph/graph/operate', json={'operation':'insert_vertex', 'payload':{'vertex':99}}).status_code == 200
    before = saved(client)
    body = {'operation':'generate_random_graph','payload':{'vertices_count':7,'seed':2}}
    response = client.post('/graph/graph/operate', json=body)
    assert response.status_code == 400
    data = response.get_json()
    assert data['trace_event_limit'] == 4000 and data['trace_available'] is False
    assert data['preserve_session'] is True and data['execution_trace'] is None
    assert saved(client) == before
    response = client.post('/graph/graph/operate', json={**body,'execution_mode':'normal'})
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['visual_state']['nodes']) == 7
    assert data['visual_state']['metadata']['edges_count'] >= 6
    assert data['trace_available'] is False and data['execution_trace'] is None
    assert data['history'][-1]['payload']['seed'] == 2
    assert client.get('/graph/graph/history').get_json()['history'] == data['history']
    reset = client.post('/graph/graph/reset')
    assert reset.status_code == 200 and reset.get_json()['history'] == []
    assert reset.get_json()['visual_state']['nodes'] == []
