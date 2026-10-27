"""Pedagogical projection of recorded canonical-book execution, never a second algorithm."""
from copy import deepcopy
from .book_source import canonical_source, verify_source, STATUS_NAMES, HASHES
from .book_c_subset import UNINIT, NULL, OWNED_RESULTS, BORROWED_RESULTS
from .pedagogy import GRAPH_FRAME_SCHEMA_VERSION, graph_frame_schema, validate_graph_frame, GRAPH_LEARNING_CATALOG
from .snapshot_pool import SnapshotPool, GraphLogicalTrace, finish_graph_trace


def _objects(memory):return {n['id']:n for n in memory.get('heap_nodes',[])}
def _walk(memory,head,kind):
    objects=_objects(memory);items=[];seen=set()
    while head not in (NULL,UNINIT,None) and isinstance(head,str) and head not in seen:
        seen.add(head);node=objects.get(head)
        if not node or node.get('kind')!=kind:break
        fields=node.get('fields',{})
        if fields.get('sig',UNINIT)==UNINIT:break
        items.append(node);head=fields['sig']
    return items


def _graph_root(memory):
    # A by-value g has its own heads; label that view, never call it published.
    for frame in reversed(memory.get('frames',[])):
        if frame.get('status')=='returning':continue
        for scope in reversed(frame.get('scopes',[])):
            cell=scope.get('variables',{}).get('g')
            if cell and cell.get('type')=='Grafo' and isinstance(cell.get('value'),dict):return cell['value'],frame['id']+':g'
        if frame.get('parameter_types',{}).get('g')=='Grafo':return frame['parameters']['g'],frame['id']+':g'
    return memory.get('graph',{'v':NULL,'a':NULL}),'caller:g'


def project_visual(memory,base):
    root,owner=_graph_root(memory);nodes=_walk(memory,root.get('v'),'struct NodoV');arcs=_walk(memory,root.get('a'),'struct NodoA')
    state=deepcopy(base);state['nodes']=[{'id':str(n['fields']['dato']),'label':str(n['fields']['dato']),'value':str(n['fields']['dato']),'marked':n['fields']['marcado']} for n in reversed(nodes)]
    edges=[];seen=set()
    for node in reversed(arcs):
        f=node['fields'];a,b,w=f['origen'],f['destino'],f['costo']
        key=(a,b,w) if state.get('directed') else (min(a,b),max(a,b),w)
        if key in seen:continue
        seen.add(key);edges.append({'source':str(a),'target':str(b),'weight':w})
    state['edges']=edges;state['weighted']=any(e['weight']!=1 for e in edges)
    raw_arcs=[{'source':str(n['fields']['origen']),'target':str(n['fields']['destino']),'weight':n['fields']['costo']} for n in reversed(arcs)]
    state['c_arcs']=raw_arcs
    pairs={(e['source'],e['target'],e['weight']) for e in raw_arcs}
    state['asymmetric_pairs']=[e for e in raw_arcs if e['source']!=e['target'] and (e['target'],e['source'],e['weight']) not in pairs] if not state.get('directed') else []
    state['metadata']={'vertices_count':len(nodes),'edges_count':len(edges),'is_empty':not nodes}
    state['last_result']=None;state['last_operation']=None
    state['book_projection']={'root_owner':owner,'heads':deepcopy(root),'source':'current symbolic C memory','unpublished':owner!='caller:g'}
    objects=_objects(memory)
    state['book_projection']['non_live_heads']=[p for p in root.values() if p not in (NULL,UNINIT) and isinstance(p,str) and p not in objects]
    return state


def _cells(memory):
    cells={}
    for frame in memory.get('frames',[]):
        status='retornado (contexto)' if frame.get('status')=='returning' else 'vivo'
        for name,value in frame.get('parameters',{}).items():
            cells[(frame['id'],name)]={'name':name,'frame_id':frame['id'],'scope':frame['function']+'#'+frame['id'],'type':frame['parameter_types'][name],'value':value,'scope_status':status}
        for scope in frame.get('scopes',[]):
            for name,cell in scope.get('variables',{}).items():cells[(scope['id'],name)]={'name':name,'frame_id':frame['id'],'scope':frame['function']+'#'+scope['id'],**cell,'scope_status':status}
    for name,cell in memory.get('external',{}).items():cells[('caller',name)]={'name':name,'frame_id':'caller','scope':'caller (fuera del TAD)',**cell,'scope_status':'vivo'}
    return cells


