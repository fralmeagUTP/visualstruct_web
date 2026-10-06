"""Graph frames from completed instructions of the four downloaded C kernels."""
from __future__ import annotations
from copy import deepcopy
from app.domain.graph.snapshot_pool import SnapshotPool, finish_graph_trace
from typing import Any
from .c_algorithm_subset import Program, GraphMachine, UNINIT, NULL
from .pedagogy import (GRAPH_FRAME_SCHEMA_VERSION, GRAPH_LEARNING_CATALOG,
    build_graph_frame, graph_frame_schema, validate_graph_frame)

OPERATIONS = frozenset({'run_dijkstra','run_bellman_ford','run_prim','run_kruskal'})


def root_variables(state: dict[str,Any]) -> dict[str,Any]:
    if not state['frames']:
        return {}
    return {name:cell['value'] for scope in state['frames'][0]['scopes']
            for name,cell in scope['variables'].items()}


def live_array(state: dict[str,Any], pointer: Any) -> list[Any] | None:
    return next((n['items'] for n in state['heap_nodes'] if n['id']==pointer and 'items' in n),None)


def graph_progress(state: dict[str,Any], operation: str) -> dict[str,Any]:
    variables=root_variables(state);objects={n['id']:n for n in state['heap_nodes']}
    vertices=live_array(state,variables.get('vertices')) or []
    distances={};previous={};visited=[];candidates=[]
    costs=live_array(state,variables.get('dist' if operation in {'run_dijkstra','run_bellman_ford'} else 'costo'))
    prev=live_array(state,variables.get('prev' if operation in {'run_dijkstra','run_bellman_ford'} else 'padre'))
    closed=live_array(state,variables.get('visitado'))
    presence=live_array(state,variables.get('alcanzable' if operation=='run_bellman_ford' else 'candidato'))
    for i,vertex in enumerate(vertices):
        if vertex==UNINIT:
            continue
        key=str(vertex)
        if costs is not None:
            value=costs[i]
            distances[key]=UNINIT if value==UNINIT else '∞' if operation=='run_dijkstra' and value==2147483647 else '∞' if presence is not None and presence[i]==0 else value
        if prev is not None:
            index=prev[i]
            previous[key]=UNINIT if index==UNINIT else None if index==-1 else vertices[index] if 0<=index<len(vertices) else UNINIT
        if closed is not None and closed[i]==1:
            visited.append(key)
        if closed is not None and not closed[i] and costs is not None and costs[i]!=UNINIT:
            if (presence is not None and presence[i]==1) or (operation=='run_dijkstra' and costs[i]<2147483647):
                candidates.append(key)
    selected_index=variables.get('u');selected=str(vertices[selected_index]) if isinstance(selected_index,int) and 0<=selected_index<len(vertices) and vertices[selected_index]!=UNINIT else None
    active_arc=variables.get('a') if operation=='run_bellman_ford' else variables.get('suces')
    active_edge=None;weight=None
    if operation=='run_kruskal':
        aristas=live_array(state,variables.get('aristas'));j=variables.get('j')
        if aristas is not None and isinstance(j,int) and 0<=j<len(aristas):active_arc=aristas[j]
    if active_arc in objects:
        fields=objects[active_arc].get('fields',{})
        if 'origen' in fields:
            active_edge=[str(fields['origen']),str(fields['destino'])];weight=fields['costo']
        elif selected is not None and fields.get('dato')!=UNINIT:
            active_edge=[selected,str(fields['dato'])]
            arc=next((n for n in state['heap_nodes'] if n['borrowed'] and n['kind']=='struct NodoA' and n['fields']['origen']==int(selected) and n['fields']['destino']==fields['dato']),None)
            if arc:weight=arc['fields']['costo']
    root=variables.get('mst' if operation=='run_kruskal' else 'arbol' if operation=='run_prim' else 'camino',NULL)
    result=[];seen=set()
    while isinstance(root,str) and root in objects and root not in seen:
        seen.add(root);node=objects[root];fields=node.get('fields',{})
        if all(fields.get(n,UNINIT)!=UNINIT for n in ['origen','destino','costo','sig']):
            result.append([fields['origen'],fields['destino'],fields['costo']])
        root=fields.get('sig',UNINIT)
    parent_map={};conjunto=variables.get('conjuntos')
    if isinstance(conjunto,dict):
        padres=live_array(state,conjunto.get('padre'))
        if padres:
            for i,par in enumerate(padres):
                if i<len(vertices) and vertices[i]!=UNINIT and isinstance(par,int) and 0<=par<len(vertices) and vertices[par]!=UNINIT:
                    parent_map[str(vertices[i])]=vertices[par]
    edges=[[str(o),str(d)] for o,d,_ in result]
    return dict(mode='mst' if operation in {'run_prim','run_kruskal'} else 'path',
        nodes=list(dict.fromkeys(v for edge in edges for v in edge)),edges=edges,tree_edges=edges,
        distances=distances,previous=previous,visited=visited,candidates=candidates,selected=selected,
        active_edge=active_edge,edge_weight=weight,iteration=variables.get('i'),parents=parent_map,
        result_arcs=result,raw_arc_order=live_array(state,variables.get('aristas')) or [])


