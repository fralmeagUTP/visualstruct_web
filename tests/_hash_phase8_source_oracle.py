"""Exact TAD/caller source and stdout contract for phase8's insert1->4."""
from app.services.trace import TraceEngine


def assert_phase8_hash_insert_source(body):
    trace = body['execution_trace']; steps = trace['steps']; source = trace['source_code'].splitlines()
    assert TraceEngine.validate_legacy_trace(trace)
    expected_line = 'printf("insert:%d:%d:%d\\n", key, value, (int)ok);'
    assert trace['caller_source_code'] == expected_line
    callers = []
    for index, step in enumerate(steps):
        if step['event_type'] == 'caller_printf':
            callers.append(index)
            assert step['instruction_event'] == {'token': 'caller_printf', 'function': 'main',
                'source_role': 'caller', 'C_executed': True, 'caller_line_text': expected_line}
            assert step['line_index'] == -1 and step['line_text'] == ''
            assert step['pedagogy']['source'] == {'line_index': None, 'line_text': expected_line,
                'function': 'main', 'source_role': 'caller'}
            assert index > 0 and step['state_snapshot'] == step['state_after'] == steps[index-1]['state_after']
            assert step['pedagogy']['state_before'] == step['state_snapshot']
            assert step['pedagogy']['state_after'] == step['state_after']
            assert step['console'] == ['insert:1:4:1\n']
            assert step['console_stdout'] == 'insert:1:4:1\n'
        else:
            assert type(step['line_index']) is int and 0 <= step['line_index'] < len(source)
            assert source[step['line_index']] == step['line_text']
            assert step['console'] == []
            assert step['console_stdout'] == ''
    assert callers == [len(steps)-1]
    assert trace['console_stdout'] == body['console_stdout'] == 'insert:1:4:1\n'
    assert trace['final_state'] == body['visual_state'] == steps[-1]['state_after']
