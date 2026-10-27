"""Focused deployment checks: real C events and failed-call graph atomicity."""
from copy import deepcopy

from app.domain.graph.snapshot_pool import expand_graph_trace


def _operate(client, operation, payload):
    return client.post('/graph/graph/operate', json={'operation': operation, 'payload': payload})


def _graph(client, edges, directed=False):
    assert _operate(client, 'create_graph', {'directed': str(directed).lower()}).get_json()['success']
    for vertex in (1, 2, 3):
        assert _operate(client, 'insert_vertex', {'vertex': str(vertex)}).get_json()['success']
    for origin, target, weight in edges:
        response = _operate(client, 'insert_edge', {'origin': str(origin), 'target': str(target), 'weight': str(weight)})
        assert response.get_json()['success']
    return response.get_json()


def test_bfs_functionless_boundaries_never_claim_to_execute_c(client):
    _graph(client, [(1, 2, 1), (2, 3, 1)])
    response = _operate(client, 'run_bfs', {'start': '1'})
    body = response.get_json()
    assert response.status_code == 200 and body['success'] and body['result'] == [1, 2, 3]
    trace = expand_graph_trace(body['execution_trace'])
    boundaries = []
    executed = []
    for step in trace['steps']:
        event = step['pedagogy']['instruction_event']
        if not event.get('function'):
            boundaries.append(event['phase'])
            assert event['C_executed'] is False
            assert step['line_index'] is None and step['line_text'] == ''
            assert event['source_role'] in {'caller', 'application'}
        else:
            executed.append(event)
            assert event['C_executed'] is True
            assert trace['source_code'].splitlines()[step['line_index']] == step['line_text']
    assert boundaries == ['caller_prepare', 'caller_receipt', 'api_publication']
    assert any(event['function'] == 'grafo_bfs' for event in executed)
    assert trace['final_state'] == body['visual_state']


def test_negative_cycle_records_failed_c_call_without_mutating_graph(client):
    before = _graph(client, [(1, 2, 1), (2, 3, -3), (3, 1, 1)], directed=True)
    response = _operate(client, 'run_bellman_ford', {'start': '1', 'end': '3'})
    after = response.get_json()
    assert response.status_code == 400 and after['success'] is False
    assert after['c_status'] == 4 and after['c_status_name'] == 'GRAFO_CICLO_NEGATIVO'
    assert after['c_return'] == 'NULL' and after['execution_started'] is True
    old_graph, new_graph = deepcopy(before['visual_state']), deepcopy(after['visual_state'])
    for state in (old_graph, new_graph):
        del state['last_operation']
        del state['last_result']
    assert old_graph == new_graph  # Includes vertices, edges, marks and identities.
    assert after['history'][:-1] == before['history']
    assert after['history'][-1] == {'operation': 'run_bellman_ford', 'payload': {'start': '1', 'end': '3'}, 'source_contract': 'graph-book/v1'}
    assert after['visual_state']['last_operation']['status'] == 'error'
    trace = expand_graph_trace(after['execution_trace'])
    memory = trace['steps'][-1]['pedagogy']['instruction_state_after']
    assert memory['allocations'] == memory['frees']
    assert memory['frames'] == []
    assert {node['id'] for node in memory['heap_nodes']} == {
        node['id'] for node in trace['steps'][0]['pedagogy']['instruction_state_before']['heap_nodes']
    }
