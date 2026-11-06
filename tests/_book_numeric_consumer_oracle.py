"""Causal stores and ownership checks for the canonical book Dijkstra trace."""
from copy import deepcopy
from _book_frame_oracle import assert_book_body


def assert_chain_dijkstra(body):
    """Check each relaxation store against live arrays, then the returned path."""
    assert_book_body(body)
    trace = body['execution_trace']
    assert body['source_contract'] == 'graph-book/v1'
    assert body['c_status_name'] == 'GRAFO_OK'
    assert body['result']['path'] == [1, 2, 3]
    assert body['result']['distance_to_destination'] == 5
    updates, predecessors, visited = [], [], []
    for step in trace['steps']:
        frame = step['pedagogy']; event = frame['instruction_event']
        assert frame['auxiliary']['kind'] == 'linear_scan'
        if event['function'] != 'grafo_dijkstra' or event['phase'] != 'write':
            continue
        name = event['name']
        if name not in {'t.dist[v]', 't.prev[v]', 't.usado[u]'}:
            continue
        before, after = frame['instruction_state_before'], frame['instruction_state_after']
        root = next(f for f in before['frames'] if f['function'] == 'grafo_dijkstra')
        env = {k: cell['value'] for scope in root['scopes'] for k, cell in scope['variables'].items()}
        old = {n['id']: n for n in before['heap_nodes']}
        new = {n['id']: n for n in after['heap_nodes']}
        work = env['t']; vertices = old[work['vertices']]['items']
        field, index, value = ('dist', env['v'], env['nueva']) if name == 't.dist[v]' else (
            ('prev', env['v'], env['u']) if name == 't.prev[v]' else ('usado', env['u'], 1))
        expected = dict(old)
        changed_items = list(old[work[field]]['items']); changed_items[index] = value
        expected[work[field]] = {**old[work[field]], 'items': changed_items}
        assert new == expected, 'A focal store must only change its physical array cell'
        if field == 'dist':
            arc = old[env['a']]['fields']
            assert value == old[work['dist']]['items'][env['u']] + arc['costo']
            updates.append((vertices[env['u']], vertices[env['v']], value))
        elif field == 'prev':
            predecessors.append((vertices[env['u']], vertices[env['v']]))
        else:
            visited.append(vertices[env['u']])
    assert updates == [(1, 2, 2), (2, 3, 5)]
    assert predecessors == [(1, 2), (2, 3)] and visited == [1, 2, 3]
    receipt = next(s['pedagogy'] for s in trace['steps']
        if s['pedagogy']['instruction_event']['phase'] == 'caller_receipt'
        and s['pedagogy']['instruction_event'].get('called_function') == 'grafo_dijkstra')
    memory = receipt['memory_state']; heap = {n['id']: n for n in memory['heap_nodes']}
    pointer = receipt['instruction_event']['returned']; arcs = []; seen = set()
    while pointer != 'NULL':
        assert pointer not in seen; seen.add(pointer)
        node = heap[pointer]; assert not node['borrowed']
        fields = node['fields']; arcs.append([fields['origen'], fields['destino'], fields['costo']])
        pointer = fields['sig']
    assert arcs == [[1, 2, 2], [2, 3, 3]]
    final = trace['steps'][-1]['pedagogy']['memory_state']
    assert final['frames'] == [] and final['external']['result']['value'] == 'NULL'
    assert final['allocations'] == final['frees']
    initial = trace['steps'][0]['pedagogy']['instruction_state_before']
    assert final['heap_nodes'] == initial['heap_nodes']
