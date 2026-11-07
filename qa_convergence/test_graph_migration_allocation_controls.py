"""Negative controls for six-gate migration's current allocation acceptance.

Mutants are temporary harnesses or deep copies of real BookSession observations.
A negative is successful only when its named semantic assertion rejects it.
"""
from copy import deepcopy
from functools import lru_cache
import unittest
import pytest
import test_current_graph_edge_allocation as allocation


@pytest.fixture(scope='module')
def native():
    result = allocation.run_native_harness()
    rows, attempts = allocation.parse_native_output(result.stdout)
    allocation.assert_native_contract(unittest.TestCase(), rows, attempts, result.returncode)
    return rows, attempts


@lru_cache(maxsize=None)
def _real_observation(scenario, fault):
    return allocation.symbolic_observation(scenario, fault)


def test_temporary_native_telemetry_preserves_original_results(native):
    original = allocation.run_native_harness(instrument=False)
    instrumented = allocation.run_native_harness()
    assert original.returncode == instrumented.returncode == 0
    observed_lines = ''.join(line + '\n' for line in instrumented.stdout.splitlines()
                             if not line.startswith('attempt '))
    assert observed_lines == original.stdout
    rows, attempts = native
    assert set(rows) == set(attempts) == {(s, f) for s in range(6) for f in range(5)}
    # Ten failures really reach malloc; the other positive indices do not.
    assert sum(a['reached'] for a in attempts.values()) == 10
    assert sum(not a['reached'] for (s, f), a in attempts.items() if f) == 14


@pytest.mark.parametrize('change', ['missing_call', 'duplicate_call', 'missing_marker', 'duplicate_marker'])
def test_telemetry_rejects_ambiguous_source_transform(change):
    source = (allocation.ROOT / 'qa_convergence/graph_edge_allocation.c').read_text()
    marker = allocation._CALL_MARKER if change.endswith('call') else '            int invariant = 1;'
    assert source.count(marker) == 1
    bad = source.replace(marker, '' if change.startswith('missing') else marker + '\n' + marker)
    with pytest.raises(AssertionError, match='Unexpected harness'):
        allocation.run_native_harness(bad)


@pytest.mark.parametrize('mutation,expected', [('status', 'native status'), ('atomicity', 'native pointer atomicity')])
def test_compiled_native_mutants_reach_named_assertion(mutation, expected):
    source = (allocation.ROOT / 'qa_convergence/graph_edge_allocation.c').read_text()
    marker = '            int invariant = 1;'
    injected = ('if (status == GRAFO_MEMORIA) status = GRAFO_OK;' if mutation == 'status'
                else 'if (status == GRAFO_MEMORIA && scenario == 1) g.v = NULL;')
    source = source.replace(marker, '            ' + injected + '\n' + marker)
    result = allocation.run_native_harness(source)
    # A compiler exception or signal is not a semantic rejection.
    assert result.returncode >= 0
    rows, attempts = allocation.parse_native_output(result.stdout)
    assert set(rows) == set(attempts) == allocation.CASE_KEYS
    if mutation == 'status':
        assert any(attempts[k]['reached'] and rows[k]['status'] == 0 for k in rows)
    else:
        assert any(not row['atomic'] for row in attempts.values())
    with pytest.raises(AssertionError, match=expected):
        allocation.assert_native_contract(unittest.TestCase(), rows, attempts, result.returncode)


_SYMBOLIC_MUTATIONS = [
    ('vertex_count', (0, 0), 'symbolic vertex count'),
    ('edge_count', (0, 0), 'symbolic edge count'),
    ('endpoint', (0, 0), 'symbolic endpoint'),
    ('status', (0, 0), 'symbolic status'),
    ('cost', (0, 0), 'symbolic cost'),
    ('state_atomicity', (1, 1), 'symbolic state atomicity'),
    ('pointer_atomicity', (1, 1), 'symbolic pointer atomicity'),
    ('allocation_balance', (0, 2), 'symbolic temporary allocation balance'),
    ('allocation_attempts', (0, 2), 'symbolic allocation attempts'),
    ('cleanup_heap', (0, 0), 'symbolic cleanup heap'),
    ('cleanup_graph', (0, 0), 'symbolic cleanup graph'),
    ('cleanup_roots', (0, 0), 'symbolic cleanup roots'),
]


def _corrupt(observation, mutation):
    result = observation['result']
    state = result['graph_after']
    if mutation == 'vertex_count': state['vertices'].append(999)
    elif mutation == 'edge_count': state['arcs'].append(deepcopy(state['arcs'][0]))
    elif mutation == 'endpoint': state['arcs'][0][0] = 999
    elif mutation == 'status': result['status'] = 1
    elif mutation == 'cost': state['arcs'][0][2] = 987
    elif mutation == 'state_atomicity': state['marks'][1] = 123
    elif mutation == 'pointer_atomicity': result['memory']['graph']['v'] = 'corrupted_pointer'
    elif mutation == 'allocation_balance': result['memory']['allocations'] += 1
    elif mutation == 'allocation_attempts': result['memory']['allocation_attempts'] += 1
    elif mutation == 'cleanup_heap': observation['cleanup_heap'] = {'live': {}}
    elif mutation == 'cleanup_graph': observation['cleanup_graph']['vertices'] = [1]
    elif mutation == 'cleanup_roots': observation['cleanup_pointers']['v'] = 'V1'
    else: raise AssertionError('Unknown mutation')


@pytest.mark.parametrize('mutation,key,expected', _SYMBOLIC_MUTATIONS, ids=[row[0] for row in _SYMBOLIC_MUTATIONS])
def test_direct_symbolic_corruption_reaches_named_assertion(native, mutation, key, expected):
    rows, attempts = native
    real = _real_observation(*key)
    allocation.assert_symbolic_contract(unittest.TestCase(), real, rows[key], attempts[key], key[1])
    baseline_before = deepcopy(real)
    corrupted = deepcopy(real)
    _corrupt(corrupted, mutation)
    assert corrupted != real, 'Mutation was not applied to real execution'
    with pytest.raises(AssertionError, match=expected):
        allocation.assert_symbolic_contract(unittest.TestCase(), corrupted, rows[key], attempts[key], key[1])
    assert real == baseline_before == _real_observation(*key), 'Cached baseline was changed'
