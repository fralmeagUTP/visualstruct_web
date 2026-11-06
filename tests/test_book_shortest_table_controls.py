"""Reject plausible but noncausal shortest-path tables at actual C boundaries."""
from copy import deepcopy
import pytest
from _book_shortest_table_oracle import assert_shortest_chain_tables
from test_phase7_trace_contract_remediation import _graph_shortest_trace


@pytest.fixture(scope='module', params=['run_dijkstra', 'run_bellman_ford'])
def chain(request):
    return request.param, _graph_shortest_trace(request.param)


@pytest.mark.parametrize('field,forged', [('distances', {'1': 0, '2': 4, '3': 5}),
    ('previous', {'1': None, '2': 3, '3': 1}), ('visited', ['1', '2', '3']),
    ('candidates', ['3'])])
def test_table_projection_rejects_synchronized_premature_values(chain, field, forged):
    operation, original = chain; body = deepcopy(original)
    step = next(s for s in body['execution_trace']['steps']
        if s['pedagogy']['instruction_event'].get('name') == 't.alcanzable[s]')
    step['debug']['graph_progress'][field] = forged
    if field == 'candidates':
        step['pedagogy']['auxiliary'][field] = forged
    else:
        step['pedagogy']['table'][field] = forged
    with pytest.raises(AssertionError):
        assert_shortest_chain_tables(body, operation)


def test_freed_vertex_table_cannot_remain_published(chain):
    operation, original = chain; body = deepcopy(original)
    step = next(s for s in body['execution_trace']['steps']
        if s['phase'] == 'free' and s['pedagogy']['instruction_event']['function'] == 'liberar_trabajo')
    value = {'1': 0, '2': 4, '3': 5}
    step['debug']['graph_progress']['distances'] = value
    step['pedagogy']['table']['distances'] = value
    with pytest.raises(AssertionError):
        assert_shortest_chain_tables(body, operation)


def test_frame_table_cannot_disagree_with_memory_even_if_debug_is_valid(chain):
    operation, original = chain; body = deepcopy(original)
    step = next(s for s in body['execution_trace']['steps']
        if s['pedagogy']['instruction_event'].get('name') == 't.alcanzable[s]')
    step['pedagogy']['table'] = {**step['pedagogy']['table'], 'distances': {'1': 99}}
    with pytest.raises(AssertionError):
        assert_shortest_chain_tables(body, operation)
