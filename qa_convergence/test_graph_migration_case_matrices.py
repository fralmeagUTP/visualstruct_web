"""Exact old case inputs survive the explicit contract/type observation changes."""
from copy import deepcopy
import pytest
from qa import test_graph_numeric_receipt as old_numeric
from qa import test_graph_vertex_publication as old_vertex
from qa import test_graph_query_publication as old_query
from qa_convergence import test_current_graph_numeric_receipt as numeric
from qa_convergence import test_current_graph_vertex_publication as vertex
from qa_convergence import test_current_graph_query_publication as query
from qa_convergence import test_current_graph_edge_allocation as allocation


def _unversion(history):
    return [{key: deepcopy(value) for key, value in entry.items() if key != 'source_contract'} for entry in history]


def assert_case_matrices(numeric_cases, vertex_cases, query_cases, scenarios, keys):
    assert numeric_cases == old_numeric.CASES and len(numeric_cases) == 7, 'numeric case inputs changed'
    assert [(op, value, _unversion(h)) for op, value, h in vertex_cases] == old_vertex.CASES, 'vertex case inputs changed'
    assert len(vertex_cases) == 5
    assert [(op, payload) for op, payload, _ in query_cases] == [(op, payload) for op, payload, _ in old_query.CASES], 'query case inputs changed'
    assert [kind for _, _, kind in query_cases] == ['int'] * 6 + ['ListaVertice', 'ListaArco'], 'accepted query result types changed'
    assert len(query_cases) == 8
    assert scenarios == {0: ((), ()), 1: ((1,), ()), 2: ((2,), ()),
                         3: ((1, 2), ()), 4: ((), ()), 5: ((1, 2), ((1, 2, 3),))}, 'allocation scenario inputs changed'
    assert keys == {(scenario, fault) for scenario in range(6) for fault in range(5)}, 'allocation case/fault matrix changed'


def test_all_30_7_5_8_case_inputs_are_retained_exactly():
    assert_case_matrices(numeric.CASES, vertex.CASES, query.CASES, allocation.SCENARIOS, allocation.CASE_KEYS)
    for op, payload, edges in numeric.CASES:
        directed = op not in {'run_prim', 'run_kruskal'}
        assert _unversion(numeric.history(edges, directed)) == old_numeric.history(edges, directed)
    assert _unversion(vertex.H) == old_vertex.H
    assert _unversion(query.H) == old_query.H


@pytest.mark.parametrize('target', ['numeric', 'vertex', 'query', 'type', 'scenario', 'fault'])
def test_case_reduction_or_reinterpretation_is_rejected(target):
    nc, vc, qc, scenarios, keys = deepcopy((numeric.CASES, vertex.CASES, query.CASES, allocation.SCENARIOS, allocation.CASE_KEYS))
    if target == 'numeric': nc.pop()
    elif target == 'vertex': vc[0] = ('insert_vertex', 4, vc[0][2])
    elif target == 'query': qc.pop()
    elif target == 'type': qc[5] = (qc[5][0], qc[5][1], None)
    elif target == 'scenario': scenarios[5] = ((1, 2), ((1, 2, 9),))
    else: keys.remove((0, 4))
    with pytest.raises(AssertionError):
        assert_case_matrices(nc, vc, qc, scenarios, keys)
