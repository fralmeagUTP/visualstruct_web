"""Canonical allocation faults preserve borrowed graph state and marks.

The former atomic-successor helper is absent from the delivered C. Exercise
the same historical cases and every actual allocation through BookSession.
"""
from copy import deepcopy
import pytest
from app.domain.graph.book_c_subset import BookSession, NULL
from _audit_graph_four_instruction_observer import cases_from_baseline


def case_input(algorithm):
    case = cases_from_baseline(algorithm)[1 if algorithm == 'prim' else 2]
    arcs = []
    for origin, target, weight in case['e']:
        arcs.append((origin, target, weight))
        if not case.get('directed', True) and origin != target:
            arcs.append((target, origin, weight))
    arguments = [case['start']] + ([case['end']] if algorithm == 'dijkstra' else [])
    return case['v'], arcs, arguments


def successful_call(algorithm):
    vertices, arcs, arguments = case_input(algorithm)
    result = BookSession(vertices, arcs).call('grafo_' + algorithm, arguments)
    assert result['status'] == 0
    return result


FAULTS = [(algorithm, attempt)
          for algorithm in ('prim', 'dijkstra')
          for attempt in range(1, successful_call(algorithm)['memory']['allocation_attempts'] + 1)]


@pytest.mark.parametrize('algorithm,attempt', FAULTS)
def test_every_reached_allocation_failure_aborts_and_frees_all_owned(algorithm, attempt):
    vertices, arcs, arguments = case_input(algorithm)
    marks = {vertex: index % 2 for index, vertex in enumerate(vertices)}
    session = BookSession(vertices, arcs, marks, fail_allocation=attempt, trace=True)
    borrowed = deepcopy(session.machine.snapshot()['heap_nodes'])
    result = session.call('grafo_' + algorithm, arguments)
    assert result['status'] == 1 and result['status_name'] == 'GRAFO_MEMORIA'
    assert result['returned'] == NULL and result['result_items'] == []
    memory = result['memory']
    # preparar allocates its five independent workspace arrays before checking
    # the batch; the chosen failed slot is still unique and all peers are freed.
    assert memory['allocation_attempts'] == max(attempt, 5)
    assert memory['allocations'] == memory['frees']
    assert memory['heap_nodes'] == borrowed and memory['frames'] == []
    assert result['graph_after']['marks'] == marks
    assert result['ownership'] == 'owned'
    assert any(event['phase'] == 'allocate' for event in result['events'])


@pytest.mark.parametrize('algorithm', ['prim', 'dijkstra'])
def test_complete_successor_result_and_integer_contract_preserved(algorithm):
    vertices, arcs, arguments = case_input(algorithm)
    session = BookSession(vertices, arcs)
    borrowed = deepcopy(session.machine.snapshot()['heap_nodes'])
    result = session.call('grafo_' + algorithm, arguments)
    assert result['status'] == 0 and result['ownership'] == 'owned'
    assert result['result_items'] == ([[3, 2, 2], [1, 3, 1]] if algorithm == 'prim'
                                      else [[1, 3, 1], [3, 2, 1]])
    assert result['memory']['allocations'] - result['memory']['frees'] == 2
    assert session.free_result(result['returned'], result['return_type']) == NULL
    assert session.machine.snapshot()['heap_nodes'] == borrowed
    assert session.machine.snapshot()['frames'] == []


@pytest.mark.parametrize('function', ['grafo_vertices', 'grafo_arcos'])
def test_borrowed_graph_lists_cannot_be_freed_as_algorithm_results(function):
    vertices, arcs, _ = case_input('dijkstra')
    session = BookSession(vertices, arcs)
    before = deepcopy(session.machine.snapshot()['heap_nodes'])
    borrowed = session.call(function)
    assert borrowed['ownership'] == 'borrowed'
    with pytest.raises(ValueError, match='borrowed'):
        session.free_result(borrowed['returned'], borrowed['return_type'])
    assert session.machine.snapshot()['heap_nodes'] == before


@pytest.mark.parametrize('function,arcs,arguments,status', [
    ('grafo_prim', [(1, 2, 1), (2, 1, 1)], [1], 5),
    ('grafo_prim', [(1, 2, 1), (2, 3, 1)], [1], 6),
    ('grafo_prim', [(1, 2, 1), (2, 1, 1)], [99], 2),
    ('grafo_dijkstra', [(1, 2, 1)], [1, 3], 2),
    ('grafo_dijkstra', [(1, 2, -1)], [1, 2], 3),
    ('grafo_dijkstra', [(1, 2, 1)], [1, 1], 0),
    ('grafo_dijkstra', [(1, 2, 1)], [1, 99], 2),
])
def test_empty_result_statuses_never_publish_partial_owned_memory(function, arcs, arguments, status):
    marks = {1: 1, 2: 0, 3: 1}
    session = BookSession([1, 2, 3], arcs, marks, trace=True)
    borrowed = deepcopy(session.machine.snapshot()['heap_nodes'])
    result = session.call(function, arguments)
    assert result['status'] == status and result['returned'] == NULL
    assert result['result_items'] == []
    assert result['memory']['allocations'] == result['memory']['frees']
    assert result['memory']['heap_nodes'] == borrowed
    assert result['graph_after']['marks'] == marks