def progress(memory,operation):
    objects=_objects(memory);locals_={};work=None;stack=[]
    for frame in memory.get('frames',[]):
        if frame.get('status')=='returning':continue
        variables=dict(frame.get('parameters',{}))
        for scope in frame.get('scopes',[]):variables.update({n:c['value'] for n,c in scope.get('variables',{}).items()})
        locals_.update(variables)
        if isinstance(variables.get('t'),dict) and 'vertices' in variables['t']:work=variables['t']
        if frame['function']=='grafo_dfs_recursivo':stack.append(variables.get('u'))
    def array(pointer):return objects.get(pointer,{}).get('items',[]) if isinstance(pointer,str) else []
    vertices=array(work.get('vertices')) if work else [];dist=array(work.get('dist')) if work else [];prev=array(work.get('prev')) if work else [];used=array(work.get('usado')) if work else [];reached=array(work.get('alcanzable')) if work else []
    distances={};previous={};visited=[];candidates=[]
    for i,v in enumerate(vertices):
        if v==UNINIT:continue
        key=str(v)
        if operation in {'run_dijkstra','run_bellman_ford','run_prim'}:
            distances[key]=dist[i] if i<len(dist) and i<len(reached) and reached[i]==1 else None
            p=prev[i] if i<len(prev) else UNINIT;previous[key]=vertices[p] if type(p)is int and 0<=p<len(vertices) else None
            if i<len(used) and used[i]==1:visited.append(key)
            elif i<len(reached) and reached[i]==1:candidates.append(key)
    u=locals_.get('u');selected=str(vertices[u]) if type(u)is int and 0<=u<len(vertices) and vertices[u]!=UNINIT else None
    queue=[]
    if operation=='run_bfs' and type(locals_.get('frente'))is int and type(locals_.get('final'))is int:
        queue=[str(vertices[i]) for i in prev[locals_['frente']:locals_['final']] if type(i)is int and 0<=i<len(vertices)]
        candidates=queue
    stack=[str(vertices[i]) for i in stack if type(i)is int and 0<=i<len(vertices)]
    pointer=locals_.get('a');active=objects.get(pointer,{}) if isinstance(pointer,str) else {};fields=active.get('fields',{})
    edge=[str(fields['origen']),str(fields['destino'])] if 'origen' in fields else None
    result_pointer=locals_.get('lista',locals_.get('camino',locals_.get('arbol',NULL)))
    if not memory.get('frames'):result_pointer=memory.get('external',{}).get('result',{}).get('value',NULL)
    result_v=_walk(memory,result_pointer,'struct NodoV');result_a=_walk(memory,result_pointer,'struct NodoA')
    nodes=[str(n['fields']['dato']) for n in result_v];edges=[[str(n['fields']['origen']),str(n['fields']['destino'])] for n in result_a]
    parent=array(locals_.get('c',{}).get('padre')) if isinstance(locals_.get('c'),dict) else []
    parents={str(vertices[i]):vertices[v] for i,v in enumerate(parent) if type(v)is int and i<len(vertices) and 0<=v<len(vertices)}
    return {'distances':distances,'previous':previous,'visited':visited,'candidates':candidates,'selected':selected,'queue':queue,'stack':stack,'nodes':nodes,'edges':edges,'tree_edges':edges,'active_edge':edge,'edge_weight':fields.get('costo'),'parents':parents,'iteration':locals_.get('k'),'work':work}


