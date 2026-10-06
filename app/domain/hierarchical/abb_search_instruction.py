"""ABB search scopes and borrowed returns; the caller exposes a boolean.

The highlighted instruction is at the recorded event boundary: entry to a call
suspends the parent; a later return event completes that same expression.
"""
from copy import deepcopy
from .pedagogy import build_hierarchical_frame, validate_hierarchical_frame


def build_abb_search_trace(trace, before_state, after_state):
    target=int(trace['payload']['value'])
    source=trace['source_code'].rstrip()+'\n\n/* Llamador equivalente al booleano expuesto por el wrapper; no es otro metodo del TAD. */\nint ejecutar_busqueda(ABBNodo* raiz) {\n    return abb_buscar(raiz, '+str(target)+') != NULL;\n}\n'
    lines=source.splitlines();heap=[];frames=[];history=[];steps=[];caller=None;returned=None;boolean_result=None
    def load(n):
        if n is None:return 'NULL'
        identity='N'+str(len(heap)+1);item={'id':identity,'value':n['value'],'left':'NULL','right':'NULL','status':'linked'};heap.append(item)
        item['left'],item['right']=load(n['left']),load(n['right']);return identity
    head=load(before_state.get('root'))
    def node(identity):return next(n for n in heap if n['id']==identity)
    def snapshot():
        state=deepcopy(before_state);state.update(abb_read_model=True,head=head,heap_nodes=deepcopy(heap),tree_frames=deepcopy(frames),caller_frame=deepcopy(caller),returned=returned,wrapper_result=boolean_result,console_stdout='');return state
    def index(text):return next(i for i,l in enumerate(lines) if l.strip()==text)
    def emit(text,phase,mutate=None,condition=None,expression=None,result=None):
        old=snapshot();owner=frames[-1]['id'] if frames else 'caller'
        if mutate:mutate()
        new=snapshot();idx=index(text);step={'step_index':len(steps),'line_index':idx,'line_text':lines[idx],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':old,'state_after':new,'debug':{'stage':phase}}
        if phase=='condition':step['condition_result']=condition
        ped=build_hierarchical_frame(structure_id='abb',operation_name='buscar',payload=trace['payload'],step=step,source_lines=lines,success=True)
        ped['concept']='compare' if phase=='condition' else 'return' if phase in {'return','caller_result'} else 'descend';ped['case']=phase;ped['phase']={'id':'buscar-'+phase,'label':phase.title(),'goal':text};ped['condition']=None
        if phase=='condition':ped['condition']={'source':text,'substituted':expression,'result':condition,'consequence':'rama registrada; cortocircuito cuando nodo es NULL'};ped['executed_branch']='cuerpo' if condition else 'else/siguiente condicion'
        previous={(f['id'],name):value for f in old['tree_frames'] for name,value in f['parameters'].items()};current={(f['id'],name):value for f in new['tree_frames'] for name,value in f['parameters'].items()}
        variables=[]
        if old['caller_frame'] or new['caller_frame']:
            variables.append({'name':'raiz','scope':'ejecutar_busqueda','frame_id':'caller','type':'ABBNodo *','previous':head if old['caller_frame'] else 'fuera de ámbito','value':head if new['caller_frame'] else 'fuera de ámbito','changed':bool(old['caller_frame'])!=bool(new['caller_frame']),'meaning':'Parametro por valor del llamador: la raiz global no cambia; compara el puntero retornado con NULL.'})
        for f in history:
            for name in ['nodo','valor']:
                key=(f['id'],name)
                if key not in previous and key not in current:continue
                a=previous.get(key,'fuera de ámbito');b=current.get(key,'fuera de ámbito')
                variables.append({'name':name,'scope':'abb_buscar#'+f['id'],'frame_id':f['id'],'type':'int' if name=='valor' else 'ABBNodo *','previous':a,'value':b,'changed':a!=b,'meaning':'Parametro por valor de la invocacion '+f['id']+'; los llamadores suspendidos conservan sus propios parametros.'})
        ped['variables']=variables
        shown=old['tree_frames'] if phase=='return' else new['tree_frames'];stack=[]
        if old['caller_frame'] or new['caller_frame']:stack.append({'function':'ejecutar_busqueda','frame_id':'caller','depth':-1,'parameters':{'raiz':head},'locals':{},'local_root':head,'local_root_address':head,'return':result if phase=='caller_result' else None,'continuation':'comparar el puntero retornado con NULL solo cuando termine la busqueda'})
        for f in shown:stack.append({'function':'abb_buscar','frame_id':f['id'],'depth':f['depth'],'parameters':deepcopy(f['parameters']),'locals':{},'local_root':f['parameters']['nodo'],'local_root_address':f['parameters']['nodo'],'return':result if phase=='return' and f['id']==owner else None,'continuation':'return abb_buscar(...) propaga el mismo alias prestado o NULL despues del retorno del hijo; no reconecta enlaces'})
        for entry in stack:
            if (phase=='return' and entry['frame_id']==owner) or (phase=='caller_result' and entry['frame_id']=='caller'):
                entry['scope_status']='terminado (contexto del retorno)'
                entry['continuation']='Retorno completado: ambito terminado. Sus parametros son el contexto de la instruccion, no variables vivas despues del paso.'
            else:
                entry['scope_status']='activo' if (new['tree_frames'] and entry['frame_id']==new['tree_frames'][-1]['id']) or (not new['tree_frames'] and entry['frame_id']=='caller') else 'suspendido'
        ped['call_stack']=stack
        objects=[{'id':n['id'],'address':n['id'],'symbolic_identity':True,'value':n['value'],'left':n['left'],'right':n['right'],'allocated':True,'freed':False} for n in heap]
        ped['memory']={'event':'none','objects_before':deepcopy(objects),'objects_after':deepcopy(objects),'allocated_objects':[],'freed_objects':[],'dangling_references':[],'stable_addresses':True,'symbolic_identities':True}
        descriptions={'caller_enter':'Entra el llamador equivalente; raiz es un parametro por valor. Aun no se ha llamado a abb_buscar ni convertido su retorno en booleano.','call':'Inicia la llamada de esta expresion. El llamador conserva nodo/valor suspendidos; el retorno pendiente no modifica enlaces ni termina todavia su ambito.','enter':'Entra una nueva invocacion con sus propios nodo/valor, incluyendo nodo NULL. Los parametros del padre no se sustituyen por los del hijo.','condition':'Evalua la condicion con esta invocacion. En NULL || igualdad, NULL cortocircuita: no lee nodo->valor. No cambia el arbol.','return':'Completa el return de esta invocacion: entrega el mismo alias prestado o NULL y termina solo su ambito. No reserva, libera ni reconecta nodos.','caller_result':'La busqueda exterior termino. El llamador compara el puntero con NULL y retorna 1 o 0; la interfaz lo presenta como booleano. No confundir este entero con el puntero retornado por el TAD.'}
        ped['narration']={level:descriptions[phase] for level in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase in {'return','caller_result'},'value':result,'reconnects_subtree':False};ped['state_before']=deepcopy(old);ped['state_after']=deepcopy(new);ped['memory_state']=deepcopy(new);ped['instruction_event']={'phase':phase,'frame_id':owner,'condition':condition,'return':result}
        ped['invariant'].update(explanation='Consulta sin mutacion: todas las reservas y enlaces iniciales siguen vivos. El TAD retorna un alias prestado o NULL; el wrapper expone un booleano.',holds=True,symbol='✓');validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
    def rec(identity):
        f={'id':'F'+str(len(history)+1),'function':'abb_buscar','depth':len(frames),'parameters':{'nodo':identity,'valor':target},'locals':{}};history.append(f)
        emit('ABBNodo* abb_buscar(ABBNodo* nodo, int valor) {','enter',lambda:frames.append(f))
        terminal=identity=='NULL' or node(identity)['value']==target
        expression='if (NULL == NULL || nodo->valor == '+str(target)+') [segundo operando no evaluado]' if identity=='NULL' else 'if ('+identity+' == NULL || '+str(node(identity)['value'])+' == '+str(target)+')'
        emit('if (nodo == NULL || nodo->valor == valor)','condition',condition=terminal,expression=expression)
        if terminal:result=identity;text='return nodo;'
        else:
            goes_left=target<node(identity)['value'];emit('if (valor < nodo->valor)','condition',condition=goes_left,expression='if ('+str(target)+' < '+str(node(identity)['value'])+')')
            side='left' if goes_left else 'right';text='return abb_buscar(nodo->'+('izquierdo' if goes_left else 'derecho')+', valor);'
            emit(text,'call');result=rec(node(identity)[side])
        def leave():
            nonlocal returned
            frames.pop();returned=result
        emit(text,'return',leave,result=result);return result
    def enter_caller():
        nonlocal caller
        caller={'function':'ejecutar_busqueda','parameters':{'raiz':head},'description':'raiz (ABBNodo *) -> '+head+'; retorno int pendiente, expuesto como booleano por el wrapper.'}
    emit('int ejecutar_busqueda(ABBNodo* raiz) {','caller_enter',enter_caller)
    call='return abb_buscar(raiz, '+str(target)+') != NULL;';emit(call,'call');result=rec(head);converted=int(result!='NULL')
    def caller_return():
        nonlocal caller,boolean_result
        caller=None;boolean_result=converted
    emit(call,'caller_result',caller_return,result=converted)
    steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    initial=deepcopy(steps[0]['pedagogy']);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={level:'Ninguna instruccion ejecutada; arbol inicial, sin parametros ni retorno futuros.' for level in ['basic','intermediate','advanced']};steps[0]['pedagogy']['initial_frame']=initial
    trace.update(source_code=source,steps=steps);return trace
