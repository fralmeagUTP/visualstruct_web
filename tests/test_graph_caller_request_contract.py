"""Real HTTP coverage of string UI payloads and retained C failures."""
from copy import deepcopy
import pytest
from app import create_app
from app.config import Config
from _graph_caller_request_contract import assert_missing_vertex_call_recorded


@pytest.fixture(scope='module', params=['run_dijkstra', 'run_bellman_ford', 'run_prim'])
def failed_call(request, tmp_path_factory):
    operation = request.param
    class Private(Config):
        TESTING = True
        SECRET_KEY = 'caller-request-contract'
        SESSION_CACHE_DIR = str(tmp_path_factory.mktemp('caller-request-session'))
    client = create_app(Private).test_client()
    def post(name, payload):
        reply = client.post('/graph/graph/operate', json={'operation': name,
            'payload': payload, 'execution_mode': 'normal'})
        return reply.get_json()
    assert post('create_graph', {'directed': operation != 'run_prim'})['success']
    assert post('insert_vertex', {'vertex': -1})['success']
    successful_payload = {'start': '-1'} if operation == 'run_prim' else {'start': '-1', 'end': '-1'}
    previous = post(operation, successful_payload)
    assert previous['success']
    previous = post(operation, successful_payload)
    submitted = {'operation': operation, 'payload': {**successful_payload, 'start': '999'}, 'execution_mode': 'normal'}
    rejected = client.post('/graph/graph/operate', json=submitted).get_json()
    return operation, previous, rejected, submitted


def test_real_browser_payload_remains_exact_after_c_failure(failed_call):
    operation, previous, rejected, submitted = failed_call
    assert rejected['history'][-1]['payload']['start'] == '999'
    # This was the caller helper's deterministic failed assumption.
    assert rejected['history'][-1]['payload']['start'] != 999
    assert_missing_vertex_call_recorded(rejected, previous, submitted, operation, -1)
    assert rejected['main_c'].count('= grafo_' + operation[4:] + '(') == 3


@pytest.mark.parametrize('corruption', ['coerced_history', 'missing_call', 'wrong_operation', 'wrong_status', 'coerced_request', 'extra_field'])
def test_caller_history_contract_rejects_changed_or_dropped_input(failed_call, corruption):
    operation, old_previous, old_rejected, old_submitted = failed_call
    previous, rejected, submitted = deepcopy((old_previous, old_rejected, old_submitted))
    if corruption == 'coerced_history':
        rejected['history'][-1]['payload']['start'] = 999
    elif corruption == 'missing_call':
        rejected['history'] = previous['history']
    elif corruption == 'wrong_operation':
        rejected['history'][-1]['operation'] = 'run_dfs'
    elif corruption == 'wrong_status':
        rejected['c_status'] = 0
    elif corruption == 'extra_field':
        submitted['payload']['unused'] = 'forged'
        rejected['history'][-1]['payload']['unused'] = 'forged'
    else:
        submitted['payload']['start'] = 999
    with pytest.raises(AssertionError):
        assert_missing_vertex_call_recorded(rejected, previous, submitted, operation, -1)