def _text(event,memory):
    phase=event['phase'];name=event.get('name','');value=event.get('value');external=memory.get('external',{});status=external.get('estado',{}).get('value')
    if not event.get('C_executed'):
        if phase=='caller_prepare':return 'El caller prepara los argumentos y las salidas. No se ejecuta una sentencia del TAD en este paso.'
        if phase=='caller_receipt':
            state=STATUS_NAMES[status] if type(status)is int and 0<=status<len(STATUS_NAMES) else 'sin salida GrafoEstado'
            result=event.get('returned');function=event.get('called_function')
            if result==NULL:tail='NULL: no hay lista devuelta que poseer o liberar. NULL no identifica por si solo un error; se consulta el estado.'
            elif function in BORROWED_RESULTS:tail='Recibe una lista prestada del grafo, no una copia ni una lista propia que deba liberar.'
            elif function in OWNED_RESULTS:tail='Recibe una lista propia. Su liberacion requiere una llamada explicita del caller; este paso no la libera.'
            elif function=='grafo_costo_arco':tail=f'Retorno de exito 0/1: {result}; salida entera: {external.get("salida",{}).get("value",UNINIT)}. No confundir el indicador con el costo.'
            else:tail='El caller recibe el retorno y publica sus cabezas cuando corresponde.'
            return f'Retorno al caller: {state}. {tail} No se ejecuta otra instruccion C.'
        return 'Frontera de la aplicacion: '+str(event.get('description') or phase)+'. No es una instruccion del TAD.'
    if phase in {'condition','operand'}:return f'Evalua {name}: {value}. Solo se ejecuta la rama alcanzada; no se anticipan otras escrituras.'
    if phase=='allocate':return 'El asignador devuelve NULL; no hay reserva nueva.' if isinstance(value,dict) and value.get('pointer')==NULL else 'La reserva se crea aqui; calloc inicializa a cero y malloc conserva campos sin inicializar hasta sus escrituras.'
    if phase=='free':return 'free(NULL) no libera ninguna reserva.' if value==NULL else 'Termina esta reserva; su identidad queda solo como registro historico y no se vuelve a leer.'
    if phase=='write':return f'Esta instruccion escribe {name} = {value}. Los demas campos conservan su valor actual.'
    if phase=='declare':return f'Comienza el ambito de {name}; el inicializador aun no se ha completado.'
    if phase=='return':return f'La funcion retorna {value if value is not None else "void"}; no libera automaticamente sus reservas ni publica las cabezas del caller.'
    if phase=='function_exit':return 'Finaliza este ambito de funcion. Sus parametros y locales son contexto historico; el llamador reanuda su instruccion.'
    if phase=='call':return f'Invoca {name}; su retorno aun no se ha asignado.'
    if phase=='stdout':return 'Este printf agrega exactamente el texto registrado a stdout.'
    return {'enter':'Entra esta funcion con sus propios parametros.','parameter':'Recibe este parametro por valor o referencia segun su tipo C.','scope_enter':'Comienza este bloque C.','scope_exit':'Termina este bloque; sus locales salen de ambito.','break':'Sale del bucle actual.','continue':'Continua con la siguiente iteracion del bucle.'}.get(phase,'Transicion registrada de la ejecucion C.')


def _retired_ids(memory):
    return {n['id'] for n in memory.get('retired_objects',[]) if isinstance(n,dict) and 'id' in n}


def _safe_value(value,retired):
    if isinstance(value,str) and value in retired:
        return {'historical_identity':value,'usable':False,'value_status':'indeterminate_after_free'}
    if isinstance(value,dict):return {k:_safe_value(v,retired) for k,v in value.items()}
    if isinstance(value,list):return [_safe_value(v,retired) for v in value]
    return value


def _retired_in(value,retired):
    if isinstance(value,str):return {value} if value in retired else set()
    if isinstance(value,dict):return set().union(*(_retired_in(v,retired) for v in value.values())) if value else set()
    if isinstance(value,list):return set().union(*(_retired_in(v,retired) for v in value)) if value else set()
    return set()


