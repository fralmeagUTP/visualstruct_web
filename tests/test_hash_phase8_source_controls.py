"""The caller sentinel is a distinct source, not a reason to relax mapping."""
from copy import deepcopy
import pytest
from _hash_phase8_source_oracle import assert_phase8_hash_insert_source
from test_phase8_visual_integration import execute_scenario


@pytest.fixture(scope='module')
def inserted():
    return execute_scenario('hash_table')


@pytest.mark.parametrize('corruption', ['caller_source', 'stdout', 'continuity', 'tad_source', 'early_stdout', 'early_stdout_synced'])
def test_phase8_hash_source_rejects_corruption(inserted, corruption):
    body = deepcopy(inserted); trace = body['execution_trace']; caller = trace['steps'][-1]
    if corruption == 'caller_source':
        forged = 'printf("forged");'
        trace['caller_source_code'] = caller['instruction_event']['caller_line_text'] = forged
        caller['pedagogy']['source']['line_text'] = forged
    elif corruption == 'stdout':
        body['console_stdout'] = trace['console_stdout'] = caller['console_stdout'] = 'insert:1:4:0\n'
        caller['console'] = ['insert:1:4:0\n']
    elif corruption in {'early_stdout', 'early_stdout_synced'}:
        trace['steps'][0]['console_stdout'] = 'FORGED\n'
        if corruption == 'early_stdout_synced':
            trace['steps'][0]['console'] = ['FORGED\n']
            trace['console_stdout'] = body['console_stdout'] = 'FORGED\ninsert:1:4:1\n'
    elif corruption == 'continuity':
        caller['state_snapshot'] = {'forged': True}
    else:
        trace['steps'][0]['line_text'] = 'wrong source'
    with pytest.raises((AssertionError, ValueError)):
        assert_phase8_hash_insert_source(body)