def variables(state: dict[str,Any]) -> dict[tuple[str,str],dict[str,Any]]:
    result={}
    retired={n['id'] for n in state['retired_objects']}
    def record(frame,scope,name,typ,value):
        def historical(current):
            if isinstance(current,str) and current in retired:
                return {'historical_identity':current,'usable':False,'value_status':'indeterminate_after_free'}
            if isinstance(current,dict):return {k:historical(v) for k,v in current.items()}
            if isinstance(current,list):return [historical(v) for v in current]
            return current
        safe=historical(value)
        result[(scope,name)]=dict(name=name,type=typ,value=safe,
            scope=frame['function']+'#'+scope,frame_id=frame['id'],usable=safe==value)
    for frame in state['frames']:
        for name,value in frame['parameters'].items():
            record(frame,frame['id'],name,frame['parameter_types'][name],value)
        for scope in frame['scopes']:
            for name,cell in scope['variables'].items():record(frame,scope['id'],name,cell['type'],cell['value'])
    for obj in state['heap_nodes']:
        if 'items' in obj:
            for i,value in enumerate(obj['items']):
                result[(obj['id'],str(i))]=dict(name=f"{obj['id']}[{i}]",type=obj['element_type'],value=value,scope='reserva '+obj['id'],frame_id=None,usable=True)
    return result


def rejection_trace(trace: dict[str,Any], before: dict[str,Any], after: dict[str,Any]) -> dict[str,Any]:
    name='grafo_'+trace['operation_name'].removeprefix('run_')
    line=f'/* Validacion API: no se invoco {name}; cero instrucciones C y cero printf. */'
    trace['source_code']=line+'\n\n'+trace['source_code'];lines=trace['source_code'].splitlines()
    step=dict(line_index=0,line_text=line,state_snapshot=deepcopy(before),state_after=deepcopy(after),console=[],debug={'stage':'input_validation','note':trace['message'],'graph_progress':{}})
    frame=build_graph_frame(operation_name=trace['operation_name'],payload=trace['payload'],step=step,source_lines=lines,success=False)
    frame.update(concept='input_validation',numeric_algorithm=True,condition=None,variables=[],call_stack=[],
        instruction_event={'function':None,'phase':'API_rejection','C_executed':False},
        narration={level:'La aplicacion rechaza antes del TAD. No se atribuyen a C condiciones, ramas, llamadas, memoria ni printf.' for level in ['basic','intermediate','advanced']})
    frame['invariant'].update(holds=None,symbol='?',evidence='Guardas de la API; ninguna invocación del algoritmo C.')
    validate_graph_frame(frame,source_code=trace['source_code']);step['pedagogy']=frame
    trace.update(steps=[step],execution_started=False,numeric_instruction_model=True,
        application_rejection=True,C_instruction_events=[],final_state=deepcopy(after),
        validation={'stage':'API','accepted':False,'message':trace['message']})
    return trace


