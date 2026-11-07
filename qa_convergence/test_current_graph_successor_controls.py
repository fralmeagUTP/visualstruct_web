"""Adversarial checks for current successors, not lost historical equivalence."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import pytest
import _canonical_publication_contract as contract
import test_current_graph_numeric_receipt as numeric
import test_current_graph_query_publication as query
import test_current_graph_vertex_publication as vertex


@lru_cache(maxsize=None)
def _body(operation, payload_json, history_json):
    return contract.execute(operation, json.loads(payload_json), json.loads(history_json))


def _cached(operation, payload, history):
    return deepcopy(_body(operation, json.dumps(payload, sort_keys=True), json.dumps(history, sort_keys=True)))


_ORACLES = {
    'numeric': (numeric, numeric.Receipt, 'test_null_and_owned_receipt'),
    'query': (query, query.Publication, 'test_typed_results'),
    'vertex': (vertex, vertex.Publication, 'test_operation_specific_boundary'),
}


def _run_oracle(name):
    _, cls, method = _ORACLES[name]
    instance = cls(methodName=method)
    # Call the method directly: assertion failures propagate to pytest.
    getattr(instance, method)()


@pytest.mark.parametrize('name', sorted(_ORACLES))
def test_current_successor_oracles_accept_real_execution(name, monkeypatch):
    monkeypatch.setattr(_ORACLES[name][0], 'execute', _cached)
    _run_oracle(name)


_MUTATIONS = [
    ('numeric', 'receipt_marked_as_C'),
    ('numeric', 'returned_pointer_disagrees'),
    ('numeric', 'owned_pointer_missing'),
    ('numeric', 'owned_memory_already_freed'),
    ('numeric', 'final_cleanup_leak'),
    ('numeric', 'null_narration_claims_owned'),
    ('query', 'receipt_marked_as_C'),
    ('query', 'wrong_return_type'),
    ('query', 'wrong_external_result'),
    ('query', 'borrowed_marked_owned'),
    ('query', 'borrowed_identity_changed'),
    ('query', 'scalar_result_reversed'),
    ('query', 'cost_output_changed'),
    ('query', 'prior_history_removed'),
    ('vertex', 'publication_marked_as_C'),
    ('vertex', 'imaginary_C_line'),
    ('vertex', 'missing_C_execution'),
    ('vertex', 'returned_graph_disagrees'),
    ('vertex', 'history_operation_changed'),
    ('vertex', 'publication_mutates_state'),
]


def _mutate(body, operation, mutation):
    trace = body['execution_trace']
    final = trace['steps'][-1]
    frames = [s['pedagogy'] for s in trace['steps'] if s['pedagogy']['instruction_event']['phase'] == 'caller_receipt']
    if mutation == 'publication_marked_as_C':
        final['pedagogy']['instruction_event']['C_executed'] = True
    elif mutation == 'imaginary_C_line':
        final['line_text'] = 'grafo_eliminar_vertice(g, 99);'
    elif mutation == 'missing_C_execution':
        trace['C_instruction_events'] = []
    elif mutation == 'history_operation_changed':
        body['history'][-1]['operation'] = 'invented_operation'
    elif mutation == 'publication_mutates_state':
        final['pedagogy']['instruction_state_after'] = {'corrupted': True}
    elif mutation == 'prior_history_removed':
        body['history'] = body['history'][-1:]
    elif mutation == 'final_cleanup_leak':
        final['pedagogy']['memory_state']['frees'] = -1
    else:
        if operation.startswith('run_'):
            function = 'grafo_' + operation[4:]
        elif operation in query.FUNCTIONS:
            function = query.FUNCTIONS[operation]
        else:
            function = 'grafo_insertar_vertice' if operation == 'insert_vertex' else 'grafo_eliminar_vertice'
        frame = next(f for f in frames if f['instruction_event'].get('called_function') == function)
        event = frame['instruction_event']
        if mutation == 'receipt_marked_as_C':
            event['C_executed'] = True
        elif mutation == 'returned_pointer_disagrees':
            body['c_return'] = 'corrupted_pointer'
        elif mutation == 'returned_graph_disagrees':
            event['returned'] = {'corrupted': True}
        elif mutation == 'owned_pointer_missing':
            if event['returned'] == 'NULL': return False
            frame['memory_state']['heap_nodes'] = []
        elif mutation == 'owned_memory_already_freed':
            if event['returned'] == 'NULL': return False
            frame['memory_state']['frees'] = frame['memory_state']['allocations']
        elif mutation == 'null_narration_claims_owned':
            if event['returned'] != 'NULL': return False
            frame['narration'] = {'basic': 'lista propia'}
        elif mutation == 'wrong_return_type':
            event['return_type'] = 'double'
        elif mutation == 'wrong_external_result':
            frame['memory_state']['external']['result'] = {'type': 'wrong', 'value': 99}
        elif mutation == 'borrowed_marked_owned':
            if not event['return_type'].startswith('Lista'): return False
            body['ownership'] = 'owned'
        elif mutation == 'borrowed_identity_changed':
            if not event['return_type'].startswith('Lista'): return False
            frame['memory_state']['graph']['v' if event['return_type'] == 'ListaVertice' else 'a'] = 'corrupted_pointer'
        elif mutation == 'scalar_result_reversed':
            if operation not in ('exists_vertex', 'exists_edge'): return False
            body['result'] = not body['result']
        elif mutation == 'cost_output_changed':
            if operation != 'edge_weight': return False
            body['output'] = 98765
        else:
            raise AssertionError('Unregistered mutation: ' + mutation)
    return True


@pytest.mark.parametrize('name,mutation', _MUTATIONS, ids=[name + '-' + mutation for name, mutation in _MUTATIONS])
def test_current_successor_rejects_each_guarantee_regression(name, mutation, monkeypatch):
    changed = []
    def corrupted(operation, payload, history):
        body = _cached(operation, payload, history)
        if _mutate(body, operation, mutation):
            changed.append(operation)
        return body
    monkeypatch.setattr(_ORACLES[name][0], 'execute', corrupted)
    with pytest.raises(AssertionError):
        _run_oracle(name)
    assert changed, 'Mutation did not reach a real applicable execution'


def test_historical_originals_still_match_existing_manifest():
    # Explicit current-contract transition: originals remain literal snapshots.
    from qa_convergence._graph_contract_migration import assert_graph_contract_migration
    assert_graph_contract_migration(Path(__file__).resolve().parents[1])


@pytest.mark.parametrize('mutation', ['dangling_endpoint', 'wrong_cost', 'missing_cleanup'])
def test_native_current_harness_rejects_invalid_results(mutation, tmp_path):
    """Mutate only a temporary test harness, never the canonical C/H sources."""
    import subprocess
    root = Path(__file__).resolve().parents[1]
    source = (root / 'qa_convergence/graph_edge_allocation.c').read_text()
    if mutation == 'missing_cleanup':
        old, new = 'grafo_destruir(&g);', '/* deliberately omitted cleanup */'
    else:
        old = 'int invariant = 1;'
        field = 'origen' if mutation == 'dangling_endpoint' else 'costo'
        new = 'if (g.a) g.a->' + field + ' = 999;\n            int invariant = 1;'
    assert source.count(old) == 1
    harness = tmp_path / 'mutant.c'
    harness.write_text(source.replace(old, new))
    exe = tmp_path / 'mutant'
    subprocess.run(['gcc', '-std=c17', '-Wall', '-Wextra', '-Werror', '-pedantic',
        '-I' + str(root / 'docs/tads_C'), str(harness), str(root / 'docs/tads_C/tad_grafo.c'),
        '-Wl,--wrap=malloc', '-Wl,--wrap=free', '-o', str(exe)], check=True, capture_output=True, timeout=30)
    result = subprocess.run([str(exe)], capture_output=True, text=True, timeout=15)
    assert result.returncode > 0, 'Invalid native result was accepted'
    assert 'result=FAIL' in result.stdout
    assert result.stdout.count('scenario=') == 30
