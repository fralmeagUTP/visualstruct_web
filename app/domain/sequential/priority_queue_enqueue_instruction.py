"""Instruction-faithful cp_encolar and cp_crear_nodo, with borrowed caller ownership."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.domain.sequential.pedagogy import (build_sequential_frame, validate_sequential_frame,
    sequential_frame_schema, SEQUENTIAL_FRAME_SCHEMA_VERSION, SEQUENTIAL_LEARNING_CATALOG)


def build_priority_queue_enqueue_trace(*, payload: dict[str, Any], source_code: str,
        code_title: str, before_state: dict[str, Any], after_state: dict[str, Any],
        success: bool, message: str, null_root: bool = False,
        allocation_failure: bool = False) -> dict[str, Any]:
    """Expose real scopes and initialized fields; private faults never enter the API payload."""
    lines = source_code.replace('\r\n', '\n').split('\n')
    value, priority = int(payload.get('value', 0)), int(payload.get('priority', 0))
    items = [] if null_root else before_state.get('items', [])
    heap = [{'id': f'N{i+1}', 'address': f'N{i+1}', 'type': 'CPNodo',
        'alive': True, 'allocated': True, 'freed': False, 'status': 'linked',
        'initialized_mask': 7, 'fields_valid': True,
        'field_validity': {'valor': True, 'prioridad': True, 'sgte': True},
        'fields': {'valor': int(item['value']), 'prioridad': int(item['priority']),
                   'sgte': f'N{i+2}' if i+1 < len(items) else None}}
        for i, item in enumerate(items)]
    objects = {h['id']: h for h in heap}
    front = heap[0]['id'] if heap else None
    rear = heap[-1]['id'] if heap else None
    quantity = len(heap)
    active, helper_active, malloc_active = True, False, False
    parent_new = helper_new = None
    new_id = None
    steps: list[dict[str, Any]] = []
    parent_start = next(i for i, line in enumerate(lines) if 'bool cp_encolar(' in line)
    helper_start = next(i for i, line in enumerate(lines) if 'static CPNodo *cp_crear_nodo(' in line)

    def snapshot() -> dict[str, Any]:
        state = deepcopy(before_state)
        reachable, node_ids, ptr = [], [], front
        while ptr is not None:
            node = objects[ptr]
            assert node['alive'] and node['initialized_mask'] == 7
            reachable.append({'value': node['fields']['valor'], 'priority': node['fields']['prioridad']})
            node_ids.append(ptr)
            ptr = node['fields']['sgte']
        out = min(range(len(reachable)), key=lambda i: reachable[i]['priority']) if reachable else -1
        state.update(items=reachable, node_ids=node_ids, size=len(reachable), empty=not reachable,
            out_index=out, delante=front or 'NULL', atras=rear or 'NULL', cantidad=quantity)
        state.pop('temporaries', None)
        if active and new_id is not None:
            # Compatibility inspection of the reserved object, not another allocation or local value.
            node = objects[new_id]
            state['temporaries'] = {'nuevo': {'id': new_id, 'allocated': True, **deepcopy(node['fields'])}}
        return state

    def emit(event: str, token: str, *, helper_line: bool = False,
            condition: bool | None = None, return_value: Any = None) -> None:
        start, end = (helper_start, parent_start) if helper_line else (parent_start, len(lines))
        indexes = [i for i in range(start, end) if token in lines[i]]
        assert indexes, (event, token)
        index = indexes[-1] if event == 'return_false' and not null_root else indexes[0]
        variables, pointers = [], []
        def variable(name, type_, value_, scope, initialized=True, valid=True, meaning=''):
            v = {'name': name, 'type': type_, 'value': value_, 'scope': scope,
                'scope_state': 'active', 'initialized': initialized, 'valid': valid, 'meaning': meaning}
            variables.append(v)
            if '*' in type_:
                pointers.append({'name': name, 'type': type_, 'target': value_, 'scope': scope,
                    'scope_state': 'active', 'initialized': initialized, 'valid': valid,
                    'alias': 'mismo objeto vivo' if value_ in objects else None})
        if not null_root:
            variable('delante', 'CPNodo *', front, 'caller', meaning='Campo del llamador vivo.')
            variable('atras', 'CPNodo *', rear, 'caller', meaning='Campo del llamador vivo.')
            variable('cantidad', 'int', quantity, 'caller', meaning='Contador, cambia sólo en cantidad++.')
        if active:
            variable('cola', 'ColaPrioridad *', None if null_root else '&cp', 'cp_encolar', meaning='Dirección prestada del objeto caller.')
            variable('valor', 'int', value, 'cp_encolar', meaning='Parámetro escalar C.')
            variable('prioridad', 'int', priority, 'cp_encolar', meaning='Parámetro escalar C.')
            if parent_new is not None:
                variable('nuevo', 'CPNodo *', parent_new['value'], 'cp_encolar',
                    parent_new['initialized'], parent_new['valid'], 'Local parent; independiente del homónimo helper.')
        if helper_active:
            variable('valor', 'int', value, 'cp_crear_nodo', meaning='Parámetro escalar del helper.')
            variable('prioridad', 'int', priority, 'cp_crear_nodo', meaning='Parámetro escalar del helper.')
            if helper_new is not None:
                variable('nuevo', 'CPNodo *', helper_new['value'], 'cp_crear_nodo',
                    helper_new['initialized'], helper_new['valid'], 'Local helper, inicializado sólo tras malloc.')
        old_vars = {(v['scope'], v['name']): v for v in steps[-1]['debug']['variables']} if steps else {}
        old_ptrs = {(p['scope'], p['name']): p for p in steps[-1]['debug']['pointers']} if steps else {}
        for v in variables:
            old = old_vars.get((v['scope'], v['name']))
            v['previous'] = old['value'] if old and old['initialized'] else None
            v['changed'] = bool(old and (old['value'], old['initialized']) != (v['value'], v['initialized']))
        for p in pointers:
            old = old_ptrs.get((p['scope'], p['name']))
            p['previous_target'] = old['target'] if old and old['initialized'] else None
            p['changed'] = bool(old and (old['target'], old['initialized']) != (p['target'], p['initialized']))
        params = {'valor': value, 'prioridad': priority}
        calls = [{'function': 'cp_encolar', 'parameters': {'cola': None if null_root else '&cp', **params},
            'return': None, 'continuation': 'caller conserva propiedad y campos'}] if active else []
        if helper_active:
            calls.append({'function': 'cp_crear_nodo', 'parameters': params, 'return': return_value,
                'continuation': 'inicializador del nuevo de cp_encolar'})
        if malloc_active:
            calls.append({'function': 'malloc', 'parameters': {'size': 'sizeof(CPNodo)'},
                'return': None, 'continuation': 'inicializador del nuevo helper', 'opaque': True})
        scopes = [{'id': name, 'kind': 'function', 'variables': deepcopy([v for v in variables if v['scope'] == name])}
                  for name, enabled in [('cp_encolar', active), ('cp_crear_nodo', helper_active)] if enabled]
        scopes = [s for s in scopes if s['variables']]
        root = {'identity': '&cp', 'type': 'ColaPrioridad', 'alive': not null_root,
            'valid': not null_root, 'initialized': not null_root, 'front': front, 'rear': rear, 'quantity': quantity}
        function = 'malloc' if malloc_active else 'cp_crear_nodo' if helper_line else 'cp_encolar'
        debug = {'token': event, 'function': function, 'root': root, 'heap': deepcopy(heap),
            'parent_new': deepcopy(parent_new) if active else None,
            'helper_new': deepcopy(helper_new) if helper_active else None,
            'variables': deepcopy(variables), 'pointers': deepcopy(pointers), 'scopes': deepcopy(scopes),
            'call_stack': deepcopy(calls), 'return_value': return_value, 'condition_result': condition}
        previous = deepcopy(steps[-1]['state_after'] if steps else before_state)
        memory_snapshot = snapshot()
        # Intermediate frames retain their public C-memory annotations. At the
        # parent return, expose the canonical logical state while retaining the
        # same derived caller memory in pedagogy (never copied from after_state).
        current = {key: value for key, value in memory_snapshot.items()
                   if active or key not in {'node_ids', 'delante', 'atras', 'cantidad'}}
        step = {'step_index': len(steps), 'line_index': index, 'line_text': lines[index],
            'event_type': event, 'phase': 'progress', 'delay_ms': 100, 'function_name': function,
            'state_snapshot': previous, 'state_after': current, 'console': [],
            'condition_result': condition, 'debug': debug}
        memory_step = {**step,
            'state_snapshot': deepcopy(steps[-1]['pedagogy']['memory_state'] if steps else before_state),
            'state_after': memory_snapshot}
        frame = build_sequential_frame(structure_id='priority_queue', operation_name='encolar',
            payload=payload, step=memory_step, success=success)
        memory = {'kind': 'priority_queue_enqueue', 'root': deepcopy(root), 'heap': deepcopy(heap),
            'parent_new': deepcopy(parent_new) if active else None,
            'helper_new': deepcopy(helper_new) if helper_active else None,
            'variables': deepcopy(variables), 'call_stack': deepcopy(calls)}
        substituted = None
        if condition is not None:
            target = None if null_root else '&cp'
            if event == 'helper_allocation_guard': target = helper_new['value']
            if event == 'parent_allocation_guard': target = parent_new['value']
            if event == 'empty_guard': target = front
            substituted = (str(target) if target is not None else 'NULL') + ' == NULL'
        frame.update(variables=variables, pointers=pointers, heap_objects=deepcopy(heap),
            heap_transition={'kind': 'allocate' if event == 'allocator_success_return' else
                'link' if event in ('front_assigned', 'rear_next_assigned', 'rear_assigned') else 'stable',
                'before': deepcopy(steps[-1]['pedagogy']['heap_objects'] if steps else heap),
                'after': deepcopy(heap), 'freed': [], 'dangling_references': []},
            scopes=scopes, call_stack=calls, memory_state=deepcopy(memory_snapshot), enqueue_memory=memory,
            condition=None if condition is None else {'source': lines[index], 'substituted': substituted,
                'result': condition, 'consequence': 'Rama C realmente ejecutada.'})
        frame['source']['function'] = function
        frame['invariant'] = {'text': 'Un objeto por reserva; el contador cambia sólo en su store y no libera memoria.',
            'holds': True, 'symbol': '✓', 'evidence': 'Campos0→1→3→7; locales homónimos separados y aliases vivos hasta su scope termina.'}
        narration = {
            'entry': 'Entra cp_encolar con dirección del caller y dos parámetros int.',
            'new_declared': 'Declara nuevo del parent indeterminado; todavía no lo lee.',
            'root_guard': 'Comprueba cola antes de acceder al objeto prestado.',
            'helper_call': 'Llama cp_crear_nodo; el nuevo del parent aún no recibe resultado.',
            'helper_entry': 'Entra el helper con parámetros propios; su nuevo es otro local.',
            'allocator_enter': 'malloc opaco inicia; el nuevo helper aún está indeterminado.',
            'allocator_success_return': 'malloc devuelve un único objeto vivo con campos sin inicializar.',
            'allocator_NULL_return': 'malloc devuelve NULL; no se crea ningún objeto.',
            'helper_new_allocated': 'Termina el inicializador del nuevo helper, con objeto vivo o NULL.',
            'helper_allocation_guard': 'Comprueba nuevo helper antes de escribir cualquier campo.',
            'value_assigned': 'Escribe valor; sólo este campo está inicializado (máscara1).',
            'priority_assigned': 'Escribe prioridad; sgte aún indeterminado (máscara3).',
            'link_assigned': 'Escribe sgte=NULL; los tres campos están inicializados (máscara7).',
            'helper_return': 'El helper retorna el mismo objeto, sin copiarlo ni liberarlo.',
            'helper_return_NULL': 'El helper retorna NULL, sin consola C ni mutación del caller.',
            'helper_exit': 'Termina sólo el scope helper; sigue vivo el scope parent y su continuación.',
            'parent_new_assigned': 'El nuevo del parent recibe el resultado del helper.',
            'parent_allocation_guard': 'Comprueba nuevo parent antes de publicar el nodo.',
            'empty_guard': 'Elige la rama según delante; no ordena por prioridad al insertar.',
            'front_assigned': 'Publica el mismo objeto en delante; atras aún conserva su valor anterior.',
            'rear_next_assigned': 'Enlaza el mismo objeto desde el atras anterior.',
            'rear_assigned': 'Reasigna atras al mismo nodo; nuevo conserva su alias vivo.',
            'count_incremented': 'Incrementa sólo cantidad; no hay free ni retirada de objeto.',
            'return_true': 'Retorna true y termina scope parent; caller y heap conservan propiedad.',
            'return_false': 'Retorna false sin mutación; el caller conserva su propiedad.'}[event]
        for level in frame['narration']: frame['narration'][level] = narration
        if event in ('return_true', 'return_false', 'helper_return', 'helper_return_NULL'):
            frame['concept'] = 'return'
        validate_sequential_frame(frame, source_code=source_code)
        step['pedagogy'] = frame
        steps.append(step)

    emit('entry', 'bool cp_encolar(')
    parent_new = {'type': 'CPNodo *', 'value': None, 'initialized': False, 'valid': False}
    emit('new_declared', 'CPNodo *nuevo;')
    emit('root_guard', 'if (cola == NULL)', condition=null_root)
    if not null_root:
        emit('helper_call', 'nuevo = cp_crear_nodo(valor, prioridad);')
        helper_active = True
        emit('helper_entry', 'static CPNodo *cp_crear_nodo(', helper_line=True)
        helper_new = {'type': 'CPNodo *', 'value': None, 'initialized': False, 'valid': False}
        malloc_active = True
        emit('allocator_enter', 'malloc(sizeof(CPNodo))', helper_line=True)
        malloc_active = False
        if allocation_failure:
            emit('allocator_NULL_return', 'malloc(sizeof(CPNodo))', helper_line=True)
        else:
            new_id = f'N{len(items)+1}'
            node = {'id': new_id, 'address': new_id, 'type': 'CPNodo', 'alive': True,
                'allocated': True, 'freed': False, 'status': 'temporary', 'initialized_mask': 0,
                'fields_valid': False, 'field_validity': {'valor': False, 'prioridad': False, 'sgte': False},
                'fields': {'valor': None, 'prioridad': None, 'sgte': None}}
            heap.append(node); objects[new_id] = node
            emit('allocator_success_return', 'malloc(sizeof(CPNodo))', helper_line=True)
        helper_new = {'type': 'CPNodo *', 'value': new_id, 'initialized': True, 'valid': True}
        emit('helper_new_allocated', 'malloc(sizeof(CPNodo))', helper_line=True)
        emit('helper_allocation_guard', 'if (nuevo == NULL)', helper_line=True, condition=allocation_failure)
        if allocation_failure:
            emit('helper_return_NULL', 'return NULL;', helper_line=True)
        else:
            for event, field, value_, mask, token in [
                ('value_assigned', 'valor', value, 1, 'nuevo->valor = valor;'),
                ('priority_assigned', 'prioridad', priority, 3, 'nuevo->prioridad = prioridad;'),
                ('link_assigned', 'sgte', None, 7, 'nuevo->sgte = NULL;')]:
                node['fields'][field] = value_; node['initialized_mask'] = mask
                node['field_validity'][field] = True; node['fields_valid'] = mask == 7
                emit(event, token, helper_line=True)
            emit('helper_return', 'return nuevo;', helper_line=True, return_value=new_id)
        helper_active = False
        emit('helper_exit', 'return NULL;' if allocation_failure else 'return nuevo;', helper_line=True, return_value=new_id)
        parent_new = {'type': 'CPNodo *', 'value': new_id, 'initialized': True, 'valid': True}
        emit('parent_new_assigned', 'nuevo = cp_crear_nodo(valor, prioridad);')
        emit('parent_allocation_guard', 'if (nuevo == NULL)', condition=allocation_failure)
        if not allocation_failure:
            emit('empty_guard', 'if (cola->delante == NULL)', condition=front is None)
            if front is None:
                front = new_id; node['status'] = 'linked'
                emit('front_assigned', 'cola->delante = nuevo;')
            else:
                objects[rear]['fields']['sgte'] = new_id; node['status'] = 'linked'
                emit('rear_next_assigned', 'cola->atras->sgte = nuevo;')
            rear = new_id; emit('rear_assigned', 'cola->atras = nuevo;')
            quantity += 1; emit('count_incremented', 'cola->cantidad++;')
    active = False
    result = not null_root and not allocation_failure
    emit('return_true' if result else 'return_false', 'return true;' if result else 'return false;', return_value=result)
    steps[0]['phase'] = 'start'; steps[-1]['phase'] = 'end'
    return {'structure_id': 'priority_queue', 'operation_name': 'encolar', 'payload': deepcopy(payload),
        'success': success, 'message': message, 'mutates': True, 'source_code': source_code,
        'code_title': code_title, 'steps': steps, 'final_state': deepcopy(after_state),
        'pedagogy_schema_version': SEQUENTIAL_FRAME_SCHEMA_VERSION,
        'pedagogy_schema': sequential_frame_schema(),
        'learning_profile': deepcopy(SEQUENTIAL_LEARNING_CATALOG['priority_queue']),
        'instruction_scope': 'cp_encolar/cp_crear_nodo scoped locals, opaque malloc, masks, aliases and bool return'}
