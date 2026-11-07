"""Adversarial controls for the explicit six-test current-contract migration."""
from copy import deepcopy
from functools import lru_cache
import html
import json
import re
import unittest
import pytest
from qa_convergence import _canonical_publication_contract as contract
from qa_convergence import test_current_graph_numeric_receipt as numeric
from qa_convergence import test_current_graph_vertex_publication as vertex
from qa_convergence import test_current_graph_query_publication as query
from qa_convergence import _graph_current_help_contract as help_contract


@lru_cache(maxsize=None)
def _body(operation, payload_json, history_json):
    return contract.execute(operation, json.loads(payload_json), json.loads(history_json))


def _cached(operation, payload, history):
    return deepcopy(_body(operation, json.dumps(payload, sort_keys=True), json.dumps(history, sort_keys=True)))


ORACLES = {'numeric': (numeric, numeric.Receipt, 'test_null_and_owned_receipt'),
           'vertex': (vertex, vertex.Publication, 'test_operation_specific_boundary'),
           'query': (query, query.Publication, 'test_typed_results')}


def _run(name):
    _, cls, method = ORACLES[name]
    getattr(cls(methodName=method), method)()


MUTATIONS = [
    ('numeric', 'null_contradictory_ownership', 'null_no_owned_claim'),
    ('numeric', 'missing_receipt_levels', 'narration_levels'),
    ('numeric', 'missing_caller_attribution', 'caller_attribution'),
    ('numeric', 'receipt_claims_c', 'caller_non_c_narration'),
    ('numeric', 'receipt_contradicts_c', 'caller_no_c_claim'),
    ('query', 'final_contradicts_c', 'api_no_c_claim'),
    ('vertex', 'insert_narrates_delete', 'insert_not_delete'),
    ('vertex', 'delete_narrates_insert', 'delete_not_insert'),
    ('vertex', 'missing_host_attribution', 'api_attribution'),
    ('vertex', 'wrong_operation_name', 'api_operation'),
    ('vertex', 'missing_final_levels', 'narration_levels'),
    ('vertex', 'missing_caller_attribution', 'caller_attribution'),
    ('vertex', 'absent_delete_removes_edge', 'vertex_edge_count'),
    ('query', 'final_claims_c', 'api_non_c'),
    ('query', 'final_has_c_line', 'api_no_c_line'),
    ('query', 'missing_host_attribution', 'api_attribution'),
    ('query', 'scalar_claims_list', 'scalar_not_list'),
    ('query', 'absent_cost_initialized', 'cost_separate_output'),
    ('query', 'absent_cost_false_success', 'cost_success_flag'),
    ('query', 'fake_input_rejection', 'api_phase'),
    ('query', 'missing_executed_c', 'query_actual_c'),
    ('query', 'query_mutates_graph', 'query_graph_unchanged:nodes'),
    ('query', 'query_publication_mutates_state', 'api_no_mutation'),
    ('query', 'missing_receipt_levels', 'narration_levels'),
    ('query', 'missing_final_levels', 'narration_levels'),
    ('query', 'external_cost_invented', 'cost_external_output'),
]


