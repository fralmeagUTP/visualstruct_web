"""Causal cola_encolar allocation, FIFO stores and typed caller/local scopes."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.domain.sequential.pedagogy import (build_sequential_frame,validate_sequential_frame,sequential_frame_schema,SEQUENTIAL_FRAME_SCHEMA_VERSION,SEQUENTIAL_LEARNING_CATALOG)


def build_queue_enqueue_trace(*,payload:dict[str,Any],source_code:str,code_title:str,
        before_state:dict[str,Any],after_state:dict[str,Any],success:bool,message:str,
        null_root:bool=False,allocation_failure:bool=False)->dict[str,Any]:
    """Model malloc as an opaque call; never read a field before its own store."""
    lines=source_code.replace('\r\n','\n').split('\n');value=int(payload.get('value',0))
    values=[] if null_root else [int(i['value']) for i in before_state.get('items',[])]
    heap=[{'id':f'N{i+1}','address':f'N{i+1}','type':'struct NodoCola',
        'alive':True,'allocated':True,'freed':False,'fields_valid':True,'initialized_mask':3,
        'field_validity':{'nro':True,'sgte':True},'status':'linked',
        'fields':{'nro':v,'sgte':f'N{i+2}' if i+1<len(values) else None}}
        for i,v in enumerate(values)]
    objects={h['id']:h for h in heap};head=heap[0]['id'] if heap else None;rear=heap[-1]['id'] if heap else None
    active=True;aux=None;allocator_active=False;steps=[];console=[]
    malloc_line='struct NodoCola *aux = (struct NodoCola *) malloc(sizeof(struct NodoCola));'
    def state():
        result=deepcopy(before_state);items=[];ptr=head
        while ptr is not None:
            h=objects[ptr];assert h['alive'] and h['initialized_mask']==3
            items.append({'value':h['fields']['nro']});ptr=h['fields']['sgte']
        result.update(items=items,size=len(items),empty=not items,delante=head or "NULL",atras=rear or "NULL");return result
    def emit(event,token,condition=None):
        indexes=[i for i,l in enumerate(lines) if token in l] if token!='@end' else [len(lines)-1]
        index=indexes[-1] if event=='return' and allocation_failure and not null_root else indexes[0]
        variables=[];pointers=[]
        if not null_root:
            for name,target in [('delante',head),('atras',rear)]:
                variables.append({'name':name,'type':'struct NodoCola *','value':target,'initialized':True,'valid':True,'scope':'caller','scope_state':'active','meaning':'Campo vivo de struct Cola propiedad del llamador.'})
                pointers.append({'name':name,'type':'struct NodoCola *','target':target,'initialized':True,'valid':True,'scope':'caller','scope_state':'active','alias':None})
        if active:
            variables.extend([{'name':'q','type':'struct Cola *','value':None if null_root else '&cola','initialized':True,'valid':True,'scope':'cola_encolar','scope_state':'active','meaning':'Dirección prestada del objeto caller, distinta de sus campos.'},
                {'name':'valor','type':'int','value':value,'initialized':True,'valid':True,'scope':'cola_encolar','scope_state':'active','meaning':'Parámetro escalar C de esta llamada.'}])
            pointers.append({'name':'q','type':'struct Cola *','target':None if null_root else '&cola','initialized':True,'valid':True,'scope':'cola_encolar','scope_state':'active','alias':'objeto caller' if not null_root else None})
            if aux is not None:
                variables.append({'name':'aux','type':'struct NodoCola *','value':aux['value'],'initialized':aux['initialized'],'valid':aux['valid'],'scope':'cola_encolar','scope_state':'active','meaning':'Alias al nodo reservado, conservado hasta retornar.'})
                pointers.append({'name':'aux','type':'struct NodoCola *','target':aux['value'],'initialized':aux['initialized'],'valid':aux['valid'],'scope':'cola_encolar','scope_state':'active','alias':'delante/atras' if aux['valid'] and aux['value'] is not None and aux['value'] in (head,rear) else None})
        previous_vars={v['name']:v for v in steps[-1]['debug']['variables']} if steps else {}
        previous_ptrs={v['name']:v for v in steps[-1]['debug']['pointers']} if steps else {}
        for v in variables:
            old=previous_vars.get(v['name']);v['previous']=old['value'] if old and old['initialized'] else None;v['changed']=bool(old and (old['value'],old['initialized'])!=(v['value'],v['initialized']))
        for ptr in pointers:
            old=previous_ptrs.get(ptr['name']);ptr['previous_target']=old['target'] if old and old['initialized'] else None;ptr['changed']=bool(old and (old['target'],old['initialized'])!=(ptr['target'],ptr['initialized']))
        root={'type':'struct Cola','identity':'&cola','front':head,'rear':rear,'value':head,'alive':not null_root,'valid':not null_root,'initialized':not null_root}
        scopes=[{'id':'cola_encolar','kind':'function','variables':deepcopy([v for v in variables if v['scope']=='cola_encolar'])}] if active else []
        calls=[{'function':'cola_encolar','parameters':{'q':None if null_root else '&cola','valor':value},'return':None,'continuation':'caller; root y heap propios siguen vivos'}] if active else []
        if allocator_active:calls.append({'function':'malloc','parameters':{'size':'sizeof(struct NodoCola)'},'return':None,'continuation':'inicializador de aux','opaque':True})
        debug={'token':event,'function':'malloc' if allocator_active else 'cola_encolar','root':root,'aux':deepcopy(aux) if active else None,'heap':deepcopy(heap),'variables':deepcopy(variables),'pointers':deepcopy(pointers),'scopes':scopes,'call_stack':deepcopy(calls),'condition_result':condition}
        current=state();previous=deepcopy(steps[-1]['state_after'] if steps else before_state)
        step={'step_index':len(steps),'line_index':index,'line_text':lines[index],'event_type':event,'phase':'progress','delay_ms':100,'state_snapshot':previous,'state_after':current,'console':deepcopy(console),'condition_result':condition,'function_name':debug['function'],'debug':debug}
        f=build_sequential_frame(structure_id='queue',operation_name='encolar',payload=payload,step=step,success=success)
        f.update(variables=variables,pointers=pointers,heap_objects=deepcopy(heap),heap_transition={'kind':'allocate' if event=='allocator_success_return' else 'link' if event in ('front_assigned','rear_next_assigned','rear_assigned') else 'stable','before':deepcopy(steps[-1]['pedagogy']['heap_objects'] if steps else heap),'after':deepcopy(heap),'freed':[],'dangling_references':[]},scopes=scopes,call_stack=calls,memory_state=None,enqueue_memory={'kind':'queue_enqueue','root':deepcopy(root),'heap':deepcopy(heap),'aux':deepcopy(aux) if active else None,'variables':deepcopy(variables),'call_stack':deepcopy(calls)},condition=None if condition is None else {'source':lines[index],'substituted':('&cola == NULL' if event=='root_guard' and not null_root else 'NULL == NULL' if event=='root_guard' else (str(head) if head is not None else 'NULL')+' == NULL' if event=='empty_guard' else (str(aux['value']) if aux and aux['value'] is not None else 'NULL')+' == NULL'),'result':condition,'consequence':'Rama C ejecutada.'})
        f['source']['function']=debug['function'];f['invariant']={'text':'La raíz alcanza sólo nodos con ambos campos inicializados; el temporal vive sin publicarse.','holds':True,'symbol':'✓','evidence':'Máscaras0→1→3; aux conserva identidad y alias tras publicar hasta retornar.'}
        narrations={'entry':'Entra cola_encolar: q recibe la dirección del objeto caller y valor el entero.', 'root_guard':'Comprueba la dirección q; una cola vacía no convierte q en NULL.', 'allocator_enter':'Comienza malloc opaco; aux todavía no recibió su resultado.', 'allocator_success_return':'malloc retorna un objeto vivo con campos sin inicializar y máscara0.', 'allocator_NULL_return':'malloc retorna NULL; no se crea ningún objeto.', 'aux_allocated':'Termina el inicializador de aux; su puntero queda determinado, vivo o NULL.', 'allocation_guard':'Comprueba aux antes de acceder a cualquier campo.', 'value_assigned':'Escribe sólo nro; sgte sigue sin inicializar (máscara1).', 'link_assigned':'Escribe sgte con NULL; ambos campos válidos (máscara3).', 'empty_guard':'Comprueba delante; elige sólo la rama vacía o no vacía.', 'front_assigned':'Publica el mismo nodo en delante; atras aún conserva el valor anterior.', 'rear_next_assigned':'Enlaza el nodo desde el anterior atras; aún no reasigna atras.', 'rear_assigned':'Reasigna atras al mismo nodo vivo; aux conserva su alias hasta retornar.', 'root_error_printf':'Imprime el diagnóstico: q es NULL, no hubo reserva.', 'allocation_error_printf':'Imprime el diagnóstico de reserva fallida; la raíz se conserva.', 'return':'Retorno void: termina sólo el scope local; caller y nodos propios siguen vivos.'}
        for level in f['narration']:f['narration'][level]=narrations[event]
        if event=='return':f['concept']='return';f['phase']={'id':'encolar-return','label':'Retorno void; scope terminado','goal':'Caller y heap conservan propiedad.'}
        validate_sequential_frame(f,source_code=source_code);step['pedagogy']=f;steps.append(step)
    emit('entry','void cola_encolar(');emit('root_guard','if (q == NULL)',null_root)
    if null_root:
        console.append('Error: cola no inicializada.');emit('root_error_printf','printf("Error: cola no inicializada.')
    else:
        aux={'type':'struct NodoCola *','initialized':False,'valid':False,'value':None};allocator_active=True;emit('allocator_enter',malloc_line);allocator_active=False
        if allocation_failure:emit('allocator_NULL_return',malloc_line);identity=None
        else:
            identity=f'N{len(values)+1}';node={'id':identity,'address':identity,'type':'struct NodoCola','alive':True,'allocated':True,'freed':False,'fields_valid':False,'initialized_mask':0,'field_validity':{'nro':False,'sgte':False},'status':'temporary','fields':{'nro':None,'sgte':None}};heap.append(node);objects[identity]=node;emit('allocator_success_return',malloc_line)
        aux={'type':'struct NodoCola *','initialized':True,'valid':True,'value':identity};emit('aux_allocated',malloc_line);emit('allocation_guard','if (aux == NULL)',allocation_failure)
        if allocation_failure:
            console.append('Error: no se pudo asignar memoria.');emit('allocation_error_printf','printf("Error: no se pudo asignar memoria.')
        else:
            node['fields']['nro']=value;node['initialized_mask']=1;node['field_validity']['nro']=True;emit('value_assigned','aux->nro = valor;')
            node['fields']['sgte']=None;node['initialized_mask']=3;node['field_validity']['sgte']=True;node['fields_valid']=True;emit('link_assigned','aux->sgte = NULL;')
            emit('empty_guard','if (q->delante == NULL)',head is None)
            if head is None:
                head=identity;node['status']='linked';emit('front_assigned','q->delante = aux;')
            else:
                objects[rear]['fields']['sgte']=identity;node['status']='linked';emit('rear_next_assigned','q->atras->sgte = aux;')
            rear=identity;emit('rear_assigned','q->atras = aux;')
    active=False;emit('return','return;' if null_root or allocation_failure else '@end')
    steps[0]['phase']='start';steps[-1]['phase']='end';steps[-1]['state_after']=deepcopy(after_state)
    return {'structure_id':'queue','operation_name':'encolar','payload':deepcopy(payload),'success':success,'message':message,'mutates':True,'code_title':code_title,'source_code':source_code,'steps':steps,'final_state':deepcopy(after_state),'pedagogy_schema_version':SEQUENTIAL_FRAME_SCHEMA_VERSION,'pedagogy_schema':sequential_frame_schema(),'learning_profile':deepcopy(SEQUENTIAL_LEARNING_CATALOG['queue']),'instruction_scope':'cola_encolar caller/locals opaque malloc fields masks aliases and void return'}
