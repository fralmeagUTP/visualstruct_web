"""Instruction model for the unchanged downloaded ABB traversal functions.

Every invocation, including a NULL child, has its own parameter scope. The
highlight names the instruction just completed; call entry and completion are
separate occurrences of the same physical C line. No heap writes occur.
"""
from copy import deepcopy
from .pedagogy import build_hierarchical_frame, validate_hierarchical_frame


def build_abb_traversal_trace(trace, before_state, after_state):
    operation = trace['operation_name']
    assert operation in {'inorden', 'preorden', 'postorden'}
    function = 'abb_' + operation
    source = trace['source_code']
    lines = source.splitlines()
    heap, frames, history, steps = [], [], [], []
    stdout = ''

    def load(node):
        if node is None:
            return 'NULL'
        identity = 'N' + str(len(heap) + 1)
        item = {'id': identity, 'value': node['value'], 'left': 'NULL', 'right': 'NULL', 'status': 'linked'}
        heap.append(item)
        item['left'], item['right'] = load(node['left']), load(node['right'])
        return identity

    head = load(before_state.get('root'))
    def node(identity):
        return next(n for n in heap if n['id'] == identity)

    def snapshot():
        state = deepcopy(before_state)
        state.update(abb_traversal_model=True, head=head, heap_nodes=deepcopy(heap),
                     tree_frames=deepcopy(frames), caller_frame=None, console_stdout=stdout)
        return state

    def line_index(text):
        return next(i for i, line in enumerate(lines) if line.strip() == text)

    def emit(text, phase, mutate=None, condition=None, index=None, fragment=''):
        old = snapshot()
        owner = frames[-1]['id'] if frames else None
        if mutate:
            mutate()
        new = snapshot()
        idx = line_index(text) if index is None else index
        event = {'phase': phase, 'frame_id': owner, 'condition': condition, 'return': 'void' if phase == 'return' else None}
        step = {'step_index': len(steps), 'line_index': idx, 'line_text': lines[idx], 'event_type': 'line',
                'delay_ms': 170, 'console': [fragment] if fragment else [],
                'state_snapshot': old, 'state_after': new, 'debug': {'stage': phase}}
        if phase == 'condition':
            step['condition_result'] = condition
        ped = build_hierarchical_frame(structure_id='abb', operation_name=operation, payload=trace['payload'],
                                       step=step, source_lines=lines, success=True)
        ped['concept'] = 'return' if phase == 'return' else 'compare' if phase == 'condition' else 'output' if phase == 'printf' else 'descend'
        ped['case'] = phase
        ped['phase'] = {'id': operation + '-' + phase, 'label': phase.title(), 'goal': lines[idx]}
        ped['condition'] = None
        if phase == 'condition':
            alias = old['tree_frames'][-1]['parameters']['nodo']
            ped['condition'] = {'source': text, 'substituted': 'if (' + alias + ' != NULL)',
                                'result': condition, 'consequence': 'cuerpo' if condition else 'omitir cuerpo'}
            ped['executed_branch'] = 'cuerpo' if condition else 'omitir cuerpo'
        a = {f['id']: f['parameters']['nodo'] for f in old['tree_frames']}
        b = {f['id']: f['parameters']['nodo'] for f in new['tree_frames']}
        ped['variables'] = [{'name': 'nodo', 'scope': function + '#' + f['id'], 'frame_id': f['id'],
                             'type': 'ABBNodo *', 'previous': a.get(f['id'], 'fuera de ámbito'),
                             'value': b.get(f['id'], 'fuera de ámbito'),
                             'changed': a.get(f['id']) != b.get(f['id']),
                             'meaning': 'Parametro por valor de esta invocacion; el retorno void termina su ambito sin liberar el nodo.'}
                            for f in history if f['id'] in a or f['id'] in b]
        shown = old['tree_frames'] if phase == 'return' else new['tree_frames']
        ped['call_stack'] = [{'function': function, 'frame_id': f['id'], 'depth': f['depth'],
                              'parameters': deepcopy(f['parameters']), 'locals': {},
                              'local_root': f['parameters']['nodo'], 'local_root_address': f['parameters']['nodo'],
                              'return': 'void' if phase == 'return' and f['id'] == owner else None,
                              'continuation': 'retoma la instruccion siguiente del llamador; no reconecta enlaces'} for f in shown]
        objects = [{'id': n['id'], 'address': n['id'], 'symbolic_identity': True, 'value': n['value'],
                    'left': n['left'], 'right': n['right'], 'allocated': True, 'freed': False} for n in heap]
        ped['memory'] = {'event': 'none', 'objects_before': deepcopy(objects), 'objects_after': deepcopy(objects),
                         'allocated_objects': [], 'freed_objects': [], 'dangling_references': [],
                         'stable_addresses': True, 'symbolic_identities': True}
        explanations = {
            'enter': 'Entra una invocacion con su propio parametro nodo, incluso si es NULL. Los llamadores quedan suspendidos.',
            'condition': 'Evalua nodo != NULL una vez. NULL omite el cuerpo y no imprime ni modifica el arbol.',
            'call': 'Inicia la llamada al hijo indicado. El parametro del llamador conserva su identidad y la estructura no cambia.',
            'resume': 'La llamada al hijo termino. Retoma este ambito sin escribir enlaces ni imprimir de nuevo.',
            'printf': 'printf emite solo el valor de este nodo seguido de un espacio, sin salto de linea. La estructura permanece intacta.',
            'return': 'Alcanza el cierre de la funcion void y retorna. Termina solo este ambito; no libera memoria ni devuelve un nodo.'}
        ped['narration'] = {level: explanations[phase] for level in ['basic', 'intermediate', 'advanced']}
        ped['return_propagation'] = {'active': phase == 'return', 'value': 'void' if phase == 'return' else None, 'reconnects_subtree': False}
        ped['state_before'], ped['state_after'], ped['memory_state'] = deepcopy(old), deepcopy(new), deepcopy(new)
        ped['instruction_event'] = event
        ped['invariant'].update(explanation='Recorrido de solo lectura: todas las identidades, valores y enlaces se conservan. La consola muestra solo printf ya ejecutados.', holds=True, symbol='✓')
        validate_hierarchical_frame(ped, source_code=source)
        step['pedagogy'] = ped
        steps.append(step)

    signature = 'void ' + function + '(ABBNodo* nodo) {'
    closing = max(i for i, line in enumerate(lines) if line.strip() == '}')
    def rec(identity):
        nonlocal stdout
        f = {'id': 'F' + str(len(history) + 1), 'function': function, 'depth': len(frames),
             'parameters': {'nodo': identity}, 'locals': {}}
        history.append(f)
        emit(signature, 'enter', lambda: frames.append(f))
        emit('if (nodo != NULL) {', 'condition', condition=identity != 'NULL')
        if identity != 'NULL':
            actions = ['print', 'left', 'right'] if operation == 'preorden' else ['left', 'print', 'right'] if operation == 'inorden' else ['left', 'right', 'print']
            for action in actions:
                if action == 'print':
                    fragment = str(node(identity)['value']) + ' '
                    def output():
                        nonlocal stdout
                        stdout += fragment
                    emit('printf("%d ", nodo->valor);', 'printf', output, fragment=fragment)
                else:
                    text = function + '(nodo->' + ('izquierdo' if action == 'left' else 'derecho') + ');'
                    emit(text, 'call')
                    rec(node(identity)[action])
                    emit(text, 'resume')
        emit('}', 'return', frames.pop, index=closing)
    rec(head)
    assert not frames
    # Preserve the endpoint schema expected by the existing API contract while
    # retaining instruction memory/scopes/console in the pedagogical projection.
    steps[-1]['state_after'] = deepcopy(after_state)
    steps[-1]['pedagogy']['state_after'] = deepcopy(after_state)
    initial = deepcopy(steps[0]['pedagogy'])
    initial.update(variables=[], call_stack=[], condition=None, memory_state=deepcopy(steps[0]['state_snapshot']), state_after=deepcopy(steps[0]['state_snapshot']))
    initial['phase']['label'] = 'Estado inicial'
    initial['narration'] = {level: 'Ninguna instruccion ejecutada; arbol inicial y consola vacia, sin parametros futuros.' for level in ['basic', 'intermediate', 'advanced']}
    steps[0]['pedagogy']['initial_frame'] = initial
    trace.update(steps=steps)
    return trace
