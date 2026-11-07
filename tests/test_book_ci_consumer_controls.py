"""Negative controls for the replacement canonical golden and numeric consumers."""
from copy import deepcopy
import pytest
from app.services.graph_structure_service import GraphStructureService as S
from _book_construction_golden_oracle import assert_book_graph_golden
from _book_numeric_consumer_oracle import assert_chain_dijkstra


def execute(commands):
    history = []
    for operation, payload in commands:
        body = S.execute_operation('graph', operation, payload, history)
        assert body['success']; history = body['history']
    return body


@pytest.fixture(scope='module')
def chain():
    return execute([('insert_vertex', {'vertex': i}) for i in (1, 2, 3)] + [
        ('insert_edge', {'origin': 1, 'target': 2, 'weight': 2}),
        ('insert_edge', {'origin': 2, 'target': 3, 'weight': 3}),
        ('run_dijkstra', {'start': 1, 'end': 3})])


@pytest.mark.parametrize('mutation', ['wrong_distance', 'missing_relaxation', 'missing_cleanup'])
def test_numeric_oracle_rejects_concrete_contract_mutations(chain, mutation):
    body = deepcopy(chain)
    if mutation == 'wrong_distance':
        body['result']['distance_to_destination'] = 6
    elif mutation == 'missing_cleanup':
        body['execution_trace']['steps'][-1]['pedagogy']['memory_state']['frees'] -= 1
    else:
        event = next(s['pedagogy']['instruction_event'] for s in body['execution_trace']['steps']
                     if s['pedagogy']['instruction_event']['name'] == 't.dist[v]')
        event['name'] = 'not_the_distance_store'
    with pytest.raises(AssertionError):
        assert_chain_dijkstra(body)


def test_golden_oracle_rejects_wrong_arc_store():
    body = execute([('create_graph', {'directed': False}), ('insert_vertex', {'vertex': 1}),
        ('insert_vertex', {'vertex': 2}), ('insert_edge', {'origin': 1, 'target': 2, 'weight': 3})])
    assert_book_graph_golden(body)
    body = deepcopy(body)
    event = body['execution_trace']['steps'][85]['pedagogy']['instruction_event']
    event['value']['costo'] = 99
    with pytest.raises(AssertionError):
        assert_book_graph_golden(body)