def _frame(operation,payload,step,event,old,new,source):
    p=progress(new,operation);oldcells=_cells(old);newcells=_cells(new);variables=[];retired_references=[]
    oldretired=_retired_ids(old);retired=_retired_ids(new)
    for key in dict.fromkeys([*oldcells,*newcells]):
        record=deepcopy(newcells.get(key) or oldcells[key]);a=oldcells.get(key,{}).get('value','fuera de ambito');b=newcells.get(key,{}).get('value','fuera de ambito')
        safe_a=_safe_value(a,oldretired);safe_b=_safe_value(b,retired);identities=_retired_in(b,retired)
        record.update(previous=safe_a,value=safe_b,changed=safe_a!=safe_b,meaning='Celda real del ambito indicado; las identidades son simbolicas.')
        if key not in newcells:record['scope_status']='terminado'
        if identities:
            record.update(usable=False,value_status='indeterminate_after_free',meaning='Identidad historica de una reserva terminada; no es un puntero utilizable ni una lectura C despues de free.')
            if a==b and safe_a!=safe_b:record['change_reason']='lifetime_ended_not_pointer_write'
            if key in newcells and record.get('scope_status')=='vivo':retired_references.append({'name':record['name'],'frame_id':record['frame_id'],'scope':record['scope'],'identities':sorted(identities),'usable':False,'value_status':'indeterminate_after_free'})
        variables.append(record)
    stack=[];completed=[]
    for i,f in enumerate(new.get('frames',[])):
        entry={'function':f['function'],'frame_id':f['id'],'depth':i,'parameters':f['parameters'],'scopes':f['scopes'],'scope_status':'terminado (contexto del retorno)' if f.get('status')=='returning' else 'activo' if i==len(new['frames'])-1 else 'suspendido'}
        (completed if f.get('status')=='returning' else stack).append(entry)
    live={f['id'] for f in new.get('frames',[])}
    for f in old.get('frames',[]):
        if f['id'] not in live:completed.append({'function':f['function'],'frame_id':f['id'],'parameters':f['parameters'],'scope_status':'terminado (contexto del retorno)','return':event.get('value')})
    oldobj=_objects(old);newobj=_objects(new);note=_text(event,new);condition=None
    if event['phase'] in {'condition','operand'}:condition={'source':event.get('name'),'substituted':str(event.get('name'))+' => '+str(event.get('value')),'result':bool(event.get('value')),'evaluated_operands':event.get('evaluated_nodes',[]),'consequence':'Solo la rama C realmente alcanzada.'}
    vertices=[{'id':n['id'],'status':'active' if n['id']==p['selected'] else 'closed' if n['id'] in p['visited'] else 'frontier' if n['id'] in p['candidates'] else 'undiscovered','distance':p['distances'].get(n['id']),'predecessor':p['previous'].get(n['id'])} for n in step['state_after'].get('nodes',[])]
    kind={'run_bfs':'queue','run_dfs':'recursive_stack','run_kruskal':'union_find','run_bellman_ford':'edge_passes','run_dijkstra':'linear_scan','run_prim':'linear_scan'}.get(operation,'none')
    items=p['queue'] if kind=='queue' else p['stack'] if kind=='recursive_stack' else [{'vertex':k,'parent':v} for k,v in p['parents'].items()] if kind=='union_find' else p['candidates']
    adjacency={n['id']:[] for n in step['state_after'].get('nodes',[])}
    for edge in step['state_after'].get('c_arcs',step['state_after'].get('edges',[])):
        adjacency.setdefault(edge['source'],[]).append({'vertex':edge['target'],'weight':edge['weight']})
    frame={'schema_version':GRAPH_FRAME_SCHEMA_VERSION,'algorithm':operation,'book_instruction_model':True,'query_operation':not operation in {'create_graph','clear_graph','insert_vertex','insert_edge','remove_vertex','remove_edge','generate_random_graph'},'construction_operation':operation in {'create_graph','clear_graph','insert_vertex','insert_edge','remove_vertex','remove_edge','generate_random_graph'},'concept':event['phase'],'case':event['phase'],'phase':{'id':operation+'-'+event['phase'],'label':event['phase'],'goal':note},'source':{'line_index':step['line_index'],'line_text':step['line_text'],'function':event.get('function'),'source_role':event.get('source_role')},'variables':variables,'call_stack':stack,'completed_call_stack':completed,'condition':condition,'auxiliary':{'kind':kind,'items':items,'selected':p['selected'],'iteration':p['iteration'],'candidates':p['candidates']},'vertices':vertices,'active_edge':{'from':p['active_edge'][0],'to':p['active_edge'][1],'weight':p['edge_weight']} if p['active_edge'] else None,'table':{'distances':p['distances'],'previous':p['previous'],'visited':p['visited'],'rows':vertices},'relaxation':None,'representation':{'directed':bool(step['state_after'].get('directed') or step['state_after'].get('asymmetric_pairs')),'policy_directed':bool(step['state_after'].get('directed')),'asymmetric_pairs':step['state_after'].get('asymmetric_pairs',[]),'adjacency':adjacency,'degrees':[]},'traversal':{'tree_edges':p['edges'],'discovery_order':p['nodes'],'active':p['selected']},'memory':{'objects_before':list(oldobj.values()),'objects_after':list(newobj.values()),'allocated':[v for k,v in newobj.items() if k not in oldobj],'freed':[v for k,v in oldobj.items() if k not in newobj],'dangling_references':[],'dangling_references_checked':False,'retired_references':retired_references,'reference_summary':f'{len(retired_references)} celdas vivas conservan identidades historicas no utilizables; no se afirma ausencia de punteros indeterminados.','historical_objects':new.get('retired_objects',[])},'memory_state':new,'instruction_state_before':old,'instruction_state_after':new,'instruction_event':event,'state_before':step['state_snapshot'],'state_after':step['state_after'],'invariant':{'name':'Estado intermedio literal del libro','holds':None,'symbol':'?','evidence':'No se certifica un resultado futuro. Referencias retiradas se conservan solo como historia.'},'narration':{level:note for level in ['basic','intermediate','advanced']},'highlight_semantics':'just-executed'}
    # Raw instruction snapshots remain exact; presentation has explicit tombstones.
    frame['memory_display']={**new,'returned':_safe_value(new.get('returned'),retired),'graph':_safe_value(new.get('graph',{}),retired),'external':_safe_value(new.get('external',{}),retired),'frames':_safe_value(new.get('frames',[]),retired),'heap_nodes':[{**n,**({'fields':_safe_value(n['fields'],retired)} if 'fields' in n else {}),**({'items':_safe_value(n['items'],retired)} if 'items' in n else {})} for n in new.get('heap_nodes',[])]}
    validate_graph_frame(frame,source_code=source);return frame


