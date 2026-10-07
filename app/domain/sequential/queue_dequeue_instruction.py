"""Causal cola_desencolar scopes, stable identities and actual free/return."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.domain.sequential.pedagogy import (build_sequential_frame, validate_sequential_frame, sequential_frame_schema, SEQUENTIAL_FRAME_SCHEMA_VERSION, SEQUENTIAL_LEARNING_CATALOG)


def build_queue_dequeue_trace(*, payload: dict[str, Any], source_code: str, code_title: str,
        before_state: dict[str, Any], after_state: dict[str, Any], success: bool,
        message: str, null_root: bool = False) -> dict[str, Any]:
    """Observe seeded valid nodes only; never read an object after its free."""
    lines=source_code.replace('\r\n','\n').split('\n')
    values=[] if null_root else [int(i['value']) for i in before_state.get('items',[])]
    heap=[{'id':f'N{i+1}','address':f'N{i+1}','type':'struct NodoCola','alive':True,
        'allocated':True,'freed':False,'fields_valid':True,'initialized_mask':3,
        'field_validity':{'nro':True,'sgte':True},'status':'linked',
        'fields':{'nro':v,'sgte':f'N{i+2}' if i+1<len(values) else None}} for i,v in enumerate(values)]
    objects={h['id']:h for h in heap}
    head=heap[0]['id'] if heap else None;rear=heap[-1]['id'] if heap else None
    aux=None;num=None;result=None;active=True;free_active=False;steps=[];console=[]
    def state() -> dict[str, Any]:
        current=deepcopy(before_state);items=[];ptr=head
        while ptr is not None:
            node=objects[ptr];assert node['alive']
            items.append({'value':node['fields']['nro']});ptr=node['fields']['sgte']
        current.update(items=items,size=len(items),empty=not items,delante=head or 'NULL',atras=rear or 'NULL')
        return current
    def emit(event: str, token: str, condition: bool | None=None, freed: list[dict[str, Any]] | None=None) -> None:
        index=next(i for i,l in enumerate(lines) if token in l)
        scope_state='active' if active else 'ended';variables=[];pointers=[]
        if not null_root:
            for name,target in [('delante',head),('atras',rear)]:
                variables.append({'name':name,'type':'struct NodoCola *','value':target,'initialized':True,'valid':True,'scope':'caller','scope_state':'active','meaning':'Campo del objeto struct Cola prestado y vivo.'})
                pointers.append({'name':name,'type':'struct NodoCola *','target':target,'initialized':True,'valid':True,'scope':'caller','scope_state':'active','alias':'aux' if aux and aux['valid'] and aux['value']==target else None})
        local=[{'name':'q','type':'struct Cola *','value':None if null_root else '&cola','initialized':True,'valid':active,'scope':'cola_desencolar','scope_state':scope_state,'meaning':'Dirección prestada; snapshot del parámetro si terminó su scope.'}]
        if active:pointers.append({'name':'q','type':'struct Cola *','target':None if null_root else '&cola','initialized':True,'valid':True,'scope':'cola_desencolar','scope_state':scope_state,'alias':'caller' if not null_root else None})
        if aux is not None:
            local.append({'name':'aux','type':'struct NodoCola *','value':aux['value'],'initialized':True,'valid':active and aux['valid'],'dangling':not aux['valid'],'scope':'cola_desencolar','scope_state':scope_state,'meaning':'ID guardado antes de free; después sólo registro histórico inutilizable, no lectura del puntero C.'})
            if active:pointers.append({'name':'aux','type':'struct NodoCola *','target':aux['value'],'initialized':True,'valid':aux['valid'],'dangling':not aux['valid'],'scope':'cola_desencolar','scope_state':scope_state,'alias':'delante/atras' if aux['valid'] and aux['value'] in (head,rear) else 'nodo separado vivo' if aux['valid'] else 'nodo liberado; no usar'})
        if num is not None:local.append({'name':'num','type':'int','value':num,'initialized':True,'valid':active,'scope':'cola_desencolar','scope_state':scope_state,'meaning':'Copia escalar independiente del nodo; snapshot al retornar.'})
        variables.extend(local)
        previous_vars={x['name']:x for x in steps[-1]['debug']['variables']} if steps else {}
        previous_ptrs={x['name']:x for x in steps[-1]['debug']['pointers']} if steps else {}
        for v in variables:
            old=previous_vars.get(v['name']);v['previous']=old.get('value') if old else None;v['changed']=bool(old and (old.get('value'),old.get('valid'),old.get('scope_state'))!=(v['value'],v['valid'],v['scope_state']))
        for p in pointers:
            old=previous_ptrs.get(p['name']);p['previous_target']=old.get('target') if old else None;p['changed']=bool(old and old.get('target')!=p['target'])
        root={'type':'struct Cola','identity':'&cola','front':head,'rear':rear,'alive':not null_root,'valid':not null_root,'initialized':not null_root}
        scopes=[{'id':'cola_desencolar','kind':'function','state':scope_state,'scope_state':scope_state,'variables':deepcopy(local)}]
        calls=[{'function':'cola_desencolar','parameters':{'q':None if null_root else '&cola'},'return_type':'int','return':None,'continuation':'Caller recibe copia int; conserva struct Cola y nodos restantes.'}] if active else []
        if free_active:calls.append({'function':'free','parameters':{'ptr':aux['value']},'return_type':'void','return':None,'opaque':True,'continuation':'cola_desencolar devuelve num copiado.'})
        debug={'token':event,'function':'free' if free_active else 'cola_desencolar','root':deepcopy(root),'aux':deepcopy(aux),'num':{'initialized':num is not None,'value':num,'type':'int','scope_state':scope_state},'result':result,'heap':deepcopy(heap),'variables':deepcopy(variables),'pointers':deepcopy(pointers),'scopes':deepcopy(scopes),'call_stack':deepcopy(calls),'condition_result':condition}
        memory_snapshot=state()
        # Retain physical roots in memory while returning the C-derived logical queue.
        current=memory_snapshot if active else {key:value for key,value in memory_snapshot.items()
            if key not in {'delante','atras'}}
        previous=deepcopy(steps[-1]['state_after'] if steps else before_state)
        step={'step_index':len(steps),'line_index':index,'line_text':lines[index],'event_type':event,'phase':'progress','delay_ms':100,'state_snapshot':previous,'state_after':current,'console':deepcopy(console),'condition_result':condition,'function_name':debug['function'],'debug':debug}
        f=build_sequential_frame(structure_id='queue',operation_name='desencolar',payload=payload,step=step,success=success)
        f.update(variables=variables,pointers=pointers,heap_objects=deepcopy(heap),heap_transition={'kind':'free' if freed else 'unlink' if event=='front_assigned' else 'stable','before':deepcopy(steps[-1]['pedagogy']['heap_objects'] if steps else heap),'after':deepcopy(heap),'freed':deepcopy(freed or []),'dangling_references':[]},scopes=scopes,call_stack=calls,memory_state=deepcopy(memory_snapshot),dequeue_memory={'kind':'queue_dequeue','guard':event in ('root_guard','error_printf','return_error'),'root':deepcopy(root),'heap':deepcopy(heap),'aux':deepcopy(aux),'num':deepcopy(debug['num']),'result':result,'scope_state':scope_state,'invalid_aliases':[{'name':'aux','historical_id':aux['value'],'usable':False}] if aux and not aux['valid'] else [],'variables':deepcopy(variables),'call_stack':deepcopy(calls)},condition=None if condition is None else {'source':lines[index],'substituted':('NULL == NULL || cortocircuito' if null_root else '&cola == NULL || '+(head or 'NULL')+' == NULL') if event=='root_guard' else (head or 'NULL')+' == NULL','result':condition,'consequence':'Rama C ejecutada.'})
        f['source']['function']=debug['function'];f['invariant']={'text':'aux conserva la identidad del nodo; num se copia antes de liberarlo.','holds':True,'symbol':'✓','evidence':'Raíces por stores reales; heap separado vivo hasta free; sin lectura posterior del nodo.'}
        narration={'entry':'Entra cola_desencolar con dirección prestada q; aux y num todavía no están declarados.','root_guard':'Evalúa NULL con cortocircuito y la condición real de vacío.','error_printf':'C imprime el diagnóstico de cola vacía antes de retornar -1.','aux_assigned':'Declara aux y copia el puntero delante al mismo nodo vivo.','num_assigned':'Declara num int y copia nro mientras el nodo vive.','front_assigned':'Reasigna delante al siguiente; aux conserva identidad y el nodo separado sigue vivo.','last_guard':'Comprueba si delante quedó NULL después de la extracción.','rear_cleared':'Escribe NULL en atras sólo cuando se retiró el último nodo.','free_enter':'Comienza free opaco del mismo objeto identificado por aux.','free_return':'Termina free; el nodo desaparece del heap vivo y sus aliases quedan inutilizables.','return_num':'Retorna la copia num y termina el scope; caller y raíces restantes siguen vivos.','return_error':'Retorna -1 después del printf y termina el scope, sin tocar enlaces.'}[event]
        for level in f['narration']:f['narration'][level]=narration
        if event.startswith('return_'):f['concept']='return';f['phase']={'id':'desencolar-return','label':'Retorno int; scope terminado','goal':'Copia escalar al caller, sin leer el nodo.'}
        validate_sequential_frame(f,source_code=source_code);step['pedagogy']=f;steps.append(step)
    emit('entry','int cola_desencolar(');empty=null_root or head is None;emit('root_guard','if (q == NULL',empty)
    if empty:
        console.append('Cola vacía. No se puede desencolar.');emit('error_printf','printf(');result=-1;active=False;emit('return_error','return -1;')
    else:
        aux={'type':'struct NodoCola *','initialized':True,'valid':True,'value':head};emit('aux_assigned','struct NodoCola *aux =')
        num=objects[head]['fields']['nro'];emit('num_assigned','int num =')
        head=objects[head]['fields']['sgte'];objects[aux['value']]['status']='detached';emit('front_assigned','q->delante = aux->sgte;')
        emit('last_guard','if (q->delante == NULL)',head is None)
        if head is None:rear=None;emit('rear_cleared','q->atras = NULL;')
        free_active=True;emit('free_enter','free(aux);');free_active=False
        freed_node=objects[aux['value']]
        # Capture safe history before invalidating the live object.
        freed_record={'id':freed_node['id'],'address':freed_node['address'],'type':freed_node['type'],'freed':True,'alive':False,'historical_fields':deepcopy(freed_node['fields'])}
        objects.pop(aux['value']);heap.remove(freed_node)
        aux['valid']=False;emit('free_return','free(aux);',freed=[freed_record]);result=num;active=False;emit('return_num','return num;')
    steps[0]['phase']='start';steps[-1]['phase']='end'
    return {'structure_id':'queue','operation_name':'desencolar','payload':deepcopy(payload),'success':success,'message':message,'mutates':True,'code_title':code_title,'source_code':source_code,'steps':steps,'final_state':deepcopy(after_state),'pedagogy_schema_version':SEQUENTIAL_FRAME_SCHEMA_VERSION,'pedagogy_schema':sequential_frame_schema(),'learning_profile':deepcopy(SEQUENTIAL_LEARNING_CATALOG['queue']),'instruction_scope':'cola_desencolar guard, typed scopes, stable root/node identities, copied int, opaque free and actual printf/return'}
