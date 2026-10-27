"""Instruction effects of the downloadable BFS and its real FIFO helpers.

Identities are symbolic, monotonically allocated and never reused. Snapshots
describe completed instructions, not interpolation from a future traversal.
Normal successful allocation is modeled; allocation-failure injection is not.
"""
from copy import deepcopy
from .snapshot_pool import SnapshotPool, GraphLogicalTrace
import re
from app.domain.graph.pedagogy import build_graph_frame, validate_graph_frame

UNINIT = 'sin inicializar'
NULL = 'NULL'


def build_bfs_trace(trace, before, after):
    source = trace['source_code']; lines = source.splitlines(); ranges = {}
    for i, row in enumerate(lines):
        m = re.match(r'\s*(?:void|int|Grafo|ListaVertice)\s+(\w+)\s*\(', row)
        if m:
            depth = 0
            for j in range(i, len(lines)):
                depth += lines[j].count('{') - lines[j].count('}')
                if j > i and depth == 0:
                    ranges[m[1]] = (i, j); break
    heap = {}; serial = 0; frames = []; retired = []; steps = []; pool = SnapshotPool(preserve_tuples=True); allocations = frees = 0
    vertices = [int(n['id']) for n in before.get('nodes', [])]
    arcs = []
    for e in before.get('edges', []):
        pair = (int(e['source']), int(e['target']))
        arcs.append(pair)
        if not before.get('directed') and pair[0] != pair[1]: arcs.append(pair[::-1])
    # C publishes each seed at the front of its list, whereas the visual model
    # serializes vertices/arcs in insertion order.
    vhead = NULL
    for value in vertices:
        key = 'V' + str(value); heap[key] = dict(id=key, kind='vertex', value=value, mark=next((int(n.get('marked',0)) for n in before.get('nodes',[]) if int(n['id'])==value),0), next=vhead); vhead=key
    ahead = NULL
    for i, (origin, target) in enumerate(arcs):
        key='E'+str(i+1);heap[key]=dict(id=key,kind='arc',origin=origin,target=target,next=ahead);ahead=key
    graph={'v':vhead,'a':ahead}; queue={'delante':NULL,'atras':NULL}; bfs=None; returned=NULL; published=NULL
    parents={}; discovery=[]; active=None; frame_counter=0
    def node(key):
        assert key in heap, ('read of non-live pointer',key)
        return heap[key]
    def chain(key):
        items=[];seen=set()
        while key in heap and key not in seen:
            seen.add(key);n=node(key);items.append(heap_node_views[key][1]);key=n.get('next',UNINIT)
        return items
    def val(f,n):return f['locals'].get(n,f['parameters'].get(n,UNINIT))
    heap_snapshot=None;heap_fingerprint=None;heap_dirty=True;heap_epoch=0;chain_cache={};marks_snapshot=None;marks_fingerprint=None
    # Cache immutable published views, never the live C-model dictionaries.
    # Complete typed value revisions catch enter/put/alias rewrite/scope exit.
    frame_views={};heap_node_views={};retired_snapshot=None;retired_revision=-1
    graph_snapshot=pool.intern(deepcopy(graph));queue_views={};frame_list_views={};snapshot_views={};progress_views={};discovery_views={};parent_views={}
    def revision(value):
        if isinstance(value,dict):return ('dict',tuple((revision(k),revision(v)) for k,v in value.items()))
        if isinstance(value,list):return ('list',tuple(map(revision,value)))
        if isinstance(value,tuple):return ('tuple',tuple(map(revision,value)))
        return pool.primitive_key(value)
    def frozen_frames():
        views=[]
        for frame in frames:
            token=revision(frame);cached=frame_views.get(frame['id'])
            if cached is None or cached[0]!=token:
                cached=(token,pool.intern(deepcopy(frame)));frame_views[frame['id']]=cached
            views.append(cached[1])
        token=tuple(map(id,views))
        if token not in frame_list_views:frame_list_views[token]=pool.intern(views)
        return frame_list_views[token]
    def snapshot():
        nonlocal heap_snapshot,heap_fingerprint,heap_epoch,marks_snapshot,marks_fingerprint,retired_snapshot,retired_revision,heap_dirty
        fingerprint=tuple((key,tuple(node.items())) for key,node in heap.items()) if heap_dirty else heap_fingerprint
        heap_dirty=False
        if fingerprint!=heap_fingerprint:
            heap_fingerprint=fingerprint;heap_epoch+=1;chain_cache.clear()
            views=[]
            for key,node_token in fingerprint:
                cached=heap_node_views.get(key)
                if cached is None or cached[0]!=node_token:
                    cached=(node_token,pool.intern(deepcopy(heap[key])));heap_node_views[key]=cached
                views.append(cached[1])
            heap_snapshot=pool.intern(views)
        def frozen_chain(pointer):
            if pointer not in chain_cache:chain_cache[pointer]=pool.intern(chain(pointer))
            return chain_cache[pointer]
        mark_key=tuple((heap['V'+str(v)]['value'],heap['V'+str(v)]['mark']) for v in reversed(vertices))
        if mark_key!=marks_fingerprint:
            marks_fingerprint=mark_key
            marks_snapshot=pool.intern([{'vertex':n['value'],'mark':n['mark'],'id':n['id']} for n in frozen_chain(vhead)])
        root=val(bfs,'recorrido') if bfs else NULL
        suces=val(bfs,'suces') if bfs else NULL
        # Retired records are appended once by free(), then never modified.
        if retired_revision!=len(retired):
            retired_snapshot=pool.intern([*(() if retired_snapshot is None else retired_snapshot),*map(lambda n:pool.intern(deepcopy(n)),retired[retired_revision if retired_revision>=0 else 0:])])
            retired_revision=len(retired)
        queue_token=revision(queue)
        if queue_token not in queue_views:queue_views[queue_token]=pool.intern(deepcopy(queue))
        frame_view=frozen_frames();queue_view=queue_views[queue_token]
        discovery_token=tuple(discovery);parent_token=tuple(parents.items())
        if discovery_token not in discovery_views:discovery_views[discovery_token]=pool.intern(list(discovery))
        if parent_token not in parent_views:parent_views[parent_token]=pool.intern(dict(parents))
        snapshot_token=(heap_epoch,id(retired_snapshot),id(frame_view),id(queue_view),root,suces,returned,published,discovery_token,parent_token,active,allocations,frees)
        if snapshot_token not in snapshot_views:
            snapshot_views[snapshot_token]=pool.intern(dict(heap_nodes=heap_snapshot,freed_nodes=retired_snapshot,frames=frame_view,
                    graph=graph_snapshot,graph_marks=marks_snapshot,
                    queue=queue_view,queue_nodes=frozen_chain(queue['delante']),result_nodes=frozen_chain(root),successor_nodes=frozen_chain(suces),
                    returned=returned,published=published,discovery=discovery_views[discovery_token],parents=parent_views[parent_token],
                    active=active,allocations=allocations,frees=frees,console_stdout=''))
        return snapshot_views[snapshot_token]
    visual_cache={};frame_cache={};call_stack_cache={};variables_cache={};variable_records={};live_nodes_cache={}
    def locate(fn,text):
        lo,hi=ranges[fn]
        for i in range(lo,hi+1):
            if text in lines[i]:return i
        raise AssertionError((fn,text))
    def emit(fn,text,phase='statement',change=None,result=None,expression=None,substituted=None,ix=None):
        old=snapshot()
        if change:change()
        new=snapshot();index=locate(fn,text) if ix is None else ix
        # State shown by the trace player is the state AFTER the highlighted
        # completed instruction. last_result stays pending until caller resume.
        visual_key=(id(new['graph_marks']),phase=='caller')
        if visual_key not in visual_cache:
            visual=deepcopy(after if phase=='caller' else before)
            if phase!='caller':
                visual['last_result']=None;visual['last_operation']=None
                marks={v['vertex']:v['mark'] for v in new['graph_marks']}
                for n in visual.get('nodes',[]):n['marked']=marks.get(int(n['id']),0)
            visual_cache[visual_key]=pool.intern(visual)
        visual=visual_cache[visual_key]
        progress_key=(id(new['result_nodes']),id(new['queue_nodes']),id(new['graph_marks']),active,id(new['parents']),id(new['discovery']))
        if progress_key not in progress_views:
            res=[str(n['value']) for n in new['result_nodes'] if n.get('value')!=UNINIT]
            q=[str(n['value']) for n in new['queue_nodes'] if n.get('value')!=UNINIT]
            marked=[str(n['vertex']) for n in new['graph_marks'] if n['mark']]
            edges=[[str(p),str(c)] for c,p in parents.items() if p is not None]
            progress_views[progress_key]=pool.intern({'mode':'traversal','nodes':res,'edges':edges,'tree_edges':edges,'queue':q,'visited':marked,
                  'selected':None if active is None else str(active),'previous':{str(k):v for k,v in parents.items()},'discovery':list(map(str,discovery))})
        progress=progress_views[progress_key]
        res=progress['nodes'];q=progress['queue'];marked=progress['visited'];edges=progress['edges']
        step={'line_index':index,'line_text':lines[index],'state_snapshot':steps[-1]['state_after'] if steps else before,'state_after':visual,
              'console':[],'debug':{'bfs_memory':new,'stage':phase,'note':'Instrucción completada; no hay salida printf en esta ruta normal.','graph_progress':progress}}
        frame_key=(index,phase,id(step['state_snapshot']),id(visual),id(progress))
        if frame_key not in frame_cache:
            base=build_graph_frame(operation_name='run_bfs',payload=trace['payload'],step=step,source_lines=lines,success=trace['success'])
            for row in base['vertices']:
                row['marked']=int(row['id'] in marked);row['status']='processed' if row['id'] in res else 'discovered' if row['id'] in marked else 'undiscovered'
            frame_cache[frame_key]=pool.intern(base)
        ped={**frame_cache[frame_key]}
        for field in ('memory','auxiliary','traversal','invariant'):ped[field]=dict(ped[field])
        ped['condition']=None if phase not in {'condition','operand'} else {'source':expression or text,'substituted':substituted or expression or text,'result':bool(result),'consequence':'Evalúa operandos actuales; no modifica la estructura.'}
        shown=old['frames'] if phase=='return' else new['frames']
        stack_key=(id(shown),phase=='return',revision(result) if phase=='return' else None)
        if stack_key not in call_stack_cache:
            call_stack_cache[stack_key]=pool.intern([dict(function=f['function'],frame_id=f['id'],depth=i,parameters=f['parameters'],locals=f['locals'],scope_status='terminado (retorno)' if phase=='return' and i==len(shown)-1 else 'activo' if i==len(shown)-1 else 'suspendido',return_value=result if phase=='return' and i==len(shown)-1 else None) for i,f in enumerate(shown)])
        ped['call_stack']=call_stack_cache[stack_key]
        variable_key=(id(old['frames']),id(new['frames']))
        if variable_key not in variables_cache:
            oldvars={(f['id'],n):v for f in old['frames'] for n,v in {**f['parameters'],**f['locals']}.items()}
            newvars={(f['id'],n):v for f in new['frames'] for n,v in {**f['parameters'],**f['locals']}.items()}
            names={f['id']:f['function'] for f in [*old['frames'],*new['frames']]}
            def typ(n,fn):return 'int' if n in {'inicio','x','valor','actual','existe','num'} else 'Grafo' if n=='g' else 'Cola *' if n=='q' else 'Cola' if n=='cola' else 'ListaArco' if n=='k' and fn=='grafo_sucesores' else 'NodoCola *' if n=='aux' else 'ListaVertice'
            records=[]
            for f,n in dict.fromkeys([*oldvars,*newvars]):
                previous=oldvars.get((f,n),'fuera de ámbito');value=newvars.get((f,n),'fuera de ámbito')
                changed=oldvars.get((f,n))!=newvars.get((f,n))
                token=(f,n,revision(previous),revision(value),changed)
                if token not in variable_records:
                    variable_records[token]=pool.intern(dict(name=n,scope=names[f]+'#'+f,frame_id=f,type=typ(n,names[f]),previous=previous,value=value,changed=changed,meaning='Local o parámetro de esta invocación; una identidad retirada es un registro, no un puntero utilizable.'))
                records.append(variable_records[token])
            variables_cache[variable_key]=pool.intern(records)
        ped['variables']=variables_cache[variable_key]
        for state in (old,new):
            identity=id(state['heap_nodes'])
            if identity not in live_nodes_cache:live_nodes_cache[identity]={n['id'] for n in state['heap_nodes']}
        liveold=live_nodes_cache[id(old['heap_nodes'])];livenew=live_nodes_cache[id(new['heap_nodes'])]
        ped['memory'].update(objects_before=old['heap_nodes'],objects_after=new['heap_nodes'],allocated=[n for n in new['heap_nodes'] if n['id'] not in liveold],freed=[n for n in old['heap_nodes'] if n['id'] not in livenew],retired_objects=new['freed_nodes'],symbolic_identities=True,records_are_not_pointer_values=True)
        ped['concept']='free' if ped['memory']['freed'] else 'allocation' if ped['memory']['allocated'] else 'condition' if ped['condition'] else 'return' if phase in {'return','caller'} else 'assignment'
        ped['auxiliary'].update(items=q,selected=active);ped['traversal'].update(discovery_order=progress['discovery'],output_order=res,tree_edges=edges)
        ped.update(state_before=step['state_snapshot'],state_after=step['state_after'],instruction_state_before=old,instruction_state_after=new,memory_state=new,highlight_semantics='just-executed',instruction_event={'function':fn,'phase':phase,'condition':result if phase in {'condition','operand'} else None,'statement':lines[index]})
        ped['invariant'].update(holds=None,symbol='?',evidence='Estado parcial real: marcado al encolar; resultado al publicar el enlace. No se anticipa el recorrido final.')
        descriptions={'enter':'Entra la función con sus propios parámetros; todavía no existen los futuros locales.', 'call':'El caller queda suspendido; el resultado de la llamada aún no se asigna.', 'return':'Retorna el valor y termina este ámbito; la asignación del caller queda pendiente.', 'caller':'El caller recibe la lista propia devuelta; su liberación ocurre fuera de BFS.', 'scope_exit':'Termina el bloque de esta iteración; sus locales salen de ámbito.', 'free':'Termina la reserva indicada. Los aliases anteriores conservan solo identidad histórica no utilizable.', 'condition':'Evalúa la condición actual sin cambiar enlaces, cola ni marcas.'}
        narration=descriptions.get(phase,'Completa solo esta escritura o declaración C. Los campos sin inicializar no se leen y no se fabrica una mutación visual.')
        ped['narration']={level:narration for level in ['basic','intermediate','advanced']}
        if not steps:
            initial=deepcopy(ped);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(ped['instruction_state_before']))
            initial['phase']['label']='Estado inicial';ped['initial_frame']=initial
        validate_graph_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(pool.intern(step))
    def enter(fn,params):
        nonlocal frame_counter
        frame_counter+=1;f={'id':'F'+str(frame_counter),'function':fn,'parameters':deepcopy(params),'locals':{}}
        emit(fn,fn+'(','enter',lambda:frames.append(f),ix=ranges[fn][0]);return f
    def put(f,text,name,value):emit(f['function'],text,change=lambda:f['locals'].__setitem__(name,deepcopy(value)))
    def cond(f,text,result,expr=None,sub=None):emit(f['function'],text,'condition',result=result,expression=expr,substituted=sub);return result
    def leave(f,text,result):emit(f['function'],text,'return',lambda:frames.pop(),result=result,ix=ranges[f['function']][1] if text=='}' else None);return result
    def call(f,text,fn,*args):
        declare='actual' if text.startswith('int actual') else 'suces' if text.startswith('ListaVertice suces') else None
        emit(f['function'],text,'call',(lambda:f['locals'].__setitem__(declare,UNINIT)) if declare else None);return fn(*args)
    def allocate(f,text,name,kind):
        def change():
            nonlocal serial,allocations,heap_dirty
            heap_dirty=True
            serial+=1;key='N'+str(serial);allocations+=1;heap[key]=dict(id=key,kind=kind,value=UNINIT,next=UNINIT);
            if kind!='queue':heap[key]['mark']=UNINIT
            f['locals'][name]=key
        emit(f['function'],text,'allocate',change);return val(f,name)
    def write(f,text,key,field,value):
        def change():
            nonlocal heap_dirty
            node(key)[field]=deepcopy(value);heap_dirty=True
        emit(f['function'],text,change=change)
    def free(f,text,key):
        def change():
            nonlocal frees,heap_dirty
            heap_dirty=True
            retired.append({**heap.pop(key),'usable':False});frees+=1
            for frame in frames:
                for area in ['parameters','locals']:
                    for n,v in frame[area].items():
                        if v==key:frame[area][n]=key+' (identidad histórica; valor indeterminado)'
        emit(f['function'],text,'free',change)
    def scan(fn,x=None):
        f=enter(fn,{'g':graph,**({} if x is None else {'x':x})});put(f,'ListaVertice k = g.v;','k',vhead)
        while cond(f,'while (k != NULL)',val(f,'k')!=NULL,sub=str(val(f,'k'))+' != NULL'):
            k=val(f,'k')
            if fn=='grafo_desmarcar':write(f,'k->marcado = 0;',k,'mark',0)
            elif cond(f,'if (k->dato == x)',node(k)['value']==x,sub=str(node(k)['value'])+' == '+str(x)):
                if fn=='grafo_marcado_vertice':return leave(f,'return k->marcado;',node(k)['mark'])
                write(f,'k->marcado = 1;',k,'mark',1);emit(fn,'break;','break');break
            put(f,'k = k->sig;','k',node(k)['next'])
        return leave(f,'return 0;' if fn=='grafo_marcado_vertice' else 'return g;',0 if fn=='grafo_marcado_vertice' else graph)
    def enqueue(value):
        f=enter('cola_encolar',{'q':'&cola','valor':value});cond(f,'if (q == NULL)',False,sub='&cola == NULL')
        aux=allocate(f,'struct NodoCola *aux =','aux','queue');cond(f,'if (aux == NULL)',False,sub=aux+' == NULL')
        write(f,'aux->nro = valor;',aux,'value',value);write(f,'aux->sgte = NULL;',aux,'next',NULL)
        if cond(f,'if (q->delante == NULL)',queue['delante']==NULL,sub=queue['delante']+' == NULL'):emit('cola_encolar','q->delante = aux;',change=lambda:queue.__setitem__('delante',aux))
        else:write(f,'q->atras->sgte = aux;',queue['atras'],'next',aux)
        emit('cola_encolar','q->atras = aux;',change=lambda:queue.__setitem__('atras',aux));return leave(f,'}','void')
    def dequeue():
        f=enter('cola_desencolar',{'q':'&cola'});text='if (q == NULL || q->delante == NULL)'
        emit('cola_desencolar',text,'operand',result=False,expression='q == NULL',substituted='&cola == NULL');emit('cola_desencolar',text,'operand',result=queue['delante']==NULL,expression='q->delante == NULL',substituted=queue['delante']+' == NULL')
        assert not cond(f,text,queue['delante']==NULL,sub='false || '+str(queue['delante']==NULL).lower())
        aux=queue['delante'];put(f,'struct NodoCola *aux = q->delante;','aux',aux);num=node(aux)['value'];put(f,'int num = aux->nro;','num',num)
        emit('cola_desencolar','q->delante = aux->sgte;',change=lambda:queue.__setitem__('delante',node(aux)['next']))
        if cond(f,'if (q->delante == NULL)',queue['delante']==NULL,sub=queue['delante']+' == NULL'):emit('cola_desencolar','q->atras = NULL;',change=lambda:queue.__setitem__('atras',NULL))
        free(f,'free(aux);',aux);return leave(f,'return num;',num)
    def successors(x):
        f=enter('grafo_sucesores',{'g':graph,'x':x});put(f,'ListaArco k = g.a;','k',ahead)
        emit('grafo_sucesores','ListaVertice ver = NULL, nuevo;',change=lambda:f['locals'].update(ver=NULL,nuevo=UNINIT))
        while cond(f,'while (k != NULL)',val(f,'k')!=NULL,sub=str(val(f,'k'))+' != NULL'):
            k=val(f,'k')
            if cond(f,'if (k->origen == x)',node(k)['origin']==x,sub=str(node(k)['origin'])+' == '+str(x)):
                nuevo=allocate(f,'nuevo = (ListaVertice)malloc','nuevo','successor')
                if cond(f,'if (nuevo != NULL)',True,sub=nuevo+' != NULL'):
                    write(f,'nuevo->sig = ver;',nuevo,'next',val(f,'ver'));write(f,'nuevo->dato = k->destino;',nuevo,'value',node(k)['target']);write(f,'nuevo->marcado = 0;',nuevo,'mark',0);put(f,'ver = nuevo;','ver',nuevo)
            put(f,'k = k->sig;','k',node(k)['next'])
        return leave(f,'return ver;',val(f,'ver'))
    bfs=enter('grafo_bfs',{'g':graph,'inicio':int(trace['payload']['start'])});start=val(bfs,'inicio')
    g=call(bfs,'g = grafo_desmarcar(g);',scan,'grafo_desmarcar');emit('grafo_bfs','g = grafo_desmarcar(g);',change=lambda:bfs['parameters'].__setitem__('g',deepcopy(g)))
    put(bfs,'struct Cola cola =','cola','&cola')
    for text,name,value in [('ListaVertice recorrido = NULL;','recorrido',NULL),('ListaVertice ultimo = NULL;','ultimo',NULL),('ListaVertice v = g.v;','v',vhead),('int existe = 0;','existe',0)]:put(bfs,text,name,value)
    while cond(bfs,'while (v != NULL)',val(bfs,'v')!=NULL,sub=str(val(bfs,'v'))+' != NULL'):
        if cond(bfs,'if (v->dato == inicio)',node(val(bfs,'v'))['value']==start,sub=str(node(val(bfs,'v'))['value'])+' == '+str(start)):
            put(bfs,'existe = 1;','existe',1);emit('grafo_bfs','break;','break');break
        put(bfs,'v = v->sig;','v',node(val(bfs,'v'))['next'])
    if cond(bfs,'if (!existe)',not val(bfs,'existe'),sub='!'+str(val(bfs,'existe'))):
        leave(bfs,'if (!existe) return NULL;',NULL)
    else:
        call(bfs,'cola_encolar(&cola, inicio);',enqueue,start);emit('grafo_bfs','cola_encolar(&cola, inicio);');call(bfs,'g = grafo_marcar_vertice(g, inicio);',scan,'grafo_marcar_vertice',start)
        def markstart():bfs['parameters']['g']=deepcopy(graph);discovery.append(start);parents[start]=None
        emit('grafo_bfs','g = grafo_marcar_vertice(g, inicio);',change=markstart)
        while cond(bfs,'while (cola.delante != NULL)',queue['delante']!=NULL,sub=queue['delante']+' != NULL'):
            actual=call(bfs,'int actual = cola_desencolar(&cola);',dequeue);active=actual;put(bfs,'int actual = cola_desencolar(&cola);','actual',actual)
            tmp=allocate(bfs,'ListaVertice tmp =','tmp','result');cond(bfs,'if (tmp == NULL)',False,sub=tmp+' == NULL')
            for text,field,value in [('tmp->dato = actual;','value',actual),('tmp->marcado = 0;','mark',0),('tmp->sig = NULL;','next',NULL)]:write(bfs,text,tmp,field,value)
            if cond(bfs,'if (recorrido == NULL)',val(bfs,'recorrido')==NULL,sub=str(val(bfs,'recorrido'))+' == NULL'):put(bfs,'if (recorrido == NULL) recorrido = tmp;','recorrido',tmp)
            else:write(bfs,'else ultimo->sig = tmp;',val(bfs,'ultimo'),'next',tmp)
            put(bfs,'ultimo = tmp;','ultimo',tmp);suces=call(bfs,'ListaVertice suces = grafo_sucesores(g, actual);',successors,actual);put(bfs,'ListaVertice suces = grafo_sucesores(g, actual);','suces',suces)
            while cond(bfs,'while (suces != NULL)',val(bfs,'suces')!=NULL,sub=str(val(bfs,'suces'))+' != NULL'):
                s=val(bfs,'suces');target=node(s)['value'];marked=call(bfs,'if (!grafo_marcado_vertice(g, suces->dato))',scan,'grafo_marcado_vertice',target)
                if cond(bfs,'if (!grafo_marcado_vertice(g, suces->dato))',not marked,sub='!'+str(marked)):
                    call(bfs,'cola_encolar(&cola, suces->dato);',enqueue,target);emit('grafo_bfs','cola_encolar(&cola, suces->dato);');call(bfs,'g = grafo_marcar_vertice(g, suces->dato);',scan,'grafo_marcar_vertice',target)
                    def markneighbor():bfs['parameters']['g']=deepcopy(graph);discovery.append(target);parents[target]=actual
                    emit('grafo_bfs','g = grafo_marcar_vertice(g, suces->dato);',change=markneighbor)
                put(bfs,'ListaVertice temp = suces;','temp',s);put(bfs,'suces = suces->sig;','suces',node(s)['next']);free(bfs,'free(temp);',s)
                emit('grafo_bfs','free(temp);','scope_exit',lambda:bfs['locals'].pop('temp',None))
            emit('grafo_bfs','while (cola.delante != NULL)','scope_exit',lambda:[bfs['locals'].pop(n,None) for n in ['actual','tmp','suces']])
        returned=val(bfs,'recorrido');leave(bfs,'return recorrido;',returned)
    published=returned;emit('grafo_bfs','return recorrido;' if returned!=NULL else 'if (!existe) return NULL;','caller')
    trace=GraphLogicalTrace(trace,snapshot_pool=pool)
    trace['steps']=steps;trace['bfs_instruction_model']=True;trace['highlight_semantics']='just-executed';trace['final_state']=deepcopy(after)
    return trace


