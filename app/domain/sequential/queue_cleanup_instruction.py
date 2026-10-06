"""Causal cola_vaciar trace with separate caller fields and retired history."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.domain.sequential.pedagogy import build_sequential_frame, validate_sequential_frame, sequential_frame_schema, SEQUENTIAL_FRAME_SCHEMA_VERSION, SEQUENTIAL_LEARNING_CATALOG


def build_queue_cleanup_trace(*, payload: dict[str, Any], source_code: str, code_title: str,
        before_state: dict[str, Any], after_state: dict[str, Any], success: bool,
        message: str, null_root: bool = False) -> dict[str, Any]:
    """Observe only valid front links; a retired rear pointer is never followed."""
    lines=source_code.replace('\r\n','\n').split('\n')
    values=[int(n['value']) for n in before_state.get('items',[])]
    heap=[{'id':f'queue-node-{i}','address':f'queue-node-{i}','type':'struct NodoCola',
        'alive':True,'allocated':True,'freed':False,'fields_valid':True,'initialized_mask':3,
        'status':'linked','fields':{'nro':v,'sgte':f'queue-node-{i+1}' if i+1<len(values) else None}}
        for i,v in enumerate(values)]
    objects={n['id']:n for n in heap};front=heap[0]['id'] if heap else None
    rear=heap[-1]['id'] if heap else None;rear_valid=True;rear_history=None
    active=True;aux=None;frees=0;steps=[]
    def state():
        result=deepcopy(before_state);items=[];pointer=front
        while pointer is not None:
            n=objects[pointer];assert n['alive'] and n['fields_valid']
            items.append({'value':n['fields']['nro']});pointer=n['fields']['sgte']
        result.update(items=items,size=len(items),empty=not items);return result
    def emit(event,token,condition=None):
        index=len(lines)-1 if token=='@end' else next(i for i,l in enumerate(lines) if token in l)
        variables=[];pointers=[]
        if not null_root:
            for name,value,valid in [('delante',front,True),('atras',rear if rear_valid else None,rear_valid)]:
                item={'name':name,'type':'struct NodoCola *','value':value,'initialized':valid,
                    'valid':valid,'scope':'cola (llamador)','scope_state':'active','previous':None,
                    'changed':event in {'root_assigned','rear_NULL_store','node_free'},
                    'meaning':'Campo del struct caller; indeterminado no se lee.'}
                variables.append(item)
                pointers.append({'name':name,'type':item['type'],'target':value,'initialized':valid,
                    'valid':valid,'scope':item['scope'],'scope_state':'active','alias':None,
                    'historical_identity':rear_history if name=='atras' and not valid else None,
                    'previous_target':None,'changed':item['changed']})
        if active:
            variables.append({'name':'q','type':'struct Cola *','value':None if null_root else '&cola',
                'initialized':True,'valid':True,'scope':'cola_vaciar','scope_state':'active',
                'previous':None,'changed':False,'meaning':'Dirección prestada del struct caller.'})
            pointers.append({'name':'q','type':'struct Cola *','target':None if null_root else '&cola',
                'initialized':True,'valid':True,'scope':'cola_vaciar','scope_state':'active',
                'alias':None if null_root else 'struct caller','previous_target':None,'changed':False})
            if aux is not None:
                variables.append({'name':'aux','type':'struct NodoCola *','value':aux['value'],
                    'initialized':aux['initialized'],'valid':aux['valid'],'scope':'cola_vaciar',
                    'scope_state':'active','previous':None,'changed':event in {'aux_assigned','node_free'},
                    'meaning':'Alias prestado; indeterminado antes de asignación y después de free.'})
                pointers.append({'name':'aux','type':'struct NodoCola *','target':aux['value'],
                    'initialized':aux['initialized'],'valid':aux['valid'],'scope':'cola_vaciar',
                    'scope_state':'active','historical_identity':aux.get('historical_identity'),
                    'alias':'delante' if aux['valid'] and aux['value']==front else None,
                    'previous_target':None,'changed':event in {'aux_assigned','node_free'}})
        root={'type':'struct Cola','identity':'&cola','alive':not null_root,'valid':not null_root,
            'initialized':not null_root,'value':front,'front':front,'rear':rear if rear_valid else None,
            'rear_valid':rear_valid and not null_root,'rear_historical_identity':rear_history,
            'initialized_mask':(3 if rear_valid else 1) if not null_root else 0,
            'fields':{'delante':front,'atras':rear if rear_valid else None},
            'field_validity':{'delante':not null_root,'atras':rear_valid and not null_root}}
        calls=['cola_vaciar'] if active else []
        scopes=([{'id':'cola_vaciar','kind':'function','variables':deepcopy([v for v in variables if v['scope']=='cola_vaciar'])}] if active else [])
        debug={'token':event,'function':'cola_vaciar','root':root,'aux':deepcopy(aux) if active else None,
            'heap':deepcopy(heap),'variables':deepcopy(variables),'pointers':deepcopy(pointers),
            'frees':frees,'condition_result':condition,'scopes':scopes,'call_stack':calls}
        current=state();previous=deepcopy(steps[-1]['state_after'] if steps else before_state)
        step={'step_index':len(steps),'line_index':index,'line_text':lines[index],'event_type':event,
            'phase':'progress','delay_ms':100,'state_snapshot':previous,'state_after':current,
            'console':[],'condition_result':condition,'function_name':'cola_vaciar','debug':debug}
        frame=build_sequential_frame(structure_id='queue',operation_name='limpiar',payload=payload,step=step,success=success)
        live=deepcopy([h for h in heap if h['alive']]);retired=deepcopy([h for h in heap if not h['alive']])
        frame.update(variables=variables,pointers=pointers,heap_objects=live,
            heap_transition={'kind':'free' if event=='node_free' else 'link' if event=='root_assigned' else 'stable',
                'before':deepcopy(steps[-1]['pedagogy']['heap_objects'] if steps else heap),'after':live,
                'freed':retired,'dangling_references':[]},
            call_stack=[{'function':'cola_vaciar','parameters':{'q':None if null_root else '&cola'},
                'return':None,'continuation':'caller; struct prestado'}] if active else [],
            scopes=scopes,memory_state=None,cleanup_memory={'kind':'queue','root':deepcopy(root),
                'heap':deepcopy(heap),'aux':deepcopy(aux) if active else None,'variables':deepcopy(variables),
                'call_stack':calls,'frees':frees},
            condition=None if condition is None else {'source':lines[index],'substituted':str(condition),
                'result':condition,'consequence':'Rama C ejecutada.'})
        frame['source']['function']='cola_vaciar'
        frame['invariant']={'text':'Front alcanza sólo nodos vivos; rear indeterminado no se lee antes de NULLstore.',
            'holds':True,'symbol':'✓','evidence':'Aux detached vive hasta free; historia no es puntero usable.'}
        if event=='return':frame['concept']='return';frame['phase']={'id':'limpiar-return','label':'Retorno void; scope terminado','goal':'Caller struct sigue vivo.'}
        for level in frame['narration']:frame['narration'][level]=f'cola_vaciar: {event}. Front cambia antes de free; aux y rear retirados se marcan indeterminados, con historia separada.'
        validate_sequential_frame(frame,source_code=source_code);step['pedagogy']=frame;steps.append(step)
    emit('entry','void cola_vaciar(')
    aux={'type':'struct NodoCola *','initialized':False,'valid':False,'value':None}
    emit('aux_declared','struct NodoCola *aux;');emit('root_guard','if (q == NULL)',null_root)
    if not null_root:
        while True:
            emit('while_guard','while (q->delante != NULL)',front is not None)
            if front is None:break
            node=objects[front];assert node['alive'] and node['fields_valid']
            aux={'type':'struct NodoCola *','initialized':True,'valid':True,'value':front}
            emit('aux_assigned','aux = q->delante;')
            front=node['fields']['sgte'];node['status']='detached';emit('root_assigned','q->delante = aux->sgte;')
            identity=aux['value']
            if identity==rear:rear_valid=False;rear_history=identity
            node.update(alive=False,allocated=False,freed=True,fields_valid=False,initialized_mask=0,
                status='freed',historical_fields=deepcopy(node['fields']),historical_initialized_mask=3,
                fields={'nro':None,'sgte':None})
            aux={'type':'struct NodoCola *','initialized':False,'valid':False,'value':None,'historical_identity':identity}
            frees+=1;emit('node_free','free(aux);')
        front=None;emit('front_NULL_store','q->delante = NULL;')
        rear=None;rear_valid=True;rear_history=None;emit('rear_NULL_store','q->atras = NULL;')
    active=False;emit('return','return;' if null_root else '@end')
    steps[0]['phase']='start';steps[-1]['phase']='end';steps[-1]['state_after']=deepcopy(after_state)
    return {'structure_id':'queue','operation_name':'limpiar','payload':deepcopy(payload),'success':success,
        'message':message,'mutates':True,'code_title':code_title,'source_code':source_code,'steps':steps,
        'final_state':deepcopy(after_state),'pedagogy_schema_version':SEQUENTIAL_FRAME_SCHEMA_VERSION,
        'pedagogy_schema':sequential_frame_schema(),'learning_profile':deepcopy(SEQUENTIAL_LEARNING_CATALOG['queue']),
        'instruction_scope':'cola_vaciar caller struct/front/rear/aux lifetimes and safe historical snapshots'}