def _mutate(body, operation, payload, mutation):
    trace = body['execution_trace']; final = trace['steps'][-1]
    function = ('grafo_' + operation[4:] if operation.startswith('run_') else
                ('grafo_insertar_vertice' if operation == 'insert_vertex' else 'grafo_eliminar_vertice')
                if operation in ('insert_vertex', 'remove_vertex') else query.FUNCTIONS[operation])
    frame = contract.receipt(trace, function)
    if mutation == 'null_contradictory_ownership':
        if frame['instruction_event']['returned'] != 'NULL': return False
        frame['narration'] = {k: v + ' También recibe una lista propia.' for k, v in frame['narration'].items()}
    elif mutation == 'missing_receipt_levels': frame['narration'] = {}
    elif mutation == 'missing_final_levels': final['pedagogy']['narration'] = {}
    elif mutation == 'missing_caller_attribution':
        frame['narration'] = {k: v.replace('Retorno al caller:', 'Retorno automático:') for k, v in frame['narration'].items()}
    elif mutation == 'receipt_claims_c':
        frame['narration'] = {k: v.replace('No se ejecuta otra instrucción C.', 'C ejecuta esta publicación.') for k, v in frame['narration'].items()}
    elif mutation == 'receipt_contradicts_c':
        frame['narration'] = {k: v + ' C ejecuta esta publicación.' for k, v in frame['narration'].items()}
    elif mutation == 'final_contradicts_c':
        final['pedagogy']['narration'] = {k: v + ' C ejecuta esta publicación.' for k, v in final['pedagogy']['narration'].items()}
    elif mutation == 'insert_narrates_delete':
        if operation != 'insert_vertex': return False
        final['pedagogy']['narration'] = {k: v + ' El caller retira los vértices.' for k, v in final['pedagogy']['narration'].items()}
    elif mutation == 'delete_narrates_insert':
        if operation != 'remove_vertex': return False
        final['pedagogy']['narration'] = {k: v + ' El caller debe insertar un vértice.' for k, v in final['pedagogy']['narration'].items()}
    elif mutation == 'missing_host_attribution':
        final['pedagogy']['narration'] = {k: v.replace('Frontera de la aplicación:', 'Una instrucción canónica:') for k, v in final['pedagogy']['narration'].items()}
    elif mutation == 'wrong_operation_name':
        final['pedagogy']['narration'] = {k: v.replace(function, 'otra_operacion') for k, v in final['pedagogy']['narration'].items()}
    elif mutation == 'absent_delete_removes_edge':
        if operation != 'remove_vertex' or payload['vertex'] != 9: return False
        final['state_after'] = {**deepcopy(final['state_after']), 'edges': []}
    elif mutation == 'final_claims_c': final['pedagogy']['instruction_event']['C_executed'] = True
    elif mutation == 'final_has_c_line': final['line_text'] = 'grafo_existe_vertice(g, 1);'
    elif mutation == 'scalar_claims_list':
        if operation.startswith('list_'): return False
        final['pedagogy']['narration'] = {k: v + ' Devuelve una lista.' for k, v in final['pedagogy']['narration'].items()}
    elif mutation in ('absent_cost_initialized', 'absent_cost_false_success', 'external_cost_invented'):
        if operation != 'edge_weight' or payload['target'] != 9: return False
        if mutation == 'absent_cost_initialized': body['output'] = 0
        elif mutation == 'absent_cost_false_success': body['success'] = True
        else: frame['memory_state']['external']['salida'] = {'type': 'int', 'value': 0}
    elif mutation == 'fake_input_rejection':
        if operation != 'edge_weight' or payload['target'] != 9: return False
        final['phase'] = 'input_validation'
    elif mutation == 'missing_executed_c': trace['C_instruction_events'] = []
    elif mutation == 'query_mutates_graph':
        final['state_after'] = deepcopy(final['state_after'])
        final['state_after']['nodes'] = []
    elif mutation == 'query_publication_mutates_state':
        final['pedagogy']['instruction_state_after'] = {'invented': True}
    else: raise ValueError(mutation)
    return True


@pytest.mark.parametrize('name', sorted(ORACLES))
def test_strengthened_publication_oracles_accept_real_runs(name, monkeypatch):
    monkeypatch.setattr(ORACLES[name][0], 'execute', _cached)
    _run(name)


@pytest.mark.parametrize('name,mutation,expected', MUTATIONS, ids=[x[0] + '-' + x[1] for x in MUTATIONS])
def test_each_pending_publication_guarantee_rejects_its_mutant(name, mutation, expected, monkeypatch):
    reached = []
    def corrupt(operation, payload, history):
        body = _cached(operation, payload, history)
        before = deepcopy(body)
        if _mutate(body, operation, payload, mutation):
            assert body != before, 'Mutation was vacuous'
            reached.append((operation, deepcopy(payload)))
        return body
    monkeypatch.setattr(ORACLES[name][0], 'execute', corrupt)
    with pytest.raises(AssertionError) as failure:
        _run(name)
    assert reached, 'No real applicable case was mutated'
    assert expected in str(failure.value), 'Wrong oracle rejected mutation: ' + str(failure.value)


@lru_cache(maxsize=1)
def _help():
    return help_contract.capture_current_graph_help()


def test_current_help_accepts_actual_rendered_pages():
    help_contract.assert_graph_help_capture(unittest.TestCase(), deepcopy(_help()))


HELP_MUTATIONS = [
    ('status', 'help_http_status'), ('capacity', 'help_rendered_capacity'),
    ('obsolete_capacity', 'help_obsolete_capacity'), ('app_c_distinction', 'help_app_c_distinction'),
    ('external_queue', 'help_no_external_queue'), ('raw_queue_label', 'help_translated_label'),
    ('structure_capacity', 'help_structure_capacity'), ('tip_capacity', 'help_tip_capacity'),
    ('code', 'help_exact_canonical_code'), ('nonexistent_function', 'help_real_function_definition'),
    ('missing_query_link', 'help_query_function_link'), ('missing_index_queue', 'help_index_queue'),
] + [(prefix + ':' + op, expected + ':' + op) for op in help_contract.AUXILIARY
     for prefix, expected in [('aux_api', 'help_auxiliary_api'), ('aux_selector', 'help_auxiliary_selector'), ('aux_contradiction', 'help_auxiliary_no_contradiction')]] + [
    ('actual_selector', 'help_no_auxiliary_selector'), ('missing_phase', 'help_all_phases')]


