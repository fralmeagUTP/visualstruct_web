"""Heap read queries: executed-line snapshots, output lifetime and independent copy.

The caller is a documented equivalent of the visible operation. The TAD bodies
come from the actual downloaded C; allocator internals remain a black box.
"""
from copy import deepcopy
from pathlib import Path
from app.services.c_code_service import CCodeService
from .pedagogy import build_hierarchical_frame, validate_hierarchical_frame


def heap_query_source(operation, caller_fragment=None):
    raw=(Path(__file__).resolve().parents[3]/'docs/tads_C/tad_monticulo_binario.c').read_text(encoding='utf-8-sig')
    extract=lambda name:CCodeService._extract_function_with_comment(raw,name)
    if operation=='raiz':
        caller='bool ejecutar_raiz(MonticuloBinario *m, int *resultado) {\n    bool ok = monticulo_raiz(m, resultado);\n    return ok;\n}'
        docs='/**\n * @brief Consulta la raiz con salida del llamador externo.\n * @param m Monticulo prestado, no modificado.\n * @param resultado Destino int del llamador externo.\n * @return true si se escribe el entero; false si falla la guarda, sin escribir.\n * @note Llamador equivalente; no es una nueva funcion publica del TAD.\n */\n'
        return extract('monticulo_raiz')+'\n\n'+docs+caller+'\n',caller
    assert operation=='a_lista'
    fragment=caller_fragment or CCodeService.get_structure_data('binary_heap')['operations']['a_lista']
    body=fragment.replace('&monticulo','m')
    caller='int ejecutar_a_lista(MonticuloBinario *m) {\n'+'\n'.join('    '+line for line in body.splitlines())+'\n    return EXIT_SUCCESS;\n}'
    docs='/**\n * @brief Copia didactica con destino independiente y vida limitada a esta llamada.\n * @param m Monticulo prestado, no modificado ni destruido por este auxiliar.\n * @return EXIT_SUCCESS tras liberar la copia; EXIT_FAILURE si la reserva falla.\n * @note El int retornado es estado, no cantidad ni arreglo. No es API nueva del TAD.\n */\n'
    return extract('monticulo_cantidad')+'\n\n'+extract('monticulo_copiar_valores')+'\n\n'+docs+caller+'\n',caller


