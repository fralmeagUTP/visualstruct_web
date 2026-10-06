"""Native C insertion instruction model: owned reserves, typed scopes and partial links."""
from copy import deepcopy
import re
from .pedagogy import build_hierarchical_frame,validate_hierarchical_frame

UNINIT='sin inicializar'
def build_rbt_insert_rejection_trace(trace,before_state,after_state):
    assert before_state==after_state
    source='/* Solicitud rechazada por la aplicacion: rbt_insertar NO fue invocado. */\n\n'+trace['source_code'];lines=source.splitlines()
    step={'step_index':0,'line_index':0,'line_text':lines[0],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':deepcopy(before_state),'state_after':deepcopy(after_state),'debug':{'stage':'application_precondition_rejected'}}
    ped=build_hierarchical_frame(structure_id='red_black',operation_name='insertar',payload=trace['payload'],step=step,source_lines=lines,success=False)
    ped.update(concept='compare',case='application_precondition_rejected',phase={'id':'application_precondition_rejected','label':'Rechazo antes del TAD','goal':lines[0]},condition=None,variables=[],call_stack=[],return_propagation={'active':False,'value':None,'reconnects_subtree':False},instruction_event={'phase':'application_precondition_rejected','C_invoked':False,'return':None},memory={'event':'none','objects_before':[],'objects_after':[],'allocated_objects':[],'freed_objects':[],'dangling_references':[]},memory_state=deepcopy(before_state))
    ped['narration']={k:'El rechazo pertenece a la aplicacion, no a una ejecucion de C: no hay malloc, escritura, printf ni retorno del TAD. El codigo restante es referencia.' for k in ['basic','intermediate','advanced']};validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped
    trace.update(source_code=source,steps=[step],application_precondition_rejected=True);return trace

def build_rbt_insert_trace(trace,before_state,after_state,*,fail_malloc=False,null_ref=False):
    value=int(trace['payload']['value']);root_ref='NULL' if null_ref else '&raiz'
    source=trace['source_code'].rstrip()+'\n\n/**\n * @brief Invoca el TAD void con la raiz prestada, sin convertir retorno en exito.\n * @param arbol Referencia escribible prestada a la raiz propiedad del caller.\n * @note La preparacion del estado previo y la liberacion final son externas a esta traza.\n * El llamador conserva propiedad de las reservas; este auxiliar no libera memoria.\n */\nvoid ejecutar_insercion(RBT *arbol) {\n    rbt_insertar(arbol, '+str(value)+');\n}\n'
    lines=source.splitlines();ranges={}
    names=['rbt_abuelo','rbt_tio','rbt_rotar_dcha','rbt_rotar_izda',*[f'rbt_insercion_caso{i}' for i in range(1,6)],'rbt_insertar','ejecutar_insercion']
    for fn in names:
        start=next(i for i,l in enumerate(lines) if re.match(r'^(?:void|RBT)\s+'+fn+r'\(.*\)\s*\{',l.strip()));depth=0
        for end in range(start,len(lines)):
            depth+=lines[end].count('{')-lines[end].count('}')
            if depth==0:break
        ranges[fn]=(start,end)
    heap=[];frames=[];history=[];steps=[];caller=None;head='NULL';stdout='';returned=None
    def load(n,parent='NULL'):
        if n is None:return 'NULL'
        ident='N'+str(len(heap)+1);item={'id':ident,'value':n['value'],'left':'NULL','right':'NULL','parent':parent,'color':n['color'],'initialized':31,'status':'linked'};heap.append(item);item['left']=load(n['left'],ident);item['right']=load(n['right'],ident);return ident
    head=load(before_state.get('root'))
    def node(i):return next(n for n in heap if n['id']==i)
    def snapshot():
        reached=set()
        def project(i):
            if i in ['NULL',UNINIT] or i in reached:return None
            reached.add(i);n=node(i)
            if n['initialized']!=31:return None
            return {'value':n['value'],'color':n['color'],'left':project(n['left']),'right':project(n['right'])}
        root=project(head)
        for n in heap:n['status']='linked' if n['id'] in reached else 'detached'
        def height(n):return 0 if n is None else 1+max(height(n['left']),height(n['right']))
        s=deepcopy(before_state);s.update(abb_read_model=True,rbt_read_model=True,rbt_insert_model=True,head=head,root=root,size=len(reached),reachable_count=len(reached),heap_count=len(heap),height=height(root),empty=head=='NULL',heap_nodes=deepcopy(heap),tree_frames=deepcopy(frames),caller_frame=deepcopy(caller),console_stdout=stdout,returned=returned,validation=None,traversals={},transient_graph=True,live_visual_projection=True)
        return s
    def index(fn,text,k=0):
        a,z=ranges[fn]
        return z if text=='}' else [i for i in range(a,z+1) if lines[i].strip()==text][k]
    def vartype(name):return 'int' if name=='dato' else 'RBT *' if name in ['arbol','r'] else 'RBT'
    def emit(text,phase,change=None,condition=None,expression=None,result=None,k=0):
        old=snapshot();f=frames[-1] if frames else None;fn=f['function'] if f else 'ejecutar_insercion';owner=f['id'] if f else 'caller'
        if change:change()
        new=snapshot()
        if phase=='enter':f=frames[-1];fn=f['function'];owner=f['id']
        ix=index(fn,text,k);step={'step_index':len(steps),'line_index':ix,'line_text':lines[ix],'event_type':'line','delay_ms':170,'console':[result] if phase=='printf' else [],'state_snapshot':old,'state_after':new,'debug':{'stage':phase}}
        if condition is not None:step['condition_result']=bool(condition)
        ped=build_hierarchical_frame(structure_id='red_black',operation_name='insertar',payload=trace['payload'],step=step,source_lines=lines,success=True)
        added=[n for n in new['heap_nodes'] if n['id'] not in {q['id'] for q in old['heap_nodes']}]
        ped.update(concept='allocation' if added else 'output' if phase=='printf' else 'compare' if condition is not None else 'return' if phase in ['return','caller'] else 'descend' if phase in ['enter','call'] else 'assignment',case=phase,phase={'id':'insertar-'+phase,'label':phase.title(),'goal':text},condition=None)
        if condition is not None:ped['condition']={'source':expression or text,'substituted':expression or text,'result':bool(condition),'consequence':'Operando alcanzado por C; el cortocircuito omite los siguientes cuando corresponde.'};ped['executed_branch']='verdadero' if condition else 'falso'
        prev={(f['id'],n):v for f in old['tree_frames'] for n,v in {**f['parameters'],**f['locals']}.items()};now={(f['id'],n):v for f in new['tree_frames'] for n,v in {**f['parameters'],**f['locals']}.items()};variables=[]
        for f in history:
            for n in dict.fromkeys([*f['parameters'],*f['locals']]):
                key=(f['id'],n)
                if key not in prev and key not in now:continue
                a=prev.get(key,'fuera de ambito');b=now.get(key,'fuera de ambito');variables.append({'name':n,'scope':f['function']+'#'+f['id'],'frame_id':f['id'],'type':vartype(n),'previous':a,'value':b,'changed':a!=b,'meaning':'Local/parametro de esta invocacion. &raiz referencia almacenamiento del caller, no una reserva; N identifica un nodo estable. Un valor sin inicializar no se lee.'})
        if old['caller_frame'] or new['caller_frame']:variables.insert(0,{'name':'arbol','scope':'ejecutar_insercion','frame_id':'caller','type':'RBT *','previous':root_ref if old['caller_frame'] else 'fuera de ambito','value':root_ref if new['caller_frame'] else 'fuera de ambito','changed':bool(old['caller_frame'])!=bool(new['caller_frame']),'meaning':'Referencia prestada a la variable raiz; la propiedad no se transfiere y el retorno es void.'})
        ped['variables']=variables;shown=old['tree_frames'] if phase=='return' else new['tree_frames'];stack=[]
        if old['caller_frame'] or new['caller_frame']:stack.append({'function':'ejecutar_insercion','frame_id':'caller','depth':-1,'parameters':{'arbol':root_ref},'locals':{},'local_root':new['head'],'local_root_address':new['head'],'return':'void' if phase=='caller' else None,'continuation':'Solo las escrituras C publican enlaces/raiz; no se publica un resultado void.'})
        for f in shown:stack.append({'function':f['function'],'frame_id':f['id'],'depth':f['depth'],'parameters':deepcopy(f['parameters']),'locals':deepcopy(f['locals']),'local_root':f['parameters'].get('n',f['parameters'].get('nodoRBT',new['head'])),'local_root_address':f['parameters'].get('n',f['parameters'].get('nodoRBT',new['head'])),'return':result if phase=='return' and f['id']==owner else None,'continuation':'La asignacion del caller sucede despues del retorno; cada alias pertenece a su propio ambito.'})
        for f in stack:f['scope_status']='terminado (contexto del retorno)' if (phase=='return' and f['frame_id']==owner) or (phase=='caller' and f['frame_id']=='caller') else 'activo' if f['frame_id']==(new['tree_frames'][-1]['id'] if new['tree_frames'] else 'caller') else 'suspendido'
        ped['call_stack']=stack
        def objects(st):return [{**n,'address':n['id'],'symbolic_identity':True,'allocated':True,'freed':False} for n in st['heap_nodes']]
        ped['memory']={'event':'allocation' if added else 'none','objects_before':objects(old),'objects_after':objects(new),'allocated_objects':[{**n,'address':n['id'],'symbolic_identity':True,'allocated':True,'freed':False} for n in added],'freed_objects':[],'dangling_references':[],'stable_addresses':True,'symbolic_identities':True}
        descriptions={'caller_enter':'Comienza el caller equivalente sobre el estado previo; no repite la preparacion.','enter':'Entra un ambito con parametros propios, sin futuros locales.','call':'El caller queda suspendido; el inicializador declarado sigue sin valor hasta retornar.','local':'Completa la asignacion del local, sin cambiar el nodo apuntado.','declaration':'Comienza el ambito del local sin inicializar; no se lee ni se inventa un alias.','operand':'Evalua solo este operando alcanzado; NULL y cortocircuito impiden accesos omitidos.','condition':'Termina la condicion con operandos actuales; no escribe enlaces ni colores.','allocate':'Completa malloc y asigna actual. Si falla no hay nueva reserva; si obtiene memoria, sus campos siguen sin inicializar.','initialize':'Escribe solo los campos de esta instruccion antes de publicar el nodo.','link':'Escribe este enlace o raiz; una rotacion parcial puede tener fragmentos/ciclos transitorios. La vista no los convierte en NULL ni certifica un arbol final.','recolor':'Escribe solo el color indicado en la reserva real; las rotaciones no recolorean por si solas.','resume':'Retoma el caller despues del retorno void, sin otra mutacion.','return':'Completa este retorno y termina el ambito; los alias retornados son prestados y la asignacion del caller sigue pendiente.','printf':'Agrega la confirmacion C exactamente despues de reparar, no antes.','caller':'Termina el caller void sin liberar reservas ni publicar un supuesto estado de exito.'}
        ped['narration']={level:descriptions[phase] for level in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase in ['return','caller'],'value':result,'reconnects_subtree':False};ped['instruction_event']={'phase':phase,'frame_id':owner,'condition':condition,'expression':expression,'return':result if phase=='return' else None};ped['state_before']=deepcopy(old);ped['state_after']=deepcopy(new);ped['memory_state']=deepcopy(new)
        ped['invariant'].update(name='Estado parcial de insercion',holds=None,symbol='?',explanation='Reservas/alias estables y escrituras C observadas. No certifica orden, padres, rojo-rojo ni altura negra de un grafo transitorio. Validar sigue siendo una consulta limitada.')
        validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
    def enter(fn,pars):
        f={'id':'F'+str(len(history)+1),'function':fn,'depth':len(frames),'parameters':pars,'locals':{}};history.append(f);emit(lines[ranges[fn][0]].strip(),'enter',lambda:frames.append(f));return f
    def leave(text='}',result='void',k=0):
        def done():
            nonlocal returned
            frames.pop();returned=result
        emit(text,'return',done,result=result,k=k);return result
    def put(f,text,name,val,phase='local'):emit(text,phase,lambda:f['locals'].__setitem__(name,val))
    def fields(text,i,flags=0,**values):
        def done():node(i).update(values);node(i)['initialized']|=flags
        emit(text,'initialize' if flags else 'recolor' if 'color' in values else 'link',done)
    def sethead(i):
        nonlocal head
        head=i
    def substitute(expr):
        f=frames[-1];vals={**f['parameters'],**f['locals']}
        def token(m):
            parts=m.group().split('->');name=parts[0]
            if name=='ROJO':return "'r'"
            if name=='NEGRO':return "'n'"
            if name not in vals:return m.group()
            v=vals[name]
            for field in parts[1:]:
                if v in ['NULL',UNINIT] or v not in {n['id'] for n in heap}:return '(acceso no evaluado)'
                v=node(v)[{'nro':'value','rbt_color':'color','padre':'parent','izq':'left','der':'right'}[field]]
            return "'r'" if v=='RED' else "'n'" if v=='BLACK' else str(v)
        return re.sub(r'\b[A-Za-z_]\w*(?:->(?:nro|rbt_color|padre|izq|der))*\b',token,expr)
    def condition(text,terms,join=None):
        results=[];rendered=[]
        for expr,getter in terms:
            v=bool(getter());results.append(v);rendered.append(substitute(expr))
            if join:
                emit(text,'operand',condition=v,expression=expr)
                steps[-1]['pedagogy']['condition']['substituted']=rendered[-1]
            if join=='&&' and not v or join=='||' and v:break
        result=all(results) if join=='&&' else any(results) if join=='||' else results[0]
        emit(text,'condition',condition=result,expression=(' '+join+' ').join(expr for expr,_ in terms) if join else terms[0][0])
        for expr,_ in terms[len(results):]:rendered.append('(omitido por cortocircuito: '+expr+')')
        steps[-1]['pedagogy']['condition']['substituted']=(' '+join+' ').join(rendered) if join else rendered[0]
        return result
    def call(text,fn,args,name=None,frame=None,declare=False):
        emit(text,'call',(lambda:frame['locals'].__setitem__(name,UNINIT)) if declare else None);v=fn(*args)
        if name:put(frame,text,name,v)
        else:emit(text,'resume')
        return v
    def abuelo(n):
        enter('rbt_abuelo',{'n':n})
        if condition('if ((n != NULL) && (n->padre != NULL))',[('n != NULL',lambda:n!='NULL'),('n->padre != NULL',lambda:node(n)['parent']!='NULL')],'&&'):return leave('return n->padre->padre;',node(node(n)['parent'])['parent'])
        return leave('return NULL;','NULL')
    def tio(n):
        f=enter('rbt_tio',{'n':n});a=call('RBT a = rbt_abuelo(n);',abuelo,[n],'a',f,True)
        if condition('if (a == NULL)',[('a == NULL',lambda:a=='NULL')]):return leave('return NULL;','NULL')
        if condition('if (n->padre == a->izq)',[('n->padre == a->izq',lambda:node(n)['parent']==node(a)['left'])]):return leave('return a->der;',node(a)['right'])
        return leave('return a->izq;',node(a)['left'])
    def rotate(fn,i):
        f=enter(fn,{'r':root_ref,'nodoRBT':i});side='left' if fn=='rbt_rotar_dcha' else 'right';other='right' if side=='left' else 'left';field='izq' if side=='left' else 'der';opposite='der' if side=='left' else 'izq'
        text=f'if (r == NULL || nodoRBT == NULL || nodoRBT->{field} == NULL) {{'
        if condition(text,[('r == NULL',lambda:root_ref=='NULL'),('nodoRBT == NULL',lambda:i=='NULL'),(f'nodoRBT->{field} == NULL',lambda:node(i)[side]=='NULL')],'||'):return leave('return;')
        parent=node(i)['parent'];b=node(i)[side];c=node(b)[other]
        for text,name,val in [('RBT padre = nodoRBT->padre;','padre',parent),('RBT A = nodoRBT;','A',i),(f'RBT B = A->{field};','B',b),(f'RBT C = B->{opposite};','C',c)]:put(f,text,name,val)
        if condition('if (padre != NULL) {',[('padre != NULL',lambda:parent!='NULL')]):
            right=condition('if (padre->der == A)',[('padre->der == A',lambda:node(parent)['right']==i)]);fields('padre->'+('der' if right else 'izq')+' = B;',parent,**{'right' if right else 'left':b})
        else:emit('*r = B;','link',lambda:sethead(b))
        fields('A->'+field+' = C;',i,**{side:c});fields('B->'+opposite+' = A;',b,**{other:i});fields('A->padre = B;',i,parent=b)
        if condition('if (C)',[('C',lambda:c!='NULL')]):fields('C->padre = A;',c,parent=i)
        fields('B->padre = padre;',b,parent=parent);return leave()
    def case5(n):
        f=enter('rbt_insercion_caso5',{'n':n,'arbol':root_ref});a=call('RBT a = rbt_abuelo(n);',abuelo,[n],'a',f,True)
        fields('n->padre->rbt_color = NEGRO;',node(n)['parent'],color='BLACK');fields('a->rbt_color = ROJO;',a,color='RED')
        ll=condition('if ((n == n->padre->izq) && (n->padre == a->izq)) {',[('n == n->padre->izq',lambda:n==node(node(n)['parent'])['left']),('n->padre == a->izq',lambda:node(n)['parent']==node(a)['left'])],'&&')
        fn='rbt_rotar_dcha' if ll else 'rbt_rotar_izda';call(fn+'(arbol, a);',rotate,[fn,a]);return leave()
    def case4(n):
        f=enter('rbt_insercion_caso4',{'n':n,'arbol':root_ref});a=call('RBT a = rbt_abuelo(n);',abuelo,[n],'a',f,True);put(f,'RBT nuevo_n = n;','nuevo_n',n)
        lr=condition('if ((n == n->padre->der) && (n->padre == a->izq)) {',[('n == n->padre->der',lambda:n==node(node(n)['parent'])['right']),('n->padre == a->izq',lambda:node(n)['parent']==node(a)['left'])],'&&')
        if lr:
            call('rbt_rotar_izda(arbol, n->padre);',rotate,['rbt_rotar_izda',node(n)['parent']]);put(f,'nuevo_n = n->izq;','nuevo_n',node(n)['left'])
        elif condition('} else if ((n == n->padre->izq) && (n->padre == a->der)) {',[('n == n->padre->izq',lambda:n==node(node(n)['parent'])['left']),('n->padre == a->der',lambda:node(n)['parent']==node(a)['right'])],'&&'):
            call('rbt_rotar_dcha(arbol, n->padre);',rotate,['rbt_rotar_dcha',node(n)['parent']]);put(f,'nuevo_n = n->der;','nuevo_n',node(n)['right'])
        call('rbt_insercion_caso5(nuevo_n, arbol);',case5,[f['locals']['nuevo_n']]);return leave()
    def case3(n):
        f=enter('rbt_insercion_caso3',{'n':n,'arbol':root_ref});t=call('RBT t = rbt_tio(n);',tio,[n],'t',f,True);put(f,'RBT a;','a',UNINIT,'declaration')
        if condition('if ((t != NULL) && (t->rbt_color == ROJO)) {',[('t != NULL',lambda:t!='NULL'),('t->rbt_color == ROJO',lambda:node(t)['color']=='RED')],'&&'):
            fields('n->padre->rbt_color = NEGRO;',node(n)['parent'],color='BLACK');fields('t->rbt_color = NEGRO;',t,color='BLACK');a=call('a = rbt_abuelo(n);',abuelo,[n],'a',f);fields('a->rbt_color = ROJO;',a,color='RED');call('rbt_insercion_caso1(a, arbol);',case1,[a])
        else:call('rbt_insercion_caso4(n, arbol);',case4,[n])
        return leave()
    def case2(n):
        enter('rbt_insercion_caso2',{'n':n,'arbol':root_ref})
        if condition('if (n->padre->rbt_color == NEGRO)',[('n->padre->rbt_color == NEGRO',lambda:node(node(n)['parent'])['color']=='BLACK')]):return leave('return;')
        call('rbt_insercion_caso3(n, arbol);',case3,[n]);return leave()
    def case1(n):
        enter('rbt_insercion_caso1',{'n':n,'arbol':root_ref})
        if condition('if (n->padre == NULL)',[('n->padre == NULL',lambda:node(n)['parent']=='NULL')]):fields('n->rbt_color = NEGRO;',n,color='BLACK')
        else:call('rbt_insercion_caso2(n, arbol);',case2,[n])
        return leave()
    def insert():
        nonlocal stdout
        f=enter('rbt_insertar',{'arbol':root_ref,'dato':value})
        if condition('if (arbol == NULL) {',[('arbol == NULL',lambda:root_ref=='NULL')]):return leave('return;',k=0)
        put(f,'RBT padre = NULL;','padre','NULL');put(f,'RBT actual = *arbol;','actual',head)
        def actual():return f['locals']['actual']
        while condition('while (actual != NULL && dato != actual->nro) {',[('actual != NULL',lambda:actual()!='NULL'),('dato != actual->nro',lambda:value!=node(actual())['value'])],'&&'):
            put(f,'padre = actual;','padre',actual())
            if condition('if (dato < actual->nro)',[('dato < actual->nro',lambda:value<node(actual())['value'])]):put(f,'actual = actual->izq;','actual',node(actual())['left'])
            elif condition('else if (dato > actual->nro)',[('dato > actual->nro',lambda:value>node(actual())['value'])]):put(f,'actual = actual->der;','actual',node(actual())['right'])
        if condition('if (actual != NULL)',[('actual != NULL',lambda:actual()!='NULL')]):return leave('return;',k=1)
        def allocate():
            if fail_malloc:f['locals']['actual']='NULL';return
            ident='N'+str(len(heap)+1);heap.append({'id':ident,'value':UNINIT,'left':UNINIT,'right':UNINIT,'parent':UNINIT,'color':UNINIT,'initialized':0,'status':'detached'});f['locals']['actual']=ident
        emit('actual = malloc(sizeof(struct nodoRBT));','allocate',allocate)
        if condition('if (actual == NULL) {',[('actual == NULL',lambda:actual()=='NULL')]):return leave('return;',k=2)
        i=actual();parent=f['locals']['padre'];fields('actual->nro = dato;',i,1,value=value);fields('actual->izq = actual->der = NULL;',i,6,left='NULL',right='NULL');fields('actual->padre = padre;',i,8,parent=parent);fields('actual->rbt_color = ROJO;',i,16,color='RED')
        if condition('if (padre == NULL) {',[('padre == NULL',lambda:parent=='NULL')]):emit('*arbol = actual;','link',lambda:sethead(i))
        elif condition('} else if (dato < padre->nro) {',[('dato < padre->nro',lambda:value<node(parent)['value'])]):fields('padre->izq = actual;',parent,left=i)
        elif condition('} else if (dato > padre->nro) {',[('dato > padre->nro',lambda:value>node(parent)['value'])]):fields('padre->der = actual;',parent,right=i)
        call('rbt_insercion_caso1(actual, arbol);',case1,[i])
        fragment='\tEl numero ha sido insertado\n'
        def output():
            nonlocal stdout
            stdout+=fragment
        emit('printf("\\tEl numero ha sido insertado\\n");','printf',output,result=fragment);return leave()
    def caller_enter():
        nonlocal caller
        caller={'function':'ejecutar_insercion','parameters':{'arbol':root_ref},'locals':{},'description':'arbol (RBT *): '+root_ref+'; almacenamiento de la raiz, no reserva RBT. Propiedad permanece en el caller.'}
    emit('void ejecutar_insercion(RBT *arbol) {','caller_enter',caller_enter);insert()
    def caller_exit():
        nonlocal caller
        caller=None
    emit('}','caller',caller_exit,result='void');steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    first=steps[0]['pedagogy'];initial=deepcopy(first);initial.update(variables=[],call_stack=[],condition=None,state_before=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']),memory_state=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={k:'Estado previo, sin parametros/locales/campos futuros y sin printf de la nueva operacion.' for k in ['basic','intermediate','advanced']};first['initial_frame']=initial
    trace.update(source_code=source,steps=steps,console=[stdout] if stdout else []);return trace
