"""ABB height: real integer locals, recursive initializer scopes and numeric returns.

The highlighted instruction is at the recorded event boundary: entry to a call
suspends the parent; a later return event completes that same expression.
"""
from copy import deepcopy
from .pedagogy import build_hierarchical_frame, validate_hierarchical_frame


def build_avl_height_trace(trace, before_state, after_state):
    source=trace['source_code'].rstrip()+'\n\n/* Llamador equivalente: expone el entero retornado por el TAD. */\nint ejecutar_altura(AVL raiz) {\n    return avl_altura(raiz);\n}\n'
    lines=source.splitlines();heap=[];frames=[];history=[];steps=[];caller=None;returned=None;height_result=None
    def load(n,parent="NULL"):
        if n is None:return 'NULL'
        identity='N'+str(len(heap)+1);item={'id':identity,'value':n['value'],'left':'NULL','right':'NULL','status':'linked','balance_factor':n['balance_factor'],'parent':parent};heap.append(item)
        item['left'],item['right']=load(n['left'],identity),load(n['right'],identity);return identity
    head=load(before_state.get('root'))
    def node(identity):return next(n for n in heap if n['id']==identity)
    def snapshot():
        state=deepcopy(before_state);state.update(abb_read_model=True,avl_read_model=True,head=head,heap_nodes=deepcopy(heap),tree_frames=deepcopy(frames),caller_frame=deepcopy(caller),returned=returned,wrapper_result=height_result,console_stdout='');return state
    def index(text):return next(i for i,l in enumerate(lines) if l.strip()==text)
    def emit(text,phase,mutate=None,condition=None,expression=None,result=None):
        old=snapshot();owner=frames[-1]['id'] if frames else 'caller'
        if mutate:mutate()
        new=snapshot();owner=new['tree_frames'][-1]['id'] if phase=='enter' else owner;idx=index(text);step={'step_index':len(steps),'line_index':idx,'line_text':lines[idx],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':old,'state_after':new,'debug':{'stage':phase}}
        if phase=='condition':step['condition_result']=condition
        ped=build_hierarchical_frame(structure_id='avl',operation_name='altura',payload=trace['payload'],step=step,source_lines=lines,success=True)
        ped['concept']='compare' if phase=='condition' else 'return' if phase in {'return','caller_result'} else 'descend';ped['case']=phase;ped['phase']={'id':'altura-'+phase,'label':phase.title(),'goal':text};ped['condition']=None
        if phase=='condition':ped['condition']={'source':text,'substituted':expression,'result':condition,'consequence':'rama registrada con los valores de esta invocacion'};ped['executed_branch']='cuerpo' if condition else 'else/siguiente condicion'
        previous={(f['id'],name):value for f in old['tree_frames'] for name,value in {**f['parameters'],**f['locals']}.items()};current={(f['id'],name):value for f in new['tree_frames'] for name,value in {**f['parameters'],**f['locals']}.items()}
        variables=[]
        if old['caller_frame'] or new['caller_frame']:
            variables.append({'name':'raiz','scope':'ejecutar_altura','frame_id':'caller','type':'AVL','previous':head if old['caller_frame'] else 'fuera de ámbito','value':head if new['caller_frame'] else 'fuera de ámbito','changed':bool(old['caller_frame'])!=bool(new['caller_frame']),'meaning':'Parametro o local de esta invocacion por valor del llamador: la raiz global no cambia; expone el entero retornado.'})
        for f in history:
            for name in ['arbol','altIzq','altDer']:
                key=(f['id'],name)
                if key not in previous and key not in current:continue
                a=previous.get(key,'fuera de ámbito');b=current.get(key,'fuera de ámbito')
                variables.append({'name':name,'scope':'avl_altura#'+f['id'],'frame_id':f['id'],'type':'AVL' if name=='arbol' else 'int','previous':a,'value':b,'changed':a!=b,'meaning':'Parametro o local de esta invocacion por valor de la invocacion '+f['id']+'; los llamadores suspendidos conservan sus propios parametros.'})
        ped['variables']=variables
        shown=old['tree_frames'] if phase=='return' else new['tree_frames'];stack=[]
        if old['caller_frame'] or new['caller_frame']:stack.append({'function':'ejecutar_altura','frame_id':'caller','depth':-1,'parameters':{'raiz':head},'locals':{},'local_root':head,'local_root_address':head,'return':result if phase=='caller_result' else None,'continuation':'exponer el entero retornado solo cuando termine el calculo de altura'})
        for f in shown:stack.append({'function':'avl_altura','frame_id':f['id'],'depth':f['depth'],'parameters':deepcopy(f['parameters']),'locals':deepcopy(f['locals']),'local_root':f['parameters']['arbol'],'local_root_address':f['parameters']['arbol'],'return':result if phase=='return' and f['id']==owner else None,'continuation':'retorno numerico de esta invocacion; los locales de los padres conservan sus valores'})
        for entry in stack:
            if (phase=='return' and entry['frame_id']==owner) or (phase=='caller_result' and entry['frame_id']=='caller'):
                entry['scope_status']='terminado (contexto del retorno)'
                entry['continuation']='Retorno completado: ambito terminado. Sus parametros son el contexto de la instruccion, no variables vivas despues del paso.'
            else:
                entry['scope_status']='activo' if (new['tree_frames'] and entry['frame_id']==new['tree_frames'][-1]['id']) or (not new['tree_frames'] and entry['frame_id']=='caller') else 'suspendido'
        ped['call_stack']=stack
        objects=[{'id':n['id'],'address':n['id'],'symbolic_identity':True,'value':n['value'],'left':n['left'],'right':n['right'],'parent':n['parent'],'balance_factor':n['balance_factor'],'allocated':True,'freed':False} for n in heap]
        ped['memory']={'event':'none','objects_before':deepcopy(objects),'objects_after':deepcopy(objects),'allocated_objects':[],'freed_objects':[],'dangling_references':[],'stable_addresses':True,'symbolic_identities':True}
        descriptions={'caller_enter':'Entra el llamador equivalente, sin un resultado futuro.','call':'El declarador ya establecio el ambito del local, que sigue sin inicializar durante la llamada. No se lee su valor. Los marcos padres quedan suspendidos.','enter':'Entra una invocacion con su propio parametro arbol, incluso si es NULL.','condition':'Evalua la condicion con los valores disponibles. La seleccion de mayor altura no modifica enlaces.','assignment':'Termino el inicializador recursivo: el local ahora contiene el entero retornado por el hijo.','return':'Completa el retorno numerico y termina solo este ambito; no modifica el arbol.','caller_result':'El llamador retorna la altura en niveles: NULL vale 0 y hoja vale 1.'}
        if phase=='call' and not frames:descriptions['call']='Inicia la llamada exterior; aun no hay parametros ni locales de avl_altura ni resultado futuro.'
        if phase=='condition' and 'altIzq > altDer' in text:ped['executed_branch']='altIzq' if condition else 'altDer'
        ped['narration']={level:descriptions[phase] for level in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase in {'return','caller_result'},'value':result,'reconnects_subtree':False};ped['state_before']=deepcopy(old);ped['state_after']=deepcopy(new);ped['memory_state']=deepcopy(new);ped['instruction_event']={'phase':phase,'frame_id':owner,'condition':condition,'return':result}
        ped['invariant'].update(explanation='Consulta sin mutacion: todas las reservas y enlaces iniciales siguen vivos; cada invocacion retorna una altura en niveles.',holds=True,symbol='✓');validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
    def rec(identity):
        f={'id':'F'+str(len(history)+1),'function':'avl_altura','depth':len(frames),'parameters':{'arbol':identity},'locals':{}};history.append(f)
        emit('int avl_altura(AVL arbol) {','enter',lambda:frames.append(f))
        terminal=identity=='NULL'
        emit('if (arbol == NULL)','condition',condition=terminal,expression='if ('+identity+' == NULL)')
        if terminal:result=0;text='return 0;'
        else:
            for name,side,field in [('altIzq','left','izq'),('altDer','right','der')]:
                declaration='int '+name+' = avl_altura(arbol->'+field+');'
                emit(declaration,'call',lambda:f['locals'].__setitem__(name,'sin inicializar'))
                value=rec(node(identity)[side])
                emit(declaration,'assignment',lambda:f['locals'].__setitem__(name,value))
            left,right=f['locals']['altIzq'],f['locals']['altDer']
            text='return (altIzq > altDer ? altIzq : altDer) + 1;'
            emit(text,'condition',condition=left>right,expression='('+str(left)+' > '+str(right)+' ? '+str(left)+' : '+str(right)+') + 1')
            result=(left if left>right else right)+1
        def leave():
            nonlocal returned
            frames.pop();returned=result
        emit(text,'return',leave,result=result);return result
    def enter_caller():
        nonlocal caller
        caller={'function':'ejecutar_altura','parameters':{'raiz':head},'description':'raiz (AVL) -> '+head+'; retorno int pendiente, expuesto como altura en niveles.'}
    emit('int ejecutar_altura(AVL raiz) {','caller_enter',enter_caller)
    call='return avl_altura(raiz);';emit(call,'call');result=rec(head)
    def caller_return():
        nonlocal caller,height_result
        caller=None;height_result=result
    emit(call,'caller_result',caller_return,result=result)
    steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    initial=deepcopy(steps[0]['pedagogy']);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={level:'Ninguna instruccion ejecutada; arbol inicial, sin parametros ni retorno futuros.' for level in ['basic','intermediate','advanced']};steps[0]['pedagogy']['initial_frame']=initial
    trace.update(source_code=source,steps=steps);return trace
