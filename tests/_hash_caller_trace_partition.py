"""Separate verified appended caller output from unchanged historical TAD frames."""
def tad_frames_with_caller(trace, expected_fragments):
    steps = trace['steps']
    count = len(expected_fragments)
    assert count > 0
    tad, caller = steps[:-count], steps[-count:]
    assert tad and all(step['event_type'] != 'caller_printf' for step in tad)
    assert [step['event_type'] for step in caller] == ['caller_printf'] * count
    assert [step['console'] for step in caller] == [[text] for text in expected_fragments]
    assert all(step['instruction_event']['function'] == 'main' and
               step['instruction_event']['source_role'] == 'caller' and
               step['instruction_event']['C_executed'] is True for step in caller)
    assert trace['console_stdout'] == ''.join(expected_fragments)
    return tad
