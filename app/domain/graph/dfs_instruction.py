"""Instruction effects of the downloadable DFS and its actual recursive/list helpers.

Identities are symbolic, monotonically allocated and never reused. Snapshots
describe completed instructions, not interpolation from a future traversal.
Normal successful allocation is modeled; allocation-failure injection is not.
"""
from copy import deepcopy
from app.domain.graph.owned_transport import OwnedTransportPool as SnapshotPool
from app.domain.graph.snapshot_pool import GraphLogicalTrace
import re
from app.domain.graph.pedagogy import build_graph_frame, validate_graph_frame

UNINIT = 'sin inicializar'
NULL = 'NULL'


def build_dfs_trace(trace, before, after):
    pool = SnapshotPool(preserve_tuples=True)
    published_before = pool.intern(before)
    source = trace['source_code']; lines = source.splitlines(); ranges = {}
    for i, row in enumerate(lines):
        m = re.match(r'\s*(?:static\s+)?(?:void|int|Grafo|ListaVertice)\s+(\w+)\s*\(', row)
        if m:
            depth = 0
            for j in range(i, len(lines)):
                depth += lines[j].count('{') - lines[j].count('}')
                if j > i and depth == 0:
                    ranges[m[1]] = (i, j); break
    heap = {}; serial = 0; frames = []; retired = []; steps = []; allocations = frees = 0
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
    graph={'v':vhead,'a':ahead}; queue={'delante':NULL,'atras':NULL,'kind':'no FIFO: pila de recursión'}; dfs=None; returned=NULL; published=NULL
    parents={}; discovery=[]; active=None; frame_counter=0
    def node(key):
        assert key in heap, ('read of non-live pointer',key)
        return heap[key]
    def chain(key):
        items=[];seen=set()
        while key in heap and key not in seen:
            seen.add(key);n=node(key);items.append(deepcopy(n));key=n.get('next',UNINIT)
        return items
    def val(f,n):return f['locals'].get(n,f['parameters'].get(n,UNINIT))
    # Cache only detached pool-owned branches; revisions describe actual writes.
    versions={name:0 for name in ('heap','frames','marks','retired','progress')}
    dirty_nodes=set(heap);dirty_frames=set();owned_nodes={};owned_frames={};owned_retired=[];branches={}
    owned_graph=pool.intern(graph);owned_queue=pool.intern(queue)
    def cached(name,revision,build):
        prior=branches.get(name)
        if prior is not None and prior[0]==revision:return prior[1]
        value=pool.intern(build());branches[name]=(revision,value);return value
    def owned_node(key):
        if key not in owned_nodes or key in dirty_nodes:
            owned_nodes[key]=pool.intern(node(key));dirty_nodes.discard(key)
        return owned_nodes[key]
    def owned_frame(frame):
        key=frame['id']
        if key not in owned_frames or key in dirty_frames:
            owned_frames[key]=pool.intern(frame);dirty_frames.discard(key)
        return owned_frames[key]
    def owned_chain(name,key):
        def build():
            items=[];seen=set();current=key
            while current in heap and current not in seen:
                seen.add(current);n=owned_node(current);items.append(n);current=n.get('next',UNINIT)
            return items
        return cached(name,(key,versions['heap']),build)
    def retired_branch():
        def build():
            for row in retired[len(owned_retired):]:owned_retired.append(pool.intern(row))
            return owned_retired
        return cached('retired',versions['retired'],build)
    def touch(heap_keys,frame_values,stack_changed,retired_changed,marks_changed,progress_changed):
        heap_keys=heap_keys() if callable(heap_keys) else heap_keys
        frame_values=frame_values() if callable(frame_values) else frame_values
        if heap_keys:
            dirty_nodes.update(heap_keys);versions['heap']+=1
        if frame_values or stack_changed:
            dirty_frames.update(frame['id'] for frame in frame_values);versions['frames']+=1
        for name,changed in [('retired',retired_changed),('marks',marks_changed),('progress',progress_changed)]:
            if changed:versions[name]+=1
    def snapshot():
        root=val(dfs,'recorrido') if dfs else UNINIT
        frame_branch=cached('frames',versions['frames'],lambda:[owned_frame(f) for f in frames])
        recursive=cached('recursive_frames',versions['frames'],lambda:[f for f in frame_branch if f['function']=='grafo_dfs_recursivo'])
        suces=val(recursive[-1],'suces') if recursive else NULL
        return pool.intern(dict(heap_nodes=cached('heap_nodes',versions['heap'],lambda:[owned_node(key) for key in heap]),freed_nodes=retired_branch(),frames=frame_branch,
                    graph=owned_graph,graph_marks=cached('graph_marks',versions['marks'],lambda:[{'vertex':n['value'],'mark':n['mark'],'id':n['id']} for n in owned_chain('vertex_chain',vhead)]),
                    queue=owned_queue,queue_nodes=owned_chain('queue_chain',queue['delante']),result_nodes=owned_chain('result_chain',root),successor_nodes=owned_chain('successor_chain',suces),
                    returned=returned,published=published,discovery=cached('discovery',versions['progress'],lambda:discovery),parents=cached('parents',versions['progress'],lambda:parents),
                    active=recursive[-1]['parameters']['actual'] if recursive else None,head_storage={'id': '&'+dfs['id']+'.recorrido' if dfs and 'recorrido' in dfs['locals'] else NULL,'value':root,'live':bool(dfs and dfs in frames and 'recorrido' in dfs['locals'])},recursive_frames=recursive,allocations=allocations,frees=frees,console_stdout=''))
    def locate(fn,text):
        lo,hi=ranges[fn]
        for i in range(lo,hi+1):
            if text in lines[i]:return i
        raise AssertionError((fn,text))
    def emit(fn,text,phase='statement',change=None,result=None,expression=None,substituted=None,ix=None,dirty_heap=(),dirty_frame_values=(),stack_changed=False,retired_changed=False,marks_changed=False,progress_changed=False):
        old=pool.intern(snapshot())
        if change:change()
        touch(dirty_heap,dirty_frame_values,stack_changed,retired_changed,marks_changed,progress_changed)
        new=pool.intern(snapshot());index=locate(fn,text) if ix is None else ix
        # State shown by the trace player is the state AFTER the highlighted
        # completed instruction. last_result stays pending until caller resume.
        visual=deepcopy(before);visual['last_result']=None;visual['last_operation']=None
        for n in visual.get('nodes',[]):n['marked']=next((v['mark'] for v in new['graph_marks'] if v['vertex']==int(n['id'])),0)
        if phase=='caller':visual=deepcopy(after)
        visual=pool.intern(visual)
        res=[str(n['value']) for n in new['result_nodes'] if n.get('value')!=UNINIT]
        q=[str(n['value']) for n in new['queue_nodes'] if n.get('value')!=UNINIT]
        marked=[str(n['vertex']) for n in new['graph_marks'] if n['mark']]
        edges=[[str(p),str(c)] for c,p in parents.items() if p is not None]
        progress={'mode':'traversal','nodes':res,'edges':edges,'tree_edges':edges,'queue':q,'visited':marked,
                  'selected':None if new['active'] is None else str(new['active']),'previous':{str(k):v for k,v in parents.items()},'discovery':list(map(str,discovery))}
        step={'line_index':index,'line_text':lines[index],'state_snapshot':steps[-1]['state_after'] if steps else published_before,'state_after':visual,
              'console':[],'debug':{'dfs_memory':new,'stage':phase,'note':'Instrucción completada; no hay salida printf en esta ruta normal.','graph_progress':progress}}
        ped=build_graph_frame(operation_name='run_dfs',payload=trace['payload'],step=step,source_lines=lines,success=trace['success'])
        ped['condition']=None if phase not in {'condition','operand'} else {'source':expression or text,'substituted':substituted or expression or text,'result':bool(result),'consequence':'Evalúa operandos actuales; no modifica la estructura.'}
        shown=old['frames'] if phase=='return' else new['frames']
        ped['call_stack']=[dict(function=f['function'],frame_id=f['id'],depth=i,parameters=f['parameters'],locals=f['locals'],scope_status='terminado (retorno)' if phase=='return' and i==len(shown)-1 else 'activo' if i==len(shown)-1 else 'suspendido',return_value=result if phase=='return' and i==len(shown)-1 else None) for i,f in enumerate(shown)]
        oldvars={(f['id'],n):v for f in old['frames'] for n,v in {**f['parameters'],**f['locals']}.items()}
        newvars={(f['id'],n):v for f in new['frames'] for n,v in {**f['parameters'],**f['locals']}.items()}
        names={f['id']:f['function'] for f in [*old['frames'],*new['frames']]}
        def typ(n,fn):return 'int' if n in {'inicio','x','valor','actual','existe','num'} else 'Grafo' if n=='g' else 'Cola *' if n=='q' else 'Cola' if n=='cola' else 'ListaVertice *' if n=='recorrido' and fn in {'grafo_dfs_recursivo','grafo_agregar_recorrido'} else 'ListaArco' if n=='k' and fn=='grafo_sucesores' else 'NodoCola *' if n=='aux' else 'ListaVertice'
        ped['variables']=[dict(name=n,scope=names[f]+'#'+f,frame_id=f,type=typ(n,names[f]),previous=oldvars.get((f,n),'fuera de ámbito'),value=newvars.get((f,n),'fuera de ámbito'),changed=oldvars.get((f,n))!=newvars.get((f,n)),meaning='Local o parámetro de esta invocación; una identidad retirada es un registro, no un puntero utilizable.') for f,n in dict.fromkeys([*oldvars,*newvars])]
        liveold={n['id'] for n in old['heap_nodes']};livenew={n['id'] for n in new['heap_nodes']}
        ped['memory'].update(objects_before=old['heap_nodes'],objects_after=new['heap_nodes'],allocated=[n for n in new['heap_nodes'] if n['id'] not in liveold],freed=[n for n in old['heap_nodes'] if n['id'] not in livenew],retired_objects=new['freed_nodes'],symbolic_identities=True,records_are_not_pointer_values=True)
        ped['concept']='free' if ped['memory']['freed'] else 'allocation' if ped['memory']['allocated'] else 'condition' if ped['condition'] else 'return' if phase in {'return','caller'} else 'assignment'
        ped['auxiliary'].update(items=[f['parameters']['actual'] for f in new['recursive_frames']],selected=new['active'],kind='recursión C');ped['traversal'].update(discovery_order=list(map(str,discovery)),output_order=res,tree_edges=edges)
        for row in ped['vertices']:
            row['marked']=int(row['id'] in marked);row['status']='processed' if row['id'] in res else 'discovered' if row['id'] in marked else 'undiscovered'
        ped.update(state_before=step['state_snapshot'],state_after=step['state_after'],instruction_state_before=old,instruction_state_after=new,memory_state=new,highlight_semantics='just-executed',instruction_event={'function':fn,'phase':phase,'condition':result if phase in {'condition','operand'} else None,'statement':lines[index]})
        ped['invariant'].update(holds=None,symbol='?',evidence='Estado parcial real: marcado al entrar en recursión; resultado al publicar el enlace. No se anticipa el recorrido final.')
        descriptions={'enter':'Entra la función con sus propios parámetros; todavía no existen los futuros locales.', 'call':'El caller queda suspendido; el resultado de la llamada aún no se asigna.', 'return':'Retorna el valor y termina este ámbito; la asignación del caller queda pendiente.', 'caller':'El caller recibe la lista propia devuelta; su liberación ocurre fuera de DFS.', 'scope_exit':'Termina el bloque de esta iteración; sus locales salen de ámbito.', 'free':'Termina la reserva indicada. Los aliases anteriores conservan solo identidad histórica no utilizable.', 'condition':'Evalúa la condición actual sin cambiar enlaces, pila ni marcas.'}
        narration=descriptions.get(phase,'Completa solo esta escritura o declaración C. Los campos sin inicializar no se leen y no se fabrica una mutación visual.')
        ped['narration']={level:narration for level in ['basic','intermediate','advanced']}
        validate_graph_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(pool.intern(step))
    def enter(fn,params):
        nonlocal frame_counter
        frame_counter+=1;f={'id':'F'+str(frame_counter),'function':fn,'parameters':deepcopy(params),'locals':{}}
        emit(fn,fn+'(','enter',lambda:frames.append(f),ix=ranges[fn][0],dirty_frame_values=(f,),stack_changed=True);return f
    def put(f,text,name,value):emit(f['function'],text,change=lambda:f['locals'].__setitem__(name,deepcopy(value)),dirty_frame_values=(f,))
    def cond(f,text,result,expr=None,sub=None):emit(f['function'],text,'condition',result=result,expression=expr,substituted=sub);return result
    def leave(f,text,result):emit(f['function'],text,'return',lambda:frames.pop(),result=result,ix=ranges[f['function']][1] if text=='}' else None,stack_changed=True);return result
    def call(f,text,fn,*args):
        declare='actual' if text.startswith('int actual') else 'suces' if text.startswith('ListaVertice suces') else None
        emit(f['function'],text,'call',(lambda:f['locals'].__setitem__(declare,UNINIT)) if declare else None,dirty_frame_values=(f,) if declare else ());return fn(*args)
    def allocate(f,text,name,kind):
        def change():
            nonlocal serial,allocations
            serial+=1;key='N'+str(serial);allocations+=1;heap[key]=dict(id=key,kind=kind,value=UNINIT,next=UNINIT);
            if kind!='queue':heap[key]['mark']=UNINIT
            f['locals'][name]=key
        emit(f['function'],text,'allocate',change,dirty_heap=lambda:(val(f,name),),dirty_frame_values=(f,));return val(f,name)
    def write(f,text,key,field,value):emit(f['function'],text,change=lambda:node(key).__setitem__(field,deepcopy(value)),dirty_heap=(key,),marks_changed=node(key)['kind']=='vertex' and field=='mark')
    def free(f,text,key):
        changed_frames=[]
        def change():
            nonlocal frees
            retired.append({**heap.pop(key),'usable':False});frees+=1
            for frame in frames:
                for area in ['parameters','locals']:
                    for n,v in frame[area].items():
                        if v==key:frame[area][n]=key+' (identidad histórica; valor indeterminado)';changed_frames.append(frame)
        emit(f['function'],text,'free',change,dirty_heap=(key,),dirty_frame_values=lambda:changed_frames,retired_changed=True)
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

    def exists(x):
        f=enter('grafo_existe_vertice',{'g':graph,'x':x});put(f,'ListaVertice k=g.v;','k',vhead)
        while True:
            k=val(f,'k');ok=k!=NULL and node(k)['value']!=x
            if not cond(f,'while ((k!=NULL)',ok,sub=str(k)+' != NULL && '+(str(node(k)['value'])+' != '+str(x) if k!=NULL else '(no evaluado)')):break
            put(f,'k=k->sig;','k',node(k)['next'])
        if cond(f,'if (k==NULL)',val(f,'k')==NULL,sub=str(val(f,'k'))+' == NULL'):return leave(f,'return 0;',0)
        return leave(f,'return 1;',1)
    def successors(x):
        f=enter('grafo_sucesores',{'g':graph,'x':x});put(f,'ListaArco k = g.a;','k',ahead)
        emit('grafo_sucesores','ListaVertice ver = NULL, nuevo;',change=lambda:f['locals'].update(ver=NULL,nuevo=UNINIT),dirty_frame_values=(f,))
        while cond(f,'while (k != NULL)',val(f,'k')!=NULL,sub=str(val(f,'k'))+' != NULL'):
            k=val(f,'k')
            if cond(f,'if (k->origen == x)',node(k)['origin']==x,sub=str(node(k)['origin'])+' == '+str(x)):
                nuevo=allocate(f,'nuevo = (ListaVertice)malloc','nuevo','successor')
                if cond(f,'if (nuevo != NULL)',True,sub=nuevo+' != NULL'):
                    write(f,'nuevo->sig = ver;',nuevo,'next',val(f,'ver'));write(f,'nuevo->dato = k->destino;',nuevo,'value',node(k)['target']);write(f,'nuevo->marcado = 0;',nuevo,'mark',0);put(f,'ver = nuevo;','ver',nuevo)
            put(f,'k = k->sig;','k',node(k)['next'])
        return leave(f,'return ver;',val(f,'ver'))
    def append(nuevo):
        f=enter('grafo_agregar_recorrido',{'recorrido':'&'+dfs['id']+'.recorrido','nuevo':nuevo})
        put(f,'ListaVertice ultimo;','ultimo',UNINIT)
        write(f,'nuevo->sig = NULL;',nuevo,'next',NULL)
        if cond(f,'if (*recorrido == NULL)',val(dfs,'recorrido')==NULL,sub=str(val(dfs,'recorrido'))+' == NULL'):
            emit('grafo_agregar_recorrido','*recorrido = nuevo;',change=lambda:dfs['locals'].__setitem__('recorrido',nuevo),dirty_frame_values=(dfs,))
            return leave(f,'if (*recorrido == NULL)','void')
        put(f,'ultimo = *recorrido;','ultimo',val(dfs,'recorrido'))
        while cond(f,'while (ultimo->sig != NULL)',node(val(f,'ultimo'))['next']!=NULL,sub=str(node(val(f,'ultimo'))['next'])+' != NULL'):
            put(f,'while (ultimo->sig != NULL)','ultimo',node(val(f,'ultimo'))['next'])
        write(f,'ultimo->sig = nuevo;',val(f,'ultimo'),'next',nuevo);return leave(f,'}','void')
    def recursive(actual,parent=None):
        f=enter('grafo_dfs_recursivo',{'g':graph,'actual':actual,'recorrido':'&'+dfs['id']+'.recorrido'})
        cond(f,'if (recorrido == NULL)',False,sub='&'+dfs['id']+'.recorrido == NULL')
        call(f,'g = grafo_marcar_vertice(g, actual);',scan,'grafo_marcar_vertice',actual)
        def mark():f['parameters']['g']=deepcopy(graph);discovery.append(actual);parents[actual]=parent
        emit('grafo_dfs_recursivo','g = grafo_marcar_vertice(g, actual);',change=mark,dirty_frame_values=(f,),progress_changed=True)
        tmp=allocate(f,'ListaVertice tmp =','tmp','result');cond(f,'if (tmp == NULL)',False,sub=tmp+' == NULL')
        write(f,'tmp->dato = actual;',tmp,'value',actual);write(f,'tmp->marcado = 0;',tmp,'mark',0)
        call(f,'grafo_agregar_recorrido(recorrido, tmp);',append,tmp);emit('grafo_dfs_recursivo','grafo_agregar_recorrido(recorrido, tmp);')
        suces=call(f,'ListaVertice suces = grafo_sucesores(g, actual);',successors,actual);put(f,'ListaVertice suces = grafo_sucesores(g, actual);','suces',suces)
        while cond(f,'while (suces)',val(f,'suces')!=NULL,sub=str(val(f,'suces'))+' != NULL'):
            s=val(f,'suces');target=node(s)['value'];marked=call(f,'if (!grafo_marcado_vertice(g, suces->dato))',scan,'grafo_marcado_vertice',target)
            if cond(f,'if (!grafo_marcado_vertice(g, suces->dato))',not marked,sub='!'+str(marked)):
                call(f,'grafo_dfs_recursivo(g, suces->dato, recorrido);',recursive,target,actual);emit('grafo_dfs_recursivo','grafo_dfs_recursivo(g, suces->dato, recorrido);')
            put(f,'ListaVertice temp = suces;','temp',s);put(f,'suces = suces->sig;','suces',node(s)['next']);free(f,'free(temp);',s)
            emit('grafo_dfs_recursivo','free(temp);','scope_exit',lambda:f['locals'].pop('temp',None),dirty_frame_values=(f,))
        return leave(f,'}','void')
    dfs=enter('grafo_dfs',{'g':graph,'inicio':int(trace['payload']['start'])});start=val(dfs,'inicio')
    found=call(dfs,'if (!grafo_existe_vertice(g, inicio))',exists,start)
    if cond(dfs,'if (!grafo_existe_vertice(g, inicio))',not found,sub='!'+str(found)):
        leave(dfs,'return NULL;',NULL)
    else:
        g=call(dfs,'g = grafo_desmarcar(g);',scan,'grafo_desmarcar');emit('grafo_dfs','g = grafo_desmarcar(g);',change=lambda:dfs['parameters'].__setitem__('g',deepcopy(g)),dirty_frame_values=(dfs,))
        put(dfs,'ListaVertice recorrido = NULL;','recorrido',NULL)
        call(dfs,'grafo_dfs_recursivo(g, inicio, &recorrido);',recursive,start);emit('grafo_dfs','grafo_dfs_recursivo(g, inicio, &recorrido);')
        returned=val(dfs,'recorrido');leave(dfs,'return recorrido;',returned)
    published=returned;emit('grafo_dfs','return recorrido;' if returned!=NULL else 'return NULL;','caller')
    steps[0]={**steps[0], 'pedagogy':{**steps[0]['pedagogy']}}
    initial=deepcopy(steps[0]['pedagogy']);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(steps[0]['pedagogy']['instruction_state_before']));initial['phase']['label']='Estado inicial';steps[0]['pedagogy']['initial_frame']=initial
    trace['steps']=steps;trace['dfs_instruction_model']=True;trace['highlight_semantics']='just-executed';trace['final_state']=deepcopy(after)
    return GraphLogicalTrace(trace,snapshot_pool=pool)


