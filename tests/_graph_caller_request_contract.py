"""The browser's original payload is preserved even when canonical C fails."""

def assert_missing_vertex_call_recorded(rejected, previous, request, operation, end=None):
    assert request['operation'] == operation
    expected = {'start': '999'}
    if operation != 'run_prim':
        assert end is not None
        expected['end'] = str(end)
    assert request['payload'] == expected
    assert rejected['success'] is False and rejected['c_status'] == 2
    assert rejected['history'][:-1] == previous['history']
    assert rejected['history'][-1] == {'operation': operation,
        'payload': request['payload'], 'source_contract': 'graph-book/v1'}
