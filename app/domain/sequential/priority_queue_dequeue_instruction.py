"""Causal cp_desencolar: initialized storage, stable aliases and opaque free."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.domain.sequential.pedagogy import build_sequential_frame, validate_sequential_frame, sequential_frame_schema, SEQUENTIAL_FRAME_SCHEMA_VERSION, SEQUENTIAL_LEARNING_CATALOG


def build_priority_queue_dequeue_trace(*, payload: dict[str, Any], source_code: str, code_title: str,
        before_state: dict[str, Any], after_state: dict[str, Any], success: bool, message: str,
        null_root: bool = False, null_value: bool = False, null_priority: bool = False) -> dict[str, Any]:
    """Execute C statement boundaries; IDs after free are saved history only."""
    lines=source_code.replace('\r\n','\n').split('\n');steps=[]
    items=[] if null_root else before_state.get('items',[])
    heap=[{'id':f'N{i+1}','address':f'N{i+1}','type':'CPNodo','alive':True,'allocated':True,'freed':False,
        'fields_valid':True,'initialized_mask':7,'field_validity':{'valor':True,'prioridad':True,'sgte':True},'status':'linked',
        'fields':{'valor':int(x['value']),'prioridad':int(x['priority']),'sgte':f'N{i+2}' if i+1<len(items) else None}}
        for i,x in enumerate(items)]
    objects={x['id']:x for x in heap};head=heap[0]['id'] if heap else None;rear=heap[-1]['id'] if heap else None
    quantity=int(before_state.get('cantidad',before_state.get('size',len(items))))
    aliases={};out={'valor':None,'prioridad':None};written={'valor':False,'prioridad':False}
    active=True;result=None;retired=[]
    def state():
        current=deepcopy(before_state);reachable=[];ptr=head
        while ptr:
            node=objects[ptr];reachable.append({'value':node['fields']['valor'],'priority':node['fields']['prioridad']});ptr=node['fields']['sgte']
        current.update(items=reachable,size=len(reachable),empty=not reachable,delante=head or 'NULL',atras=rear or 'NULL',cantidad=quantity)
        # Alias values are symbolic snapshots, not evaluations of freed C pointers.
        current.update({k:(v or 'NULL') for k,v in aliases.items()})
        current.update({k:v for k,v in out.items() if written[k]})
        return current
    def emit(event,token,condition=None,freed=None):
        index=next(i for i,l in enumerate(lines) if token in l);scope='active' if active else 'ended'
        variables=[];pointers=[]
        root={'type':'ColaPrioridad','identity':'&cp','alive':not null_root,'valid':not null_root,'front':head,'rear':rear,'quantity':quantity}
        for name,target in [('delante',head),('atras',rear)]:
            variables.append({'name':name,'type':'CPNodo *','value':target,'initialized':not null_root,'valid':not null_root,'scope':'caller','scope_state':'active'})
            pointers.append({'name':name,'type':'CPNodo *','target':target,'initialized':not null_root,'valid':not null_root,'scope':'caller','scope_state':'active'})
        variables.append({'name':'cantidad','type':'int','value':quantity,'initialized':not null_root,'valid':not null_root,'scope':'caller','scope_state':'active'})
        local=[]
        for name,typ,target in [('cola','ColaPrioridad *',None if null_root else '&cp'),('valor','int *',None if null_value else '&caller_valor'),('prioridad','int *',None if null_priority else '&caller_prioridad')]:
            local.append({'name':name,'type':typ,'value':target,'initialized':True,'valid':active,'scope':'cp_desencolar','scope_state':scope})
            pointers.append({'name':name,'type':typ,'target':target,'initialized':True,'valid':active,'scope':'cp_desencolar','scope_state':scope})
        for name,value in aliases.items():
            usable=active and (value is None or value in objects);dangling=value is not None and value not in objects
            local.append({'name':name,'type':'CPNodo *','value':value,'initialized':True,'valid':usable,'dangling':dangling,'scope':'cp_desencolar','scope_state':scope,'meaning':'Identidad histÃ³rica guardada antes de free; no evaluar si es invÃ¡lida.'})
            pointers.append({'name':name,'type':'CPNodo *','target':value,'initialized':True,'valid':usable,'dangling':dangling,'historical_id':value if dangling else None,'scope':'cp_desencolar','scope_state':scope})
        for name in declared:
            if name not in aliases:local.append({'name':name,'type':'CPNodo *','value':None,'initialized':False,'valid':False,'scope':'cp_desencolar','scope_state':scope,'meaning':'Indeterminado; no leer ni interpretar como NULL.'})
        for name in ['valor','prioridad']:
            variables.append({'name':'caller_'+name,'type':'int','value':out[name],'initialized':written[name],'valid':True,'scope':'caller','scope_state':'active','address':'&caller_'+name})
        variables.extend(local)
        calls=[{'function':'cp_desencolar','parameters':{'cola':None if null_root else '&cp','valor':None if null_value else '&caller_valor','prioridad':None if null_priority else '&caller_prioridad'},'return_type':'bool','return':None,'continuation':'Caller recibe bool y conserva ambas copias int.'}] if active else []
        scopes=[{'id':'cp_desencolar','kind':'function','state':scope,'scope_state':scope,'variables':deepcopy(local)}]
        current=state();previous=deepcopy(steps[-1]['state_after'] if steps else before_state)
        debug={'token':event,'function':'cp_desencolar','root':deepcopy(root),'variables':deepcopy(variables),'pointers':deepcopy(pointers),'scopes':deepcopy(scopes),'call_stack':deepcopy(calls),'heap':deepcopy(heap),'result':result}
        step={'step_index':len(steps),'line_index':index,'line_text':lines[index],'event_type':event,'phase':'progress','delay_ms':100,'state_snapshot':previous,'state_after':current,'console':[],'condition_result':condition,'function_name':'cp_desencolar','debug':debug}
        frame=build_sequential_frame(structure_id='priority_queue',operation_name='desencolar',payload=payload,step=step,success=success)
        invalid=[{'name':x['name'],'historical_id':x['target'],'usable':False} for x in pointers if x.get('dangling')]
        memory={'kind':'priority_queue_dequeue','root':deepcopy(root),'heap':deepcopy(heap),'retired':deepcopy(retired),'variables':deepcopy(variables),'pointers':deepcopy(pointers),'call_stack':deepcopy(calls),'scope_state':scope,'outputs':{'value':out['valor'],'priority':out['prioridad'],'value_written':written['valor'],'priority_written':written['prioridad']},'invalid_aliases':invalid,'result':result}
        substituted=None
        if condition is not None:
            if token.startswith('if (cola == NULL'):substituted=('NULL' if null_root else '&cp')+' == NULL || '+(head or 'NULL')+' == NULL || '+('NULL' if null_value else '&caller_valor')+' == NULL || '+('NULL' if null_priority else '&caller_prioridad')+' == NULL (cortocircuito)'
            elif token.startswith('while'):substituted=(aliases.get('actual') or 'NULL')+' != NULL'
            elif token.startswith('if (actual->prioridad'):substituted=str(objects[aliases['actual']]['fields']['prioridad'])+' < '+str(objects[aliases['objetivo']]['fields']['prioridad'])
            elif token.startswith('if (objetivo =='):substituted=(aliases['objetivo'] or 'NULL')+' == '+(head or 'NULL')
            elif token.startswith('if (cola->delante'):substituted=(head or 'NULL')+' == NULL'
            elif token.startswith('if (cola->atras'):substituted=(rear or 'NULL')+' == '+(aliases['objetivo'] or 'NULL')
            else:substituted=str(quantity)+' > 0'
        frame.update(variables=variables,pointers=pointers,scopes=scopes,call_stack=calls,heap_objects=deepcopy(heap),memory_state=None,dequeue_memory=memory,
            heap_transition={'kind':'free' if freed else 'unlink' if event=='unlink' else 'stable','before':deepcopy(steps[-1]['pedagogy']['heap_objects'] if steps else heap),'after':deepcopy(heap),'freed':deepcopy(freed or []),'dangling_references':[], 'invalid_historical_aliases':deepcopy(invalid), 'opaque_call':{'function':'free','argument_historical_id':freed[0]['id'],'completed':True,'return_type':'void'} if freed else None},
            condition=None if condition is None else {'source':lines[index],'substituted':substituted,'result':condition,'consequence':'EvaluaciÃ³n C con cortocircuito y operandos vivos.'})
        frame['source']['function']='cp_desencolar';frame['invariant']={'text':'BÃºsqueda parcial; candidato mÃ­nimo del prefijo, empates conservan primer nodo.','holds':True,'symbol':'âœ“','evidence':'RaÃ­ces y cantidad sÃ³lo cambian en sus stores; IDs histÃ³ricos separados de lecturas vivas.'}
        narration=('Declara CPNodo * indeterminado; todavÃ­a no existe valor usable.' if event=='declare' else 'Free opaco terminÃ³; el objeto desaparece del heap vivo y todos sus aliases quedan inutilizables.' if event=='free' else 'Retorno bool y fin del scope local; caller y raÃ­ces restantes siguen vivos.' if event=='return' else 'Copia int al almacenamiento independiente del caller antes de free.' if event=='output' else 'EvalÃºa la condiciÃ³n real y recorre solamente su rama.' if condition is not None else 'Ejecuta esta asignaciÃ³n C; conserva identidad de objetos y demÃ¡s valores.')
        for level in frame['narration']:frame['narration'][level]=narration
        if event=='return':frame['concept']='return'
        validate_sequential_frame(frame,source_code=source_code);step['pedagogy']=frame;steps.append(step)
    declared=[];emit('entry','bool cp_desencolar(')
    for name in ['actual','prev','objetivo','objetivoPrev']:declared.append(name);emit('declare','CPNodo *'+name+';')
    reject=null_root or head is None or null_value or null_priority;emit('guard','if (cola == NULL',reject)
    if reject:result=False;active=False;emit('return','return false;')
    else:
        aliases['actual']=head;emit('assign','actual = cola->delante;')
        aliases['prev']=None;emit('assign','prev = NULL;')
        aliases['objetivo']=aliases['actual'];emit('assign','objetivo = actual;')
        aliases['objetivoPrev']=None;emit('assign','objetivoPrev = NULL;')
        while True:
            emit('loop','while (actual != NULL)',aliases['actual'] is not None)
            if aliases['actual'] is None:break
            better=objects[aliases['actual']]['fields']['prioridad']<objects[aliases['objetivo']]['fields']['prioridad'];emit('compare','if (actual->prioridad < objetivo->prioridad)',better)
            if better:
                aliases['objetivo']=aliases['actual'];emit('assign','objetivo = actual;')
                aliases['objetivoPrev']=aliases['prev'];emit('assign','objetivoPrev = prev;')
            aliases['prev']=aliases['actual'];emit('assign','prev = actual;')
            aliases['actual']=objects[aliases['actual']]['fields']['sgte'];emit('assign','actual = actual->sgte;')
        target=aliases['objetivo'];node=objects[target]
        emit('guard','if (objetivo == cola->delante)',target==head)
        if target==head:
            head=node['fields']['sgte'];node['status']='detached';emit('unlink','cola->delante = objetivo->sgte;')
            emit('guard','if (cola->delante == NULL)',head is None)
            if head is None:rear=None;emit('assign','cola->atras = NULL;')
        else:
            objects[aliases['objetivoPrev']]['fields']['sgte']=node['fields']['sgte'];node['status']='detached';emit('unlink','objetivoPrev->sgte = objetivo->sgte;')
            emit('guard','if (cola->atras == objetivo)',rear==target)
            if rear==target:rear=aliases['objetivoPrev'];emit('assign','cola->atras = objetivoPrev;')
        out['valor']=node['fields']['valor'];written['valor']=True;emit('output','*valor = objetivo->valor;')
        out['prioridad']=node['fields']['prioridad'];written['prioridad']=True;emit('output','*prioridad = objetivo->prioridad;')
        record={'id':target,'address':target,'type':'CPNodo','freed':True,'alive':False,'historical_fields':deepcopy(node['fields'])};retired.append(record);heap.remove(node);objects.pop(target);emit('free','free(objetivo);',freed=[record])
        emit('guard','if (cola->cantidad > 0)',quantity>0)
        if quantity>0:quantity-=1;emit('counter','cola->cantidad--;')
        result=True;active=False;emit('return','return true;')
    steps[0]['phase']='start';steps[-1]['phase']='end'
    return {'structure_id':'priority_queue','operation_name':'desencolar','payload':deepcopy(payload),'success':success,'message':message,'mutates':True,'code_title':code_title,'source_code':source_code,'steps':steps,'final_state':deepcopy(after_state),'pedagogy_schema_version':SEQUENTIAL_FRAME_SCHEMA_VERSION,'pedagogy_schema':sequential_frame_schema(),'learning_profile':deepcopy(SEQUENTIAL_LEARNING_CATALOG['priority_queue']),'instruction_scope':'cp_desencolar initialized scopes, stable ties, outputs before opaque free and guarded counter'}
