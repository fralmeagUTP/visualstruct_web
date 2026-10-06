"""Recorded AVL deletion statements and nested query/rotation scopes; symbolic lifetimes."""
from copy import deepcopy
from app.services.c_code_service import CCodeService
from .pedagogy import build_hierarchical_frame,validate_hierarchical_frame

NUMERIC={'x','tmp','feL','feR','altIzq','altDer'}
def build_avl_delete_rejection_trace(trace,before_state,after_state):
    """Application precondition explanation: the public C method was not invoked."""
    assert before_state==after_state
    source='/* Solicitud rechazada por la aplicacion antes de invocar avl_eliminar. */\n\n'+trace['source_code']
    step={'step_index':0,'line_index':0,'line_text':source.splitlines()[0],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':deepcopy(before_state),'state_after':deepcopy(after_state),'debug':{'stage':'application_precondition_rejected'}}
    ped=build_hierarchical_frame(structure_id='avl',operation_name='eliminar',payload=trace['payload'],step=step,source_lines=source.splitlines(),success=False)
    ped.update(concept='compare',case='application_precondition_rejected',phase={'id':'application_precondition_rejected','label':'Solicitud rechazada antes del TAD','goal':'La aplicacion conserva el arbol y no invoca el metodo C.'},condition=None,variables=[],call_stack=[],return_propagation={'active':False,'value':None,'reconnects_subtree':False},instruction_event={'phase':'application_precondition_rejected','C_invoked':False,'return':None},memory={'event':'none','objects_before':[],'objects_after':[],'allocated_objects':[],'freed_objects':[],'dangling_references':[]})
    ped['narration']={level:'La aplicacion rechazo la solicitud antes del TAD; el C mostrado es referencia, no instrucciones ejecutadas. El arbol permanece igual y no hay retorno C, reserva, free ni printf.' for level in ['basic','intermediate','advanced']};validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped
    trace.update(source_code=source,steps=[step],application_precondition_rejected=True);return trace

def build_avl_delete_trace(trace,before_state,after_state,*,null_ref=False):
    value=int(trace['payload']['value']);root_reference='NULL' if null_ref else '&raiz';raw=(CCodeService._DOCS_TADS_C/'tad_avl.c').read_text(encoding='utf-8-sig');bodies={}
    for fn,signature in [('avl_eliminar','void'),('rebalancearTrasEliminar','static void'),('avl_buscar','AVL'),('avl_minimo','AVL'),('avl_altura','int'),('avl_RSD','void'),('avl_RSI','void'),('avl_RDD','void'),('avl_RDI','void')]:
        # Public prototypes precede two definitions: select the actual body, not a declaration.
        start=raw.index(signature+' '+fn+'(')
        while raw.index(';',start)<raw.index('{',start):start=raw.index(signature+' '+fn+'(',start+1)
        opening=raw.index('{',start);depth=1;end=opening+1
        while depth:depth+=int(raw[end]=='{')-int(raw[end]=='}');end+=1
        bodies[fn]=raw[start:end]
    source='\n\n'.join(bodies.values())+'\n\n/**\n * @brief Invoca Eliminar sin convertir su retorno void en un estado de exito.\n * @param arbol Referencia prestada a la raiz propiedad del llamador.\n * @note El TAD libera la reserva fisica retirada; el llamador conserva el arbol restante.\n */\nvoid ejecutar_eliminacion(AVL *arbol) {\n    avl_eliminar(arbol, '+str(value)+');\n}\n'
    lines=source.splitlines();ranges={}
    for fn in [*bodies,'ejecutar_eliminacion']:
        start=next(i for i,l in enumerate(lines) if (' '+fn+'(') in l and l.rstrip().endswith('{'));depth=0
        for end in range(start,len(lines)):
            depth+=lines[end].count('{')-lines[end].count('}')
            if depth==0:break
        ranges[fn]=(start,end)
    heap=[];freed=[];frames=[];history=[];steps=[];caller=None;head='NULL';returned=None
    def load(n,parent='NULL'):
        if n is None:return 'NULL'
        identity='N'+str(len(heap)+1);item={'id':identity,'value':n['value'],'balance_factor':n['balance_factor'],'left':'NULL','right':'NULL','parent':parent,'status':'linked'};heap.append(item);item['left']=load(n['left'],identity);item['right']=load(n['right'],identity);return identity
    head=load(before_state.get('root'))
    def node(i):return next(n for n in heap if n['id']==i)
    def snapshot():
        reached=set()
        def tree(i):
            if i=='NULL' or i in reached:return None
            reached.add(i);n=node(i);left,right=tree(n['left']),tree(n['right']);return {'value':n['value'],'left':left,'right':right,'balance_factor':n['balance_factor'],'height':1+max(left['height'] if left else 0,right['height'] if right else 0)}
        root=tree(head)
        for n in heap:n['status']='linked' if n['id'] in reached else 'detached'
        state=deepcopy(before_state);state.update(abb_read_model=True,avl_read_model=True,avl_delete_model=True,head=head,root=root,size=len(reached),height=root['height'] if root else 0,empty=not reached,heap_nodes=deepcopy(heap),freed_nodes=deepcopy(freed),tree_frames=deepcopy(frames),caller_frame=deepcopy(caller),returned=returned,validation=None,traversals={},console_stdout='',transient_graph=True,operand_evaluation_order='primero derecha, luego izquierda; eleccion legal para las llamadas puras en la resta, no impuesta por C')
        return state
    def index(fn,text,k=0):
        a,z=ranges[fn]
        if text=='}':return z
        return [i for i in range(a,z+1) if lines[i].strip()==text][k]
    def vartype(fn,name):return 'int' if name in NUMERIC else 'AVL *' if name=='r' or (name=='raiz' and fn in ['avl_eliminar','rebalancearTrasEliminar']) else 'AVL'
    def emit(text,phase,mutate=None,condition=None,k=0,expression=None,result=None,source_index=None):
        old=snapshot();f=frames[-1] if frames else None;fn=f['function'] if f else 'ejecutar_eliminacion';owner=f['id'] if f else 'caller'
        if mutate:mutate()
        new=snapshot()
        if phase=='enter':fn=frames[-1]['function'];owner=frames[-1]['id']
        idx=index(fn,text,k) if source_index is None else source_index;step={'step_index':len(steps),'line_index':idx,'line_text':lines[idx],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':old,'state_after':new,'debug':{'stage':phase}}
        if phase=='condition':step['condition_result']=bool(condition)
        ped=build_hierarchical_frame(structure_id='avl',operation_name='eliminar',payload=trace['payload'],step=step,source_lines=lines,success=True);retired=[n for n in old['heap_nodes'] if n['id'] not in {n['id'] for n in new['heap_nodes']}]
        ped['concept']='free' if retired else 'compare' if phase=='condition' else 'return' if phase in ['return','caller'] else 'descend' if phase in ['call','enter'] else 'assignment';ped['case']=phase;ped['phase']={'id':'eliminar-'+phase,'label':phase.title(),'goal':text};ped['condition']=None
        if phase=='condition':ped['condition']={'source':text,'substituted':expression or text,'result':bool(condition),'consequence':'rama u operando ejecutado con valores actuales; cortocircuito omite el siguiente si corresponde'};ped['executed_branch']='verdadero' if condition else 'falso'
        previous={(f['id'],n):v for f in old['tree_frames'] for n,v in {**f['parameters'],**f['locals']}.items()};current={(f['id'],n):v for f in new['tree_frames'] for n,v in {**f['parameters'],**f['locals']}.items()};variables=[]
        for invocation in history:
            for name in dict.fromkeys([*invocation['parameters'],*invocation['locals'],*(n for fid,n in previous if fid==invocation['id'])]):
                key=(invocation['id'],name)
                if key not in previous and key not in current:continue
                a=previous.get(key,'fuera de ambito');b=current.get(key,'fuera de ambito');variables.append({'name':name,'scope':invocation['function']+'#'+invocation['id'],'frame_id':invocation['id'],'type':vartype(invocation['function'],name),'previous':a,'value':b,'changed':a!=b,'meaning':'Parametro/local propio; N es identidad simbolica. Alias de reservas terminadas son historicos e inutilizables; no se leen punteros despues de free.'})
        if old['caller_frame'] or new['caller_frame']:variables.insert(0,{'name':'arbol','scope':'ejecutar_eliminacion','frame_id':'caller','type':'AVL *','previous':root_reference if old['caller_frame'] else 'fuera de ambito','value':root_reference if new['caller_frame'] else 'fuera de ambito','changed':bool(old['caller_frame'])!=bool(new['caller_frame']),'meaning':'Referencia a la variable raiz; su valor actual es '+head+'. Eliminar retorna void, no una raiz ni estado de exito.'})
        ped['variables']=variables;shown=old['tree_frames'] if phase=='return' else new['tree_frames'];stack=[]
        if old['caller_frame'] or new['caller_frame']:stack.append({'function':'ejecutar_eliminacion','frame_id':'caller','depth':-1,'parameters':{'arbol':root_reference},'locals':{},'local_root':head,'local_root_address':head,'return':'void' if phase=='caller' else None,'continuation':'Invocacion void; raiz se publica solamente donde escribe el TAD.'})
        for f in shown:stack.append({'function':f['function'],'frame_id':f['id'],'depth':f['depth'],'parameters':deepcopy(f['parameters']),'locals':deepcopy(f['locals']),'local_root':f['parameters'].get('nodo',f['parameters'].get('arbol',head)),'local_root_address':f['parameters'].get('nodo',f['parameters'].get('arbol',head)),'return':result if phase=='return' and f['id']==owner else None,'continuation':'El retorno termina este marco; la asignacion del llamador sucede en un evento posterior.'})
        for f in stack:f['scope_status']='terminado (contexto del retorno)' if (phase=='return' and f['frame_id']==owner) or (phase=='caller' and f['frame_id']=='caller') else 'activo' if f['frame_id']==(new['tree_frames'][-1]['id'] if new['tree_frames'] else 'caller') else 'suspendido'
        ped['call_stack']=stack
        def objects(st):return [{**n,'address':n['id'],'symbolic_identity':True,'allocated':True,'freed':False} for n in st['heap_nodes']]
        dead={n['id'] for n in freed};dangling=[{'frame_id':f['id'],'name':name,'address':v,'usable':False,'meaning':'identidad historica de reserva terminada; no puntero vivo'} for f in new['tree_frames'] for name,v in {**f['parameters'],**f['locals']}.items() if v in dead]
        ped['memory']={'event':'free' if retired else 'none','objects_before':objects(old),'objects_after':objects(new),'allocated_objects':[],'freed_objects':[{**n,'address':n['id'],'symbolic_identity':True,'allocated':False,'freed':True} for n in retired],'dangling_references':[],'unusable_reference_records':dangling,'records_are_not_pointer_values':True,'retired_objects':deepcopy(freed),'stable_addresses':True,'symbolic_identities':True}
        description={'caller_enter':'Entra el llamador equivalente sin resultado futuro.','enter':'Entra una funcion con parametros propios, sin futuros locales.','call':'Transfiere control; un local declarado para el inicializador aun no tiene valor hasta retornar.','condition':'Evalua este operando/condicion con los valores actuales; respeta cortocircuito.','after':'Completa esta instruccion o asignacion del llamador; no adelanta otros enlaces ni FE.','scope_exit':'Termina este bloque C: sus locales dejan de existir sin liberar reservas ni asignar NULL.', 'free':'Termina la vida de la reserva fisica retirada. Los alias restantes son historicos inutilizables, no NULL ficticio.','return':'Completa el retorno de esta funcion; no asigna todavia el local del llamador.','caller':'Termina la invocacion void; no devuelve un estado C de exito.'}[phase]
        if fn=='rebalancearTrasEliminar' and 'avl_altura(' in text:description+=' En esta resta se elige primero la altura derecha y despues la izquierda; C permite otro orden.'
        ped['narration']={level:description for level in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase in ['return','caller'],'value':result,'reconnects_subtree':False};ped['state_before']=deepcopy(old);ped['state_after']=deepcopy(new);ped['memory_state']=deepcopy(new);ped['instruction_event']={'phase':phase,'frame_id':owner,'condition':condition,'return':result}
        ped['invariant'].update(holds=None,symbol='?',explanation='Estado transitorio ejecutado: intercambio puede violar orden, reconexion/FE pueden ser parciales. Reservas terminadas y alias historicos no se desreferencian; no se certifica AVL final.')
        validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
    def enter(fn,parameters):
        f={'id':'F'+str(len(history)+1),'function':fn,'depth':len(frames),'parameters':parameters,'locals':{}};history.append(f);emit(bodies[fn].splitlines()[0],'enter',lambda:frames.append(f));return f
    def cond(t,v,**kw):emit(t,'condition',condition=bool(v),**kw);return bool(v)
    def put(f,t,**kw):emit(t,'after',lambda:f['locals'].update(kw))
    def field(t,i,**kw):emit(t,'after',lambda:node(i).update(kw))
    def leave(text='}',result='void'):
        def finish():
            nonlocal returned
            frames.pop();returned=result
        emit(text,'return',finish,result=result);return result
    def set_head(i):
        nonlocal head
        head=i
    def scope_exit(f,names,opening):
        start=index(f['function'],opening);depth=1;closing=None
        for i in range(start,len(lines)):
            segment=lines[i][lines[i].index('{')+1:] if i==start else lines[i]
            for c in segment:
                depth+=int(c=='{')-int(c=='}')
                if depth==0:closing=i;break
            if closing is not None:break
        assert closing is not None
        emit(lines[closing].strip(),'scope_exit',lambda:[f['locals'].pop(n) for n in names],source_index=closing)
    def height(i):
        f=enter('avl_altura',{'arbol':i})
        if cond('if (arbol == NULL)',i=='NULL',expression=i+' == NULL'):return leave('return 0;',result=0)
        for name,side,cs in [('altIzq','left','izq'),('altDer','right','der')]:
            t='int '+name+' = avl_altura(arbol->'+cs+');';emit(t,'call',lambda:f['locals'].update({name:'sin inicializar'}));v=height(node(i)[side]);put(f,t,**{name:v})
        t='return (altIzq > altDer ? altIzq : altDer) + 1;';a,b=f['locals']['altIzq'],f['locals']['altDer'];cond(t,a>b,expression=str(a)+' > '+str(b));return leave(t,result=max(a,b)+1)
    def search(i):
        enter('avl_buscar',{'raiz':i,'x':value})
        if cond('if (!raiz)',i=='NULL',expression='!'+i):return leave('return NULL;',result='NULL')
        if cond('if (x < raiz->nro)',value<node(i)['value'],expression=str(value)+' < '+str(node(i)['value'])):t='return avl_buscar(raiz->izq, x);';side='left'
        elif cond('if (x > raiz->nro)',value>node(i)['value'],expression=str(value)+' > '+str(node(i)['value'])):t='return avl_buscar(raiz->der, x);';side='right'
        else:return leave('return raiz;',result=i)
        emit(t,'call');result=search(node(i)[side]);return leave(t,result=result)
    def minimum(i):
        f=enter('avl_minimo',{'nodo':i})
        while cond('while (nodo->izq)',node(f['parameters']['nodo'])['left']!='NULL',expression=node(f['parameters']['nodo'])['left']+' != NULL'):
            n=f['parameters']['nodo'];emit('nodo = nodo->izq;','after',lambda:f['parameters'].update(nodo=node(n)['left']))
        return leave('return nodo;',result=f['parameters']['nodo'])
    def rotate(fn,i):
        f=enter(fn,{'r':root_reference,'nodo':i});left=fn in ['avl_RSD','avl_RDD'];side='left' if left else 'right';child=node(i)[side] if i!='NULL' else 'NULL';double=fn in ['avl_RDD','avl_RDI'];other='right' if left else 'left';cs='izq' if left else 'der';co='der' if left else 'izq'
        guard=f'if (r == NULL || nodo == NULL || nodo->{cs} == NULL'+(f' || nodo->{cs}->{co} == NULL' if double else '')+') {'
        if cond(guard,null_ref,expression=root_reference+' == NULL') or cond(guard,i=='NULL',expression=i+' == NULL') or cond(guard,child=='NULL',expression=child+' == NULL') or (double and cond(guard,node(child)[other]=='NULL',expression=node(child)[other]+' == NULL')):leave('return;');return
        if double:
            put(f,'AVL A = nodo;',A=i);put(f,'AVL B = A->'+cs+';',B=child)
            for callee,target,name in [('avl_RSI' if left else 'avl_RSD',child,'B'),('avl_RSD' if left else 'avl_RSI',i,'A')]:
                t=callee+'(r, '+name+');';emit(t,'call');rotate(callee,target);emit(t,'after')
        else:
            parent=node(i)['parent'];put(f,'AVL padre = nodo->padre;',padre=parent);put(f,'AVL A = nodo;',A=i);put(f,'AVL B = A->'+cs+';',B=child);transfer=node(child)[other];put(f,'AVL C = B->'+co+';',C=transfer)
            if cond('if (padre) {',parent!='NULL',expression=parent+' != NULL'):
                right=cond('if (padre->der == A)',node(parent)['right']==i,expression=node(parent)['right']+' == '+i);field('padre->'+('der' if right else 'izq')+' = B;',parent,**{'right' if right else 'left':child})
            else:emit('*r = B;','after',lambda:set_head(child))
            field('A->'+cs+' = C;',i,**{side:transfer});field('B->'+co+' = A;',child,**{other:i});field('A->padre = B;',i,parent=child)
            if cond('if (C)',transfer!='NULL',expression=transfer+' != NULL'):field('C->padre = A;',transfer,parent=i)
            field('B->padre = padre;',child,parent=parent);a,b=node(i)['balance_factor'],node(child)['balance_factor']
            ta='A->FE = A->FE '+('+ 1 - (B->FE < 0 ? B->FE : 0);' if left else '- 1 - (B->FE > 0 ? B->FE : 0);');branch=cond(ta,b<0 if left else b>0,expression=str(b)+(' < 0' if left else ' > 0'));newa=a+1-(b if branch else 0) if left else a-1-(b if branch else 0);field(ta,i,balance_factor=newa)
            tb='B->FE = B->FE '+('+ 1 + (A->FE > 0 ? A->FE : 0);' if left else '- 1 + (A->FE < 0 ? A->FE : 0);');branch=cond(tb,newa>0 if left else newa<0,expression=str(newa)+(' > 0' if left else ' < 0'));newb=b+1+(newa if branch else 0) if left else b-1+(newa if branch else 0);field(tb,child,balance_factor=newb)
        leave()
    def rebalance(i):
        f=enter('rebalancearTrasEliminar',{'raiz':root_reference,'nodo':i})
        while cond('while (nodo) {',f['parameters']['nodo']!='NULL',expression=f['parameters']['nodo']+' != NULL'):
            n=f['parameters']['nodo'];t='nodo->FE = avl_altura(nodo->der) - avl_altura(nodo->izq);';emit(t,'call');rh=height(node(n)['right']);lh=height(node(n)['left']);field(t,n,balance_factor=rh-lh)
            if cond('if (nodo->FE == -2) {',node(n)['balance_factor']==-2,expression=str(node(n)['balance_factor'])+' == -2'):left=True
            elif cond('} else if (nodo->FE == 2) {',node(n)['balance_factor']==2,expression=str(node(n)['balance_factor'])+' == 2'):left=False
            else:left=None
            if left is not None:
                name='L' if left else 'R';cs='izq' if left else 'der';child=node(n)['left' if left else 'right'];put(f,'AVL '+name+' = nodo->'+cs+';',**{name:child});num='feL' if left else 'feR';t='int '+num+' = ('+name+' ? (avl_altura('+name+'->der) - avl_altura('+name+'->izq)) : 0);';emit(t,'call',lambda:f['locals'].update({num:'sin inicializar'}))
                if cond(t,child!='NULL',expression=child+' != NULL'):a=height(node(child)['right']);b=height(node(child)['left']);fe=a-b
                else:fe=0
                put(f,t,**{num:fe});double=cond('if ('+num+(' > 0' if left else ' < 0')+') {',fe>0 if left else fe<0,expression=str(fe)+(' > 0' if left else ' < 0'));fn=('avl_RDD' if double else 'avl_RSD') if left else ('avl_RDI' if double else 'avl_RSI');t=fn+'(raiz, nodo);';emit(t,'call');rotate(fn,n);emit(t,'after');scope_exit(f,[name,num],'if (nodo->FE == -2) {' if left else '} else if (nodo->FE == 2) {')
            emit('nodo = nodo->padre;','after',lambda:f['parameters'].update(nodo=node(n)['parent']))
        leave()
    def delete():
        f=enter('avl_eliminar',{'raiz':root_reference,'x':value})
        if cond('if (raiz == NULL) {',null_ref,expression=root_reference+' == NULL'):leave('return;');return
        t='AVL z = avl_buscar(*raiz, x);';emit(t,'call',lambda:f['locals'].update(z='sin inicializar'));z=search(head);put(f,t,z=z)
        if cond('if (!z) return;',z=='NULL',expression='!'+z):leave('if (!z) return;');return
        t='while (z->izq && z->der) {'
        while cond(t,node(f['locals']['z'])['left']!='NULL',expression=node(f['locals']['z'])['left']+' != NULL') and cond(t,node(f['locals']['z'])['right']!='NULL',expression=node(f['locals']['z'])['right']+' != NULL'):
            z=f['locals']['z'];t2='AVL s = avl_minimo(z->der);';emit(t2,'call',lambda:f['locals'].update(s='sin inicializar'));s=minimum(node(z)['right']);put(f,t2,s=s);put(f,'int tmp = z->nro;',tmp=node(z)['value']);field('z->nro = s->nro;',z,value=node(s)['value']);field('s->nro = tmp;',s,value=f['locals']['tmp']);put(f,next(l.strip() for l in lines if l.strip().startswith('z = s;')),z=s);scope_exit(f,['s','tmp'],'while (z->izq && z->der) {')
        z=f['locals']['z'];parent=node(z)['parent'];put(f,'AVL padre = z->padre;',padre=parent);t='AVL child = (z->izq) ? z->izq : z->der;';left=cond(t,node(z)['left']!='NULL',expression=node(z)['left']+' != NULL');child=node(z)['left' if left else 'right'];put(f,t,child=child)
        if cond('if (child) child->padre = padre;',child!='NULL',expression=child+' != NULL'):field('if (child) child->padre = padre;',child,parent=parent)
        if cond('if (!padre) {',parent=='NULL',expression='!'+parent):emit('*raiz = child;','after',lambda:set_head(child))
        elif cond('} else if (padre->izq == z) {',node(parent)['left']==z,expression=node(parent)['left']+' == '+z):field('padre->izq = child;',parent,left=child)
        else:field('padre->der = child;',parent,right=child)
        def retire():freed.append(deepcopy(node(z)));heap.remove(node(z))
        emit('free(z);','call');emit('free(z);','free',retire,result=z);emit('free(z);','after')
        if cond('if (padre) rebalancearTrasEliminar(raiz, padre);',parent!='NULL',expression=parent+' != NULL'):
            t='if (padre) rebalancearTrasEliminar(raiz, padre);';emit(t,'call');rebalance(parent);emit(t,'after')
        leave()
    def caller_enter():
        nonlocal caller
        caller={'function':'ejecutar_eliminacion','parameters':{'arbol':root_reference},'description':'arbol (AVL *) -> '+root_reference+'; retorna void. Reservas terminadas no son punteros utilizables.'}
    emit('void ejecutar_eliminacion(AVL *arbol) {','caller_enter',caller_enter);emit('avl_eliminar(arbol, '+str(value)+');','call');delete()
    def caller_exit():
        nonlocal caller
        caller=None
    emit('}','caller',caller_exit,result='void');steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    initial=deepcopy(steps[0]['pedagogy']);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={l:'Ninguna instruccion ejecutada, sin parametros/retornos futuros ni reservas retiradas.' for l in ['basic','intermediate','advanced']};steps[0]['pedagogy']['initial_frame']=initial
    trace.update(source_code=source,steps=steps);return trace
