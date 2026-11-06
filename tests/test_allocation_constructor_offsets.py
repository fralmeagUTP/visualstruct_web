"""Runtime CALL caches must not hide or broaden a node-allocation failure."""
from copy import deepcopy
import dis
import json
import re

import pytest

from app.domain.sequential import tad_lista
from app.domain.sequential.allocation_failure_instruction import (
    _constructor_calls, is_node_allocation_failure,
)
from test_sequential_acceptance_criteria_focal import FAULTS, test_required_allocation_failure_C_API as run_failure
from test_residual58_focal_cases import residual58_app, residual58_client


@pytest.mark.parametrize('fault', FAULTS, ids=lambda row: row[0])
def test_constructor_failure_preserves_heap_and_privacy(
    residual58_client, residual58_app, monkeypatch, tmp_path, fault,
):
    run_failure(residual58_client, residual58_app, monkeypatch, tmp_path, fault)
    proof = json.loads((tmp_path / 'allocation-failure-proof.json').read_text())
    body = proof['body']
    trace = body['execution_trace']
    assert proof['status'] == 400
    assert proof['denied_allocations'] == 1 and proof['session_unchanged']
    assert trace['allocation_failure'] and trace['execution_started']
    assert trace['mutates'] is False
    assert body['error'] == trace['error'] == {
        'code': 'allocation_failed', 'stage': 'operation', 'object_created': False,
    }
    assert trace['final_state'] == body['visual_state']
    family, operation = fault[1:3]
    expected_return = ({'type': 'void', 'value': None} if family in {'stack', 'queue', 'linked_list'}
                       else {'type': 'Nodo *', 'value': 'NULL'} if family == 'sublist' and operation == 'insertar_padre'
                       else {'type': 'bool', 'value': False})
    assert trace['c_return'] == expected_return
    from app.services.execution_trace_service import ExecutionTraceService
    heap = deepcopy(trace['steps'][0]['pedagogy']['heap_objects'])
    for step in trace['steps']:
        line = step['line_text'].strip()
        assert not re.search(r'->\w+\s*=(?!=)', line)
        assert step['event_type'] != 'allocator_success_return'
        expected_console = ExecutionTraceService._printf_literal(step['line_text'], preserve_trailing_newlines=True) if line.startswith('printf(') else None
        assert step['console'] == ([expected_console] if expected_console is not None else [])
        pedagogy = step['pedagogy']
        assert pedagogy['heap_objects'] == heap
        assert pedagogy['heap_transition']['before'] == pedagogy['heap_transition']['after']
        assert not pedagogy['heap_transition']['freed']
        if fault[1] in {'priority_queue', 'circular_list', 'sublist'}:
            assert not step['console']
    assert 'Private deterministic allocation denial' not in json.dumps(body)
    assert 'Traceback' not in json.dumps(body)


def test_call_offsets_exclude_next_real_instruction():
    code = tad_lista.lista_insertar_final.__code__
    instructions = list(dis.get_instructions(code))
    accepted = _constructor_calls(code, 'NodoLista')
    assert accepted
    assert all(offset % 2 == 0 and offset + 1 not in accepted for offset in accepted)
    for index, instruction in enumerate(instructions):
        if instruction.offset in accepted:
            assert instruction.opname.startswith('CALL')
            assert instructions[index + 1].offset not in accepted


def test_later_call_memory_error_is_not_constructor_failure(monkeypatch):
    def later_failure():
        raise MemoryError('Synthetic metadata denial')

    def operation(lista, valor):
        NodoLista(nro=valor)
        later_failure()

    # Give the synthetic operation the same constructor global as real domain code.
    monkeypatch.setitem(operation.__globals__, 'NodoLista', tad_lista.NodoLista)
    monkeypatch.setattr(tad_lista, 'lista_insertar_final', operation)
    with pytest.raises(MemoryError) as caught:
        operation([None], 7)
    assert not is_node_allocation_failure(caught.value, 'linked_list', 'insertar_final')
    assert not is_node_allocation_failure(caught.value, 'linked_list', 'unknown')


def test_constructor_failure_in_wrong_function_is_not_relabelled(monkeypatch):
    def denied(**kwargs):
        raise MemoryError('Synthetic constructor denial')

    monkeypatch.setattr(tad_lista, 'NodoLista', denied)
    with pytest.raises(MemoryError) as caught:
        tad_lista.lista_insertar_inicio([None], 7)
    assert is_node_allocation_failure(caught.value, 'linked_list', 'insertar_inicio')
    assert not is_node_allocation_failure(caught.value, 'linked_list', 'insertar_final')


def test_replay_constructor_failure_is_not_operation_failure(monkeypatch):
    from app.services.structure_service import StructureService

    def replay_failure(*args, **kwargs):
        raise MemoryError('Synthetic replay denial')

    monkeypatch.setattr(StructureService, '_rebuild_adapter', replay_failure)
    with pytest.raises(MemoryError, match='Synthetic replay denial'):
        StructureService.execute_operation(
            'linked_list', 'insertar_final', {'value': 99},
            [{'operation': 'insertar_final', 'payload': {'value': 7}}],
        )
