"""AVL height-balance validator: recursive pure height calls, live integer locals and short-circuit returns.

The highlighted instruction is at the recorded event boundary: entry to a call
suspends the parent; a later return event completes that same expression.
"""
from copy import deepcopy
from .pedagogy import build_hierarchical_frame, validate_hierarchical_frame


def build_avl_validate_trace(trace, before_state, after_state):
    from app.services.c_code_service import CCodeService
    source=trace['source_code'].rstrip()+'\n\n'+CCodeService.get_structure_data('avl')['operations']['altura'].rstrip()+'\n\n/**\n * @brief Expone equilibrio por alturas calculado, distinto de metadata backend.\n * @param raiz Raiz prestada, con enlaces finitos/aciclicos.\n * @return 1 equilibrado por alturas, 0 desequilibrado. No revisa orden ni FE almacenado.\n */\nint ejecutar_equilibrio(AVL raiz) {\n    return avl_validar_fes(raiz);\n}\n'
    lines=source.splitlines();heap=[];frames=[];history=[];steps=[];caller=None;returned=None;height_result=None
    def load(n,parent="NULL"):
        if n is None:return 'NULL'
        identity='N'+str(len(heap)+1);item={'id':identity,'value':n['value'],'left':'NULL','right':'NULL','status':'linked','balance_factor':n['balance_factor'],'parent':parent};heap.append(item)
        item['left'],item['right']=load(n['left'],identity),load(n['right'],identity);return identity
    head=load(before_state.get('root'))
    def node(identity):return next(n for n in heap if n['id']==identity)
    def snapshot():
        state=deepcopy(before_state);state.update(abb_read_model=True,avl_read_model=True,avl_validate_model=True,validation=None,backend_validation=before_state.get('validation'),height_balance_result=None if height_result is None else bool(height_result),head=head,heap_nodes=deepcopy(heap),tree_frames=deepcopy(frames),caller_frame=deepcopy(caller),operand_evaluation_order='derecho y luego izquierdo (eleccion legal, no orden obligatorio de C)',returned=returned,wrapper_result=height_result,console_stdout='');return state
    def index(text,function):
        start=next(i for i,l in enumerate(lines) if l.strip().startswith('int '+function+'('));return next(i for i in range(start,len(lines)) if lines[i].strip()==text)
    def emit(text,phase,mutate=None,condition=None,expression=None,result=None,occurrence=0):
        old=snapshot();owner=frames[-1]['id'] if frames else 'caller'
        if mutate:mutate()
        new=snapshot();owner=new['tree_frames'][-1]['id'] if phase=='enter' else owner;function=(new['tree_frames'][-1]['function'] if phase=='enter' else old['tree_frames'][-1]['function']) if (new['tree_frames'] if phase=='enter' else old['tree_frames']) else 'ejecutar_equilibrio';idx=index(text,function);idx=[i for i in range(next(i for i,l in enumerate(lines) if l.strip().startswith('int '+function+'(')),len(lines)) if lines[i].strip()==text][occurrence];step={'step_index':len(steps),'line_index':idx,'line_text':lines[idx],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':old,'state_after':new,'debug':{'stage':phase}}
        if phase=='condition':step['condition_result']=condition
        ped=build_hierarchical_frame(structure_id='avl',operation_name='validar',payload=trace['payload'],step=step,source_lines=lines,success=True)
        ped['concept']='compare' if phase=='condition' else 'return' if phase in {'return','caller_result'} else 'descend';ped['case']=phase;ped['phase']={'id':'altura-'+phase,'label':phase.title(),'goal':text};ped['condition']=None
        if phase=='condition':ped['condition']={'source':text,'substituted':expression,'result':condition,'consequence':'rama registrada con los valores de esta invocacion'};ped['executed_branch']='cuerpo' if condition else 'else/siguiente condicion'
        previous={(f['id'],name):value for f in old['tree_frames'] for name,value in {**f['parameters'],**f['locals']}.items()};current={(f['id'],name):value for f in new['tree_frames'] for name,value in {**f['parameters'],**f['locals']}.items()}
        variables=[]
        if old['caller_frame'] or new['caller_frame']:
            variables.append({'name':'raiz','scope':'ejecutar_equilibrio','frame_id':'caller','type':'AVL','previous':head if old['caller_frame'] else 'fuera de ámbito','value':head if new['caller_frame'] else 'fuera de ámbito','changed':bool(old['caller_frame'])!=bool(new['caller_frame']),'meaning':'Parametro o local de esta invocacion por valor del llamador: la raiz global no cambia; expone el entero de equilibrio por alturas.'})
        for f in history:
            for name in [*f['parameters'],*f['locals']]:
                key=(f['id'],name)
                if key not in previous and key not in current:continue
                a=previous.get(key,'fuera de ámbito');b=current.get(key,'fuera de ámbito')
                variables.append({'name':name,'scope':f['function']+'#'+f['id'],'frame_id':f['id'],'type':'AVL' if name in {'arbol','nodo'} else 'int','previous':a,'value':b,'changed':a!=b,'meaning':'Parametro o local de esta invocacion por valor de la invocacion '+f['id']+'; los llamadores suspendidos conservan sus propios parametros.'})
        ped['variables']=variables
        shown=old['tree_frames'] if phase=='return' else new['tree_frames'];stack=[]
        if old['caller_frame'] or new['caller_frame']:stack.append({'function':'ejecutar_equilibrio','frame_id':'caller','depth':-1,'parameters':{'raiz':head},'locals':{},'local_root':head,'local_root_address':head,'return':result if phase=='caller_result' else None,'continuation':'exponer el entero retornado solo al completar equilibrio por alturas'})
        for f in shown:stack.append({'function':f['function'],'frame_id':f['id'],'depth':f['depth'],'parameters':deepcopy(f['parameters']),'locals':deepcopy(f['locals']),'local_root':next(iter(f['parameters'].values())),'local_root_address':next(iter(f['parameters'].values())),'return':result if phase=='return' and f['id']==owner else None,'continuation':'retorno numerico de esta invocacion; los locales de los padres conservan sus valores'})
        for entry in stack:
            if (phase=='return' and entry['frame_id']==owner) or (phase=='caller_result' and entry['frame_id']=='caller'):
                entry['scope_status']='terminado (contexto del retorno)'
                entry['continuation']='Retorno completado: ambito terminado. Sus parametros son el contexto de la instruccion, no variables vivas despues del paso.'
            else:
                entry['scope_status']='activo' if (new['tree_frames'] and entry['frame_id']==new['tree_frames'][-1]['id']) or (not new['tree_frames'] and entry['frame_id']=='caller') else 'suspendido'
        ped['call_stack']=stack
        objects=[{'id':n['id'],'address':n['id'],'symbolic_identity':True,'value':n['value'],'left':n['left'],'right':n['right'],'parent':n['parent'],'balance_factor':n['balance_factor'],'allocated':True,'freed':False} for n in heap]
        ped['memory']={'event':'none','objects_before':deepcopy(objects),'objects_after':deepcopy(objects),'allocated_objects':[],'freed_objects':[],'dangling_references':[],'stable_addresses':True,'symbolic_identities':True}
        descriptions={'caller_enter':'Entra el llamador equivalente, sin un resultado futuro.','call':'Transfiere control y suspende al padre; si es inicializador, el local permanece sin inicializar. En fe se elige evaluar altura derecha y luego izquierda: C permite otro orden de operandos sin cambiar esta consulta pura.','enter':'Entra una invocacion de la funcion resaltada, con su parametro propio, incluso NULL.','condition':'Evalua la condicion con los valores disponibles. La seleccion de mayor altura no modifica enlaces.','assignment':'Termino el inicializador recursivo: el local ahora contiene el entero retornado por el hijo.','return':'Completa el retorno de la funcion resaltada y termina solo este ambito, sin alterar el arbol.','caller_result':'Retorna equilibrio por alturas 0/1; no certifica orden ABB ni FE almacenado. La validacion backend es metadata separada.'}
        if phase=='call' and not frames:descriptions['call']='Inicia la llamada exterior; aun no hay parametros ni locales de avl_altura ni resultado futuro.'
        if phase=='condition' and 'altIzq > altDer' in text:ped['executed_branch']='altIzq' if condition else 'altDer'
        ped['narration']={level:descriptions[phase] for level in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase in {'return','caller_result'},'value':result,'reconnects_subtree':False};ped['state_before']=deepcopy(old);ped['state_after']=deepcopy(new);ped['memory_state']=deepcopy(new);ped['instruction_event']={'phase':phase,'frame_id':owner,'condition':condition,'return':result}
        ped['invariant'].update(explanation='Consulta sin mutacion: auxiliar calcula equilibrio por alturas, distinto del orden+equilibrio del backend. FE almacenado no se consulta. En la resta C no fija orden de operandos: esta reproduccion elige derecho y luego izquierdo, ambos completos antes de asignar fe.',holds=True,symbol='✓');validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
    def height(identity):
        f={'id':'F'+str(len(history)+1),'function':'avl_altura','depth':len(frames),'parameters':{'arbol':identity},'locals':{}};history.append(f)
        emit('int avl_altura(AVL arbol) {','enter',lambda:frames.append(f))
        terminal=identity=='NULL'
        emit('if (arbol == NULL)','condition',condition=terminal,expression='if ('+identity+' == NULL)')
        if terminal:result=0;text='return 0;'
        else:
            for name,side,field in [('altIzq','left','izq'),('altDer','right','der')]:
                declaration='int '+name+' = avl_altura(arbol->'+field+');'
                emit(declaration,'call',lambda:f['locals'].__setitem__(name,'sin inicializar'))
                value=height(node(identity)[side])
                emit(declaration,'assignment',lambda:f['locals'].__setitem__(name,value))
            left,right=f['locals']['altIzq'],f['locals']['altDer']
            text='return (altIzq > altDer ? altIzq : altDer) + 1;'
            emit(text,'condition',condition=left>right,expression='('+str(left)+' > '+str(right)+' ? '+str(left)+' : '+str(right)+') + 1')
            result=(left if left>right else right)+1
        def leave():
            nonlocal returned
            frames.pop();returned=result
        emit(text,'return',leave,result=result);return result
    def rec(identity):
        f={'id':'F'+str(len(history)+1),'function':'avl_validar_fes','depth':len(frames),'parameters':{'nodo':identity},'locals':{}};history.append(f)
        emit('int avl_validar_fes(AVL nodo) {','enter',lambda:frames.append(f))
        terminal=identity=='NULL';emit('if (nodo == NULL) {','condition',condition=terminal,expression=identity+' == NULL')
        occurrence=0
        if terminal:result=1;text='return 1;'
        else:
            declaration='int fe = avl_altura(nodo->der) - avl_altura(nodo->izq);'
            emit(declaration,'call',lambda:f['locals'].__setitem__('fe','sin inicializar'))
            right=height(node(identity)['right']);emit(declaration,'call')
            left=height(node(identity)['left']);factor=right-left
            emit(declaration,'assignment',lambda:f['locals'].__setitem__('fe',factor))
            invalid=factor < -1 or factor > 1
            emit('if (fe < -1 || fe > 1) {','condition',condition=invalid,expression=f'{factor} < -1 || '+('[cortocircuito]' if factor < -1 else f'{factor} > 1'))
            if invalid:result=0;text='return 0;'
            else:
                result=1;text='return 1;';occurrence=1
                for side,field,k in [('left','izq',1),('right','der',2)]:
                    call='if (!avl_validar_fes(nodo->'+field+')) {';emit(call,'call');value=rec(node(identity)[side])
                    emit(call,'condition',condition=not value,expression='!'+str(value)+' [retorno de '+field+']')
                    if not value:result=0;text='return 0;';occurrence=k;break
        def leave():
            nonlocal returned
            frames.pop();returned=result
        emit(text,'return',leave,result=result,occurrence=occurrence);return result
    def enter_caller():
        nonlocal caller
        caller={'function':'ejecutar_equilibrio','parameters':{'raiz':head},'description':'raiz (AVL) -> '+head+'; retorno int pendiente de equilibrio por alturas; backend valida orden y equilibrio aparte.'}
    emit('int ejecutar_equilibrio(AVL raiz) {','caller_enter',enter_caller)
    call='return avl_validar_fes(raiz);';emit(call,'call');result=rec(head)
    def caller_return():
        nonlocal caller,height_result
        caller=None;height_result=result
    emit(call,'caller_result',caller_return,result=result)
    steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    initial=deepcopy(steps[0]['pedagogy']);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={level:'Ninguna instruccion ejecutada; arbol inicial, sin parametros ni retorno futuros.' for level in ['basic','intermediate','advanced']};steps[0]['pedagogy']['initial_frame']=initial
    trace.update(source_code=source,steps=steps);return trace
