"""Read native-observer return context without resurrecting expired scopes."""
def context_stack(pedagogy):
    live = pedagogy['call_stack']
    completed = pedagogy.get('completed_call_stack', [])
    live_ids = {frame.get('frame_id') for frame in live}
    for frame in completed:
        assert frame.get('frame_id') not in live_ids
        assert frame.get('scope_status', '').startswith('terminado')
    return [*live, *completed]
