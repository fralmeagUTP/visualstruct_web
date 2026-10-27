"""Statement execution for the approved Hash H1 creation/insertion C kernel.

Heap identities are symbolic, stable by key within this operation. Never read an
uninitialized C field. Explicit caller cleanup precedes recreation; that boundary
is outside th_inicializar. Other Hash operations retain their existing planner.
"""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.domain.hash.pedagogy import build_hash_frame, hash_frame_schema, HASH_LEARNING_CATALOG


def build_hash_instruction_trace(*, operation_name: str, payload: dict[str, Any],
        source_code: str, code_title: str, before_state: dict[str, Any],
        after_state: dict[str, Any], success: bool, message: str, **_: Any) -> dict[str, Any]:
    """Execute bounded C statements with explicit locals, scopes and heap masks."""
    lines = source_code.replace('\r\n', '\n').split('\n')
    operation = operation_name
    frames: list[dict[str, Any]] = []
    state = deepcopy(before_state)
    heap: list[dict[str, Any]] = []
    capacity = int(before_state.get('metadata', {}).get('capacity', 0))
    count = int(before_state.get('metadata', {}).get('size', 0))
    array_id: str | None = 'bucket-array' if capacity else None
    cells = [True] * capacity
    for bucket in before_state.get('buckets', []):
        for entry in bucket.get('entries', []):
            heap.append({'id': entry['address'], 'kind': 'node', 'initialized_mask': 7,
                         'key': entry['key'], 'value': entry['value'], 'next': None if entry.get('next') in (None, '', 'NULL') else entry['next']})
    locals_: dict[str, dict[str, Any]] = {}
    stack: list[str] = []
    comparisons = hash_calls = 0
    link_writes = value_writes = key_writes = count_writes = 0
    allocation_attempts = allocation_count = 0
    index: int | None = None
    actual: str | None = None
    new: str | None = None
    i: int | None = None
    return_status: bool | int | None = None
    found_observed = False
    raw_observed: int | None = None
    normalized_observed: int | None = None
    allocated: list[str] = []
    freed: list[str] = []

    def local(name: str, ctype: str, value: Any = None, initialized: bool = True) -> None:
        locals_[name] = {'type': ctype, 'initialized': initialized, 'value': value if initialized else None}

    def find(token: str, function: str) -> int:
        start = next((j for j, row in enumerate(lines) if function + '(' in row.replace(' ', '') and '{' in row), 0)
        last = token.startswith('@last:')
        token = token.removeprefix('@last:')
        compact = ''.join(token.split())
        for j in (range(len(lines)-1, start-1, -1) if last else range(start, len(lines))):
            if compact in ''.join(lines[j].split()):
                return j
        raise ValueError(f'Hash C source missing {function}: {token}')

    def node(identity: str | None) -> dict[str, Any] | None:
        return next((n for n in heap if n['id'] == identity), None)

    def refresh() -> None:
        for bucket in state.get('buckets', []):
            bucket['size'] = len(bucket.get('entries', []))
            bucket['collisions'] = max(0, bucket['size'] - 1)
        lengths = [len(b.get('entries', [])) for b in state.get('buckets', [])]
        state['metadata'] = {'capacity': capacity, 'size': count,
            'load_factor': round(count / capacity, 6) if capacity else 0,
            'chain_lengths': lengths, 'collisions': sum(max(0, n-1) for n in lengths),
            'occupied_buckets': sum(n > 0 for n in lengths), 'empty_buckets': sum(n == 0 for n in lengths),
            'max_chain_length': max(lengths, default=0), 'is_empty': count == 0, 'capacity_policy': 'fixed'}

    def emit(token: str, source: str | None, function: str, condition: bool | None = None) -> None:
        refresh()
        j = find(source, function) if source else -1
        previous = deepcopy(frames[-1]['state_after'] if frames else before_state)
        current = deepcopy(state)
        debug = {'token': token, 'function': function, 'call_stack': list(stack),
            'variables': deepcopy(locals_), 'condition_result': condition,
            'scopes': [{'function': name, 'variables': {key.split('.', 1)[-1]: deepcopy(value) for key, value in locals_.items() if (key.startswith(name + '.') if position else '.' not in key)}} for position, name in enumerate(stack)],
            'root_identity': '&tabla',
            'root': {'capacity': capacity, 'size': count, 'bucket_pointer': array_id},
            'bucket_initialization': list(cells), 'heap': deepcopy(heap),
            'indice': index, 'i': i, 'actual': actual, 'nuevo': new, 'return_status': return_status,
            'comparisons': comparisons, 'hash_calls': hash_calls,
            'link_writes': link_writes, 'value_writes': value_writes, 'key_writes': key_writes, 'count_writes': count_writes,
            'allocation_attempts': allocation_attempts, 'allocations': allocation_count,
            'allocated': list(allocated), 'freed': list(freed),
            'identity_policy': 'symbolic allocation identities, not physical addresses'}
        step = {'step_index': len(frames), 'line_index': j,
            'line_text': lines[j] if j >= 0 else '', 'event_type': token,
            'phase': 'progress', 'delay_ms': 170, 'state_snapshot': previous,
            'state_after': current, 'console': [], 'debug': debug,
            'instruction_event': {'token': token, 'function': function, 'condition': condition}}
        frame = build_hash_frame(operation_name=operation, payload=payload, step={**step,
            'hash_initial_state': current if operation == 'create_table' else before_state},
            source_lines=lines, success=success)
        frame['condition'] = None if condition is None else {'source': step['line_text'], 'result': condition,
            'substituted': str(condition), 'consequence': 'Rama C efectivamente ejecutada.'}
        frame['source']['function'] = function
        frame['hash'].update({'raw_remainder': raw_observed, 'normalized_index': normalized_observed,
            'normalization_applied': raw_observed is not None and raw_observed < 0 and normalized_observed is not None,
            'normalization_expression': None if normalized_observed is None else f'Indice calculado: {normalized_observed}',
            'expression': None if raw_observed is None else f'{payload.get("key")} % {capacity} = {raw_observed}'})
        initial_bucket = next((b for b in before_state.get('buckets', []) if b.get('index') == normalized_observed), {})
        frame['chain']['examined'] = [e['key'] for e in initial_bucket.get('entries', [])[:comparisons]]
        frame['chain']['found'] = found_observed
        if not found_observed:
            frame['chain']['match_position'] = None
            frame['chain']['position_kind'] = 'aún no encontrado'
        frame['chain']['current_index'] = comparisons - 1 if comparisons else None

        frame['variables'] = {name: value['value'] for name, value in locals_.items()}
        frame['variables'].update({'tabla->capacidad': capacity, 'tabla->cantidad': count, 'retorno': return_status})
        frame['struct_fields'] = {'tabla': {'identity': '&tabla', 'capacidad': capacity, 'cantidad': count, 'buckets': array_id}}
        frame['pointers'] = {'actual': actual or 'NULL', 'nuevo': new or 'NULL',
            'bucket_head': f'bucket[{index}]' if index is not None else 'NULL', 'anterior': 'fuera de alcance'}
        frame['cost'].update({'comparisons': comparisons, 'nodes_visited': comparisons, 'hash_evaluations': hash_calls})
        frame['memory'].update({'objects_after': deepcopy(heap), 'allocated': deepcopy(allocated),
            'freed': deepcopy(freed), 'initialized_fields': [name for bit, name in [(1, 'clave'), (2, 'valor'), (4, 'siguiente')] if (node(new) or {}).get('initialized_mask', 0) & bit],
            'allocation_attempted': token in {'bucket_allocate', 'node_allocate'},
            'allocation_failed': token == 'node_allocate' and new is None,
            'bucket_initialization': list(cells), 'heap': deepcopy(heap),
            'null_checked': token in {'bucket_allocation_guard', 'node_null_guard'},
            'bucket_array_is_null': array_id is None,
            'links_changed': token in {'node_next_write', 'head_publish', 'bucket_null_write'},
            'call_stack': list(stack), 'variables': deepcopy(locals_),
            'scopes': deepcopy(debug['scopes']), 'struct_fields': deepcopy(frame['struct_fields'])})
        pending_count = token == 'head_publish'
        frame['invariant'].update({'name': 'Seguridad de memoria y consistencia del estado C intermedio',
            'count_consistent': frame['invariant']['holds'], 'count_update_pending': pending_count,
            'holds': frame['invariant']['holds'] or pending_count,
            'evidence': f'cantidad={count}; nodos publicados={sum(len(b["entries"]) for b in state.get("buckets", []))}; incremento pendiente={pending_count}'})
        frame['narration']['advanced'] = f'{function}: {token}; variables tipadas y campos inicializados en memoria.'
        step['pedagogy'] = frame
        frames.append(step)

    simulated_failure = payload.get('simulate_allocation_failure') in (True, 'true', '1', 1)
    # Public input validation is not a C kernel call or a malloc failure.
    if not success and not (operation == 'insert' and simulated_failure and 'malloc simulado' in message.lower()):
        emit('input_rejected', None, 'public_validation')
        frames[-1]['state_after'] = deepcopy(after_state)
        frames[-1]['pedagogy']['state_after'] = deepcopy(after_state)
    elif operation == 'create_table':
        # Caller owns existing storage; th_inicializar itself does not free it.
        freed = [n['id'] for n in heap] + ([array_id] if array_id else [])
        heap = []; array_id = None; cells = []; capacity = count = 0
        state['buckets'] = []
        emit('caller_recreate', None, 'caller')
        freed = []
        function = 'th_inicializar'; stack = [function]
        local('tabla', 'TablaHash *', '&tabla'); local('capacidad', 'int', int(payload['capacity']))
        emit('init_entry', 'void th_inicializar(', function)
        emit('init_guard', 'if (!tabla || capacidad <= 0)', function, False)
        capacity = int(payload['capacity']); emit('capacity_write', 'tabla->capacidad = capacidad;', function)
        count = 0; count_writes += 1; emit('size_zero', 'tabla->cantidad = 0;', function)
        array_id = 'bucket-array:replacement'; allocation_attempts += 1; allocation_count += 1; allocated = [array_id]; cells = [False] * capacity
        state['buckets'] = [{'index': j, 'entries': [], 'size': 0, 'collisions': 0, 'initialized': False} for j in range(capacity)]
        emit('bucket_allocate', 'tabla->buckets = (THNodo**)malloc', function); allocated = []
        emit('bucket_allocation_guard', 'if (tabla->buckets)', function, True)
        i = 0; local('i', 'int', i); emit('bucket_loop_init', 'for (int i = 0;', function)
        while True:
            emit('bucket_loop_test', 'for (int i = 0;', function, i < capacity)
            if i >= capacity: break
            cells[i] = True; link_writes += 1; state['buckets'][i]['initialized'] = True
            emit('bucket_null_write', 'tabla->buckets[i] = NULL;', function)
            i += 1; local('i', 'int', i); emit('bucket_loop_increment', 'for (int i = 0;', function)
        i = None; locals_.pop('i'); stack = []; locals_ = {}
        emit('init_return', 'void th_inicializar(', function)
    else:
        function = 'th_insertar'; stack = [function]
        key, value = int(payload['key']), int(payload['value'])
        local('tabla', 'TablaHash *', '&tabla');local('clave', 'int', key);local('valor', 'int', value)
        emit('insert_entry', 'bool th_insertar(', function)
        invalid = array_id is None or capacity <= 0
        emit('insert_guard', 'if (!tabla || !tabla->buckets', function, invalid)
        if invalid:
            return_status = False; stack = []; locals_ = {}
            emit('insert_return', 'if (!tabla || !tabla->buckets', function)
        else:
            local('indice', 'int', initialized=False)
            emit('index_call', 'int indice = th_indice', function)
            stack.append('th_indice')
            local('th_indice.tabla', 'const TablaHash *', '&tabla')
            local('th_indice.clave', 'int', key)
            hash_calls += 1; emit('index_entry', 'int th_indice(', 'th_indice')
            emit('index_guard', 'if (!tabla || tabla->capacidad <= 0)', 'th_indice', False)
            raw = abs(key) % capacity * (-1 if key < 0 else 1)
            index = raw; raw_observed = raw; normalized_observed = raw if raw >= 0 else None; local('th_indice.indice', 'int', raw)
            emit('raw_modulo', 'int indice = clave % tabla->capacidad;', 'th_indice')
            emit('negative_modulo_guard', 'if (indice < 0)', 'th_indice', raw < 0)
            if raw < 0:
                index += capacity; normalized_observed = index; local('th_indice.indice', 'int', index)
                emit('normalize_modulo', 'indice += tabla->capacidad;', 'th_indice')
            return_status = index;stack.pop()
            for scoped_name in ('th_indice.tabla', 'th_indice.clave', 'th_indice.indice'):
                locals_.pop(scoped_name)
            emit('index_return', 'return indice;', 'th_indice')
            local('indice', 'int', index); return_status = None
            emit('index_assign', 'int indice = th_indice', function)
            bucket = state['buckets'][index]
            actual = bucket['entries'][0]['address'] if bucket['entries'] else None
            local('actual', 'THNodo *', actual)
            emit('actual_init', 'THNodo *actual = tabla->buckets[indice];', function)
            found = False
            while True:
                emit('search_test', 'while (actual != NULL)', function, actual is not None)
                if actual is None: break
                current = node(actual); comparisons += 1
                found = current['key'] == key; found_observed = found
                emit('key_compare', 'if (actual->clave == clave)', function, found)
                if found:
                    current['value'] = value; value_writes += 1
                    for entry in bucket['entries']:
                        if entry['address'] == actual: entry['value'] = value
                    emit('update_value', 'actual->valor = valor;', function)
                    break
                actual = current['next'];local('actual', 'THNodo *', actual)
                emit('actual_advance', 'actual = actual->siguiente;', function)
            if not found:
                allocation_attempts += 1
                new = None if simulated_failure else f'0xHASH-{key}'
                local('nuevo', 'THNodo *', new)
                if new:
                    allocation_count += 1
                    heap.append({'id': new, 'kind': 'node', 'initialized_mask': 0, 'key': None, 'value': None, 'next': None})
                    allocated = [new]
                emit('node_allocate', 'THNodo *nuevo = (THNodo*)malloc', function); allocated = []
                emit('node_null_guard', 'if (!nuevo) return false;', function, new is None)
                if new:
                    obj = node(new);obj['key'] = key;obj['initialized_mask'] |= 1; key_writes += 1
                    emit('node_key_write', 'nuevo->clave = clave;', function)
                    obj['value'] = value;obj['initialized_mask'] |= 2; value_writes += 1
                    emit('node_value_write', 'nuevo->valor = valor;', function)
                    obj['next'] = bucket['entries'][0]['address'] if bucket['entries'] else None;obj['initialized_mask'] |= 4; link_writes += 1
                    emit('node_next_write', 'nuevo->siguiente = tabla->buckets[indice];', function)
                    link_writes += 1
                    bucket['entries'].insert(0, {'key': key, 'value': value, 'address': new, 'next': obj['next'], 'bucket': index})
                    emit('head_publish', 'tabla->buckets[indice] = nuevo;', function)
                    count += 1;count_writes += 1;emit('size_increment', 'tabla->cantidad++;', function)
            return_status = found or new is not None
            stack = [];locals_ = {};actual = new = index = None
            emit('insert_return', ('return true;' if found else '@last:return true;') if return_status else 'if (!nuevo) return false;', function)
    # Feedback is attached only at operation return, after all C writes.
    frames[-1]['state_after'] = deepcopy(after_state)
    frames[-1]['pedagogy']['state_after'] = deepcopy(after_state)
    frames[0]['phase'] = 'start';frames[-1]['phase'] = 'end'
    return {'structure_id': 'hash_table', 'operation_name': operation, 'payload': deepcopy(payload),
        'success': success, 'mutates': success, 'message': message, 'source_code': source_code,
        'code_title': code_title, 'steps': frames, 'final_state': deepcopy(after_state),
        'pedagogy_schema_version': 1, 'pedagogy_schema': hash_frame_schema(),
        'learning_profile': deepcopy(HASH_LEARNING_CATALOG), 'instruction_scope': 'th_inicializar/th_insertar/th_indice'}
