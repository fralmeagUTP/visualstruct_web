"""Instruction boundaries of the unchanged ABB deletion and minimum dependency.

Pointer identities are symbolic. Ended lifetimes retain saved records, never
dereferenceable pointer values. Call entry does not publish its future return.
"""
from copy import deepcopy
from .pedagogy import build_hierarchical_frame, validate_hierarchical_frame


def build_abb_delete_trace(trace, before_state, after_state):
    from app.services.c_code_service import CCodeService
    value=int(trace['payload']['value'])
    source=trace['source_code'].rstrip()+'\n\n'+CCodeService.get_structure_data('abb')['operations']['minimo'].rstrip()
    heap=[];live=set();frames=[];history=[];retired=[];steps=[];caller=None;returned=None
    def load(n):
        if n is None:return 'NULL'
        identity='N'+str(len(heap)+1);item={'id':identity,'value':n['value'],'left':'NULL','right':'NULL','status':'linked'};heap.append(item)
        item['left'],item['right']=load(n['left']),load(n['right']);return identity
    head=load(before_state.get('root'));live.update(n['id'] for n in heap)
    def node(identity):return next(n for n in heap if n['id']==identity)
    def reference(identity):return identity if identity in {'NULL','sin inicializar'} or identity in live else identity+' [valor indeterminado; identidad historica]'
    def projection(identity):
        if identity not in live:return None
        n=node(identity);return {'value':n['value'],'left':projection(n['left']),'right':projection(n['right'])}
    prep='\n'.join('    arbol = abb_insertar(arbol, '+str(n['value'])+');' for n in heap)
    source+='\n\n/* Main equivalente: preparacion ya realizada antes de esta traza. */\nint main(void) {\n    ABBNodo *arbol = NULL;\n'+prep+'\n    arbol = abb_eliminar(arbol, '+str(value)+');\n    return 0;\n}\n'
    lines=source.splitlines()
    starts={fn:next(i for i,l in enumerate(lines) if l.strip().startswith('ABBNodo* '+fn+'(')) for fn in ['abb_eliminar','abb_encontrarMinimo']}
    def index(text,fn,occurrence=0):
        start=starts[fn] if fn in starts else next(i for i,l in enumerate(lines) if l.strip()=='int main(void) {')
        return [i for i in range(start,len(lines)) if lines[i].strip()==text][occurrence]
    def snapshot():
        state=deepcopy(before_state);active=deepcopy(frames);reached=set()
        def walk(identity):
            if identity not in live or identity in reached:return
            reached.add(identity);n=node(identity);walk(n['left']);walk(n['right'])
        walk(head)
        for f in active:
            f['parameters']['nodo']=reference(f['parameters']['nodo'])
            for name in f['locals']:f['locals'][name]=reference(f['locals'][name])
        current=[{**deepcopy(n),'left':reference(n['left']),'right':reference(n['right']),'status':'linked' if n['id'] in reached else 'detached'} for n in heap if n['id'] in live]
        root=projection(head)
        def height(n):return 0 if n is None else 1+max(height(n['left']),height(n['right']))
        def traversal(n,order):
            if n is None:return []
            a,b=traversal(n['left'],order),traversal(n['right'],order);v=[n['value']]
            return v+a+b if order=='preorden' else a+b+v if order=='postorden' else a+v+b
        state.update(abb_read_model=True,abb_delete_model=True,head=reference(head),head_identity=head,heap_nodes=current,freed_nodes=deepcopy(retired),tree_frames=active,caller_frame=None if caller is None else {'function':'main','parameters':{},'locals':{'arbol':reference(head)},'description':'arbol (ABBNodo *): '+reference(head)+'; publica el retorno solo al completar la llamada.'},returned=reference(returned) if returned is not None else None,console_stdout='',root=root,size=len(reached),reserved_count=len(live),empty=root is None,height=height(root),traversals={o:traversal(root,o) for o in ['inorden','preorden','postorden']},live_visual_projection=True,validation=None)
        return state
    def objects(state):return [{'id':n['id'],'address':n['id'],'symbolic_identity':True,'value':n['value'],'left':n['left'],'right':n['right'],'allocated':True,'freed':False} for n in state['heap_nodes']]
    descriptions={
        'caller_enter':'Entra al main equivalente con su raiz previamente preparada; no reejecuta esa preparacion.',
        'enter':'Entra una invocacion con sus propios parametros. El padre permanece suspendido.',
        'condition':'Evalua la condicion con los valores de esta invocacion, sin cambiar el arbol.',
        'call':'Inicia la llamada, evaluando los argumentos ahora. Su retorno y la asignacion permanecen pendientes; no hay estado futuro.',
        'assignment':'Escribe solo el alias o valor indicado. Copiar el valor del sucesor conserva ambas reservas; puede haber valores duplicados transitorios.',
        'free':'Termina la vida de esta reserva. Los alias a ella son registros historicos inutilizables; no se leen ni se asignan ficticiamente a NULL.',
        'return':'Termina este ambito y retorna el puntero indicado. El llamador todavia debe asignarlo a su enlace o raiz.',
        'link':'La llamada ya retorno; ahora escribe solo el enlace indicado con el reemplazo vivo o NULL.',
        'caller':'La llamada exterior ya retorno; ahora el main publica la raiz sin leer su valor anterior.',
        'caller_exit':'El main retorna 0; termina su ambito, conservando las reservas restantes.'}
    def emit(text,phase,mutate=None,condition=None,expression=None,result=None,fn=None,occurrence=0):
        old=snapshot();owner=frames[-1]['id'] if frames else 'caller';function=fn or (frames[-1]['function'] if frames else 'main')
        if mutate:mutate()
        new=snapshot()
        if phase=='enter':owner=new['tree_frames'][-1]['id']
        idx=index(text,function,occurrence);step={'step_index':len(steps),'line_index':idx,'line_text':lines[idx],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':old,'state_after':new,'debug':{'stage':phase}}
        if phase=='condition':step['condition_result']=condition
        ped=build_hierarchical_frame(structure_id='abb',operation_name='eliminar',payload=trace['payload'],step=step,source_lines=lines,success=True)
        ped.update(concept={'condition':'compare','free':'free','return':'return','link':'link','caller':'link'}.get(phase,'assignment'),case=phase,phase={'id':'eliminar-'+phase,'label':phase.title(),'goal':text},condition=None)
        if phase=='condition':ped['condition']={'source':text,'substituted':expression,'result':condition,'consequence':'rama evaluada de esta invocacion'};ped['executed_branch']='cuerpo' if condition else 'else/salida'
        previous={(f['id'],name):v for f in old['tree_frames'] for name,v in {**f['parameters'],**f['locals']}.items()};current={(f['id'],name):v for f in new['tree_frames'] for name,v in {**f['parameters'],**f['locals']}.items()};variables=[]
        if old['caller_frame'] or new['caller_frame']:variables.append({'name':'arbol','scope':'main','frame_id':'caller','type':'ABBNodo *','previous':old['head'] if old['caller_frame'] else 'fuera de ámbito','value':new['head'] if new['caller_frame'] else 'fuera de ámbito','changed':old['head']!=new['head'] or bool(old['caller_frame'])!=bool(new['caller_frame']),'meaning':'Raiz local; el retorno no la asigna hasta completar la llamada.'})
        for f in history:
            for name in ['nodo','valor','temp']:
                key=(f['id'],name)
                if key not in previous and key not in current:continue
                a=previous.get(key,'fuera de ámbito');b=current.get(key,'fuera de ámbito');variables.append({'name':name,'scope':f['function']+'#'+f['id'],'frame_id':f['id'],'type':'int' if name=='valor' else 'ABBNodo *','previous':a,'value':b,'changed':a!=b,'meaning':'Ambito propio; temp no se inicializa antes del retorno del minimo. Identidades terminadas son historicas, no valores leidos.'})
        ped['variables']=variables;shown=old['tree_frames'] if phase=='return' else new['tree_frames'];stack=[]
        if old['caller_frame'] or new['caller_frame']:stack.append({'function':'main','frame_id':'caller','depth':-1,'parameters':{},'locals':{'arbol':new['head']},'local_root':new['head'],'local_root_address':new['head'],'return':0 if phase=='caller_exit' else None,'continuation':'asignar raiz al completar abb_eliminar'})
        for f in shown:stack.append({'function':f['function'],'frame_id':f['id'],'depth':f['depth'],'parameters':deepcopy(f['parameters']),'locals':deepcopy(f['locals']),'local_root':f['parameters']['nodo'],'local_root_address':f['parameters']['nodo'],'return':reference(result) if phase=='return' and f['id']==owner else None,'continuation':'el retorno no escribe por si solo el enlace del padre'})
        for f in stack:f['scope_status']='terminado (contexto del retorno)' if (phase=='return' and f['frame_id']==owner) or (phase=='caller_exit' and f['frame_id']=='caller') else 'activo' if (new['tree_frames'] and f['frame_id']==new['tree_frames'][-1]['id']) or (not new['tree_frames'] and f['frame_id']=='caller') else 'suspendido'
        ped['call_stack']=stack;records=[]
        if new['caller_frame'] and head!='NULL' and head not in live:records.append({'kind':'caller','name':'arbol','identity':head,'usable':False,'historical_identity':True})
        for f in frames:
            for name,identity in {**f['parameters'],**f['locals']}.items():
                if name!='valor' and identity not in {'NULL','sin inicializar'} and identity not in live:records.append({'kind':'parameter' if name=='nodo' else 'local','frame':f['id'],'name':name,'identity':identity,'usable':False,'historical_identity':True})
        for n in heap:
            if n['id'] in live:
                for side in ['left','right']:
                    if n[side]!='NULL' and n[side] not in live:records.append({'kind':'field','object':n['id'],'name':side,'identity':n[side],'usable':False,'historical_identity':True})
        ped['memory']={'event':'free' if phase=='free' else 'link' if phase in {'link','caller'} else 'none','objects_before':objects(old),'objects_after':objects(new),'allocated_objects':[],'freed_objects':[n for n in objects(old) if n['id'] not in live],'dangling_references':[],'unusable_reference_records':records,'retired_objects':deepcopy(retired),'stable_addresses':True,'symbolic_identities':True,'records_are_not_pointer_values':True}
        ped['narration']={level:descriptions[phase] for level in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase in {'return','link','caller'},'value':reference(result) if result is not None and phase!='caller_exit' else result,'reconnects_subtree':phase in {'link','caller'}};ped['state_before']=deepcopy(old);ped['state_after']=deepcopy(new);ped['memory_state']=deepcopy(new);ped['instruction_event']={'phase':phase,'frame_id':owner,'function':function,'condition':condition,'return':reference(result) if result is not None and phase!='caller_exit' else result}
        ped['invariant'].update(name='Vida de reservas y publicaciones pendientes',holds=True,symbol='✓',explanation='Identidades y enlaces se conservan hasta su instruccion real. La proyeccion viva no afirma que el C escribio NULL ni certifica orden estricto durante la copia transitoria del sucesor.')
        validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
    def invocation(fn,identity,arg=None):
        f={'id':'F'+str(len(history)+1),'function':fn,'depth':len(frames),'parameters':{'nodo':identity},'locals':{}}
        if arg is not None:f['parameters']['valor']=arg
        history.append(f);emit('ABBNodo* '+fn+'(ABBNodo* nodo'+(', int valor' if arg is not None else '')+') {','enter',lambda:frames.append(f),fn=fn);return f
    def finish(text,pointer):
        nonlocal returned
        def leave():
            nonlocal returned
            frames.pop();returned=pointer
        emit(text,'return',leave,result=pointer);return pointer
    def minimum(identity):
        f=invocation('abb_encontrarMinimo',identity)
        emit('if (nodo == NULL) {','condition',condition=identity=='NULL',expression=reference(identity)+' == NULL')
        if identity=='NULL':return finish('return NULL;','NULL')
        cursor=identity
        while True:
            child=node(cursor)['left'];emit('while (nodo->izquierdo != NULL)','condition',condition=child!='NULL',expression=reference(child)+' != NULL')
            if child=='NULL':break
            cursor=child;emit('nodo = nodo->izquierdo;','assignment',lambda:f['parameters'].update(nodo=cursor))
        return finish('return nodo;',cursor)
    def rec(identity,arg):
        f=invocation('abb_eliminar',identity,arg);emit('if (nodo == NULL) return nodo;','condition',condition=identity=='NULL',expression=reference(identity)+' == NULL')
        if identity=='NULL':return finish('if (nodo == NULL) return nodo;','NULL')
        n=node(identity);emit('if (valor < nodo->valor)','condition',condition=arg<n['value'],expression=str(arg)+' < '+str(n['value']))
        side='left' if arg<n['value'] else 'right' if arg>n['value'] else None
        if side!='left':emit('else if (valor > nodo->valor)','condition',condition=arg>n['value'],expression=str(arg)+' > '+str(n['value']))
        if side:
            field='izquierdo' if side=='left' else 'derecho';text='nodo->'+field+' = abb_eliminar(nodo->'+field+', valor);';emit(text,'call');replacement=rec(n[side],arg);emit(text,'link',lambda:n.update({side:replacement}),result=replacement)
        else:
            left=n['left'];right=n['right'];emit('if (nodo->izquierdo == NULL) {','condition',condition=left=='NULL',expression=reference(left)+' == NULL')
            if left!='NULL':emit('} else if (nodo->derecho == NULL) {','condition',condition=right=='NULL',expression=reference(right)+' == NULL')
            if left=='NULL' or right=='NULL':
                replacement=right if left=='NULL' else left;emit('ABBNodo* temp = nodo->'+('derecho' if left=='NULL' else 'izquierdo')+';','assignment',lambda:f['locals'].update(temp=replacement))
                def release():
                    retired.append({'id':identity,'value':n['value'],'left':reference(n['left']),'right':reference(n['right']),'status':'freed','historical_identity':True,'contents_are_historical':True});live.remove(identity)
                emit('free(nodo);','free',release,occurrence=0 if left=='NULL' else 1)
                if left!='NULL':
                    # Same spelling, different physical branch return line.
                    def leave_second():
                        nonlocal returned
                        frames.pop();returned=replacement
                    emit('return temp;','return',leave_second,result=replacement,occurrence=1)
                    return replacement
                return finish('return temp;',replacement)
            text='ABBNodo* temp = abb_encontrarMinimo(nodo->derecho);';emit(text,'call',lambda:f['locals'].update(temp='sin inicializar'));successor=minimum(right);emit(text,'assignment',lambda:f['locals'].update(temp=successor),result=successor)
            successor_value=node(successor)['value'];emit('nodo->valor = temp->valor;','assignment',lambda:n.update(value=successor_value))
            text='nodo->derecho = abb_eliminar(nodo->derecho, temp->valor);';emit(text,'call');replacement=rec(right,successor_value);emit(text,'link',lambda:n.update(right=replacement),result=replacement)
        return finish('return nodo;',identity)
    def enter_caller():
        nonlocal caller
        caller=True
    call='arbol = abb_eliminar(arbol, '+str(value)+');';emit(call,'caller_enter',enter_caller);emit(call,'call');replacement=rec(head,value)
    def publish():
        nonlocal head
        head=replacement
    emit(call,'caller',publish,result=replacement)
    def leave_caller():
        nonlocal caller
        caller=None
    emit('return 0;','caller_exit',leave_caller,result=0);assert snapshot()['root']==after_state.get('root')
    steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    initial=deepcopy(steps[0]['pedagogy']);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={level:'Ninguna instruccion ejecutada; sin ambitos ni retornos futuros.' for level in ['basic','intermediate','advanced']};steps[0]['pedagogy']['initial_frame']=initial
    trace.update(source_code=source,steps=steps);return trace
