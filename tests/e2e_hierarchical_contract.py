"""Identity-based memory and separate live/historical C frames, without lossy sets."""
from e2e_trace_contracts import reveal_public


def same_nodes(actual, expected):
    """Presentation may prioritize a focused identity; data and multiplicity may not change."""
    assert len(actual) == len(expected)
    assert len({n['id'] for n in actual}) == len(actual)
    assert len({n['id'] for n in expected}) == len(expected)
    assert sorted(actual, key=lambda n:n['id']) == sorted(expected, key=lambda n:n['id'])
    return True


def memory_cards(row, expected):
    assert len(row['nodes']) == len(row['cards']) == len(expected)
    actual_ids=[n['id'] for n in row['nodes']]
    assert len(set(actual_ids)) == len(actual_ids)
    cards=dict(zip(actual_ids,row['cards']))
    assert set(cards) == {n['id'] for n in expected}
    for node in expected:
        fields=f"valor: {node['value']} · izquierdo: {node['left']} · derecho: {node['right']}"
        assert fields in cards[node['id']]
    return [(node,cards[node['id']]) for node in expected]


def color_label(color):
    return {'RED':'rojo','BLACK':'negro'}.get(color,color)


STACK_RECORDS = """el => ({live:[...el.querySelectorAll(':scope > .hier-stack-frame')].map(x=>x.textContent),completed:[...el.querySelectorAll(':scope > details > .hier-stack-frame')].map(x=>x.textContent),details:el.querySelectorAll(':scope > details').length})"""


def scope_frames(frame):
    calls=frame['call_stack']
    ended=lambda call:call.get('scope_status')=='terminado (contexto del retorno)'
    return ([c for c in calls if not ended(c)],frame.get('completed_call_stack',[])+[c for c in calls if ended(c)])


def live_call_count(frame):
    return len(scope_frames(frame)[0])


def assert_stack_records(records, frame):
    def display(value):return str(value).lower() if isinstance(value,bool) else str(value)
    def text(call,historical):
        status='ámbito terminado (registro histórico)' if historical else 'profundidad '+display(call['depth'])
        root=call.get('local_root_address') or call.get('local_root') or 'NULL'
        result=call.get('return')
        if result is None:result='sin valor de retorno registrado' if historical else 'pendiente'
        continuation=(' · '+call['continuation']) if not historical and call.get('continuation') else ''
        return f"{call['function']} · {status}raíz local registrada: {root}retorno: {display(result)}{continuation}"
    live,completed=scope_frames(frame)
    assert records['live'] == [text(c,False) for c in live]
    assert records['completed'] == [text(c,True) for c in completed]
    assert records['details'] == int(bool(completed))


def assert_hier_stack(page, frame):
    assert_stack_records(page.locator('#hier-stack-view').evaluate(STACK_RECORDS),frame)


def assert_completed_scope(page,frame):
    assert scope_frames(frame)[1], 'Return must record the ended scope'
    row=page.locator('#hier-stack-view > details > .hier-stack-frame').last
    reveal_public(page,row)
    assert 'ámbito terminado (registro histórico)' in row.inner_text()
    assert_hier_stack(page,frame)
