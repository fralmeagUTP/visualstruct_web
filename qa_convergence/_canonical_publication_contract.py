"""Current canonical publication helpers; no unavailable historical snapshots."""
from copy import deepcopy
from unittest.mock import patch
from app.services.graph_structure_service import GraphStructureService as S
from app.domain.graph.snapshot_pool import expand_graph_trace
from tests._book_frame_oracle import assert_book_body


def canonical_history(commands):
    return [{**deepcopy(entry), 'source_contract': S.SOURCE_CONTRACT} for entry in commands]


def execute(operation, payload, history):
    body = S.execute_operation('graph', operation, payload, history)
    assert body.get('execution_trace') is not None, body.get('message')
    body['execution_trace'] = expand_graph_trace(body['execution_trace'])
    assert_book_body(body)
    return body


def receipt(trace, function):
    return next(step['pedagogy'] for step in trace['steps']
        if step['pedagogy']['instruction_event']['phase'] == 'caller_receipt'
        and step['pedagogy']['instruction_event'].get('called_function') == function)


def assert_narration_does_not_change_execution(operation, payload, history):
    """Changing presentation wording must preserve every execution/source field."""
    original = execute(operation, payload, history)
    with patch('app.domain.graph.book_trace._text', return_value='Texto de prueba sin efecto C.') as narration:
        reworded = execute(operation, payload, history)
    assert narration.call_count > 0, 'La prueba no invocó la función de narración sustituida.'
    original_steps = original['execution_trace']['steps']
    reworded_steps = reworded['execution_trace']['steps']
    for field, values in [
        ('narration', lambda step: step['pedagogy']['narration']),
        ('phase.goal', lambda step: step['pedagogy']['phase']['goal']),
        ('debug.note', lambda step: step['debug']['note']),
    ]:
        assert [values(step) for step in original_steps] != [values(step) for step in reworded_steps], (
            'La sustitución no cambió la presentación: ' + field)
    assert len(original['execution_trace']['steps']) == len(reworded['execution_trace']['steps'])
    assert original['execution_trace']['C_instruction_events'] == reworded['execution_trace']['C_instruction_events']
    def execution_projection(body):
        projected_steps = []
        for step in body['execution_trace']['steps']:
            # Only these three fields are text derived by the narration function.
            # Do not mutate interned dictionaries shared by otherwise distinct steps.
            frame = {key: value for key, value in step['pedagogy'].items() if key != 'narration'}
            frame['phase'] = {key: value for key, value in frame['phase'].items() if key != 'goal'}
            projected_steps.append({**step, 'pedagogy': frame,
                'debug': {key: value for key, value in step['debug'].items() if key != 'note'}})
        return {**body, 'execution_trace': {**body['execution_trace'], 'steps': projected_steps}}
    assert execution_projection(original) == execution_projection(reworded)
