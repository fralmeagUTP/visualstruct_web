"""Check shortest-path table transport against live canonical Trabajo cells."""
from _book_frame_oracle import assert_book_body
from app.domain.graph.book_c_subset import UNINIT


def active_work(memory, function):
    roots = [frame for frame in memory['frames']
        if frame['function'] == function and frame.get('status') != 'returning']
    assert len(roots) <= 1
    if not roots:
        return None
    values = [scope['variables']['t']['value'] for scope in roots[0]['scopes']
        if 't' in scope['variables']]
    assert len(values) <= 1
    return values[0] if values and isinstance(values[0], dict) else None


def arrays(memory, work):
    heap = {node['id']: node for node in memory['heap_nodes']}
    return {name: heap.get(work.get(name), {}).get('items', [])
        for name in ['vertices', 'dist', 'prev', 'usado', 'alcanzable']} if work else {
            name: [] for name in ['vertices', 'dist', 'prev', 'usado', 'alcanzable']}


def expected_tables(memory, function):
    values = arrays(memory, active_work(memory, function))
    vertices = values['vertices']; distances = {}; previous = {}; visited = []; candidates = []
    for index, vertex in enumerate(vertices):
        if vertex == UNINIT:
            continue
        key = str(vertex)
        reached = index < len(values['alcanzable']) and values['alcanzable'][index] == 1
        distances[key] = values['dist'][index] if reached and index < len(values['dist']) else None
        predecessor = values['prev'][index] if index < len(values['prev']) else None
        previous[key] = vertices[predecessor] if type(predecessor) is int and 0 <= predecessor < len(vertices) else None
        if index < len(values['usado']) and values['usado'][index] == 1:
            visited.append(key)
        elif reached:
            candidates.append(key)
    return {'distances': distances, 'previous': previous, 'visited': visited, 'candidates': candidates}


def assert_shortest_chain_tables(body, operation):
    """Preserve initialization, reachability, source, lifetime and final-path checks."""
    assert_book_body(body)
    trace = body['execution_trace']; steps = trace['steps']; function = 'grafo_' + operation[4:]
    assert body['source_contract'] == 'graph-book/v1' and trace['book_instruction_model']
    assert steps[0]['phase'] == 'caller_prepare'
    assert trace['C_instruction_events'][0]['phase'] == 'enter'
    assert steps[-1]['phase'] == 'api_publication'
    assert steps[0]['debug']['graph_progress']['distances'] == steps[0]['debug']['graph_progress']['previous'] == {}
    assert steps[-1]['debug']['graph_progress']['distances'] == steps[-1]['debug']['graph_progress']['previous'] == {}
    mask_writes = []; work_frees = []
    for index, step in enumerate(steps):
        frame = step['pedagogy']; event = frame['instruction_event']; memory = frame['instruction_state_after']
        expected = expected_tables(memory, function)
        for name, value in expected.items():
            assert step['debug']['graph_progress'][name] == value, (index, name)
        assert frame['table']['distances'] == expected['distances']
        assert frame['table']['previous'] == expected['previous']
        assert frame['table']['visited'] == expected['visited']
        assert frame['auxiliary']['candidates'] == expected['candidates']
        if event['function'] == function and event['phase'] == 'write' and event.get('name') == 't.alcanzable[s]':
            mask_writes.append(index)
        if event['function'] == 'liberar_trabajo' and event['phase'] == 'free':
            work_frees.append(index)
    # calloc stores zero but cannot publish reachability before the mask store.
    assert len(mask_writes) == 1
    initialized = mask_writes[0]; frame = steps[initialized]['pedagogy']
    before, after = frame['instruction_state_before'], frame['instruction_state_after']
    work = active_work(before, function); old = arrays(before, work); new = arrays(after, work)
    assert set(old['vertices']) == {1, 2, 3}
    start = old['vertices'].index(1)
    assert old['dist'] == [0, 0, 0] and old['alcanzable'] == [0, 0, 0]
    assert new['alcanzable'] == [1 if i == start else 0 for i in range(3)]
    assert {key: value for key, value in new.items() if key != 'alcanzable'} == {
        key: value for key, value in old.items() if key != 'alcanzable'}
    assert steps[initialized-1]['debug']['graph_progress']['distances'] == {'1': None, '2': None, '3': None}
    assert steps[initialized]['debug']['graph_progress']['distances'] == {'1': 0, '2': None, '3': None}
    assert steps[initialized]['debug']['graph_progress']['previous'] == {'1': None, '2': None, '3': None}
    # Canonical liberar_trabajo frees vertices first, then prev/used/mask/dist.
    assert len(work_frees) == 5 and initialized < work_frees[0]
    first = steps[work_frees[0]]['pedagogy']; memory = first['instruction_state_before']
    work = active_work(memory, function); final_arrays = arrays(memory, work); vertices = final_arrays['vertices']
    assert dict(zip(vertices, final_arrays['dist'])) == {1: 0, 2: 4, 3: 5}
    assert {vertex: None if final_arrays['prev'][i] == -1 else vertices[final_arrays['prev'][i]]
        for i, vertex in enumerate(vertices)} == {1: None, 2: 1, 3: 2}
    assert steps[work_frees[0]-1]['debug']['graph_progress']['distances'] == {'1': 0, '2': 4, '3': 5}
    assert steps[work_frees[0]-1]['debug']['graph_progress']['previous'] == {'1': None, '2': 1, '3': 2}
    for index, name in zip(work_frees, ['vertices', 'prev', 'usado', 'alcanzable', 'dist']):
        frame = steps[index]['pedagogy']; pointer = work[name]
        assert frame['instruction_event']['value'] == pointer
        assert pointer in {node['id'] for node in frame['instruction_state_before']['heap_nodes']}
        assert pointer not in {node['id'] for node in frame['instruction_state_after']['heap_nodes']}
        assert pointer in {node['id'] for node in frame['instruction_state_after']['retired_objects']}
        assert steps[index]['debug']['graph_progress']['distances'] == {}
        assert steps[index]['debug']['graph_progress']['previous'] == {}
    receipt = next(step for step in steps if step['phase'] == 'caller_receipt'
        and step['pedagogy']['instruction_event'].get('called_function') == function)
    assert receipt['pedagogy']['instruction_event']['returned'] == body['c_return'] != 'NULL'
    assert body['success'] and body['c_status'] == 0
    assert body['result']['distance_to_destination'] == 5 and body['result']['path'] == [1, 2, 3]
    assert body['result']['path_arcs'] == [[1, 2, 4], [2, 3, 1]]
    final = steps[-1]['pedagogy']['memory_state']
    assert final['external']['result']['value'] == 'NULL' and final['allocations'] == final['frees']
    assert final['heap_nodes'] == steps[0]['pedagogy']['instruction_state_before']['heap_nodes']