class BookTraceCollector:
    """Streaming callback: retain interned states, never a duplicate raw transition log."""
    def __init__(self, *, operation_name, payload, before_state, source_code=None):
        self.source=source_code or canonical_source();verify_source(self.source);self.lines=self.source.splitlines()
        self.operation=operation_name;self.payload=deepcopy(payload);self.before=deepcopy(before_state)
        self.pool=SnapshotPool(preserve_tuples=True);self.steps=[];self.previous=self.pool.intern(self.before)
        self.last_memory=None;self.events=[];self.closed=False

    def _append(self,event,old,new,visual):
        is_c=bool(event.get('C_executed'));idx=event['line_index'] if is_c else None;line=self.lines[idx] if is_c else ''
        note=_text(event,new)
        step={'step_index':len(self.steps),'line_index':idx,'line_text':line,'event_type':'line' if is_c else 'host_boundary','phase':event['phase'],'delay_ms':100,'state_snapshot':self.previous,'state_after':visual,'console':[event['value']] if event['phase']=='stdout' else [],'debug':{'stage':event['phase'],'note':note,'graph_memory':new,'graph_progress':progress(new,self.operation)}}
        if event['phase'] in {'condition','operand'}:step['condition_result']=bool(event.get('value'))
        step['pedagogy']=_frame(self.operation,self.payload,step,event,old,new,self.source)
        if not self.steps:
            initial=deepcopy(step['pedagogy']);initial.update(variables=[],call_stack=[],completed_call_stack=[],condition=None,memory_state=old,memory_display=old,instruction_state_after=old,state_before=self.before,state_after=self.before)
            initial['instruction_event']={'phase':'initial','function':None,'line_index':-1,'C_executed':False,'source_role':'application'}
            initial['source']={'line_index':None,'line_text':'','function':None,'source_role':'application'}
            initial['phase']={'id':'initial','label':'Estado inicial','goal':'Antes de ejecutar C o preparar argumentos.'}
            initial['narration']={k:'Estado previo; no hay locales ni resultado futuros.' for k in ['basic','intermediate','advanced']};step['pedagogy']['initial_frame']=initial
        interned=self.pool.intern(step);self.steps.append(interned);self.previous=interned['state_after'];self.last_memory=new

    def callback(self,event,before,after):
        if self.closed:raise ValueError('Book trace collector already finished')
        old=self.pool.intern(before);new=self.pool.intern(after);event=self.pool.intern(event)
        if self.last_memory is not None and old is not self.last_memory:raise ValueError('Book trace memory discontinuity; caller boundary must be recorded')
        if event.get('C_executed'):self.events.append(event)
        self._append(event,old,new,self.pool.intern(project_visual(new,self.before)))

    def finish(self, *, after_state, success=True, message='', compact=False, result=None):
        if self.closed:raise ValueError('Book trace collector already finished')
        executed=bool(self.steps)
        memory=self.last_memory or self.pool.intern({'frames':[],'heap_nodes':[],'retired_objects':[],'external':{},'graph':{'v':NULL,'a':NULL},'returned':UNINIT,'console_stdout':''})
        boundary={'phase':'api_publication' if executed else 'api_rejection','function':None,'line_index':-1,'C_executed':False,'source_role':'application','description':message or 'Publica el resultado y la politica de representacion de la aplicacion'}
        self._append(boundary,memory,memory,self.pool.intern(deepcopy(after_state)));self.closed=True
        trace=GraphLogicalTrace(snapshot_pool=self.pool,structure_id='graph',operation_name=self.operation,payload=self.payload,success=success,message=message,source_code=self.source,source_sha256=HASHES['tad_grafo.c'],code_title='Grafo — C canónico del libro',steps=self.steps,final_state=deepcopy(after_state),console_mode='events',book_instruction_model=True,execution_started=executed,C_instruction_events=self.events,pedagogy_schema_version=GRAPH_FRAME_SCHEMA_VERSION,pedagogy_schema=graph_frame_schema(),highlight_semantics='just-executed')
        return finish_graph_trace(trace,self.pool,compact)


def build_book_trace(*,operation_name,payload,before_state,after_state,execution,success=True,message='',compact=False):
    collector=BookTraceCollector(operation_name=operation_name,payload=payload,before_state=before_state,source_code=execution.get('source_code'))
    for t in execution.get('transitions',[]):collector.callback(t['event'],t['before'],t['after'])
    return collector.finish(after_state=after_state,success=success,message=message,compact=compact)