def build_dfs_rejection_trace(trace, before, after):
    """Application guard rejection is not an invocation of the C function."""
    source="/* Validacion de la aplicacion: no se invoco grafo_dfs; no hay ejecucion C ni printf. */\n\n"+trace['source_code']
    lines=source.splitlines();step={'line_index':0,'line_text':lines[0],'state_snapshot':deepcopy(before),'state_after':deepcopy(after),'console':[],'debug':{'stage':'input_validation','note':trace['message'],'graph_progress':{'mode':'traversal','nodes':[],'edges':[],'queue':[],'visited':[]}}}
    frame=build_graph_frame(operation_name='run_dfs',payload=trace['payload'],step=step,source_lines=lines,success=False)
    frame.update(concept='input_validation',call_stack=[],variables=[],condition=None,narration={level:'La aplicacion rechaza la entrada antes de llamar DFS. El C crudo comprueba inicio antes de desmarcar; si falta retorna NULL y conserva las marcas previas.' for level in ['basic','intermediate','advanced']})
    frame['invariant'].update(holds=None,symbol='?',evidence='No se ejecuto el TAD C: no se infieren ramas, marcas, reservas ni printf.')
    validate_graph_frame(frame,source_code=source);step['pedagogy']=frame
    trace.update(source_code=source,steps=[step],console=[],final_state=deepcopy(after),dfs_application_rejection=True)
    return trace