def build_graph_numeric_trace(*, operation_name: str, payload: dict[str,Any], source_code: str,
    code_title: str, before_state: dict[str,Any], after_state: dict[str,Any], success: bool,
    message: str, _compact: bool = True) -> dict[str,Any]:
    trace=dict(structure_id='graph',operation_name=operation_name,payload=deepcopy(payload),source_code=source_code,
        code_title=code_title,success=success,message=message,mutates=False,steps=[],
        pedagogy_schema_version=GRAPH_FRAME_SCHEMA_VERSION,pedagogy_schema=graph_frame_schema(),
        learning_profile=deepcopy(GRAPH_LEARNING_CATALOG[operation_name]))
    result_wrapper=after_state.get('last_result') or {};result=result_wrapper.get('result') or {}
    cycle_executed=operation_name=='run_bellman_ford' and isinstance(result,dict) and bool(result.get('has_negative_cycle'))
    if not success and not cycle_executed:
        return finish_graph_trace(rejection_trace(trace,before_state,after_state),SnapshotPool(),_compact)
    program=Program(source_code);lines=source_code.splitlines();steps=[];pool=SnapshotPool()
    seed_vertices=[int(n['id']) for n in before_state.get('nodes',[])]
    marks={int(n['id']):int(n.get('marked',0)) for n in before_state.get('nodes',[])}
    arcs=[]
    for edge in before_state.get('edges',[]):
        o,d,w=int(edge['source']),int(edge['target']),int(edge['weight']);arcs.append((o,d,w))
        if not before_state.get('directed') and o!=d:arcs.append((d,o,w))
    pending=deepcopy(before_state);pending['last_result']=None;pending['last_operation']=None
    notes={'enter':'Entra esta función; sólo existen parámetros, todavía no sus locales.',
        'parameter':'Parámetro de esta invocación, con identidad prestada o valor por copia.',
        'declare':'Declara esta variable. No lee ni asigna un valor futuro a almacenamiento sin inicializar.',
        'write':'Completa exactamente esta escritura C; no anticipa la siguiente.',
        'condition':'Evalúa la condición con el estado actual. Sólo continúa su rama real.',
        'operand':'Evalúa este operando. El corto circuito puede omitir los siguientes.',
        'call':'El caller prepara la llamada y queda suspendido; el retorno aún no se asigna.',
        'return':'Calcula el retorno; termina la invocación y después se reanuda el caller.',
        'scope_enter':'Comienza este ámbito; sus futuras declaraciones todavía no existen.',
        'scope_exit':'Termina este ámbito; sus variables ya no son utilizables.',
        'allocate':'Reserva auxiliar propia. malloc deja celdas sin inicializar; calloc escribe ceros.',
        'free':'Retira esta reserva; los aliases sólo conservan identidad histórica, nunca un puntero utilizable.',
        'stdout':'printf escribe ahora el diagnóstico; no había salido antes.',
        'break':'Termina sólo el bucle actual, sin ejecutar su incremento ni futuras iteraciones.',
        'goto':'Salta a la limpieza autorizada, retirando los ámbitos abandonados.',
        'label':'Continúa en la etiqueta real de limpieza.'}
    def callback(event,old,new):
        index=event['line_index'];phase=event['phase'];progress=graph_progress(new,operation_name)
        step=dict(line_index=index,line_text=lines[index],state_snapshot=deepcopy(steps[-1]['state_after'] if steps else before_state),
            state_after=deepcopy(pending),console=[event['value'].rstrip('\n')] if phase=='stdout' else [],
            debug={'stage':phase,'note':notes[phase],'graph_memory':new,'graph_progress':progress})
        # The legacy frame builder infers relaxation from final distances.
        # Disable that inference: C arrays and the actual write events are authoritative.
        frame_step={**step, 'debug':{**step['debug'], 'graph_progress':{**progress,'active_edge':None,'edges':[]}}}
        frame=build_graph_frame(operation_name=operation_name,payload=payload,step=frame_step,source_lines=lines,success=success)
        frame['active_edge']=({'from':progress['active_edge'][0],'to':progress['active_edge'][1],'weight':progress['edge_weight']} if progress['active_edge'] else None)
        frame['condition']=dict(source=event['name'],substituted=event['name']+' ⇒ '+str(event['value']),result=bool(event['value']),
            consequence='Sólo se evalúan operandos registrados; no se fabrica ninguna escritura.') if phase in {'condition','operand'} else None
        if phase in {'condition','operand'}:
            evaluated=[n for n in event.get('evaluated_nodes',[]) if n['pos']>=event['pos'] and n['end']<=event['pos']+len(event['name'])]
            frame['condition']['evaluated_nodes']=evaluated
            shown=[n['source']+'='+str(n['value'].get('exact_integer')) if isinstance(n['value'],dict) and 'exact_integer' in n['value'] else n['source']+'='+str(n['value']) for n in evaluated if n['kind'] in {'name','index','field','call','cast'}]
            frame['condition']['substituted']=event['name']+' ⇒ '+str(bool(event['value']))+(' · '+', '.join(shown) if shown else '')
        previous=variables(old);current=variables(new)
        frame['variables']=[]
        for key in dict.fromkeys([*previous,*current]):
            record=deepcopy(current.get(key) or previous[key]);old_value=previous.get(key,{}).get('value','fuera de ámbito');new_value=current.get(key,{}).get('value','fuera de ámbito')
            record.update(previous=old_value,value=new_value,changed=old_value!=new_value,meaning='Parámetro/local/celda de este ámbito. Las identidades retiradas no son valores de puntero legibles.')
            frame['variables'].append(record)
        frame['call_stack']=[dict(function=f['function'],frame_id=f['id'],depth=i,parameters=deepcopy(f['parameters']),
            locals={name:deepcopy(cell['value']) for scope in f['scopes'] for name,cell in scope['variables'].items()},
            scopes=deepcopy(f['scopes']),scope_status='terminado (retorno)' if (phase=='return' or f.get('status')=='returning') and i==len(new['frames'])-1 else 'activo' if i==len(new['frames'])-1 else 'suspendido',
            return_value=event['value'] if phase=='return' and i==len(new['frames'])-1 else None) for i,f in enumerate(new['frames'])]
        old_objects={n['id']:n for n in old['heap_nodes']};new_objects={n['id']:n for n in new['heap_nodes']}
        frame['memory'].update(objects_before=old['heap_nodes'],objects_after=new['heap_nodes'],
            allocated=[n for key,n in new_objects.items() if key not in old_objects],freed=[n for key,n in old_objects.items() if key not in new_objects],
            retired_objects=new['retired_objects'],symbolic_identities=True,records_are_not_pointer_values=True)
        kind='linear_candidates' if operation_name=='run_dijkstra' else 'candidate_flags_and_costs' if operation_name=='run_prim' else 'stored_arc_passes' if operation_name=='run_bellman_ford' else 'stable_bubble_and_union_find'
        frame['auxiliary'].update(kind=kind,items=progress['raw_arc_order'] if operation_name=='run_kruskal' else progress['candidates'])
        frame['relaxation']=None # Numeric effects are actual arrays/writes, never inferred from the final result.
        frame['concept']='condition' if phase in {'condition','operand'} else 'allocation' if phase=='allocate' else phase
        frame['phase'].update(id=operation_name+'-'+phase,label=phase,goal=notes[phase])
        frame['invariant'].update(holds=None,symbol='?',evidence='Estado parcial observado: sólo arrays/campos inicializados se leen. Grafo prestado sin modificaciones; no se afirma un resultado futuro.')
        frame.update(numeric_algorithm=True,state_before=deepcopy(step['state_snapshot']),state_after=deepcopy(step['state_after']),
            instruction_state_before=old,instruction_state_after=new,memory_state=new,
            instruction_event={**event,'C_executed':True,'statement':lines[index]},highlight_semantics='just-executed',
            narration={level:notes[phase] for level in ['basic','intermediate','advanced']})
        # Explain only a completed Kruskal rejection proved by its C operands.
        if (operation_name == 'run_kruskal' and event['function'] == 'grafo_kruskal'
                and phase == 'condition' and not event['value']):
            root_calls = {node['source']: node['value']
                for node in frame['condition']['evaluated_nodes'] if node['kind'] == 'call'}
            left = root_calls.get('grafo_encontrar_conjunto(&conjuntos, u)')
            right = root_calls.get('grafo_encontrar_conjunto(&conjuntos, v)')
            if type(left) is int and type(right) is int and left >= 0 and left == right:
                explanation = (f'Se descarta esta arista: ambos extremos pertenecen al mismo '
                    f'conjunto (raiz {left}). Agregarla formaria un ciclo; la condicion C '
                    'es falsa y la rama de insercion y Union no se ejecuta.')
                frame['narration'] = {level: explanation
                    for level in ['basic', 'intermediate', 'advanced']}
        validate_graph_frame(frame,source_code=source_code);step['pedagogy']=frame
        if not steps:
            initial=deepcopy(frame);initial.update(variables=[],call_stack=[],condition=None,concept='initial',
                instruction_state_after=deepcopy(old),memory_state=deepcopy(old),
                state_before=deepcopy(before_state),state_after=deepcopy(before_state),instruction_event={'function':None,'phase':'initial','C_executed':False})
            initial['phase'].update(label='Estado inicial',goal='Antes de ejecutar la primera instrucción C.');initial['narration']={level:'Estado inicial: sólo existe el grafo prestado, sin locales, arrays, resultado ni stdout futuros.' for level in ['basic','intermediate','advanced']};frame['initial_frame']=initial
        steps.append(pool.intern(step))
    machine=GraphMachine(program,seed_vertices,arcs,marks,callback=callback)
    fn='grafo_'+operation_name.removeprefix('run_');args=[machine.graph]
    if operation_name in {'run_dijkstra','run_bellman_ford'}:args.extend([int(payload['start']),int(payload['end'])])
    elif operation_name=='run_prim':args.append(int(payload['start']))
    returned=machine.invoke(fn,args);last=deepcopy(steps[-1]);final_memory=machine.snapshot()
    observed=[];pointer=returned
    while pointer!=NULL:
        node=machine.heap[pointer];fields=node['fields'];observed.append([fields['origen'],fields['destino'],fields['costo']]);pointer=fields['sig']
    if operation_name in {'run_prim','run_kruskal'}:
        assert observed==[list(edge) for edge in result['mst_edges']],('C-model/API MST divergence',observed,result)
    else:
        expected_edges=[list(edge[:2]) for edge in observed]
        assert expected_edges==result['path_edges'],('C-model/API path divergence',expected_edges,result)
        assert cycle_executed==('Se detecto un ciclo negativo.' in machine.stdout),('C-model/API cycle divergence',machine.stdout,result)
        if observed:assert sum(w for _,_,w in observed)==result['distance_to_destination']
    # Caller receipt is explicit context outside C, not a fabricated extra C instruction.
    last_return=next(event for event in reversed(machine.events) if event['phase']=='return' and event['function']==fn)
    index=last_return['line_index'];last.update(line_index=index,line_text=lines[index],state_snapshot=deepcopy(pending),state_after=deepcopy(after_state),console=[])
    final_progress=graph_progress(final_memory,operation_name);final_progress['result_arcs']=observed;final_progress['edges']=[[str(o),str(d)] for o,d,_ in observed];final_progress['tree_edges']=final_progress['edges'];final_progress['nodes']=list(dict.fromkeys(v for edge in final_progress['edges'] for v in edge))
    last['debug']=dict(stage='caller_receipt',note='El caller recibe la lista propia devuelta. No se ejecuta otra instrucción C ni otra consulta.',graph_memory=final_memory,graph_progress=final_progress)
    last['pedagogy']=deepcopy(last['pedagogy']);frame=last['pedagogy'];frame.update(concept='caller_receipt',variables=[],call_stack=[],condition=None,relaxation=None,
        source={'line_index':index,'line_text':lines[index]},state_before=deepcopy(pending),state_after=deepcopy(after_state),
        instruction_state_before=deepcopy(steps[-1]['pedagogy']['instruction_state_after']),instruction_state_after=final_memory,memory_state=final_memory,
        instruction_event={'function':None,'phase':'caller_receipt','C_executed':False,'returned':returned},
        narration={level:last['debug']['note'] for level in ['basic','intermediate','advanced']})
    frame['phase'].update(id=operation_name+'-caller',label='Retorno al caller',goal=last['debug']['note']);frame['traversal']['tree_edges']=final_progress['edges'];frame['traversal']['discovery_order']=final_progress['nodes'];frame['auxiliary'].update(items=[],selected=None);validate_graph_frame(frame,source_code=source_code);steps.append(pool.intern(last))
    trace.update(steps=steps,final_state=deepcopy(after_state),numeric_instruction_model=True,execution_started=True,
        highlight_semantics='just-executed',C_instruction_events=machine.events,
        numeric_C_memory=final_memory,returned_arcs=observed,
        instruction_scope='Four named downloaded C kernels and actual helpers; typed symbolic ABI model. Native C execution is QA evidence, not a compiler invocation in the application.',
        resource_scope='No event sampling or final-state interpolation. Finite fixture QA does not certify large-input transport, allocation failures or all C implementations.')
    return finish_graph_trace(trace,pool,_compact)