def _corrupt_help(captured, mutation):
    markup = captured['html']
    if mutation == 'status': captured['status'] = 503
    elif mutation == 'capacity': markup = markup.replace(f'aplicación es {help_contract.MAX_VERTICES} vértices', 'aplicación es 999 vértices')
    elif mutation == 'obsolete_capacity': markup += '<p>200 vértices</p>'
    elif mutation == 'app_c_distinction': markup = markup.replace('no es un límite del TAD C', 'es un límite del TAD C')
    elif mutation == 'external_queue': markup += '<p>Este código depende del TAD Cola.</p>'
    elif mutation == 'raw_queue_label': markup += '<a>queue</a>'
    elif mutation == 'structure_capacity': captured['structure']['max_vertices'] = -1
    elif mutation == 'tip_capacity': captured['module']['tips'][0] = 'Sin información de capacidad.'
    elif mutation == 'code': markup = markup.replace('GRAFO_DESCONECTADO', 'GRAFO_INVENTADO')
    elif mutation == 'nonexistent_function': markup += '<a data-book-function="grafo_funcion_inventada">Inventada</a>'
    elif mutation == 'missing_query_link': markup = markup.replace('data-book-function="grafo_existe_vertice"', 'data-retired-function="grafo_existe_vertice"')
    elif mutation == 'missing_index_queue': markup = markup.replace('cola de índices propia, sin depender del TAD Cola', 'cola externa')
    elif mutation.startswith(('aux_api:', 'aux_selector:', 'aux_contradiction:')):
        prefix, operation = mutation.split(':')
        pattern = r'(<dt>[^\n]*<code>' + operation + r'</code></dt>\s*<dd>)(.*?)(</dd>)'
        def replace(match):
            description = match[2]
            if prefix == 'aux_api': description = description.replace('API', 'interfaz desconocida')
            elif prefix == 'aux_contradiction': description += ' También aparece en el selector.'
            else:
                description = description.replace('no aparece como opción independiente del selector', 'aparece en el selector')
                description = description.replace('sin control independiente en el selector', 'con control independiente en el selector')
            return match[1] + description + match[3]
        markup, count = re.subn(pattern, replace, markup, flags=re.S)
        assert count == 1
    elif mutation == 'actual_selector':
        page = captured['pages']['construccion']
        page['html'] = re.sub(r"data-allowed-operations='([^']*)'", lambda m: "data-allowed-operations='" + json.dumps(json.loads(html.unescape(m[1])) + ['exists_vertex']) + "'", page['html'], count=1)
    elif mutation == 'missing_phase': del captured['pages']['recorridos']
    else: raise ValueError(mutation)
    captured['html'] = markup


@pytest.mark.parametrize('mutation,expected', HELP_MUTATIONS, ids=[x[0] for x in HELP_MUTATIONS])
def test_help_rejects_each_false_rendered_contract(mutation, expected):
    captured = deepcopy(_help()); before = deepcopy(captured)
    _corrupt_help(captured, mutation)
    assert captured != before, 'Vacuous help mutation'
    with pytest.raises(AssertionError) as failure:
        help_contract.assert_graph_help_capture(unittest.TestCase(), captured)
    assert expected in str(failure.value), 'Wrong help oracle: ' + str(failure.value)


def _assert_invalid_input_without_c(body):
    case = unittest.TestCase()
    case.assertFalse(body['success'], 'invalid_input_success')
    case.assertTrue(body['preserve_session'], 'invalid_input_preserves_session')
    case.assertEqual(body['history'], [], 'invalid_input_preserves_history')
    trace = body['execution_trace']
    case.assertFalse(trace['execution_started'], 'invalid_input_execution_not_started')
    case.assertEqual(trace['C_instruction_events'], [], 'invalid_input_no_c_events')
    case.assertEqual(len(trace['steps']), 1, 'invalid_input_single_rejection')
    step = trace['steps'][0]
    case.assertEqual(step['phase'], 'api_rejection', 'invalid_input_api_rejection')
    case.assertEqual(step['line_text'], '', 'invalid_input_no_c_line')
    case.assertIsNone(step['line_index'], 'invalid_input_no_c_index')
    event = step['pedagogy']['instruction_event']
    case.assertFalse(event['C_executed'], 'invalid_input_no_c_execution')
    case.assertEqual(event['source_role'], 'application', 'invalid_input_application_role')


@pytest.mark.parametrize('operation,payload', [('insert_vertex', {'vertex': 'bad'}), ('remove_vertex', {'vertex': None})])
def test_invalid_vertex_input_is_application_rejection_without_c(operation, payload):
    from app.services.graph_structure_service import GraphStructureService
    body = GraphStructureService.execute_operation('graph', operation, payload, [])
    _assert_invalid_input_without_c(body)
    mutant = deepcopy(body)
    mutant['execution_trace']['steps'][0]['pedagogy']['instruction_event']['C_executed'] = True
    assert mutant != body
    with pytest.raises(AssertionError, match='invalid_input_no_c_execution'):
        _assert_invalid_input_without_c(mutant)
