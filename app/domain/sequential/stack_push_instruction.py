"""Causal pila_apilar allocation and stores with typed caller/local scopes."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.domain.sequential.pedagogy import (build_sequential_frame,validate_sequential_frame,sequential_frame_schema,SEQUENTIAL_FRAME_SCHEMA_VERSION,SEQUENTIAL_LEARNING_CATALOG)


def build_stack_push_trace(*,payload:dict[str,Any],source_code:str,code_title:str,
        before_state:dict[str,Any],after_state:dict[str,Any],success:bool,message:str,
        null_root:bool=False,allocation_failure:bool=False)->dict[str,Any]:
    """Model malloc as an opaque call; never read a field before its own store."""
    lines=source_code.replace('\r\n','\n').split('\n');value=int(payload.get('value',0))
    values=[] if null_root else [int(i['value']) for i in before_state.get('items',[])]
    heap=[{'id':f'push-existing-{i}','address':f'push-existing-{i}','type':'struct NodoPila',
        'alive':True,'allocated':True,'freed':False,'fields_valid':True,'initialized_mask':3,
        'field_validity':{'nro':True,'sgte':True},'status':'linked',
        'fields':{'nro':v,'sgte':f'push-existing-{i+1}' if i+1<len(values) else None}}
        for i,v in enumerate(values)]
    objects={h['id']:h for h in heap};head=heap[0]['id'] if heap else None
    active=True;aux=None;allocator_active=False;steps=[];console=[]
    malloc_line='ptrPila aux = (ptrPila) malloc(sizeof(struct NodoPila));'
    def state():
        result=deepcopy(before_state);items=[];ptr=head
        while ptr is not None:
            h=objects[ptr];assert h['alive'] and h['initialized_mask']==3
            items.append({'value':h['fields']['nro']});ptr=h['fields']['sgte']
        result.update(items=items,size=len(items),empty=not items);return result
    def emit(event,token,condition=None):
        indexes=[i for i,l in enumerate(lines) if token in l] if token!='@end' else [len(lines)-1]
        index=indexes[-1] if event=='return' and allocation_failure and not null_root else indexes[0]
        variables=[];pointers=[]
        if not null_root:
            variables.append({'name':'pila','type':'ptrPila','value':head,'initialized':True,'valid':True,'scope':'caller','scope_state':'active','meaning':'Slot cabeza propiedad del llamador.'})
            pointers.append({'name':'pila','type':'ptrPila','target':head,'initialized':True,'valid':True,'scope':'caller','scope_state':'active','alias':None})
        if active:
            variables.extend([{'name':'p','type':'ptrPila *','value':None if null_root else '&pila','initialized':True,'valid':True,'scope':'pila_apilar','scope_state':'active','meaning':'Dirección prestada del slot caller, distinta de *p.'},
                {'name':'valor','type':'int','value':value,'initialized':True,'valid':True,'scope':'pila_apilar','scope_state':'active','meaning':'Parámetro escalar C de esta llamada.'}])
            pointers.append({'name':'p','type':'ptrPila *','target':None if null_root else '&pila','initialized':True,'valid':True,'scope':'pila_apilar','scope_state':'active','alias':'slot caller' if not null_root else None})
            if aux is not None:
                variables.append({'name':'aux','type':'ptrPila','value':aux['value'],'initialized':aux['initialized'],'valid':aux['valid'],'scope':'pila_apilar','scope_state':'active','meaning':'Alias al nodo reservado, conservado hasta retornar.'})
                pointers.append({'name':'aux','type':'ptrPila','target':aux['value'],'initialized':aux['initialized'],'valid':aux['valid'],'scope':'pila_apilar','scope_state':'active','alias':'pila / *p' if aux['valid'] and aux['value'] is not None and aux['value']==head else None})
        previous_vars={v['name']:v for v in steps[-1]['debug']['variables']} if steps else {}
        previous_ptrs={v['name']:v for v in steps[-1]['debug']['pointers']} if steps else {}
        for v in variables:
            old=previous_vars.get(v['name']);v['previous']=old['value'] if old and old['initialized'] else None;v['changed']=bool(old and (old['value'],old['initialized'])!=(v['value'],v['initialized']))
        for ptr in pointers:
            old=previous_ptrs.get(ptr['name']);ptr['previous_target']=old['target'] if old and old['initialized'] else None;ptr['changed']=bool(old and (old['target'],old['initialized'])!=(ptr['target'],ptr['initialized']))
        root={'type':'ptrPila','identity':'&pila','value':head,'alive':not null_root,'valid':not null_root,'initialized':not null_root}
        scopes=[{'id':'pila_apilar','kind':'function','variables':deepcopy([v for v in variables if v['scope']=='pila_apilar'])}] if active else []
        calls=[{'function':'pila_apilar','parameters':{'p':None if null_root else '&pila','valor':value},'return':None,'continuation':'caller; root y heap propios siguen vivos'}] if active else []
        if allocator_active:calls.append({'function':'malloc','parameters':{'size':'sizeof(struct NodoPila)'},'return':None,'continuation':'inicializador de aux','opaque':True})
        debug={'token':event,'function':'malloc' if allocator_active else 'pila_apilar','root':root,'aux':deepcopy(aux) if active else None,'heap':deepcopy(heap),'variables':deepcopy(variables),'pointers':deepcopy(pointers),'scopes':scopes,'call_stack':deepcopy(calls),'condition_result':condition}
        current=state();previous=deepcopy(steps[-1]['state_after'] if steps else before_state)
        step={'step_index':len(steps),'line_index':index,'line_text':lines[index],'event_type':event,'phase':'progress','delay_ms':100,'state_snapshot':previous,'state_after':current,'console':deepcopy(console),'condition_result':condition,'function_name':debug['function'],'debug':debug}
        f=build_sequential_frame(structure_id='stack',operation_name='apilar',payload=payload,step=step,success=success)
        f.update(variables=variables,pointers=pointers,heap_objects=deepcopy(heap),heap_transition={'kind':'allocate' if event=='allocator_success_return' else 'link' if event=='root_assigned' else 'stable','before':deepcopy(steps[-1]['pedagogy']['heap_objects'] if steps else heap),'after':deepcopy(heap),'freed':[],'dangling_references':[]},scopes=scopes,call_stack=calls,memory_state=None,push_memory={'kind':'stack_push','root':deepcopy(root),'heap':deepcopy(heap),'aux':deepcopy(aux) if active else None,'variables':deepcopy(variables),'call_stack':deepcopy(calls)},condition=None if condition is None else {'source':lines[index],'substituted':('&pila == NULL' if event=='root_guard' and not null_root else 'NULL == NULL' if event=='root_guard' else (str(aux['value']) if aux and aux['value'] is not None else 'NULL')+' == NULL'),'result':condition,'consequence':'Rama C ejecutada.'})
        f['source']['function']=debug['function'];f['invariant']={'text':'La raíz alcanza sólo nodos con ambos campos inicializados; el temporal vive sin publicarse.','holds':True,'symbol':'✓','evidence':'Máscaras0→1→3; aux conserva identidad y alias tras publicar hasta retornar.'}
        narrations={'entry':'Entra pila_apilar: p recibe la dirección del slot caller y valor el entero.', 'root_guard':'Comprueba la dirección p; una pila vacía no convierte p en NULL.', 'allocator_enter':'Comienza malloc opaco; aux todavía no recibió su resultado.', 'allocator_success_return':'malloc retorna un objeto vivo con campos sin inicializar y máscara0.', 'allocator_NULL_return':'malloc retorna NULL; no se crea ningún objeto.', 'aux_allocated':'Termina el inicializador de aux; su puntero queda determinado, vivo o NULL.', 'allocation_guard':'Comprueba aux antes de acceder a cualquier campo.', 'value_assigned':'Escribe sólo nro; sgte sigue sin inicializar (máscara1).', 'link_assigned':'Escribe sgte con la cabeza anterior; ambos campos válidos (máscara3).', 'root_assigned':'Publica el mismo nodo en *p; aux sigue siendo alias válido.', 'root_error_printf':'Imprime el diagnóstico: p es NULL, no hubo reserva.', 'allocation_error_printf':'Imprime el diagnóstico de reserva fallida; la raíz se conserva.', 'return':'Retorno void: termina sólo el scope local; caller y nodos propios siguen vivos.'}
        for level in f['narration']:f['narration'][level]=narrations[event]
        if event=='return':f['concept']='return';f['phase']={'id':'apilar-return','label':'Retorno void; scope terminado','goal':'Caller y heap conservan propiedad.'}
        validate_sequential_frame(f,source_code=source_code);step['pedagogy']=f;steps.append(step)
    emit('entry','void pila_apilar(');emit('root_guard','if (p == NULL)',null_root)
    if null_root:
        console.append('Error: pila no inicializada.');emit('root_error_printf','printf("Error: pila no inicializada.')
    else:
        aux={'type':'ptrPila','initialized':False,'valid':False,'value':None};allocator_active=True;emit('allocator_enter',malloc_line);allocator_active=False
        if allocation_failure:emit('allocator_NULL_return',malloc_line);identity=None
        else:
            identity='push-new';node={'id':identity,'address':identity,'type':'struct NodoPila','alive':True,'allocated':True,'freed':False,'fields_valid':False,'initialized_mask':0,'field_validity':{'nro':False,'sgte':False},'status':'temporary','fields':{'nro':None,'sgte':None}};heap.append(node);objects[identity]=node;emit('allocator_success_return',malloc_line)
        aux={'type':'ptrPila','initialized':True,'valid':True,'value':identity};emit('aux_allocated',malloc_line);emit('allocation_guard','if (aux == NULL)',allocation_failure)
        if allocation_failure:
            console.append('Error: No se pudo asignar memoria.');emit('allocation_error_printf','printf("Error: No se pudo asignar memoria.')
        else:
            node['fields']['nro']=value;node['initialized_mask']=1;node['field_validity']['nro']=True;emit('value_assigned','aux->nro = valor;')
            node['fields']['sgte']=head;node['initialized_mask']=3;node['field_validity']['sgte']=True;node['fields_valid']=True;emit('link_assigned','aux->sgte = *p;')
            head=identity;node['status']='linked';emit('root_assigned','*p = aux;')
    active=False;emit('return','return;' if null_root or allocation_failure else '@end')
    steps[0]['phase']='start';steps[-1]['phase']='end';steps[-1]['state_after']=deepcopy(after_state)
    return {'structure_id':'stack','operation_name':'apilar','payload':deepcopy(payload),'success':success,'message':message,'mutates':True,'code_title':code_title,'source_code':source_code,'steps':steps,'final_state':deepcopy(after_state),'pedagogy_schema_version':SEQUENTIAL_FRAME_SCHEMA_VERSION,'pedagogy_schema':sequential_frame_schema(),'learning_profile':deepcopy(SEQUENTIAL_LEARNING_CATALOG['stack']),'instruction_scope':'pila_apilar caller/locals opaque malloc fields masks aliases and void return'}
