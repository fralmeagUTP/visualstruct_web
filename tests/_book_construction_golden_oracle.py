"""Exact canonical insertion golden: two arc allocations, stores and publications."""
from copy import deepcopy
from _book_frame_oracle import assert_book_body


def assert_book_graph_golden(body):
    assert_book_body(body)
    trace = body['execution_trace']; steps = trace['steps']
    focal = []
    for i, step in enumerate(steps):
        frame = step['pedagogy']; event = frame['instruction_event']
        if (event['function'] == 'grafo_insertar_arco' and
            (event['phase'] == 'allocate' or (event['phase'] == 'write' and event['name'] in {'*nuevo', 'g.a'}))) or event['phase'] == 'caller_receipt':
            focal.append((i, frame))
    assert [i for i, _ in focal] == [80, 85, 86, 90, 183, 188, 189, 193]
    assert [f['instruction_event']['name'] for _, f in focal] == ['malloc', '*nuevo', 'g.a', 'caller_receipt'] * 2
    for j, (_, frame) in enumerate(focal):
        before, after = frame['instruction_state_before'], frame['instruction_state_after']
        event = frame['instruction_event']; name = event['name']; identity = 'M1' if j < 4 else 'M2'
        old = {n['id']: n for n in before['heap_nodes']}; new = {n['id']: n for n in after['heap_nodes']}
        expected = deepcopy(old); graph = dict(before['graph'])
        fields = {'origen': 1 if j < 4 else 2, 'destino': 2 if j < 4 else 1,
                  'costo': 3, 'sig': 'NULL' if j < 4 else 'M1'}
        assert before['frees'] == after['frees'] == 0
        assert before['retired_objects'] == after['retired_objects'] == []
        if name == 'malloc':
            assert event['value'] == {'pointer': identity, 'size': 24, 'zeroed': False}
            assert after['allocations'] == before['allocations'] + 1
            expected[identity] = {'id': identity, 'kind': 'struct NodoA', 'borrowed': False,
                'alive': True, 'bytes': 24, 'fields': {k: 'sin inicializar' for k in fields}}
        elif name == '*nuevo':
            assert event['value'] == fields
            expected[identity]['fields'] = fields
        elif name == 'g.a':
            assert event['value'] == identity
            root = next(f for f in after['frames'] if f['function'] == 'grafo_insertar_arco')
            assert root['parameters']['g']['a'] == identity
        else:
            graph['a'] = identity
            assert event['returned'] == graph and event['C_executed'] is False
        assert new == expected and after['graph'] == graph
    final = steps[-1]['pedagogy']['memory_state']
    assert final['graph'] == {'v': 'V2', 'a': 'M2'}
    assert final['frames'] == [] and len(final['heap_nodes']) == 4
    assert final['allocations'] == 2 and final['frees'] == 0
    assert body['console_stdout'] == 'insert_edge: estado=0\ninsert_edge inverso: estado=0\n'
