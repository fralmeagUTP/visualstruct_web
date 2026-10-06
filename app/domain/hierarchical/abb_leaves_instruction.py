"""ABB leaf-count expression operands are distinct from declared C variables.

The highlighted instruction is at the recorded event boundary: entry to a call
suspends the parent; a later return event completes that same expression.
"""
from copy import deepcopy
from .pedagogy import build_hierarchical_frame, validate_hierarchical_frame


def build_abb_leaves_trace(trace, before_state, after_state, evaluation_order='left-first'):
    if evaluation_order not in {'left-first','right-first'}:raise ValueError('Invalid leaf operand evaluation order')
    source=trace['source_code'].rstrip()+'\n\n/* C no fija el orden de los operandos. Modelo: '+evaluation_order+' (opcion permitida). Llamador equivalente: expone el entero del TAD. */\nint ejecutar_hojas(ABBNodo* raiz) {\n    return abb_contarHojas(raiz);\n}\n'
    lines=source.splitlines();heap=[];frames=[];history=[];steps=[];caller=None;returned=None;leaf_result=None
    def load(n):
        if n is None:return 'NULL'
        identity='N'+str(len(heap)+1);item={'id':identity,'value':n['value'],'left':'NULL','right':'NULL','status':'linked'};heap.append(item)
        item['left'],item['right']=load(n['left']),load(n['right']);return identity
    head=load(before_state.get('root'))
    def node(identity):return next(n for n in heap if n['id']==identity)
    def snapshot():
        state=deepcopy(before_state);state.update(abb_read_model=True,head=head,heap_nodes=deepcopy(heap),tree_frames=deepcopy(frames),caller_frame=deepcopy(caller),returned=returned,wrapper_result=leaf_result,console_stdout='',operand_evaluation_order=evaluation_order);return state
    def index(text):return next(i for i,l in enumerate(lines) if l.strip()==text)
    def emit(text,phase,mutate=None,condition=None,expression=None,result=None):
        old=snapshot();owner=frames[-1]['id'] if frames else 'caller'
        if mutate:mutate()
        new=snapshot();idx=index(text);step={'step_index':len(steps),'line_index':idx,'line_text':lines[idx],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':old,'state_after':new,'debug':{'stage':phase}}
        if phase=='condition':step['condition_result']=condition
        ped=build_hierarchical_frame(structure_id='abb',operation_name='contar_hojas',payload=trace['payload'],step=step,source_lines=lines,success=True)
        ped['concept']='compare' if phase=='condition' else 'return' if phase in {'return','caller_result'} else 'descend';ped['case']=phase;ped['phase']={'id':'hojas-'+phase,'label':phase.title(),'goal':text};ped['condition']=None
        if phase=='condition':ped['condition']={'source':text,'substituted':expression,'result':condition,'consequence':'rama registrada con los valores de esta invocacion'};ped['executed_branch']='cuerpo' if condition else 'else/siguiente condicion'
        previous={(f['id'],name):value for f in old['tree_frames'] for name,value in {**f['parameters'],**f['locals']}.items()};current={(f['id'],name):value for f in new['tree_frames'] for name,value in {**f['parameters'],**f['locals']}.items()}
        variables=[]
        if old['caller_frame'] or new['caller_frame']:
            variables.append({'name':'raiz','scope':'ejecutar_hojas','frame_id':'caller','type':'ABBNodo *','previous':head if old['caller_frame'] else 'fuera de ámbito','value':head if new['caller_frame'] else 'fuera de ámbito','changed':bool(old['caller_frame'])!=bool(new['caller_frame']),'meaning':'Parametro o local de esta invocacion por valor del llamador: la raiz global no cambia; expone el entero retornado.'})
        for f in history:
            for name in ['nodo']:
                key=(f['id'],name)
                if key not in previous and key not in current:continue
                a=previous.get(key,'fuera de ámbito');b=current.get(key,'fuera de ámbito')
                variables.append({'name':name,'scope':'abb_contarHojas#'+f['id'],'frame_id':f['id'],'type':'ABBNodo *' if name=='nodo' else 'int','previous':a,'value':b,'changed':a!=b,'meaning':'Parametro o local de esta invocacion por valor de la invocacion '+f['id']+'; los llamadores suspendidos conservan sus propios parametros.'})
        ped['variables']=variables
        shown=old['tree_frames'] if phase=='return' else new['tree_frames'];stack=[]
        if old['caller_frame'] or new['caller_frame']:stack.append({'function':'ejecutar_hojas','frame_id':'caller','depth':-1,'parameters':{'raiz':head},'locals':{},'local_root':head,'local_root_address':head,'return':result if phase=='caller_result' else None,'continuation':'exponer el entero retornado solo cuando termine el conteo de hojas'})
        for f in shown:stack.append({'function':'abb_contarHojas','frame_id':f['id'],'depth':f['depth'],'parameters':deepcopy(f['parameters']),'locals':{},'expression':deepcopy(f['expression']),'local_root':f['parameters']['nodo'],'local_root_address':f['parameters']['nodo'],'return':result if phase=='return' and f['id']==owner else None,'continuation':'retorno numerico de esta invocacion; el padre conserva los operandos ya evaluados, no locales C'})
        for entry in stack:
            if (phase=='return' and entry['frame_id']==owner) or (phase=='caller_result' and entry['frame_id']=='caller'):
                entry['scope_status']='terminado (contexto del retorno)'
                entry['continuation']='Retorno completado: ambito terminado. Sus parametros son el contexto de la instruccion, no variables vivas despues del paso.'
            else:
                entry['scope_status']='activo' if (new['tree_frames'] and entry['frame_id']==new['tree_frames'][-1]['id']) or (not new['tree_frames'] and entry['frame_id']=='caller') else 'suspendido'
        ped['call_stack']=stack
        objects=[{'id':n['id'],'address':n['id'],'symbolic_identity':True,'value':n['value'],'left':n['left'],'right':n['right'],'allocated':True,'freed':False} for n in heap]
        ped['memory']={'event':'none','objects_before':deepcopy(objects),'objects_after':deepcopy(objects),'allocated_objects':[],'freed_objects':[],'dangling_references':[],'stable_addresses':True,'symbolic_identities':True}
        descriptions={'caller_enter':'Entra el llamador equivalente, sin resultado futuro.','call':'Inicia la llamada exterior; aun no hay parametros ni resultados futuros.','enter':'Entra una invocacion con su propio parametro nodo, incluso NULL.','condition':'Evalua la condicion; && no evalua el enlace derecho si el izquierdo no es NULL. No modifica el arbol.','return':'Completa el retorno numerico y termina solo este ambito; no modifica el arbol.','caller_result':'El llamador expone el numero de hojas retornado por el helper mostrado.'}
        if phase.startswith('call_'):descriptions[phase]='Inicia el operando '+phase[5:]+'. El padre espera su resultado, conservando los otros operandos ya evaluados. Son resultados de expresion, no variables C. Orden '+evaluation_order+' elegido por el modelo, no garantizado por C.'
        if phase.startswith('operand_'):descriptions[phase]='El hijo termino; este operando contiene su retorno numerico. El otro conserva su propio estado. Aun no retorna la suma hasta que ambos terminen; no se declaran locales C.'
        ped['expression_evaluation']=deepcopy(new['tree_frames'][-1]['expression']) if new['tree_frames'] else None
        ped['narration']={level:descriptions[phase] for level in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase in {'return','caller_result'},'value':result,'reconnects_subtree':False};ped['state_before']=deepcopy(old);ped['state_after']=deepcopy(new);ped['memory_state']=deepcopy(new);ped['instruction_event']={'phase':phase,'frame_id':owner,'condition':condition,'return':result}
        ped['invariant'].update(explanation='Consulta sin mutacion: todas las reservas y enlaces iniciales siguen vivos; cada invocacion retorna un conteo de hojas; los operandos no son variables locales.',holds=True,symbol='✓');validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
    def rec(identity):
        f={'id':'F'+str(len(history)+1),'function':'abb_contarHojas','depth':len(frames),'parameters':{'nodo':identity},'locals':{},'expression':None};history.append(f)
        emit('int abb_contarHojas(ABBNodo* nodo) {','enter',lambda:frames.append(f))
        terminal=identity=='NULL'
        emit('if (nodo == NULL) {','condition',condition=terminal,expression='if ('+identity+' == NULL)')
        if terminal:result=0;text='return 0;'
        else:
            n=node(identity);leaf=n['left']=='NULL' and n['right']=='NULL'
            substituted='if ('+n['left']+' == NULL && '+(n['right']+' == NULL' if n['left']=='NULL' else 'segundo operando no evaluado')+')'
            emit('if (nodo->izquierdo == NULL && nodo->derecho == NULL) {','condition',condition=leaf,expression=substituted)
            if leaf:result=1;text='return 1;'
            else:
                text='return abb_contarHojas(nodo->izquierdo) + abb_contarHojas(nodo->derecho);'
                for side in (['left','right'] if evaluation_order=='left-first' else ['right','left']):
                    def begin():
                        if f['expression'] is None:f['expression']={'left':'no evaluado','right':'no evaluado'}
                        f['expression'][side]='en evaluacion'
                    emit(text,'call_'+side,begin);value=rec(n[side])
                    emit(text,'operand_'+side,lambda:f['expression'].__setitem__(side,value),result=value)
                result=f['expression']['left']+f['expression']['right']
        def leave():
            nonlocal returned
            frames.pop();returned=result
        emit(text,'return',leave,result=result);return result
    def enter_caller():
        nonlocal caller
        caller={'function':'ejecutar_hojas','parameters':{'raiz':head},'description':'raiz (ABBNodo *) -> '+head+'; retorno int pendiente, expuesto como numero de hojas.'}
    emit('int ejecutar_hojas(ABBNodo* raiz) {','caller_enter',enter_caller)
    call='return abb_contarHojas(raiz);';emit(call,'call');result=rec(head)
    def caller_return():
        nonlocal caller,leaf_result
        caller=None;leaf_result=result
    emit(call,'caller_result',caller_return,result=result)
    steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    initial=deepcopy(steps[0]['pedagogy']);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={level:'Ninguna instruccion ejecutada; arbol inicial, sin parametros ni retorno futuros.' for level in ['basic','intermediate','advanced']};steps[0]['pedagogy']['initial_frame']=initial
    trace.update(source_code=source,steps=steps);return trace
