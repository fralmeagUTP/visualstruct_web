"""Completed actual C extraction instructions, live buffer and external output."""
from copy import deepcopy
from pathlib import Path
from app.services.c_code_service import CCodeService
from .pedagogy import build_hierarchical_frame,validate_hierarchical_frame

def heap_extract_source():
    raw=(Path(__file__).resolve().parents[3]/'docs/tads_C/tad_monticulo_binario.c').read_text(encoding='utf-8-sig')
    blocks={s:CCodeService._extract_function_with_comment(raw,n) for s,n in [('compare','comparar'),('swap','intercambiar'),('down','heapify_down'),('extract','monticulo_extraer_raiz')]}
    blocks['caller']="""/**
 * @brief Llamador equivalente de la extraccion visible; no es nueva API del TAD.
 * @param m Monticulo existente.
 * @param resultado Alias al entero externo; no se lee antes de escribirlo.
 * @return Estado bool, distinto del entero extraido.
 */
bool ejecutar_extraer(MonticuloBinario *m, int *resultado) {
    bool ok = monticulo_extraer_raiz(m, resultado);
    return ok;
}"""
    return '\n\n'.join(blocks.values())+'\n',blocks

def build_heap_extract_trace(trace,before_state,after_state):
    source,blocks=heap_extract_source();lines=source.splitlines();quantity=before_state['size'];capacity=before_state['capacity'];written=quantity
    frames=[];steps=[];retired=[];active=[];last_return=None;counts={};reference='A1' if capacity else 'NULL';success=quantity>0
    output={'initialized':False,'value':None};objects=[{'id':'A1','capacity':capacity,'live':True,'cells':[{'index':i,'initialized':True if i<quantity else None,'value':before_state['array'][i] if i<quantity else None} for i in range(capacity)]}] if capacity else []
    names={'caller':'ejecutar_extraer','extract':'monticulo_extraer_raiz','down':'heapify_down','compare':'comparar','swap':'intercambiar'}
    def obj():return objects[0]
    def values():return [c['value'] for c in obj()['cells'][:written]] if objects else []
    def snapshot():
        state=deepcopy(before_state);state.update(heap_query_model=True,heap_extract_model=True,query_operation='extraer_raiz',query_frames=deepcopy(frames),array=values()[:quantity],size=quantity,capacity=capacity,empty=quantity==0,root=None,console_stdout='',active_copy_index=None,heap_active_indices=list(active),heap_data_reference=reference,heap_allocations=deepcopy(objects),heap_retired=[],heap_written=written,heap_pending_index=None,caller_output=deepcopy(output),last_return=deepcopy(last_return));return state
    def enter(scope,params):
        counts[scope]=counts.get(scope,0)+1;ident=scope+'-'+str(counts[scope]) if scope in ['compare','swap'] else scope
        frames.append({'id':ident,'kind':scope,'function':names[scope],'parameters':params,'locals':{}})
    def leave(result=None):
        nonlocal last_return
        f=frames.pop();last_return={'function':f['function'],'type':'void' if f['kind'] in ['down','swap'] else 'bool','value':result}
    def locate(scope,text,phase,occurrence=0):
        start=source.index(blocks[scope]);base=source[:start].count('\n');local=blocks[scope].splitlines()
        if text=='}' and phase=='return':return base+len(local)-1
        return base+[i for i,l in enumerate(local) if l.strip()==text][occurrence]
    def emit(scope,text,phase,mutate=None,condition=None,expression=None,result=None,note=None,indices=(),occurrence=0):
        nonlocal active
        previous=snapshot();active=list(indices)
        if mutate:mutate()
        current=snapshot();idx=locate(scope,text,phase,occurrence)
        step={'step_index':len(steps),'line_index':idx,'line_text':lines[idx],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':previous,'state_after':current,'debug':{'stage':phase}}
        if condition is not None:step['condition_result']=condition
        ped=build_hierarchical_frame(structure_id='binary_heap',operation_name='extraer_raiz',payload=trace['payload'],step=step,source_lines=lines,success=trace['success'])
        ped.update(concept='compare' if condition is not None else 'return' if phase=='return' else 'allocation' if phase=='allocation' else 'assignment',case=phase,phase={'id':scope+'-'+phase,'label':phase.replace('_',' ').title(),'goal':text})
        ped['condition']={'source':text,'substituted':expression,'result':condition,'consequence':'cuerpo' if condition else 'salida/siguiente'} if condition is not None else None;ped['executed_branch']=('cuerpo' if condition else 'salida/siguiente') if condition is not None else None
        old={f['id']:f for f in previous['query_frames']};new={f['id']:f for f in current['query_frames']};variables=[]
        for ident in dict.fromkeys([*old,*new]):
            a=old.get(ident,{});b=new.get(ident,{});f=b or a;prev={**a.get('parameters',{}),**a.get('locals',{})};now={**b.get('parameters',{}),**b.get('locals',{})}
            for name in dict.fromkeys([*prev,*now]):
                typ='MonticuloBinario *' if name=='m' else 'int *' if name=='resultado' or f['kind']=='swap' and name in ['a','b'] else 'bool' if name=='ok' else 'TipoMonticulo' if name=='tipo' else 'int'
                variables.append({'name':name,'frame_id':ident,'scope':f['function']+'#'+ident,'type':typ,'previous':prev.get(name,'fuera de ambito'),'value':now.get(name,'fuera de ambito'),'changed':prev.get(name)!=now.get(name),'meaning':'Parametro/local C real; los a/b de comparar son enteros por valor y los de intercambiar alias int *. Identidades de vidas simbolicas.'})
        for name,typ,field in [('m->datos','int *','heap_data_reference'),('m->cantidad','int','size'),('m->capacidad','int','capacity')]:variables.append({'name':name,'frame_id':'external','scope':'M1 compartido','type':typ,'previous':previous[field],'value':current[field],'changed':previous[field]!=current[field],'meaning':'Campos reales: cantidad cambia solo en su decremento; extraer no libera ni reduce capacidad.'})
        variables.append({'name':'salida','frame_id':'external','scope':'R1 externo','type':'int','previous':previous['caller_output']['value'] if previous['caller_output']['initialized'] else 'sin inicializar','value':current['caller_output']['value'] if current['caller_output']['initialized'] else 'sin inicializar','changed':previous['caller_output']!=current['caller_output'],'meaning':'Entero escrito por *resultado; independiente del retorno bool.'})
        ped['variables']=variables;shown=previous['query_frames'] if phase=='return' else current['query_frames']
        ped['call_stack']=[{'function':f['function'],'frame_id':f['id'],'depth':i,'parameters':deepcopy(f['parameters']),'locals':deepcopy(f['locals']),'local_root':'M1' if 'm' in f['parameters'] else None,'local_root_address':'M1' if 'm' in f['parameters'] else None,'return':result if phase=='return' and i==len(shown)-1 else None,'scope_status':'terminado (contexto del retorno)' if phase=='return' and i==len(shown)-1 else 'suspendido' if i<len(shown)-1 else 'activo','continuation':'Retornar reanuda el llamador. Cada llamada repetida tiene otro ambito; bool no es valor ni cantidad.'} for i,f in enumerate(shown)]
        def memory(state):return [dict(o,address=o['id'],allocated=o['live'],freed=not o['live'],symbolic_identity=True) for o in state['heap_allocations']]
        ped['memory']={'event':phase if phase=='allocation' else 'none','objects_before':memory(previous),'objects_after':memory(current),'allocated_objects':[{'id':o['id'],'address':o['id']} for o in current['heap_allocations'] if o['live'] and not any(a['id']==o['id'] and a['live'] for a in previous['heap_allocations'])],'freed_objects':[{'id':o['id'],'address':o['id']} for o in previous['heap_allocations'] if o['live'] and not any(a['id']==o['id'] and a['live'] for a in current['heap_allocations'])],'dangling_references':[],'stable_addresses':False,'symbolic_identities':True,'historical_objects':deepcopy(retired)}
        ped['array'].update(active_index=active[0] if active else None,parent_index=None)
        explanation=note or {'enter':'Entra este ambito con los argumentos C por valor o los alias indicados.','declaration':'Declara el local sin inicializar; aun no hay resultado ni memoria nueva.','call':'Evalua argumentos y llama al C real. El llamador queda suspendido.','resume':'Reanuda el llamador; solo se asigna el retorno si esta instruccion contiene un inicializador.','condition':'Evalua la condicion real y el cortocircuito. No modifica celdas ni cantidad.','assignment':'Solo escribe el campo, local o celda indicado. Las tres instrucciones del intercambio no son un cambio atomico.','allocation':'realloc exitoso termina A1 y crea A2 conservando el prefijo inicializado. datos es indeterminado hasta publicarlo; capacidad conserva su valor hasta su propia asignacion. No se simula el asignador ni se evalua el puntero anterior.','return':'Termina este ambito. El bool es estado; el retorno void no aporta valor.'}[phase]
        ped['narration']={level:explanation for level in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase=='return','value':result,'reconnects_subtree':False}
        ped.update(state_before=deepcopy(previous),state_after=deepcopy(current),memory_state=deepcopy(current),instruction_event={'scope':scope,'phase':phase,'condition':condition,'return':result})
        ped['invariant'].update(name='Estado intermedio de Extraer',holds=None,symbol='—',evidence_by_node_or_path=[],explanation='La vista logica sigue cantidad, la memoria conserva la cola inicializada fuera de cantidad. El descenso y sus intercambios parciales aun no afirman el invariante final.')
        validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
    emit('caller','bool ejecutar_extraer(MonticuloBinario *m, int *resultado) {','enter',lambda:enter('caller',{'m':'M1','resultado':'R1'}));caller=frames[-1]
    call='bool ok = monticulo_extraer_raiz(m, resultado);';emit('caller',call,'call',lambda:caller['locals'].update(ok='sin inicializar'))
    emit('extract','bool monticulo_extraer_raiz(MonticuloBinario *m, int *resultado) {','enter',lambda:enter('extract',{'m':'M1','resultado':'R1'}))
    guard='if (m == NULL || m->cantidad == 0 || resultado == NULL) return false;'
    emit('extract',guard,'condition',condition=not success,expression='M1 == NULL || '+str(quantity)+' == 0'+(' [cortocircuito; resultado no se evalua]' if not success else ' || R1 == NULL'))
    if success:
        emit('extract','*resultado = m->datos[0];','assignment',lambda:output.update(initialized=True,value=values()[0]),indices=[0],note='Escribe el entero externo R1 antes de reducir cantidad; aun no retorna el bool.')
        def decrement():
            nonlocal quantity
            quantity-=1
        emit('extract','m->cantidad--;','assignment',decrement,note='Reduce cantidad sin liberar memoria. La antigua cola sigue inicializada en A1, fuera del prefijo logico.')
        emit('extract','if (m->cantidad > 0) {','condition',condition=quantity>0,expression=f'{quantity} > 0')
        if quantity>0:
            emit('extract','m->datos[0] = m->datos[m->cantidad];','assignment',lambda:obj()['cells'][0].update(value=values()[quantity]),indices=[0,quantity])
            call_down='heapify_down(m, 0);';emit('extract',call_down,'call')
            i=0;emit('down','static void heapify_down(MonticuloBinario *m, int indice) {','enter',lambda:enter('down',{'m':'M1','indice':i}));down=frames[-1]
            emit('down','int hijo_izq, hijo_der, seleccionado;','declaration',lambda:down['locals'].update(hijo_izq='sin inicializar',hijo_der='sin inicializar',seleccionado='sin inicializar'))
            def compare(aidx,bidx,text):
                a=values()[aidx];b=values()[bidx];emit('down',text,'call',indices=[aidx,bidx]);emit('compare','static bool comparar(TipoMonticulo tipo, int a, int b) {','enter',lambda:enter('compare',{'tipo':0,'a':a,'b':b}))
                emit('compare','if (tipo == MONTICULO_MIN) {','condition',condition=True,expression='0 == MONTICULO_MIN');res=a<b;emit('compare','return a < b;','return',lambda:leave(res),result=res);return res
            while True:
                emit('down','while (1) {','condition',condition=True,expression='1')
                left=2*i+1;right=2*i+2;selected=i
                emit('down','hijo_izq = 2 * indice + 1;','assignment',lambda:down['locals'].update(hijo_izq=left))
                emit('down','hijo_der = 2 * indice + 2;','assignment',lambda:down['locals'].update(hijo_der=right))
                emit('down','seleccionado = indice;','assignment',lambda:down['locals'].update(seleccionado=selected))
                for child,label in [(left,'hijo_izq'),(right,'hijo_der')]:
                    text=f'if ({label} < m->cantidad && comparar(m->tipo, m->datos[{label}], m->datos[seleccionado])) {{'
                    cmp=compare(child,selected,text) if child<quantity else False
                    emit('down',text,'condition',condition=child<quantity and cmp,expression=f'{child} < {quantity}'+(' && '+str(cmp).lower()+' [retorno comparar]' if child<quantity else ' [cortocircuito; comparar no se llama]'))
                    if child<quantity and cmp:
                        selected=child;emit('down',f'seleccionado = {label};','assignment',lambda:down['locals'].update(seleccionado=selected))
                emit('down','if (seleccionado != indice) {','condition',condition=selected!=i,expression=f'{selected} != {i}')
                if selected==i:
                    emit('down','break;','assignment',note='break sale del bucle sin modificar el buffer ni cantidad.');break
                swapcall='intercambiar(&m->datos[indice], &m->datos[seleccionado]);';emit('down',swapcall,'call')
                emit('swap','static void intercambiar(int *a, int *b) {','enter',lambda:enter('swap',{'a':f'&A1[{i}]','b':f'&A1[{selected}]'}));swap=frames[-1];temp=values()[i]
                emit('swap','int temp = *a;','assignment',lambda:swap['locals'].update(temp=temp),indices=[i])
                emit('swap','*a = *b;','assignment',lambda:obj()['cells'][i].update(value=values()[selected]),indices=[i,selected])
                emit('swap','*b = temp;','assignment',lambda:obj()['cells'][selected].update(value=temp),indices=[selected])
                emit('swap','}','return',leave);emit('down',swapcall,'resume')
                i=selected;emit('down','indice = seleccionado;','assignment',lambda:down['parameters'].update(indice=i))
            emit('down','}','return',leave);emit('extract',call_down,'resume')
    emit('extract','return true;' if success else guard,'return',lambda:leave(success),result=success)
    emit('caller',call,'resume',lambda:caller['locals'].update(ok=success));emit('caller','return ok;','return',lambda:leave(success),result=success)
    steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    initial=deepcopy(steps[0]['pedagogy']);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={level:'Ninguna instruccion ejecutada: salida no inicializada, buffer y cantidad originales.' for level in ['basic','intermediate','advanced']};steps[0]['pedagogy']['initial_frame']=initial
    trace.update(source_code=source,steps=steps);return trace