def build_heap_query_trace(trace,before_state,after_state):
    operation=trace['operation_name'];source,caller_source=heap_query_source(operation,trace.get('source_code') if operation=='a_lista' else None)
    lines=source.splitlines();values=list(before_state['array']);count=len(values);capacity=before_state['capacity']
    frames=[];steps=[];buffer=None;retired=None;active_index=None;last_return=None;wrapper_status=None;observed=None
    output={'id':'salida','type':'int','initialized':False,'value':None}
    pointer_history='B1 [valor indeterminado; identidad historica]'
    def snapshot():
        result=deepcopy(before_state);result.update(heap_query_model=True,query_operation=operation,query_frames=deepcopy(frames),caller_output=deepcopy(output),destination=deepcopy(buffer),retired_destination=deepcopy(retired),active_copy_index=active_index,last_return=deepcopy(last_return),wrapper_status=wrapper_status,observed_result=deepcopy(observed),console_stdout='')
        return result
    def line(text,scope):
        signature={'caller':caller_source.splitlines()[0],'count':'int monticulo_cantidad(const MonticuloBinario *m) {','root':'bool monticulo_raiz(const MonticuloBinario *m, int *resultado) {','copy':'int monticulo_copiar_valores(const MonticuloBinario *m, int *destino, int capacidad) {'}[scope]
        start=next(i for i,l in enumerate(lines) if l.strip()==signature)
        return next(i for i in range(start,len(lines)) if lines[i].strip()==text)
    def describe(frame):
        return frame['function']+'#'+frame['id']
    types={'m':'const MonticuloBinario *','resultado':'int *','destino':'int *','capacidad':'int','cantidad':'int','buffer':'int *','usados':'int','a_copiar':'int','i':'int','ok':'bool'}
    def emit(scope,text,phase,mutate=None,condition=None,expression=None,result=None,note=None):
        nonlocal active_index
        previous=snapshot()
        active_index=None # Instruction context; highlight only the actual read/write, not a future for index.
        if mutate:mutate()
        current=snapshot();idx=line(text,scope)
        step={'step_index':len(steps),'line_index':idx,'line_text':lines[idx],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':previous,'state_after':current,'debug':{'stage':phase}}
        if condition is not None:step['condition_result']=condition
        ped=build_hierarchical_frame(structure_id='binary_heap',operation_name=operation,payload=trace['payload'],step=step,source_lines=lines,success=trace['success'])
        ped.update(concept='compare' if condition is not None else 'return' if phase=='return' else 'allocation' if phase=='allocation' else 'free' if phase=='free' else 'assignment',case=phase,phase={'id':scope+'-'+phase,'label':phase.replace('_',' ').title(),'goal':text})
        ped['condition']={'source':text,'substituted':expression,'result':condition,'consequence':'cuerpo' if condition else 'siguiente instruccion'} if condition is not None else None
        ped['executed_branch']=('cuerpo' if condition else 'salida/siguiente') if condition is not None else None
        old={f['id']:f for f in previous['query_frames']};new={f['id']:f for f in current['query_frames']};variables=[]
        for ident in dict.fromkeys([*old,*new]):
            a=old.get(ident,{});b=new.get(ident,{});before={**a.get('parameters',{}),**a.get('locals',{})};after={**b.get('parameters',{}),**b.get('locals',{})}
            for name in dict.fromkeys([*before,*after]):
                typ='MonticuloBinario *' if name=='m' and ident=='caller' else types[name]
                variables.append({'name':name,'scope':describe(b or a),'frame_id':ident,'type':typ,'previous':before.get(name,'fuera de ambito'),'value':after.get(name,'fuera de ambito'),'changed':before.get(name)!=after.get(name),'meaning':'Parametro/local real; pendiente indica inicializador no terminado. Identidades simbolicas, no direcciones reales.'})
        if operation=='raiz':variables.append({'name':'salida','scope':'llamador externo','frame_id':'external','type':'int','previous':previous['caller_output']['value'] if previous['caller_output']['initialized'] else 'sin inicializar','value':output['value'] if output['initialized'] else 'sin inicializar','changed':previous['caller_output']!=output,'meaning':'Entero independiente; solo *resultado lo escribe. Bool de retorno no es este valor.'})
        ped['variables']=variables;shown=previous['query_frames'] if phase=='return' else current['query_frames']
        ped['call_stack']=[{'function':f['function'],'frame_id':f['id'],'depth':depth,'parameters':deepcopy(f['parameters']),'locals':deepcopy(f['locals']),'local_root':'M1','local_root_address':'M1','return':result if phase=='return' and depth==len(shown)-1 else None,'scope_status':'terminado (contexto del retorno)' if phase=='return' and depth==len(shown)-1 else 'suspendido' if depth<len(shown)-1 else 'activo','continuation':'El TAD permanece intacto. La copia y la salida son destinos del llamador.'} for depth,f in enumerate(shown)]
        def objects(state):
            objects=[{'id':'A1','address':'A1','allocated':True,'freed':False,'capacity':capacity,'initialized_values':list(values),'symbolic_identity':True}]
            if state['destination']:objects.append({'id':'B1','address':'B1','allocated':True,'freed':False,'capacity':state['destination']['capacity'],'cells':deepcopy(state['destination']['cells']),'symbolic_identity':True})
            return objects
        ped['memory']={'event':phase if phase in {'allocation','free'} else 'none','objects_before':objects(previous),'objects_after':objects(current),'allocated_objects':[{'id':'B1','address':'B1'}] if phase=='allocation' and buffer else [],'freed_objects':[{'id':'B1','address':'B1'}] if phase=='free' and previous['destination'] else [],'dangling_references':[],'stable_addresses':True,'symbolic_identities':True}
        if retired:ped['memory']['historical_destination']=deepcopy(retired)
        ped['array'].update(active_index=active_index,parent_index=None if active_index is None or active_index==0 else (active_index-1)//2)
        explanation=note or {'enter':'Entra un ambito con parametros por valor. M1 designa la misma estructura, A1 su arreglo existente.','call':'El inicializador queda pendiente hasta el retorno de la llamada; aun no hay valor calculado.','resume':'El retorno inicializa exclusivamente el local del llamador. No escribe el monticulo.','condition':'Evalua la condicion C real y el cortocircuito. No modifica estructura ni destino.','assignment':'Escribe solo el destino o local indicado por esta instruccion.','loop_init':'Inicializa i dentro del ambito del for; no cambia la estructura.','loop_increment':'Incrementa i; no copia ni muta valores.','allocation':'La reserva del ejemplo es exitosa y contiene enteros sin inicializar. No es una reserva del monticulo. Internos de malloc no se simulan.','free':'Termina la vida de B1. Sus valores previos son solo registros historicos; no se leen punteros ni memoria liberados. A1 permanece vivo.','return':'Termina este ambito; el retorno queda pendiente de asignacion en el llamador.','loop_condition':'Evalua el for. El cuerpo del bucle didactico solo es un comentario: no muta ni vuelve a copiar.'}[phase]
        ped['narration']={level:explanation for level in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase=='return','value':result,'reconnects_subtree':False}
        ped.update(state_before=deepcopy(previous),state_after=deepcopy(current),memory_state=deepcopy(current),instruction_event={'scope':scope,'phase':phase,'condition':condition,'return':result})
        ped['invariant'].update(holds=True,symbol='V',explanation='Consulta: M1/A1, cantidad, capacidad y orden interno permanecen iguales. Solo se escriben salida o destino independiente; no hay intercambio ni cambio del arbol.')
        validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
    def enter(scope,function,params):
        frame={'id':scope,'function':function,'parameters':params,'locals':{}};frames.append(frame);return frame
    def leave(scope,status):
        nonlocal last_return,wrapper_status
        last_return={'function':frames[-1]['function'],'value':status};frames.pop()
        if scope=='caller':wrapper_status=status
    if operation=='raiz':
        emit('caller',caller_source.splitlines()[0],'enter',lambda:enter('caller','ejecutar_raiz',{'m':'M1','resultado':'&salida'}));caller=frames[0]
        text='bool ok = monticulo_raiz(m, resultado);';emit('caller',text,'call',lambda:caller['locals'].update(ok='sin inicializar'))
        emit('root','bool monticulo_raiz(const MonticuloBinario *m, int *resultado) {','enter',lambda:enter('root','monticulo_raiz',{'m':'M1','resultado':'&salida'}))
        guard='if (m == NULL || m->cantidad == 0 || resultado == NULL) return false;'
        emit('root',guard,'condition',condition=count==0,expression='if (M1 == NULL || '+str(count)+' == 0'+(' [cortocircuito; resultado no se evalua]' if count==0 else ' || &salida == NULL')+')')
        if count:
            def store_root():
                nonlocal active_index
                output.update(initialized=True,value=values[0]);active_index=0
            emit('root','*resultado = m->datos[0];','assignment',store_root)
        emit('root','return true;' if count else guard,'return',lambda:leave('root',bool(count)),result=bool(count))
        emit('caller',text,'resume',lambda:caller['locals'].update(ok=bool(count)))
        emit('caller','return ok;','return',lambda:leave('caller',bool(count)),result=bool(count))
    else:
        emit('caller',caller_source.splitlines()[0],'enter',lambda:enter('caller','ejecutar_a_lista',{'m':'M1'}));caller=frames[0]
        text='int cantidad = monticulo_cantidad(m);';emit('caller',text,'call',lambda:caller['locals'].update(cantidad='sin inicializar'))
        emit('count','int monticulo_cantidad(const MonticuloBinario *m) {','enter',lambda:enter('count','monticulo_cantidad',{'m':'M1'}))
        emit('count','if (m == NULL) return 0;','condition',condition=False,expression='if (M1 == NULL)')
        emit('count','return m->cantidad;','return',lambda:leave('count',count),result=count)
        emit('caller',text,'resume',lambda:caller['locals'].update(cantidad=count))
        def allocate():
            nonlocal buffer
            caller['locals']['buffer']='B1' if count else 'NULL'
            if count:buffer={'id':'B1','capacity':count,'cells':[{'index':i,'initialized':False,'value':None} for i in range(count)]}
        emit('caller','int *buffer = cantidad > 0 ? malloc((size_t)cantidad * sizeof *buffer) : NULL;','allocation' if count else 'assignment',allocate,condition=count>0,expression=str(count)+' > 0 ? malloc('+str(count)+' * sizeof(int)) : NULL',note=None if count else 'cantidad es 0: el condicional elige NULL sin invocar malloc; no hay reserva ni valores de destino.')
        emit('caller','if (cantidad > 0 && buffer == NULL) {','condition',condition=False,expression='if ('+str(count)+' > 0'+(' && B1 == NULL)' if count else ' [cortocircuito; buffer no se evalua])'))
        text='int usados = monticulo_copiar_valores(m, buffer, cantidad);';emit('caller',text,'call',lambda:caller['locals'].update(usados='sin inicializar'))
        emit('copy','int monticulo_copiar_valores(const MonticuloBinario *m, int *destino, int capacidad) {','enter',lambda:enter('copy','monticulo_copiar_valores',{'m':'M1','destino':'B1' if count else 'NULL','capacidad':count}));copy=frames[-1]
        guard='if (m == NULL || destino == NULL || capacidad <= 0) return 0;'
        emit('copy',guard,'condition',condition=count==0,expression='if (M1 == NULL || '+('NULL == NULL [cortocircuito; capacidad no se evalua])' if count==0 else 'B1 == NULL || '+str(count)+' <= 0)'))
        if count:
            emit('copy','int a_copiar = m->cantidad < capacidad ? m->cantidad : capacidad;','assignment',lambda:copy['locals'].update(a_copiar=count),condition=False,expression=str(count)+' < '+str(count)+' ? '+str(count)+' : '+str(count),note='El condicional compara cantidad < capacidad; aqui son iguales y elige capacidad. No reserva ni copia aun.')
            loop='for (int i = 0; i < a_copiar; i++) {'
            emit('copy',loop,'loop_init',lambda:copy['locals'].update(i=0))
            for i in range(count+1):
                emit('copy',loop,'condition',(lambda:copy['locals'].pop('i')) if i==count else None,condition=i<count,expression='for (; '+str(i)+' < '+str(count)+'; )')
                if i==count:break
                def store(index=i):
                    nonlocal active_index
                    buffer['cells'][index].update(initialized=True,value=values[index]);active_index=index
                emit('copy','destino[i] = m->datos[i];','assignment',store,note='Copia A1['+str(i)+'] en B1['+str(i)+']; solo este elemento pasa a estar inicializado. A1 y el arbol no cambian.')
                emit('copy',loop,'loop_increment',lambda index=i:copy['locals'].update(i=index+1))
            emit('copy','return a_copiar;','return',lambda:leave('copy',count),result=count)
        else:emit('copy',guard,'return',lambda:leave('copy',0),result=0)
        def resume():
            nonlocal observed,active_index
            caller['locals']['usados']=count;observed=[cell['value'] for cell in buffer['cells']] if buffer else [];active_index=None
        emit('caller',text,'resume',resume)
        loop='for (int i = 0; i < usados; i++) {';emit('caller',loop,'loop_init',lambda:caller['locals'].update(i=0))
        for i in range(count+1):
            emit('caller',loop,'loop_condition',(lambda:caller['locals'].pop('i')) if i==count else None,condition=i<count,expression='for (; '+str(i)+' < '+str(count)+'; )')
            if i<count:emit('caller',loop,'loop_increment',lambda index=i:caller['locals'].update(i=index+1))
        def release():
            nonlocal buffer,retired
            if buffer:retired={'id':'B1','capacity':count,'cells':deepcopy(buffer['cells']),'status':'vida terminada; registro anterior a free'};caller['locals']['buffer']=pointer_history
            buffer=None
        emit('caller','free(buffer);','free',release,note=None if count else 'free(NULL) no hace nada: no libera A1 ni crea una reserva historica. buffer sigue NULL.')
        emit('caller','return EXIT_SUCCESS;','return',lambda:leave('caller',0),result=0)
    steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    initial=deepcopy(steps[0]['pedagogy']);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={level:'Ninguna instruccion ejecutada; no hay salida inicializada ni copia futura.' for level in ['basic','intermediate','advanced']};steps[0]['pedagogy']['initial_frame']=initial
    trace.update(source_code=source,steps=steps);return trace
