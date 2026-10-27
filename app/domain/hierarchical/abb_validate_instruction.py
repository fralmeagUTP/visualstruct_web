"""ABB optional strict bounds and executed recursive short-circuit scopes."""
from copy import deepcopy
from .pedagogy import build_hierarchical_frame, validate_hierarchical_frame


def build_abb_validate_trace(trace, before_state, after_state):
    source=trace['source_code'].rstrip()+'\n\n/* Llamador equivalente: expone el estado entero calculado por el auxiliar, sin nueva API del TAD. */\nint ejecutar_validacion(ABBNodo* raiz) {\n    return abb_validar_rango(raiz, 0, 0, 0, 0);\n}\n'
    lines=source.splitlines();heap=[];frames=[];history=[];steps=[];caller=None;returned=None;validation_result=None
    def load(n):
        if n is None:return 'NULL'
        identity='N'+str(len(heap)+1);item={'id':identity,'value':n['value'],'left':'NULL','right':'NULL','status':'linked'};heap.append(item)
        item['left'],item['right']=load(n['left']),load(n['right']);return identity
    head=load(before_state.get('root'))
    def node(identity):return next(n for n in heap if n['id']==identity)
    def snapshot():
        state=deepcopy(before_state);state.update(abb_read_model=True,abb_validate_model=True,head=head,heap_nodes=deepcopy(heap),tree_frames=deepcopy(frames),caller_frame=deepcopy(caller),returned=returned,wrapper_result=validation_result,console_stdout='',validation=None if validation_result is None else bool(validation_result));return state
    def index(text,occurrence=0):return [i for i,l in enumerate(lines) if l.strip()==text][occurrence]
    def emit(text,phase,mutate=None,condition=None,expression=None,result=None,occurrence=0):
        old=snapshot();owner=frames[-1]['id'] if frames else 'caller'
        if mutate:mutate()
        new=snapshot();idx=index(text,occurrence);step={'step_index':len(steps),'line_index':idx,'line_text':lines[idx],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':old,'state_after':new,'debug':{'stage':phase}}
        if phase=='condition':step['condition_result']=condition
        ped=build_hierarchical_frame(structure_id='abb',operation_name='validar',payload=trace['payload'],step=step,source_lines=lines,success=True)
        ped['concept']='compare' if phase=='condition' else 'return' if phase in {'return','caller_result'} else 'descend';ped['case']=phase;ped['phase']={'id':'validar-'+phase,'label':phase.title(),'goal':text};ped['condition']=None
        if phase=='condition':ped['condition']={'source':text,'substituted':expression,'result':condition,'consequence':'rama registrada con los valores de esta invocacion'};ped['executed_branch']='cuerpo' if condition else 'else/siguiente condicion'
        previous={(f['id'],name):value for f in old['tree_frames'] for name,value in {**f['parameters'],**f['locals']}.items()};current={(f['id'],name):value for f in new['tree_frames'] for name,value in {**f['parameters'],**f['locals']}.items()}
        variables=[]
        if old['caller_frame'] or new['caller_frame']:
            variables.append({'name':'raiz','scope':'ejecutar_validacion','frame_id':'caller','type':'ABBNodo *','previous':head if old['caller_frame'] else 'fuera de ámbito','value':head if new['caller_frame'] else 'fuera de ámbito','changed':bool(old['caller_frame'])!=bool(new['caller_frame']),'meaning':'Parametro o local de esta invocacion por valor del llamador: la raiz global no cambia; expone validez 0/1; limites ausentes no se comparan.'})
        for f in history:
            for name in ['nodo','hay_minimo','minimo','hay_maximo','maximo']:
                key=(f['id'],name)
                if key not in previous and key not in current:continue
                a=previous.get(key,'fuera de ámbito');b=current.get(key,'fuera de ámbito')
                variables.append({'name':name,'scope':'abb_validar_rango#'+f['id'],'frame_id':f['id'],'type':'ABBNodo *' if name=='nodo' else 'int','previous':a,'value':b,'changed':a!=b,'meaning':'Parametro o local de esta invocacion por valor de la invocacion '+f['id']+'; los llamadores suspendidos conservan sus propios parametros.'})
        ped['variables']=variables
        shown=old['tree_frames'] if phase=='return' else new['tree_frames'];stack=[]
        if old['caller_frame'] or new['caller_frame']:stack.append({'function':'ejecutar_validacion','frame_id':'caller','depth':-1,'parameters':{'raiz':head},'locals':{},'local_root':head,'local_root_address':head,'return':result if phase=='caller_result' else None,'continuation':'exponer validez 0/1 solo cuando termine la validacion'})
        for f in shown:stack.append({'function':'abb_validar_rango','frame_id':f['id'],'depth':f['depth'],'parameters':deepcopy(f['parameters']),'locals':deepcopy(f['locals']),'local_root':f['parameters']['nodo'],'local_root_address':f['parameters']['nodo'],'return':result if phase=='return' and f['id']==owner else None,'continuation':'retorno numerico de esta invocacion; los parametros de los padres conservan sus limites'})
        for entry in stack:
            if (phase=='return' and entry['frame_id']==owner) or (phase=='caller_result' and entry['frame_id']=='caller'):
                entry['scope_status']='terminado (contexto del retorno)'
                entry['continuation']='Retorno completado: ambito terminado. Sus parametros son el contexto de la instruccion, no variables vivas despues del paso.'
            else:
                entry['scope_status']='activo' if (new['tree_frames'] and entry['frame_id']==new['tree_frames'][-1]['id']) or (not new['tree_frames'] and entry['frame_id']=='caller') else 'suspendido'
        ped['call_stack']=stack
        objects=[{'id':n['id'],'address':n['id'],'symbolic_identity':True,'value':n['value'],'left':n['left'],'right':n['right'],'allocated':True,'freed':False} for n in heap]
        ped['memory']={'event':'none','objects_before':deepcopy(objects),'objects_after':deepcopy(objects),'allocated_objects':[],'freed_objects':[],'dangling_references':[],'stable_addresses':True,'symbolic_identities':True}
        descriptions={'caller_enter':'Entra el llamador equivalente, sin un resultado futuro.','call':'Evalua argumentos y transfiere el control al hijo. El if espera su retorno; no declara un local para guardar ese resultado. Los padres conservan sus parametros.','enter':'Entra una invocacion con nodo y sus cuatro parametros escalares propios, incluso si es NULL.','condition':'Evalua la condicion con los valores disponibles. Los indicadores controlan cortocircuito: no se comparan limites ausentes. El retorno del hijo decide si se visita el siguiente subarbol.','assignment':'Termino el inicializador recursivo: el local ahora contiene el entero retornado por el hijo.','return':'Completa el retorno numerico y termina solo este ambito; no modifica el arbol.','caller_result':'El llamador retorna validez int: NULL vale 1; un limite violado vale 0. El resultado se conoce despues del retorno.'}
        if phase=='call' and not frames:descriptions['call']='Inicia la llamada exterior; aun no hay parametros ni locales de abb_validar_rango ni resultado futuro.'
        ped['narration']={level:descriptions[phase] for level in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase in {'return','caller_result'},'value':result,'reconnects_subtree':False};ped['state_before']=deepcopy(old);ped['state_after']=deepcopy(new);ped['memory_state']=deepcopy(new);ped['instruction_event']={'phase':phase,'frame_id':owner,'condition':condition,'return':result}
        ped['invariant'].update(explanation='Consulta sin mutacion: todas las reservas y enlaces iniciales siguen vivos; cada invocacion retorna validez 0/1; la consulta no altera reservas ni enlaces.',holds=True,symbol='✓');validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
    def rec(identity,hay_minimo,minimo,hay_maximo,maximo):
        f={'id':'F'+str(len(history)+1),'function':'abb_validar_rango','depth':len(frames),'parameters':{'nodo':identity,'hay_minimo':hay_minimo,'minimo':minimo,'hay_maximo':hay_maximo,'maximo':maximo},'locals':{}};history.append(f)
        emit('int abb_validar_rango(ABBNodo* nodo, int hay_minimo, int minimo, int hay_maximo, int maximo) {','enter',lambda:frames.append(f))
        terminal=identity=='NULL';emit('if (nodo == NULL) {','condition',condition=terminal,expression=identity+' == NULL')
        if terminal:result=1;text='return 1;';occurrence=0
        else:
            value=node(identity)['value'];lower=bool(hay_minimo and value<=minimo);invalid=lower or bool(hay_maximo and value>=maximo)
            expression=f'({hay_minimo} && '+(f'{value} <= {minimo}' if hay_minimo else '[limite inferior ausente; valor no se compara]')+') || '+('[cortocircuito; limite superior no se evalua]' if lower else f'({hay_maximo} && '+(f'{value} >= {maximo}' if hay_maximo else '[limite superior ausente; valor no se compara]')+')')
            emit('if ((hay_minimo && nodo->valor <= minimo) || (hay_maximo && nodo->valor >= maximo)) {','condition',condition=invalid,expression=expression)
            if invalid:result=0;text='return 0;';occurrence=0
            else:
                left='if (!abb_validar_rango(nodo->izquierdo, hay_minimo, minimo, 1, nodo->valor)) {';emit(left,'call');lv=rec(node(identity)['left'],hay_minimo,minimo,1,value);emit(left,'condition',condition=not lv,expression='!'+str(lv)+' [retorno del subarbol izquierdo]')
                if not lv:result=0;text='return 0;';occurrence=1
                else:
                    right='if (!abb_validar_rango(nodo->derecho, 1, nodo->valor, hay_maximo, maximo)) {';emit(right,'call');rv=rec(node(identity)['right'],1,value,hay_maximo,maximo);emit(right,'condition',condition=not rv,expression='!'+str(rv)+' [retorno del subarbol derecho]')
                    if not rv:result=0;text='return 0;';occurrence=2
                    else:result=1;text='return 1;';occurrence=1
        def leave():
            nonlocal returned
            frames.pop();returned=result
        emit(text,'return',leave,result=result,occurrence=occurrence);return result
    def enter_caller():
        nonlocal caller
        caller={'function':'ejecutar_validacion','parameters':{'raiz':head},'description':'raiz (ABBNodo *) -> '+head+'; retorno int de validez pendiente. Limites iniciales ausentes.'}
    emit('int ejecutar_validacion(ABBNodo* raiz) {','caller_enter',enter_caller)
    call='return abb_validar_rango(raiz, 0, 0, 0, 0);';emit(call,'call');result=rec(head,0,0,0,0)
    def caller_return():
        nonlocal caller,validation_result
        caller=None;validation_result=result
    emit(call,'caller_result',caller_return,result=result)
    steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    initial=deepcopy(steps[0]['pedagogy']);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={level:'Ninguna instruccion ejecutada; arbol inicial sin validez, parametros ni retornos futuros.' for level in ['basic','intermediate','advanced']};steps[0]['pedagogy']['initial_frame']=initial
    trace.update(source_code=source,steps=steps);return trace
