"""Causal pila_destruir lifecycle; retired pointer storage is never followed."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.domain.sequential.pedagogy import (
    build_sequential_frame, validate_sequential_frame, sequential_frame_schema,
    SEQUENTIAL_FRAME_SCHEMA_VERSION, SEQUENTIAL_LEARNING_CATALOG,
)


def build_stack_cleanup_trace(*, payload: dict[str, Any], source_code: str,
        code_title: str, before_state: dict[str, Any], after_state: dict[str, Any],
        success: bool, message: str, null_root: bool = False) -> dict[str, Any]:
    """Model the existing mutable root, function local aux and each real C store."""
    lines = source_code.replace('\r\n', '\n').split('\n')
    original = [int(item['value']) for item in before_state.get('items', [])]
    heap = [{'id':f'stack-node-{i}', 'address':f'stack-node-{i}', 'type':'struct NodoPila',
        'alive':True, 'allocated':True, 'freed':False, 'fields_valid':True,
        'initialized_mask':3, 'status':'linked', 'fields':{'nro':value,
        'sgte':f'stack-node-{i+1}' if i+1 < len(original) else None}}
        for i,value in enumerate(original)]
    objects = {h['id']:h for h in heap}
    head = heap[0]['id'] if heap else None
    active = True
    aux: dict[str, Any] | None = None
    steps: list[dict[str, Any]] = []
    frees = 0

    def state() -> dict[str, Any]:
        result = deepcopy(before_state)
        pointer = head
        values = []
        while pointer is not None:
            node = objects[pointer]
            assert node['alive'] and node['fields_valid']
            values.append({'value':node['fields']['nro']})
            pointer = node['fields']['sgte']
        result.update(items=values, size=len(values), empty=not values)
        return result

    def emit(event: str, token: str, condition: bool | None = None) -> None:
        index = len(lines)-1 if token == '@end' else next(i for i,line in enumerate(lines) if token in line)
        current = state()
        previous = deepcopy(steps[-1]['state_after'] if steps else before_state)
        variables = []
        pointers = []
        if active:
            variables.append({'name':'p', 'type':'ptrPila *', 'value':None if null_root else '&pila',
                'initialized':True, 'valid':True, 'scope':'pila_destruir', 'scope_state':'active',
                'previous':None, 'changed':False, 'meaning':'Dirección prestada del slot cabeza del llamador.'})
            pointers.append({'name':'p', 'type':'ptrPila *', 'target':None if null_root else '&pila',
                'alias':None if null_root else 'slot cabeza del llamador', 'valid':True,
                'previous_target':None, 'changed':False, 'scope':'pila_destruir', 'scope_state':'active'})
            if aux is not None:
                variables.append({'name':'aux', 'type':'ptrPila', 'value':aux['value'],
                    'initialized':aux['initialized'], 'valid':aux['valid'], 'scope':'pila_destruir',
                    'scope_state':'active', 'previous':None, 'changed':event in {'aux_assigned','node_free'},
                    'meaning':'Nodo prestado; indeterminado antes de asignación y después de free.'})
                pointers.append({'name':'aux', 'type':'ptrPila', 'target':aux['value'],
                    'initialized':aux['initialized'], 'valid':aux['valid'],
                    'status':'live' if aux['valid'] else 'indeterminate',
                    'historical_identity':aux.get('historical_identity'), 'alias':None,
                    'previous_target':None, 'changed':event in {'aux_assigned','node_free'},
                    'scope':'pila_destruir', 'scope_state':'active'})
        debug = {'token':event, 'function':'pila_destruir', 'root':{'type':'ptrPila', 'identity':'&pila',
            'alive':not null_root, 'initialized':True, 'valid':True, 'value':head},
            'variables':deepcopy(variables), 'aux':deepcopy(aux) if active else None,
            'heap':deepcopy(heap), 'frees':frees, 'condition_result':condition,
            'call_stack':['pila_destruir'] if active else [],
            'scopes':[{'id':'pila_destruir','kind':'function','variables':deepcopy(variables)}] if active else [],
            'identity_policy':'operation-local symbols; historical IDs are not usable pointer values'}
        step = {'step_index':len(steps), 'line_index':index, 'line_text':lines[index],
            'event_type':event, 'phase':'progress', 'delay_ms':100,
            'state_snapshot':previous, 'state_after':current, 'console':[],
            'condition_result':condition, 'function_name':'pila_destruir', 'debug':debug}
        frame = build_sequential_frame(structure_id='stack', operation_name='limpiar',
            payload=payload, step=step, success=success)
        live = deepcopy([h for h in heap if h['alive']])
        retired = deepcopy([h for h in heap if not h['alive']])
        frame.update(variables=variables, pointers=pointers, heap_objects=live,
            heap_transition={'kind':'free' if event=='node_free' else 'link' if event=='root_assigned' else 'stable',
                'before':deepcopy(steps[-1]['pedagogy']['heap_objects'] if steps else heap),
                'after':live, 'freed':retired, 'dangling_references':[]},
            call_stack=[{'function':'pila_destruir','parameters':{'p':None if null_root else '&pila'},
                'return':None,'continuation':'llamador; root prestado'}] if active else [],
            scopes=deepcopy(debug['scopes']), memory_state=None,
            cleanup_memory={'root':deepcopy(debug['root']), 'heap':deepcopy(heap),
                'variables':deepcopy(variables), 'aux':deepcopy(aux) if active else None,
                'call_stack':deepcopy(debug['call_stack']), 'frees':frees},
            condition=None if condition is None else {'source':lines[index], 'substituted':str(condition),
                'result':condition,'consequence':'Rama C ejecutada.'})
        frame['invariant'] = {'text':'Cabeza alcanza sólo nodos vivos; aux desconectado vive hasta free.',
            'holds':True, 'symbol':'✓','evidence':'Recorrido root sólo por heap vivo; pointer aux indeterminado no se inspecciona.'}
        frame['source']['function'] = 'pila_destruir'
        if event == 'return':
            frame['concept']='return'
            frame['phase']={'id':'limpiar-return','label':'Retorno void; ámbito terminado','goal':'Cierra el scope; root del llamador sigue vivo.'}
        for level in frame['narration']:
            frame['narration'][level] = ('pila_destruir: '+event+'. *p cambia antes de free; aux retirado queda indeterminado, no NULL. '
                'La copia histórica se conserva separada y no se usa como puntero.')
        validate_sequential_frame(frame, source_code=source_code)
        step['pedagogy']=frame
        steps.append(step)

    emit('entry','void pila_destruir(')
    aux={'type':'ptrPila','initialized':False,'valid':False,'value':None,'reason':'declared uninitialized'}
    emit('aux_declared','ptrPila aux;')
    emit('root_guard','if (p == NULL)',null_root)
    if not null_root:
        while True:
            emit('while_guard','while (*p != NULL)',head is not None)
            if head is None:
                break
            node=objects[head]
            assert node['alive'] and node['fields_valid']
            aux={'type':'ptrPila','initialized':True,'valid':True,'value':head}
            emit('aux_assigned','aux = *p;')
            head=node['fields']['sgte']
            node['status']='detached'
            emit('root_assigned','*p = aux->sgte;')
            identity=aux['value']
            node.update(alive=False, allocated=False, freed=True, fields_valid=False,
                initialized_mask=0, status='freed', historical_fields=deepcopy(node['fields']),
                historical_initialized_mask=3, fields={'nro':None,'sgte':None})
            aux={'type':'ptrPila','initialized':False,'valid':False,'value':None,
                'historical_identity':identity,'reason':'indeterminate after free'}
            frees+=1
            emit('node_free','free(aux);')
    active=False
    emit('return','return;' if null_root else '@end')
    steps[0]['phase']='start'
    steps[-1]['phase']='end'
    steps[-1]['state_after']=deepcopy(after_state)
    return {'structure_id':'stack','operation_name':'limpiar','payload':deepcopy(payload),
        'success':success,'message':message,'mutates':True,'code_title':code_title,
        'source_code':source_code,'steps':steps,'final_state':deepcopy(after_state),
        'pedagogy_schema_version':SEQUENTIAL_FRAME_SCHEMA_VERSION,'pedagogy_schema':sequential_frame_schema(),
        'learning_profile':deepcopy(SEQUENTIAL_LEARNING_CATALOG['stack']),
        'instruction_scope':'pila_destruir mutable root/aux function scope/lifetime, safe historical snapshots'}
