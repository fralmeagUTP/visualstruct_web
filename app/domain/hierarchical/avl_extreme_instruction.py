"""AVL extrema: actual C/auxiliary loops and a guarded equivalent API caller."""
from copy import deepcopy
from .pedagogy import build_hierarchical_frame, validate_hierarchical_frame

def build_avl_extreme_trace(trace,before_state,after_state):
    op=trace['operation_name'];assert op in {'minimo','maximo'}
    fn='avl_'+op;callerfn='ejecutar_'+op
    caller_code='int '+callerfn+'(AVL raiz, int *resultado) {\n    if (raiz == NULL)\n        return 0;\n    AVL encontrado = '+fn+'(raiz);\n    *resultado = encontrado->nro;\n    return 1;\n}'
    source=trace['source_code'].rstrip()+'\n\n/* Llamador equivalente: guarda de vacio, alias prestado y salida int. No es API nueva del TAD. */\n'+caller_code+'\n'
    lines=source.splitlines();heap=[];frames=[];steps=[];caller=None;returned=None;wrapper_result=None;output={'identity':'salida','type':'int','initialized':False,'value':None}
    def load(n,parent='NULL'):
        if n is None:return 'NULL'
        identity='N'+str(len(heap)+1);item={'id':identity,'value':n['value'],'left':'NULL','right':'NULL','parent':parent,'balance_factor':n['balance_factor'],'status':'linked'};heap.append(item)
        item['left'],item['right']=load(n['left'],identity),load(n['right'],identity);return identity
    head=load(before_state.get('root'))
    def node(identity):return next(n for n in heap if n['id']==identity)
    def snapshot():
        state=deepcopy(before_state);state.update(abb_read_model=True,avl_read_model=True,avl_extreme_model=True,head=head,heap_nodes=deepcopy(heap),tree_frames=deepcopy(frames),caller_frame=deepcopy(caller),returned=returned,wrapper_result=wrapper_result,caller_output=deepcopy(output),console_stdout='')
        if state['caller_frame']:state['caller_frame']['description']='raiz (AVL) -> '+head+'; resultado (int *) -> &salida; salida: '+(str(output['value']) if output['initialized'] else 'sin inicializar')
        return state
    def emit(text,phase,mutate=None,condition=None,expression=None,result=None,scope='caller'):
        old=snapshot()
        if mutate:mutate()
        new=snapshot();idx=next(i for i,l in enumerate(lines) if l.strip()==text)
        step={'step_index':len(steps),'line_index':idx,'line_text':lines[idx],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':old,'state_after':new,'debug':{'stage':phase}}
        if condition is not None:step['condition_result']=condition
        ped=build_hierarchical_frame(structure_id='avl',operation_name=op,payload=trace['payload'],step=step,source_lines=lines,success=head!='NULL')
        ped['concept']='return' if phase in {'return','caller_result'} else 'compare' if condition is not None else 'assignment';ped['case']=phase;ped['phase']={'id':op+'-'+phase,'label':phase.title(),'goal':text}
        ped['condition']={'source':text,'substituted':expression,'result':condition,'consequence':'cuerpo' if condition else 'siguiente instruccion'} if condition is not None else None
        ped['executed_branch']='cuerpo' if condition else 'salida/siguiente' if condition is not None else None
        variables=[]
        for key,typ in [('raiz','AVL'),('resultado','int *'),('encontrado','AVL')]:
            a={**(old['caller_frame'] or {}).get('parameters',{}),**(old['caller_frame'] or {}).get('locals',{})};b={**(new['caller_frame'] or {}).get('parameters',{}),**(new['caller_frame'] or {}).get('locals',{})}
            if key in a or key in b:variables.append({'name':key,'scope':callerfn,'frame_id':'caller','type':typ,'previous':a.get(key,'fuera de ámbito'),'value':b.get(key,'fuera de ámbito'),'changed':a.get(key)!=b.get(key),'meaning':'Parametro/local del llamador; salida es un int del llamador, no una reserva AVL.'})
        for key in ['nodo','raiz','aux']:
            a={**old['tree_frames'][0]['parameters'],**old['tree_frames'][0]['locals']} if old['tree_frames'] else {};b={**new['tree_frames'][0]['parameters'],**new['tree_frames'][0]['locals']} if new['tree_frames'] else {}
            if key in a or key in b:variables.append({'name':key,'scope':fn+'#F1','frame_id':'F1','type':'AVL','previous':a.get(key,'fuera de ámbito'),'value':b.get(key,'fuera de ámbito'),'changed':a.get(key)!=b.get(key),'meaning':'Alias local por valor; cambiarlo no modifica raiz, nodos ni enlaces.'})
        if old['caller_output']['initialized'] or new['caller_output']['initialized']:
            variables.append({'name':'salida','scope':'main equivalente','frame_id':'main','type':'int','previous':old['caller_output']['value'] if old['caller_output']['initialized'] else 'sin inicializar','value':new['caller_output']['value'] if new['caller_output']['initialized'] else 'sin inicializar','changed':old['caller_output']!=new['caller_output'],'meaning':'Destino int del llamador escrito solo por *resultado, sin malloc ni mutacion del arbol.'})
        ped['variables']=variables;stack=[]
        shown_caller=old['caller_frame'] if phase=='caller_result' else new['caller_frame']
        if shown_caller:stack.append({'function':callerfn,'frame_id':'caller','depth':-1,'parameters':deepcopy(shown_caller['parameters']),'locals':deepcopy(shown_caller['locals']),'local_root':head,'local_root_address':head,'return':result if phase=='caller_result' else None,'scope_status':'terminado (contexto del retorno)' if phase=='caller_result' else 'suspendido' if new['tree_frames'] else 'activo','continuation':'Guarda de vacio, llamada valida, lectura del alias prestado y escritura de salida; 0 significa vacio,1 exito.'})
        for f in old['tree_frames'] if phase=='return' else new['tree_frames']:
            stack.append({'function':fn,'frame_id':'F1','depth':0,'parameters':deepcopy(f['parameters']),'locals':deepcopy(f['locals']),'local_root':next(iter(f['parameters'].values())),'local_root_address':next(iter(f['parameters'].values())),'return':result if phase=='return' else None,'scope_status':'terminado (contexto del retorno)' if phase=='return' else 'activo','continuation':'Un solo ambito iterativo. Retorno prestado; no reconecta, reserva ni libera.'})
        ped['call_stack']=stack;objects=[{'id':n['id'],'address':n['id'],'symbolic_identity':True,'value':n['value'],'left':n['left'],'right':n['right'],'parent':n['parent'],'balance_factor':n['balance_factor'],'allocated':True,'freed':False} for n in heap]
        ped['memory']={'event':'none','objects_before':deepcopy(objects),'objects_after':deepcopy(objects),'allocated_objects':[],'freed_objects':[],'dangling_references':[],'stable_addresses':True,'symbolic_identities':True}
        narration={'caller_enter':'Entra el llamador equivalente. salida aun no tiene un valor inicializado.','caller_condition':'La guarda del llamador evita invocar el C de Minimo con NULL; el C publico requiere nodo no nulo. La interfaz rechaza el vacio.','call':'La declaracion de encontrado inicia su ambito, pero su inicializador sigue pendiente hasta que retorne la funcion.','enter':'Entra una unica invocacion iterativa con parametros por valor.','condition':'Evalua la condicion real: Minimo lee izq de un nodo vivo; Maximo cortocircuita si aux es NULL.','assignment':'Cambia solo el alias local del recorrido; raiz y heap quedan intactos.','return':'Entrega un alias prestado y termina el unico ambito del TAD/auxiliar; no devuelve una reserva nueva.','caller_assignment':'El inicializador de encontrado termina con el mismo alias prestado.','caller_store':'Lee encontrado->nro y escribe exclusivamente el int de salida del llamador. No muta el arbol.','caller_result':'Termina el llamador: 0 rechaza vacio sin leer salida ni llamar al TAD;1 indica que salida ya contiene el extremo.'}[phase]
        ped['narration']={level:narration for level in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase in {'return','caller_result'},'value':result,'reconnects_subtree':False};ped['state_before']=deepcopy(old);ped['state_after']=deepcopy(new);ped['memory_state']=deepcopy(new);ped['instruction_event']={'phase':phase,'frame_id':scope,'condition':condition,'return':result}
        ped['invariant'].update(explanation='Consulta de solo lectura: identidades/enlaces/padres/FE se conservan. El destino int es del llamador; vacio es un rechazo y no una llamada C invalida.',holds=True,symbol='✓');validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
    def caller_enter():
        nonlocal caller
        caller={'function':callerfn,'parameters':{'raiz':head,'resultado':'&salida'},'locals':{}}
    emit('int '+callerfn+'(AVL raiz, int *resultado) {','caller_enter',caller_enter)
    emit('if (raiz == NULL)','caller_condition',condition=head=='NULL',expression='if ('+head+' == NULL)')
    if head!='NULL':
        text='AVL encontrado = '+fn+'(raiz);';emit(text,'call',lambda:caller['locals'].update(encontrado='sin inicializar'))
        parameter='nodo' if op=='minimo' else 'raiz';f={'id':'F1','function':fn,'depth':0,'parameters':{parameter:head},'locals':{}}
        emit('AVL '+fn+'(AVL '+parameter+') {','enter',lambda:frames.append(f),scope='F1');cursor=head
        if op=='maximo':emit('AVL aux = raiz;','assignment',lambda:f['locals'].update(aux=cursor),scope='F1')
        while True:
            side='left' if op=='minimo' else 'right';child=node(cursor)[side];condition=child!='NULL'
            text='while (nodo->izq)' if op=='minimo' else 'while (aux != NULL && aux->der != NULL) {'
            expression='while ('+child+')' if op=='minimo' else 'while ('+cursor+' != NULL && '+child+' != NULL)'
            emit(text,'condition',condition=condition,expression=expression,scope='F1')
            if not condition:break
            cursor=child
            emit('nodo = nodo->izq;' if op=='minimo' else 'aux = aux->der;','assignment',lambda:f['parameters'].update(nodo=cursor) if op=='minimo' else f['locals'].update(aux=cursor),scope='F1')
        def leave():
            nonlocal returned
            returned=cursor;frames.pop()
        emit('return nodo;' if op=='minimo' else 'return aux;','return',leave,result=cursor,scope='F1')
        emit('AVL encontrado = '+fn+'(raiz);','caller_assignment',lambda:caller['locals'].update(encontrado=cursor))
        emit('*resultado = encontrado->nro;','caller_store',lambda:output.update(initialized=True,value=node(cursor)['value']))
    def caller_leave():
        nonlocal caller,wrapper_result
        caller=None;wrapper_result=int(head!='NULL')
    emit('return 0;' if head=='NULL' else 'return 1;','caller_result',caller_leave,result=int(head!='NULL'))
    steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    initial=deepcopy(steps[0]['pedagogy']);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={level:'Ninguna instruccion ejecutada; salida sin inicializar y sin resultados futuros.' for level in ['basic','intermediate','advanced']};steps[0]['pedagogy']['initial_frame']=initial
    trace.update(source_code=source,steps=steps);return trace
