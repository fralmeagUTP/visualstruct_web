"""Causal cp_vaciar trace with separate caller fields and retired history."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.domain.sequential.pedagogy import build_sequential_frame, validate_sequential_frame, sequential_frame_schema, SEQUENTIAL_FRAME_SCHEMA_VERSION, SEQUENTIAL_LEARNING_CATALOG


def build_priority_queue_cleanup_trace(*, payload: dict[str, Any], source_code: str, code_title: str,
        before_state: dict[str, Any], after_state: dict[str, Any], success: bool,
        message: str, null_root: bool = False) -> dict[str, Any]:
    """Track cp_vaciar scopes and object lifetimes without reading retired fields."""
    lines=source_code.replace('\r\n','\n').split('\n')
    values=[(int(n['value']),int(n['priority'])) for n in before_state.get('items',[])]
    heap=[{'id':f'priority-node-{i}','address':f'priority-node-{i}','type':'CPNodo',
        'alive':True,'allocated':True,'freed':False,'fields_valid':True,'initialized_mask':7,
        'status':'linked','fields':{'valor':v,'prioridad':priority,'sgte':f'priority-node-{i+1}' if i+1<len(values) else None}}
        for i,(v,priority) in enumerate(values)]
    objects={n['id']:n for n in heap};front=heap[0]['id'] if heap else None
    rear=heap[-1]['id'] if heap else None;rear_valid=True;rear_history=None
    active=True;aux=None;next_ptr=None;quantity=len(values);frees=0;steps=[]
    def state():
        result=deepcopy(before_state);items=[];pointer=front
        while pointer is not None:
            n=objects[pointer];assert n['alive'] and n['fields_valid']
            items.append({'value':n['fields']['valor'],'priority':n['fields']['prioridad']});pointer=n['fields']['sgte']
        result.update(items=items,size=quantity,cantidad=quantity,empty=front is None,delante=front,atras=rear,node_ids=[n['id'] for n in heap if n['alive'] and n['status']=='linked'],out_index=min(range(len(items)),key=lambda i:items[i]['priority']) if items else -1);return result
    def emit(event,token,condition=None):
        index=len(lines)-1 if token=='@end' else (max(i for i,l in enumerate(lines) if token in l) if event=='rear_final_NULL_store' else next(i for i,l in enumerate(lines) if token in l))
        variables=[];pointers=[]
        if not null_root:
            for name,value,valid in [('delante',front,True),('atras',rear if rear_valid else None,rear_valid)]:
                item={'name':name,'type':'CPNodo *','value':value,'initialized':valid,
                    'valid':valid,'scope':'cp (llamador)','scope_state':'active','previous':None,
                    'changed':event in {'root_assigned','rear_last_NULL_store'},
                    'meaning':'Campo del struct caller; indeterminado no se lee.'}
                variables.append(item)
                pointers.append({'name':name,'type':item['type'],'target':value,'initialized':valid,
                    'valid':valid,'scope':item['scope'],'scope_state':'active','alias':None,
                    'historical_identity':rear_history if name=='atras' and not valid else None,
                    'previous_target':None,'changed':item['changed']})
        if not null_root:
            variables.append({'name':'cantidad','type':'int','value':quantity,'initialized':True,'valid':True,'scope':'cp (llamador)','scope_state':'active','previous':None,'changed':event in {'quantity_decrement','quantity_zero_store'},'meaning':'Campo caller; decrece después de free.'})
        if active:
            variables.append({'name':'cola','type':'ColaPrioridad *','value':None if null_root else '&cp',
                'initialized':True,'valid':True,'scope':'cp_vaciar','scope_state':'active',
                'previous':None,'changed':False,'meaning':'Dirección prestada del struct caller.'})
            pointers.append({'name':'cola','type':'ColaPrioridad *','target':None if null_root else '&cp',
                'initialized':True,'valid':True,'scope':'cp_vaciar','scope_state':'active',
                'alias':None if null_root else 'struct caller','previous_target':None,'changed':False})
            for pointer_name,pointer_data in [('aux',aux),('next',next_ptr)]:
                if pointer_data is None:continue
                local=pointer_data
                variables.append({'name':pointer_name,'type':'CPNodo *','value':local['value'],
                    'initialized':local['initialized'],'valid':local['valid'],'scope':'cp_vaciar',
                    'scope_state':'active','previous':None,'changed':event in {'aux_assigned','node_free'},
                    'meaning':'Alias prestado; indeterminado antes de asignación y después de free.'})
                pointers.append({'name':pointer_name,'type':'CPNodo *','target':local['value'],
                    'initialized':local['initialized'],'valid':local['valid'],'scope':'cp_vaciar',
                    'scope_state':'active','historical_identity':local.get('historical_identity'),
                    'alias':'delante' if local['valid'] and local['value']==front else None,
                    'previous_target':None,'changed':event in {'aux_assigned','node_free'}})
        prior_variables={v['name']:v for v in steps[-1]['debug']['variables']} if steps else {}
        prior_pointers={v['name']:v for v in steps[-1]['debug']['pointers']} if steps else {}
        for v in variables:
            previous=prior_variables.get(v['name']);v['previous']=previous['value'] if previous and previous.get('valid') else None
            v['changed']=bool(previous and (previous['value'],previous['initialized'])!=(v['value'],v['initialized']))
        for ptr in pointers:
            previous=prior_pointers.get(ptr['name']);ptr['previous_target']=previous['target'] if previous and previous.get('valid') else None
            ptr['changed']=bool(previous and (previous['target'],previous['initialized'])!=(ptr['target'],ptr['initialized']))
            aliases=[p['name'] for p in pointers if p is not ptr and p.get('valid') and ptr.get('valid') and ptr['target'] is not None and p['target']==ptr['target']]
            if aliases:ptr['alias']=', '.join(aliases)
        root={'type':'ColaPrioridad','identity':'&cp','alive':not null_root,'valid':not null_root,
            'initialized':not null_root,'value':front,'front':front,'rear':rear if rear_valid else None,
            'rear_valid':rear_valid and not null_root,'rear_historical_identity':rear_history,
            'initialized_mask':7 if not null_root else 0,
            'cantidad':quantity,'fields':{'delante':front,'atras':rear if rear_valid else None,'cantidad':quantity},
            'field_validity':{'delante':not null_root,'atras':rear_valid and not null_root,'cantidad':not null_root}}
        calls=['cp_vaciar'] if active else []
        scopes=([{'id':'cp_vaciar','kind':'function','variables':deepcopy([v for v in variables if v['scope']=='cp_vaciar'])}] if active else [])
        debug={'token':event,'function':'cp_vaciar','root':root,'aux':deepcopy(aux) if active else None,'next':deepcopy(next_ptr) if active else None,
            'heap':deepcopy(heap),'variables':deepcopy(variables),'pointers':deepcopy(pointers),
            'frees':frees,'condition_result':condition,'scopes':scopes,'call_stack':calls}
        current=state();previous=deepcopy(steps[-1]['state_after'] if steps else before_state)
        step={'step_index':len(steps),'line_index':index,'line_text':lines[index],'event_type':event,
            'phase':'progress','delay_ms':100,'state_snapshot':previous,'state_after':current,
            'console':[],'condition_result':condition,'function_name':'cp_vaciar','debug':debug}
        frame=build_sequential_frame(structure_id='priority_queue',operation_name='limpiar',payload=payload,step=step,success=success)
        live=deepcopy([h for h in heap if h['alive']]);retired=deepcopy([h for h in heap if not h['alive']])
        frame.update(variables=variables,pointers=pointers,heap_objects=live,
            heap_transition={'kind':'free' if event=='node_free' else 'link' if event=='root_assigned' else 'stable',
                'before':deepcopy(steps[-1]['pedagogy']['heap_objects'] if steps else heap),'after':live,
                'freed':retired,'dangling_references':[]},
            call_stack=[{'function':'cp_vaciar','parameters':{'cola':None if null_root else '&cp'},
                'return':None,'continuation':'caller; struct prestado'}] if active else [],
            scopes=scopes,memory_state=None,cleanup_memory={'kind':'priority_queue','root':deepcopy(root),
                'heap':deepcopy(heap),'aux':deepcopy(aux) if active else None,'next':deepcopy(next_ptr) if active else None,'variables':deepcopy(variables),
                'call_stack':calls,'frees':frees},
            condition=None if condition is None else {'source':lines[index],'substituted':str(condition),
                'result':condition,'consequence':'Rama C ejecutada.'})
        frame['source']['function']='cp_vaciar'
        frame['invariant']={'text':'Front alcanza sólo nodos vivos; rear se limpia antes del último free; cantidad decrece después de free.',
            'holds':True,'symbol':'✓','evidence':'Aux detached conserva identidad hasta free; next vivo/NULL; historia no es puntero usable.'}
        if event=='return':frame['concept']='return';frame['phase']={'id':'limpiar-return','label':'Retorno void; scope terminado','goal':'Caller struct sigue vivo.'}
        for level in frame['narration']:frame['narration'][level]=f'cp_vaciar: {event}. next conserva el sucesor; aux desconectado vive hasta free; cantidad decrece después. Aux retirado es indeterminado; historia separada.'
        validate_sequential_frame(frame,source_code=source_code);step['pedagogy']=frame;steps.append(step)
    emit('entry','void cp_vaciar(')
    aux={'type':'CPNodo *','initialized':False,'valid':False,'value':None}
    emit('aux_declared','CPNodo *aux;')
    next_ptr={'type':'CPNodo *','initialized':False,'valid':False,'value':None}
    emit('next_declared','CPNodo *next;');emit('root_guard','if (cola == NULL)',null_root)
    if not null_root:
        aux={'type':'CPNodo *','initialized':True,'valid':True,'value':front}
        emit('aux_initial','aux = cola->delante;')
        while True:
            emit('while_guard','while (aux != NULL)',aux['value'] is not None)
            if aux['value'] is None:break
            node=objects[aux['value']];assert node['alive'] and node['fields_valid']
            next_ptr={'type':'CPNodo *','initialized':True,'valid':True,'value':node['fields']['sgte']}
            emit('next_assigned','next = aux->sgte;')
            front=next_ptr['value'];node['status']='detached';emit('root_assigned','cola->delante = next;')
            last=rear==aux['value'];emit('rear_guard','if (cola->atras == aux)',last)
            if last:rear=None;emit('rear_last_NULL_store','cola->atras = NULL;')
            identity=aux['value']
            node.update(alive=False,allocated=False,freed=True,fields_valid=False,initialized_mask=0,
                status='freed',historical_fields=deepcopy(node['fields']),historical_initialized_mask=7,
                fields={'valor':None,'prioridad':None,'sgte':None})
            aux={'type':'CPNodo *','initialized':False,'valid':False,'value':None,'historical_identity':identity}
            frees+=1;emit('node_free','free(aux);')
            positive=quantity>0;emit('quantity_guard','if (cola->cantidad > 0)',positive)
            if positive:quantity-=1;emit('quantity_decrement','cola->cantidad--;')
            aux=deepcopy(next_ptr);emit('aux_advance','aux = next;')
        front=None;emit('front_NULL_store','cola->delante = NULL;')
        rear=None;emit('rear_final_NULL_store','cola->atras = NULL;')
        quantity=0;emit('quantity_zero_store','cola->cantidad = 0;')
    active=False;emit('return','return;' if null_root else '@end')
    steps[0]['phase']='start';steps[-1]['phase']='end';steps[-1]['state_after']=deepcopy(after_state)
    return {'structure_id':'priority_queue','operation_name':'limpiar','payload':deepcopy(payload),'success':success,
        'message':message,'mutates':True,'code_title':code_title,'source_code':source_code,'steps':steps,
        'final_state':deepcopy(after_state),'pedagogy_schema_version':SEQUENTIAL_FRAME_SCHEMA_VERSION,
        'pedagogy_schema':sequential_frame_schema(),'learning_profile':deepcopy(SEQUENTIAL_LEARNING_CATALOG['priority_queue']),
        'instruction_scope':'cp_vaciar caller struct/front/rear/aux lifetimes and safe historical snapshots'}