def build_bfs_rejection_trace(trace, before, after):
    """Application guard rejection is not an invocation of the C function."""
    source="/* Validacion de la aplicacion: no se invoco grafo_bfs; no hay ejecucion C ni printf. */\n\n"+trace['source_code']
    lines=source.splitlines();step={'line_index':0,'line_text':lines[0],'state_snapshot':deepcopy(before),'state_after':deepcopy(after),'console':[],'debug':{'stage':'input_validation','note':trace['message'],'graph_progress':{'mode':'traversal','nodes':[],'edges':[],'queue':[],'visited':[]}}}
    frame=build_graph_frame(operation_name='run_bfs',payload=trace['payload'],step=step,source_lines=lines,success=False)
    frame.update(concept='input_validation',call_stack=[],variables=[],condition=None,narration={level:'La aplicacion rechaza la entrada antes de llamar BFS. El C crudo tiene un contrato distinto: desmarca y retorna NULL si falta inicio.' for level in ['basic','intermediate','advanced']})
    frame['invariant'].update(holds=None,symbol='?',evidence='No se ejecuto el TAD C: no se infieren ramas, marcas, reservas ni printf.')
    validate_graph_frame(frame,source_code=source);step['pedagogy']=frame
    trace.update(source_code=source,steps=[step],console=[],final_state=deepcopy(after),bfs_application_rejection=True)
    return trace
