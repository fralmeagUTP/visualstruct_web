"""Causal readonly cp_frente: const borrowed scopes, stable aliases and independent outputs."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.domain.sequential.pedagogy import build_sequential_frame, validate_sequential_frame, sequential_frame_schema, SEQUENTIAL_FRAME_SCHEMA_VERSION, SEQUENTIAL_LEARNING_CATALOG


def build_priority_queue_front_trace(*, payload: dict[str, Any], source_code: str, code_title: str,
        before_state: dict[str, Any], after_state: dict[str, Any], success: bool, message: str,
        null_root: bool = False, null_value: bool = False, null_priority: bool = False,
        caller_value: int = 0, caller_priority: int = 0) -> dict[str, Any]:
    """Execute C statement boundaries; Borrowed const pointers observe live fields; the queue and heap never change."""
    lines=source_code.replace('\r\n','\n').split('\n');steps=[]
    items=[] if null_root else before_state.get('items',[])
    heap=[{'id':f'N{i+1}','address':f'N{i+1}','type':'CPNodo','alive':True,'allocated':True,'freed':False,
        'fields_valid':True,'initialized_mask':7,'field_validity':{'valor':True,'prioridad':True,'sgte':True},'status':'linked',
        'fields':{'valor':int(x['value']),'prioridad':int(x['priority']),'sgte':f'N{i+2}' if i+1<len(items) else None}}
        for i,x in enumerate(items)]
    objects={x['id']:x for x in heap};head=heap[0]['id'] if heap else None;rear=heap[-1]['id'] if heap else None
    quantity=int(before_state.get('cantidad',before_state.get('size',len(items))))
    aliases={};out={'valor':caller_value,'prioridad':caller_priority};written={'valor':False,'prioridad':False}
    active=True;result=None
    def state():
        current=deepcopy(before_state);reachable=[];ptr=head
        while ptr:
            node=objects[ptr];reachable.append({'value':node['fields']['valor'],'priority':node['fields']['prioridad']});ptr=node['fields']['sgte']
        current.update(items=reachable,size=len(reachable),empty=not reachable,delante=head or 'NULL',atras=rear or 'NULL',cantidad=quantity)
        # Alias values are symbolic borrowed live-node IDs; return snapshots are outside local scope.
        current.update({k:(v or 'NULL') for k,v in aliases.items()})
        current.update({k:v for k,v in out.items() if written[k]})
        return current
    def emit(event,token,condition=None):
        index=next(i for i,l in enumerate(lines) if token in l);scope='active' if active else 'ended'
        variables=[];pointers=[]
        root={'type':'ColaPrioridad','identity':'&cp','alive':not null_root,'valid':not null_root,'front':head,'rear':rear,'quantity':quantity}
        for name,target in [('delante',head),('atras',rear)]:
            variables.append({'name':name,'type':'CPNodo *','value':target,'initialized':not null_root,'valid':not null_root,'scope':'caller','scope_state':'active'})
            pointers.append({'name':name,'type':'CPNodo *','target':target,'initialized':not null_root,'valid':not null_root,'scope':'caller','scope_state':'active'})
        variables.append({'name':'cantidad','type':'int','value':quantity,'initialized':not null_root,'valid':not null_root,'scope':'caller','scope_state':'active'})
        local=[]
        for name,typ,target in [('cola','const ColaPrioridad *',None if null_root else '&cp'),('valor','int *',None if null_value else '&caller_valor'),('prioridad','int *',None if null_priority else '&caller_prioridad')]:
            local.append({'name':name,'type':typ,'value':target,'initialized':True,'valid':active,'scope':'cp_frente','scope_state':scope})
            pointers.append({'name':name,'type':typ,'target':target,'initialized':True,'valid':active,'scope':'cp_frente','scope_state':scope})
        for name,value in aliases.items():
            usable=active and (value is None or value in objects);dangling=value is not None and value not in objects
            local.append({'name':name,'type':'const CPNodo *','value':value,'initialized':True,'valid':usable,'dangling':dangling,'scope':'cp_frente','scope_state':scope,'meaning':'Identidad histÃ³rica guardada antes de free; no evaluar si es invÃ¡lida.'})
            pointers.append({'name':name,'type':'const CPNodo *','target':value,'initialized':True,'valid':usable,'dangling':dangling,'historical_id':value if dangling else None,'scope':'cp_frente','scope_state':scope})
        for name in declared:
            if name not in aliases:local.append({'name':name,'type':'const CPNodo *','value':None,'initialized':False,'valid':False,'scope':'cp_frente','scope_state':scope,'meaning':'Indeterminado; no leer ni interpretar como NULL.'})
        for name in ['valor','prioridad']:
            variables.append({'name':'caller_'+name,'type':'int','value':out[name],'initialized':True,'written':written[name],'valid':True,'scope':'caller','scope_state':'active','address':'&caller_'+name})
        variables.extend(local)
        calls=[{'function':'cp_frente','parameters':{'cola':None if null_root else '&cp','valor':None if null_value else '&caller_valor','prioridad':None if null_priority else '&caller_prioridad'},'return_type':'bool','return':None,'continuation':'Caller recibe bool y conserva ambas copias int.'}] if active else []
        scopes=[{'id':'cp_frente','kind':'function','state':scope,'scope_state':scope,'variables':deepcopy(local)}]
        memory_snapshot=state()
        # C stores remain in their physical snapshot; return exposes only the public TAD.
        current=memory_snapshot if active else {key:value for key,value in memory_snapshot.items()
            if key not in {'delante','atras','cantidad','actual','prev','objetivo','objetivoPrev','valor','prioridad'}}
        if not active:
            current['out_index']=min(range(len(current['items'])),key=lambda i:current['items'][i]['priority']) if current['items'] else -1
        previous=deepcopy(steps[-1]['state_after'] if steps else before_state)
        debug={'token':event,'function':'cp_frente','root':deepcopy(root),'variables':deepcopy(variables),'pointers':deepcopy(pointers),'scopes':deepcopy(scopes),'call_stack':deepcopy(calls),'heap':deepcopy(heap),'result':result}
        step={'step_index':len(steps),'line_index':index,'line_text':lines[index],'event_type':event,'phase':'progress','delay_ms':100,'state_snapshot':previous,'state_after':current,'console':[],'condition_result':condition,'function_name':'cp_frente','debug':debug}
        frame=build_sequential_frame(structure_id='priority_queue',operation_name='frente',payload=payload,step=step,success=success)
        invalid=[{'name':x['name'],'historical_id':x['target'],'usable':False} for x in pointers if x.get('dangling')]
        memory={'kind':'priority_queue_front','root':deepcopy(root),'heap':deepcopy(heap),'variables':deepcopy(variables),'pointers':deepcopy(pointers),'call_stack':deepcopy(calls),'scope_state':scope,'outputs':{'value':out['valor'],'priority':out['prioridad'],'value_written':written['valor'],'priority_written':written['prioridad']},'invalid_aliases':invalid,'result':result}
        substituted=None
        if condition is not None:
            if token.startswith('if (cola == NULL'):substituted=('NULL' if null_root else '&cp')+' == NULL || '+(head or 'NULL')+' == NULL || '+('NULL' if null_value else '&caller_valor')+' == NULL || '+('NULL' if null_priority else '&caller_prioridad')+' == NULL (cortocircuito)'
            elif token.startswith('while'):substituted=(aliases.get('actual') or 'NULL')+' != NULL'
            elif token.startswith('if (actual->prioridad'):substituted=str(objects[aliases['actual']]['fields']['prioridad'])+' < '+str(objects[aliases['objetivo']]['fields']['prioridad'])
        frame.update(variables=variables,pointers=pointers,scopes=scopes,call_stack=calls,heap_objects=deepcopy(heap),memory_state=deepcopy(memory_snapshot),front_memory=memory,
            heap_transition={'kind':'stable','before':deepcopy(steps[-1]['pedagogy']['heap_objects'] if steps else heap),'after':deepcopy(heap),'freed':[],'dangling_references':[]},
            condition=None if condition is None else {'source':lines[index],'substituted':substituted,'result':condition,'consequence':'EvaluaciÃ³n C con cortocircuito y operandos vivos.'})
        frame['source']['function']='cp_frente';frame['invariant']={'text':'BÃºsqueda parcial; candidato mÃ­nimo del prefijo, empates conservan primer nodo.','holds':True,'symbol':'âœ“','evidence':'RaÃ­ces y cantidad sÃ³lo cambian en sus stores; IDs histÃ³ricos separados de lecturas vivas.'}
        narration=('Declara CPNodo * indeterminado; todavÃ­a no existe valor usable.' if event=='declare' else 'Free opaco terminÃ³; el objeto desaparece del heap vivo y todos sus aliases quedan inutilizables.' if event=='free' else 'Retorno bool y fin del scope local; caller y raÃ­ces restantes siguen vivos.' if event=='return' else 'Copia int al almacenamiento independiente del caller sin modificar el nodo ni la cola.' if event=='output' else 'EvalÃºa la condiciÃ³n real y recorre solamente su rama.' if condition is not None else 'Ejecuta esta asignaciÃ³n C; conserva identidad de objetos y demÃ¡s valores.')
        for level in frame['narration']:frame['narration'][level]=narration
        if event=='return':frame['concept']='return'
        validate_sequential_frame(frame,source_code=source_code);step['pedagogy']=frame;steps.append(step)
    declared=[];emit('entry','bool cp_frente(')
    for name in ['actual','objetivo']:declared.append(name);emit('declare','const CPNodo *'+name+';')
    reject=null_root or head is None or null_value or null_priority;emit('guard','if (cola == NULL',reject)
    if reject:result=False;active=False;emit('return','return false;')
    else:
        aliases['objetivo']=head;emit('assign','objetivo = cola->delante;')
        aliases['actual']=objects[head]['fields']['sgte'];emit('assign','actual = cola->delante->sgte;')
        while True:
            emit('loop','while (actual != NULL)',aliases['actual'] is not None)
            if aliases['actual'] is None:break
            better=objects[aliases['actual']]['fields']['prioridad']<objects[aliases['objetivo']]['fields']['prioridad'];emit('compare','if (actual->prioridad < objetivo->prioridad)',better)
            if better:aliases['objetivo']=aliases['actual'];emit('assign','objetivo = actual;')
            aliases['actual']=objects[aliases['actual']]['fields']['sgte'];emit('assign','actual = actual->sgte;')
        node=objects[aliases['objetivo']]
        out['valor']=node['fields']['valor'];written['valor']=True;emit('output','*valor = objetivo->valor;')
        out['prioridad']=node['fields']['prioridad'];written['prioridad']=True;emit('output','*prioridad = objetivo->prioridad;')
        result=True;active=False;emit('return','return true;')
    steps[0]['phase']='start';steps[-1]['phase']='end'
    return {'structure_id':'priority_queue','operation_name':'frente','payload':deepcopy(payload),'success':success,'message':message,'mutates':False,'code_title':code_title,'source_code':source_code,'steps':steps,'final_state':deepcopy(after_state),'pedagogy_schema_version':SEQUENTIAL_FRAME_SCHEMA_VERSION,'pedagogy_schema':sequential_frame_schema(),'learning_profile':deepcopy(SEQUENTIAL_LEARNING_CATALOG['priority_queue']),'instruction_scope':'cp_frente const scopes, stable ties, readonly live aliases, two caller outputs and bool return'}
