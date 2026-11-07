"""Executed AVL insertion/rotation states, preserving reservation identities and partial links."""
from copy import deepcopy
import re
from app.services.c_code_service import CCodeService
from .pedagogy import build_hierarchical_frame,validate_hierarchical_frame

def build_avl_insert_trace(trace,before_state,after_state,*,fail_malloc=False,null_ref=False):
    value=int(trace['payload']['value']);root_reference='NULL' if null_ref else '&raiz';raw=(CCodeService._DOCS_TADS_C/'tad_avl.c').read_text(encoding='utf-8-sig');bodies={}
    for fn in ['avl_insertar','avl_RSD','avl_RSI','avl_RDD','avl_RDI']:
        start=raw.index('void '+fn+'(');opening=raw.index('{',start);depth=1;end=opening+1
        while depth:depth+=int(raw[end]=='{')-int(raw[end]=='}');end+=1
        bodies[fn]=raw[start:end]
    source='\n\n'.join(bodies.values())+'\n\n/**\n * @brief Llama al TAD de insercion void sin convertirlo en un estado de error.\n * @param arbol Referencia prestada a la raiz del llamador.\n * @note La reserva nueva queda propiedad del llamador; el TAD no imprime ni libera.\n */\nvoid ejecutar_insercion(AVL *arbol) {\n    avl_insertar(arbol, '+str(value)+');\n}\n'
    lines=source.splitlines();ranges={}
    for fn in [*bodies,'ejecutar_insercion']:
        start=next(i for i,l in enumerate(lines) if l.strip().startswith('void '+fn+'('));depth=0
        for end in range(start,len(lines)):
            depth+=lines[end].count('{')-lines[end].count('}')
            if depth==0:break
        ranges[fn]=(start,end)
    heap=[];frames=[];history=[];steps=[];caller=None;head='NULL'
    def load(n,parent='NULL'):
        if n is None:return 'NULL'
        identity='N'+str(len(heap)+1);item={'id':identity,'value':n['value'],'balance_factor':n['balance_factor'],'left':'NULL','right':'NULL','parent':parent,'status':'linked'};heap.append(item);item['left']=load(n['left'],identity);item['right']=load(n['right'],identity);return identity
    head=load(before_state.get('root'))
    def node(i):return next(n for n in heap if n['id']==i)
    def snapshot():
        reached=set()
        def tree(i):
            if i in ['NULL','sin inicializar'] or i in reached:return None
            reached.add(i);n=node(i);left,right=tree(n['left']),tree(n['right'])
            return {'value':n['value'],'left':left,'right':right,'balance_factor':n['balance_factor'],'height':1+max(left['height'] if left else 0,right['height'] if right else 0)}
        root=tree(head)
        for n in heap:n['status']='linked' if n['id'] in reached else 'detached'
        state=deepcopy(before_state);state.update(abb_read_model=True,avl_read_model=True,avl_insert_model=True,head=head,root=root,size=len(reached),height=root['height'] if root else 0,empty=not reached,heap_nodes=deepcopy(heap),tree_frames=deepcopy(frames),caller_frame=deepcopy(caller),validation=None,traversals={},console_stdout='',transient_graph=True)
        return state
    def index(fn,text,k=0):
        a,z=ranges[fn]
        if text=='}':return z
        return [i for i in range(a,z+1) if lines[i].strip()==text][k]
    def emit(text,phase,mutate=None,condition=None,k=0,expression=None):
        old=snapshot();f=frames[-1] if frames else None;fn=f['function'] if f else 'ejecutar_insercion';owner=f['id'] if f else 'caller'
        if mutate:mutate()
        new=snapshot()
        if phase=='enter':fn=frames[-1]['function'];owner=frames[-1]['id']
        idx=index(fn,text,k);step={'step_index':len(steps),'line_index':idx,'line_text':lines[idx],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':old,'state_after':new,'debug':{'stage':phase}}
        if phase=='condition':step['condition_result']=condition
        ped=build_hierarchical_frame(structure_id='avl',operation_name='insertar',payload=trace['payload'],step=step,source_lines=lines,success=True)
        added=[n for n in new['heap_nodes'] if n['id'] not in {n['id'] for n in old['heap_nodes']}];concept='allocation' if added else 'compare' if phase=='condition' else 'return' if phase in ['return','caller'] else 'descend' if phase in ['call','enter'] else 'assignment'
        ped['concept']=concept;ped['case']=phase;ped['phase']={'id':'insertar-'+phase,'label':phase.title(),'goal':text};ped['condition']=None
        if phase=='condition':ped['condition']={'source':text,'substituted':expression or text,'result':condition,'consequence':'rama registrada con los valores actuales'};ped['executed_branch']='cuerpo/operando verdadero' if condition else 'else/salida/operando falso'
        previous={(f['id'],n):v for f in old['tree_frames'] for n,v in {**f['parameters'],**f['locals']}.items()};current={(f['id'],n):v for f in new['tree_frames'] for n,v in {**f['parameters'],**f['locals']}.items()};variables=[]
        for invocation in history:
            for name in dict.fromkeys([*invocation['parameters'],*invocation['locals']]):
                key=(invocation['id'],name)
                if key not in previous and key not in current:continue
                a=previous.get(key,'fuera de ambito');b=current.get(key,'fuera de ambito');variables.append({'name':name,'scope':invocation['function']+'#'+invocation['id'],'frame_id':invocation['id'],'type':'int' if name=='x' else 'AVL *' if name in ['raiz','r'] else 'AVL','previous':a,'value':b,'changed':a!=b,'meaning':'Parametro/local de esta invocacion; &raiz es la referencia a la variable global, N identifica una reserva estable.'})
        if old['caller_frame'] or new['caller_frame']:variables.insert(0,{'name':'arbol','scope':'ejecutar_insercion','frame_id':'caller','type':'AVL *','previous':root_reference if old['caller_frame'] else 'fuera de ambito','value':root_reference if new['caller_frame'] else 'fuera de ambito','changed':bool(old['caller_frame'])!=bool(new['caller_frame']),'meaning':'Referencia a la variable raiz; su valor actual es '+new['head']+'. La llamada retorna void, no un puntero a publicar.'})
        ped['variables']=variables;shown=old['tree_frames'] if phase=='return' else new['tree_frames'];stack=[]
        if old['caller_frame'] or new['caller_frame']:stack.append({'function':'ejecutar_insercion','frame_id':'caller','depth':-1,'parameters':{'arbol':root_reference},'locals':{},'local_root':new['head'],'local_root_address':new['head'],'return':'void' if phase=='caller' else None,'continuation':'El TAD escribe raiz/enlaces en sus instrucciones; el llamador no publica un retorno.'})
        for f in shown:stack.append({'function':f['function'],'frame_id':f['id'],'depth':f['depth'],'parameters':deepcopy(f['parameters']),'locals':deepcopy(f['locals']),'local_root':f['parameters'].get('nodo',new['head']),'local_root_address':f['parameters'].get('nodo',new['head']),'return':'void' if phase=='return' and f['id']==owner else None,'continuation':'Cada local y alias pertenece a esta invocacion; padres suspendidos conservan sus valores.'})
        for f in stack:f['scope_status']='terminado (contexto del retorno)' if (phase=='return' and f['frame_id']==owner) or (phase=='caller' and f['frame_id']=='caller') else 'activo' if f['frame_id']==(new['tree_frames'][-1]['id'] if new['tree_frames'] else 'caller') else 'suspendido'
        ped['call_stack']=stack
        def objects(st):return [{**n,'address':n['id'],'symbolic_identity':True,'allocated':True,'freed':False} for n in st['heap_nodes']]
        ped['memory']={'event':'allocation' if added else 'none','objects_before':objects(old),'objects_after':objects(new),'allocated_objects':[{**n,'address':n['id'],'symbolic_identity':True,'allocated':True,'freed':False} for n in added],'freed_objects':[],'dangling_references':[],'stable_addresses':True,'symbolic_identities':True}
        narrations={'caller_enter':'Entra el llamador equivalente, con referencia a raiz. No hay resultado futuro.','enter':'Entra esta funcion con parametros propios; no crea alias de futuros locales.','call':'Transfiere control. En malloc nuevo tiene ambito pero sigue sin inicializar hasta retornar.','condition':'Evalua esta condicion con los valores actuales; no cambia enlaces ni FE.','after':'Completa esta instruccion: inicializacion, enlace o FE cambia solo donde escribe el C. Una reserva nueva puede seguir desconectada.','break':'Termina este bucle; conserva las reservas y los locales hasta salir del ambito.','return':'Retorno void: termina solo este ambito; no libera, imprime ni devuelve una raiz.','caller':'Retorno del llamador void, sin una nueva asignacion ficticia de raiz.'}
        ped['narration']={level:narrations[phase] for level in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase in ['return','caller'],'value':'void' if phase in ['return','caller'] else None,'reconnects_subtree':False};ped['state_before']=deepcopy(old);ped['state_after']=deepcopy(new);ped['memory_state']=deepcopy(new);ped['instruction_event']={'phase':phase,'frame_id':owner,'condition':condition,'return':'void' if phase in ['return','caller'] else None}
        ped['invariant'].update(holds=None,symbol='?',explanation='Estado transitorio real: reservas conservan identidad y campos escritos. Padre/enlaces/FE parciales pueden incumplir el AVL final; no se certifica equilibrio durante la reconexion.')
        validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
        if phase=='return' and text=='}' and fn in {'avl_RSD','avl_RSI','avl_RDD','avl_RDI'}:
            rotation_frames=[frame for frame in old['tree_frames'] if frame['function'] in {'avl_RSD','avl_RSI','avl_RDD','avl_RDI'}]
            if rotation_frames[0]['id']==owner:
                labels={'avl_RSD':('LL','Rotación simple a la derecha (LL).'),'avl_RSI':('RR','Rotación simple a la izquierda (RR).'),'avl_RDD':('LR','Rotación doble izquierda-derecha (LR).'),'avl_RDI':('RL','Rotación doble derecha-izquierda (RL).')}
                kind,message=labels[fn];step['debug']['rotation_hint']={'type':kind,'message':message}
        rotation_calls={'avl_RSD(raiz, padre);':'LL','avl_RSI(raiz, padre);':'RR','avl_RDD(raiz, padre);':'LR','avl_RDI(raiz, padre);':'RL'}
        if fn=='avl_insertar' and text in rotation_calls and phase in {'call','after'}:
            kind=rotation_calls[text]
            if phase=='call':
                pivot_id=old['tree_frames'][-1]['locals']['padre']
                pivot=next(item for item in old['heap_nodes'] if item['id']==pivot_id)
                if pivot['balance_factor'] in {-2,2}:
                    by_id={item['id']:item for item in old['heap_nodes']};path=[];current=pivot_id
                    while current!='NULL':
                        path.append(by_id[current]['value']);current=by_id[current]['parent']
                    step['debug'].update(stage='pre_rebalance',instruction_phase=phase,unbalanced_key=pivot['value'],unbalanced_node_id=pivot_id,path_keys=list(reversed(path)),active_keys=[pivot['value']],rotation_message='Rotacion AVL '+kind+' seleccionada para el nodo '+str(pivot['value'])+'.')
            elif steps[-2].get('debug',{}).get('rotation_hint',{}).get('type')==kind:
                prior=next(item['debug'] for item in reversed(steps[:-1]) if item['line_index']==idx and item.get('debug',{}).get('stage')=='pre_rebalance')
                step['debug'].update(stage='rebalance',instruction_phase=phase,unbalanced_key=prior['unbalanced_key'],unbalanced_node_id=prior['unbalanced_node_id'],path_keys=list(prior['path_keys']),active_keys=list(prior['active_keys']),rotation_message='Rotacion AVL '+kind+' aplicada al nodo '+str(prior['unbalanced_key'])+'.')
    def enter(fn,parameters):
        f={'id':'F'+str(len(history)+1),'function':fn,'depth':len(frames),'parameters':parameters,'locals':{}};history.append(f);emit(bodies[fn].splitlines()[0],'enter',lambda:frames.append(f));return f
    def cond(t,v,**kw):emit(t,'condition',condition=bool(v),**kw);return bool(v)
    def put(f,t,**kw):emit(t,'after',lambda:f['locals'].update(kw))
    def field(t,i,**kw):emit(t,'after',lambda:node(i).update(kw))
    def leave(text='}',k=0):emit(text,'return',lambda:frames.pop(),k=k)
    def rotate(fn,i):
        nonlocal head
        f=enter(fn,{'r':'&raiz','nodo':i});left=fn in ['avl_RSD','avl_RDD'];side='left' if left else 'right';child=node(i)[side] if i!='NULL' else 'NULL';double=fn in ['avl_RDD','avl_RDI'];other='right' if left else 'left';fieldname='izq' if left else 'der';othername='der' if left else 'izq'
        guard=f'if (r == NULL || nodo == NULL || nodo->{fieldname} == NULL'+(f' || nodo->{fieldname}->{othername} == NULL' if double else '')+') {'
        if cond(guard,i=='NULL' or child=='NULL' or (double and node(child)[other]=='NULL'),expression='referencia valida; nodo '+i+'; hijo '+child):leave('return;');return
        if double:
            put(f,'AVL A = nodo;',A=i);put(f,'AVL B = A->'+fieldname+';',B=child)
            for callee,target in [('avl_RSI' if left else 'avl_RSD',child),('avl_RSD' if left else 'avl_RSI',i)]:
                text=callee+'(r, '+('B' if target==child else 'A')+');';emit(text,'call');rotate(callee,target);emit(text,'after')
        else:
            parent=node(i)['parent'];put(f,'AVL padre = nodo->padre;',padre=parent);put(f,'AVL A = nodo;',A=i);put(f,'AVL B = A->'+fieldname+';',B=child);transfer=node(child)[other];put(f,'AVL C = B->'+othername+';',C=transfer)
            if cond('if (padre) {',parent!='NULL',expression=parent+' != NULL'):
                right=cond('if (padre->der == A)',node(parent)['right']==i,expression=node(parent)['right']+' == '+i);field('padre->'+('der' if right else 'izq')+' = B;',parent,**{'right' if right else 'left':child})
            else:emit('*r = B;','after',lambda:set_head(child))
            field('A->'+fieldname+' = C;',i,**{side:transfer});field('B->'+othername+' = A;',child,**{other:i});field('A->padre = B;',i,parent=child)
            if cond('if (C)',transfer!='NULL',expression=transfer+' != NULL'):field('C->padre = A;',transfer,parent=i)
            field('B->padre = padre;',child,parent=parent)
            a,b=node(i)['balance_factor'],node(child)['balance_factor'];ta='A->FE = A->FE '+('+ 1 - (B->FE < 0 ? B->FE : 0);' if left else '- 1 - (B->FE > 0 ? B->FE : 0);');branch=cond(ta,b<0 if left else b>0,expression=f'{b} '+('< 0' if left else '> 0'));newa=a+1-(b if branch else 0) if left else a-1-(b if branch else 0);field(ta,i,balance_factor=newa)
            tb='B->FE = B->FE '+('+ 1 + (A->FE > 0 ? A->FE : 0);' if left else '- 1 + (A->FE < 0 ? A->FE : 0);');branch=cond(tb,newa>0 if left else newa<0,expression=f'{newa} '+('> 0' if left else '< 0'));newb=b+1+(newa if branch else 0) if left else b-1+(newa if branch else 0);field(tb,child,balance_factor=newb)
        leave()
    def set_head(i):
        nonlocal head
        head=i
    def insert():
        f=enter('avl_insertar',{'raiz':'NULL' if null_ref else '&raiz','x':value})
        if cond('if (raiz == NULL) {',null_ref,expression=('NULL' if null_ref else '&raiz')+' == NULL'):leave('return;');return
        put(f,'AVL padre = NULL, actual = *raiz;',padre='NULL',actual=head)
        while cond('while (actual != NULL) {',f['locals']['actual']!='NULL',expression=f['locals']['actual']+' != NULL'):
            i=f['locals']['actual'];put(f,'padre = actual;',padre=i);v=node(i)['value']
            if cond('if (x < actual->nro)',value<v,expression=f'{value} < {v}'):put(f,'actual = actual->izq;',actual=node(i)['left'])
            elif cond('else if (x > actual->nro)',value>v,expression=f'{value} > {v}'):put(f,'actual = actual->der;',actual=node(i)['right'])
            else:leave('return; // no duplicados');return
        t='AVL nuevo = malloc(sizeof(*nuevo));';emit(t,'call',lambda:f['locals'].update(nuevo='sin inicializar'))
        identity='NULL' if fail_malloc else 'N'+str(len(heap)+1)
        def allocate():
            f['locals']['nuevo']=identity
            if identity!='NULL':heap.append({'id':identity,'value':'sin inicializar','balance_factor':'sin inicializar','left':'sin inicializar','right':'sin inicializar','parent':'sin inicializar','status':'detached'})
        emit(t,'after',allocate)
        if cond('if (nuevo == NULL) {',identity=='NULL',expression=identity+' == NULL'):leave('return;',k=1);return
        field('nuevo->nro = x;',identity,value=value);field('nuevo->FE = 0;',identity,balance_factor=0);field('nuevo->izq = nuevo->der = NULL;',identity,left='NULL',right='NULL');parent=f['locals']['padre'];field('nuevo->padre = padre;',identity,parent=parent)
        if cond('if (padre == NULL) {',parent=='NULL',expression=parent+' == NULL'):emit('*raiz = nuevo;','after',lambda:set_head(identity));leave('return;',k=2);return
        left=cond('if (x < padre->nro)',value<node(parent)['value'],expression=f'{value} < '+str(node(parent)['value']));field('padre->'+('izq' if left else 'der')+' = nuevo;',parent,**{'left' if left else 'right':identity});put(f,'AVL n = nuevo;',n=identity)
        while cond('while (padre != NULL) {',f['locals']['padre']!='NULL',expression=f['locals']['padre']+' != NULL'):
            parent=f['locals']['padre'];n=f['locals']['n'];left=cond('if (n == padre->izq)',n==node(parent)['left'],expression=n+' == '+node(parent)['left']);field('padre->FE'+('--;' if left else '++;'),parent,balance_factor=node(parent)['balance_factor']+(-1 if left else 1));factor=node(parent)['balance_factor']
            if cond('if (padre->FE == 0)',factor==0,expression=f'{factor} == 0'):emit('break;','break');break
            if cond('if (padre->FE == -2) {',factor==-2,expression=f'{factor} == -2'):
                fn='avl_RSD' if cond('if (n->FE <= 0)',node(n)['balance_factor']<=0,expression=str(node(n)['balance_factor'])+' <= 0') else 'avl_RDD';t=fn+'(raiz, padre);';emit(t,'call');rotate(fn,parent);emit(t,'after');emit('break;','break',k=1);break
            if cond('if (padre->FE == 2) {',factor==2,expression=f'{factor} == 2'):
                fn='avl_RSI' if cond('if (n->FE >= 0)',node(n)['balance_factor']>=0,expression=str(node(n)['balance_factor'])+' >= 0') else 'avl_RDI';t=fn+'(raiz, padre);';emit(t,'call');rotate(fn,parent);emit(t,'after');emit('break;','break',k=2);break
            put(f,'n = padre;',n=parent);put(f,'padre = padre->padre;',padre=node(parent)['parent'])
        leave()
    def caller_enter():
        nonlocal caller
        caller={'function':'ejecutar_insercion','parameters':{'arbol':root_reference},'description':'arbol (AVL *) -> '+root_reference+'; retorna void. La referencia no es una reserva nodo.'}
    emit('void ejecutar_insercion(AVL *arbol) {','caller_enter',caller_enter);emit('avl_insertar(arbol, '+str(value)+');','call');insert()
    def caller_exit():
        nonlocal caller
        caller=None
    emit('}','caller',caller_exit);steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    initial=deepcopy(steps[0]['pedagogy']);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={l:'Estado inicial: ninguna instruccion ni reserva nueva ejecutada.' for l in ['basic','intermediate','advanced']};steps[0]['pedagogy']['initial_frame']=initial
    trace.update(source_code=source,steps=steps);return trace
