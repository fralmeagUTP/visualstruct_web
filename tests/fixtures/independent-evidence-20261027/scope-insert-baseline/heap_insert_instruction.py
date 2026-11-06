"""Completed C instructions for Heap Insertar; physical cells versus cantidad."""
from copy import deepcopy
from pathlib import Path
from app.services.c_code_service import CCodeService
from .pedagogy import build_hierarchical_frame,validate_hierarchical_frame

INSERT_RESERVE_ERROR='No se pudo reservar memoria para insertar en el monticulo.'

def heap_insert_source():
    raw=(Path(__file__).resolve().parents[3]/'docs/tads_C/tad_monticulo_binario.c').read_text(encoding='utf-8-sig')
    blocks={scope:CCodeService._extract_function_with_comment(raw,name) for scope,name in [('reserve','asegurar_capacidad'),('compare','comparar'),('swap','intercambiar'),('up','heapify_up'),('insert','monticulo_insertar')]}
    blocks['caller']='''/**
 * @brief Llamador equivalente de la insercion visible, sin nueva API del TAD.
 * @param m Monticulo prestado; conserva el contenido previo si falla la reserva.
 * @param valor Entero C que se insertara.
 * @return El bool del TAD; no es el valor insertado ni la cantidad.
 */
bool ejecutar_insertar(MonticuloBinario *m, int valor) {
    bool ok = monticulo_insertar(m, valor);
    return ok;
}'''
    return '\n\n'.join(blocks.values())+'\n',blocks

def build_heap_insert_trace(trace,before_state,after_state):
    source,blocks=heap_insert_source();lines=source.splitlines();value=int(trace['payload']['value']);quantity=before_state['size'];capacity=before_state['capacity']
    reference='A1' if capacity else 'NULL';frames=[];steps=[];retired=[];active=[];last_return=None;counts={};written=quantity
    objects=[{'id':'A1','capacity':capacity,'live':True,'cells':[{'index':i,'initialized':True if i<quantity else None,'value':before_state['array'][i] if i<quantity else None} for i in range(capacity)]}] if capacity else []
    current_id='A1' if capacity else None;success=trace['success'];names={'caller':'ejecutar_insertar','insert':'monticulo_insertar','reserve':'asegurar_capacidad','up':'heapify_up','compare':'comparar','swap':'intercambiar'}
    def obj():return next(o for o in objects if o['id']==current_id and o['live'])
    def values():return [c['value'] for c in obj()['cells'][:written]] if current_id else []
    def snapshot():
        state=deepcopy(before_state);published=reference in ['A1','A2'] and any(o['id']==reference and o['live'] for o in objects)
        state.update(heap_query_model=True,heap_insert_model=True,query_operation='insertar',query_frames=deepcopy(frames),array=values() if published else [],size=quantity,capacity=capacity,empty=quantity==0,root=None,console_stdout='',active_copy_index=None,heap_active_indices=list(active),heap_data_reference=reference,heap_allocations=deepcopy(objects),heap_retired=deepcopy(retired),heap_written=written,heap_pending_index=quantity if written>quantity else None,last_return=deepcopy(last_return))
        return state
    def enter(scope,params):
        counts[scope]=counts.get(scope,0)+1;ident=scope+'-'+str(counts[scope]) if scope in ['compare','swap'] else scope
        frames.append({'id':ident,'kind':scope,'function':names[scope],'parameters':params,'locals':{}})
    def leave(result=None):
        nonlocal last_return
        f=frames.pop();last_return={'function':f['function'],'type':'void' if f['kind'] in ['up','swap'] else 'bool','value':result}
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
        ped=build_hierarchical_frame(structure_id='binary_heap',operation_name='insertar',payload=trace['payload'],step=step,source_lines=lines,success=trace['success'])
        ped.update(concept='compare' if condition is not None else 'return' if phase=='return' else 'allocation' if phase=='allocation' else 'assignment',case=phase,phase={'id':scope+'-'+phase,'label':phase.replace('_',' ').title(),'goal':text})
        ped['condition']={'source':text,'substituted':expression,'result':condition,'consequence':'cuerpo' if condition else 'salida/siguiente'} if condition is not None else None;ped['executed_branch']=('cuerpo' if condition else 'salida/siguiente') if condition is not None else None
        old={f['id']:f for f in previous['query_frames']};new={f['id']:f for f in current['query_frames']};variables=[]
        for ident in dict.fromkeys([*old,*new]):
            a=old.get(ident,{});b=new.get(ident,{});f=b or a;prev={**a.get('parameters',{}),**a.get('locals',{})};now={**b.get('parameters',{}),**b.get('locals',{})}
            for name in dict.fromkeys([*prev,*now]):
                typ='MonticuloBinario *' if name=='m' else 'int *' if name=='nuevos_datos' or f['kind']=='swap' and name in ['a','b'] else 'bool' if name=='ok' else 'TipoMonticulo' if name=='tipo' else 'int'
                variables.append({'name':name,'frame_id':ident,'scope':f['function']+'#'+ident,'type':typ,'previous':prev.get(name,'fuera de ambito'),'value':now.get(name,'fuera de ambito'),'changed':prev.get(name)!=now.get(name),'meaning':'Parametro/local C real; los a/b de comparar son enteros por valor y los de intercambiar alias int *. Identidades de vidas simbolicas.'})
        for name,typ,field in [('m->datos','int *','heap_data_reference'),('m->cantidad','int','size'),('m->capacidad','int','capacity')]:variables.append({'name':name,'frame_id':'external','scope':'M1 compartido','type':typ,'previous':previous[field],'value':current[field],'changed':previous[field]!=current[field],'meaning':'Campos reales; escribir datos[cantidad] aun no incrementa cantidad. No se lee un puntero indeterminado.'})
        ped['variables']=variables;shown=previous['query_frames'] if phase=='return' else current['query_frames']
        ped['call_stack']=[{'function':f['function'],'frame_id':f['id'],'depth':i,'parameters':deepcopy(f['parameters']),'locals':deepcopy(f['locals']),'local_root':'M1' if 'm' in f['parameters'] else None,'local_root_address':'M1' if 'm' in f['parameters'] else None,'return':result if phase=='return' and i==len(shown)-1 else None,'scope_status':'terminado (contexto del retorno)' if phase=='return' and i==len(shown)-1 else 'suspendido' if i<len(shown)-1 else 'activo','continuation':'Retornar reanuda el llamador. Cada llamada repetida tiene otro ambito; bool no es valor ni cantidad.'} for i,f in enumerate(shown)]
        def memory(state):return [dict(o,address=o['id'],allocated=o['live'],freed=not o['live'],symbolic_identity=True) for o in state['heap_allocations']]
        ped['memory']={'event':phase if phase=='allocation' else 'none','objects_before':memory(previous),'objects_after':memory(current),'allocated_objects':[{'id':o['id'],'address':o['id']} for o in current['heap_allocations'] if o['live'] and not any(a['id']==o['id'] and a['live'] for a in previous['heap_allocations'])],'freed_objects':[{'id':o['id'],'address':o['id']} for o in previous['heap_allocations'] if o['live'] and not any(a['id']==o['id'] and a['live'] for a in current['heap_allocations'])],'dangling_references':[],'stable_addresses':False,'symbolic_identities':True,'historical_objects':deepcopy(retired)}
        ped['array'].update(active_index=active[0] if active else None,parent_index=None)
        explanation=note or {'enter':'Entra este ambito con los argumentos C por valor o los alias indicados.','declaration':'Declara el local sin inicializar; aun no hay resultado ni memoria nueva.','call':'Evalua argumentos y llama al C real. El llamador queda suspendido.','resume':'Reanuda el llamador; solo se asigna el retorno si esta instruccion contiene un inicializador.','condition':'Evalua la condicion real y el cortocircuito. No modifica celdas ni cantidad.','assignment':'Solo escribe el campo, local o celda indicado. Las tres instrucciones del intercambio no son un cambio atomico.','allocation':'realloc exitoso termina A1 y crea A2 conservando el prefijo inicializado. datos es indeterminado hasta publicarlo; capacidad conserva su valor hasta su propia asignacion. No se simula el asignador ni se evalua el puntero anterior.','return':'Termina este ambito. El bool es estado; el retorno void no aporta valor.'}[phase]
        ped['narration']={level:explanation for level in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase=='return','value':result,'reconnects_subtree':False}
        ped.update(state_before=deepcopy(previous),state_after=deepcopy(current),memory_state=deepcopy(current),instruction_event={'scope':scope,'phase':phase,'condition':condition,'return':result})
        ped['invariant'].update(name='Estado intermedio de Insertar',holds=None,symbol='—',evidence_by_node_or_path=[],explanation='Los dibujos siguen celdas escritas, incluyendo datos[cantidad] pendiente; cantidad se incrementa al final. Intercambios parciales y realloc no afirman el invariante final ni leen memoria terminada.')
        validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
    emit('caller','bool ejecutar_insertar(MonticuloBinario *m, int valor) {','enter',lambda:enter('caller',{'m':'M1','valor':value}));caller=frames[-1]
    call='bool ok = monticulo_insertar(m, valor);';emit('caller',call,'call',lambda:caller['locals'].update(ok='sin inicializar'))
    emit('insert','bool monticulo_insertar(MonticuloBinario *m, int valor) {','enter',lambda:enter('insert',{'m':'M1','valor':value}))
    emit('insert','if (m == NULL) return false;','condition',condition=False,expression='M1 == NULL')
    guard='if (!asegurar_capacidad(m, m->cantidad + 1)) {';emit('insert',guard,'call')
    target=quantity+1;emit('reserve','static bool asegurar_capacidad(MonticuloBinario *m, int capacidad_objetivo) {','enter',lambda:enter('reserve',{'m':'M1','capacidad_objetivo':target}));reserve=frames[-1]
    emit('reserve','int nueva_capacidad;','declaration',lambda:reserve['locals'].update(nueva_capacidad='sin inicializar'))
    emit('reserve','int *nuevos_datos;','declaration',lambda:reserve['locals'].update(nuevos_datos='sin inicializar'))
    emit('reserve','if (m == NULL || capacidad_objetivo <= 0) {','condition',condition=False,expression=f'M1 == NULL || {target} <= 0')
    enough=capacity>=target and reference!='NULL'
    emit('reserve','if (m->capacidad >= capacidad_objetivo && m->datos != NULL) {','condition',condition=enough,expression=f'{capacity} >= {target}'+(' && '+reference+' != NULL' if capacity>=target else ' [cortocircuito; datos no se evalua]'))
    if not enough:
        n=capacity if capacity>0 else 10;emit('reserve','nueva_capacidad = (m->capacidad > 0) ? m->capacidad : MONTICULO_CAPACIDAD_POR_DEFECTO;','assignment',lambda:reserve['locals'].update(nueva_capacidad=n),condition=capacity>0,expression=f'{capacity} > 0 ? {capacity} : 10')
        while True:
            emit('reserve','while (nueva_capacidad < capacidad_objetivo) {','condition',condition=n<target,expression=f'{n} < {target}')
            if n>=target:break
            emit('reserve','if (nueva_capacidad > INT_MAX / 2) {','condition',condition=False,expression=f'{n} > INT_MAX / 2')
            n*=2;emit('reserve','nueva_capacidad *= 2;','assignment',lambda:reserve['locals'].update(nueva_capacidad=n))
        def allocate():
            nonlocal reference,current_id
            reserve['locals']['nuevos_datos']='A2' if success else 'NULL'
            if success:
                old=deepcopy(obj()) if current_id else None
                if old:
                    retired.append(dict(old,status='registro anterior a realloc exitoso; no memoria accesible'));obj().update(live=False,cells=[]);reference='indeterminado (A1 historico)'
                cells=deepcopy(old['cells']) if old else [];cells.extend({'index':i,'initialized':False,'value':None} for i in range(len(cells),n));objects.append({'id':'A2','capacity':n,'live':True,'cells':cells});current_id='A2'
        emit('reserve','nuevos_datos = (int *)realloc(m->datos, sizeof(int) * (size_t)nueva_capacidad);','allocation',allocate,note=None if success else 'realloc falla y devuelve NULL: A1 sigue vivo y datos, cantidad, capacidad y contenido no cambian. No se escribe el valor nuevo.')
        emit('reserve','if (nuevos_datos == NULL) {','condition',condition=not success,expression=('A2' if success else 'NULL')+' == NULL')
        if success:
            def publish():
                nonlocal reference
                reference='A2'
            emit('reserve','m->datos = nuevos_datos;','assignment',publish)
            def grow():
                nonlocal capacity
                capacity=n
            emit('reserve','m->capacidad = nueva_capacidad;','assignment',grow)
    emit('reserve','return true;' if success else 'return false;','return',lambda:leave(success),result=success,occurrence=0 if enough else -1)
    emit('insert',guard,'condition',condition=not success,expression='!'+str(success).lower())
    if success:
        def store():
            nonlocal written
            obj()['cells'][quantity].update(initialized=True,value=value);written=quantity+1
        emit('insert','m->datos[m->cantidad] = valor;','assignment',store,indices=[quantity],note=f'Escribe {value} en {reference}[{quantity}]. La celda queda inicializada, pero cantidad aun es {quantity}.')
        emit('insert','heapify_up(m, m->cantidad);','call')
        i=quantity;p=int((i-1)/2);emit('up','static void heapify_up(MonticuloBinario *m, int indice) {','enter',lambda:enter('up',{'m':'M1','indice':i}));up=frames[-1]
        emit('up','int padre = (indice - 1) / 2;','assignment',lambda:up['locals'].update(padre=p),note='Division entera C trunca hacia cero: para indice 0, (-1)/2 es 0. No se lee datos[-1].')
        loop='while (indice > 0 && comparar(m->tipo, m->datos[indice], m->datos[padre])) {'
        while True:
            cmp=False
            if i>0:
                a=values()[i];b=values()[p];emit('up',loop,'call',indices=[i,p])
                emit('compare','static bool comparar(TipoMonticulo tipo, int a, int b) {','enter',lambda:enter('compare',{'tipo':0,'a':a,'b':b}))
                emit('compare','if (tipo == MONTICULO_MIN) {','condition',condition=True,expression='0 == MONTICULO_MIN')
                cmp=a<b;emit('compare','return a < b;','return',lambda:leave(cmp),result=cmp)
            emit('up',loop,'condition',condition=i>0 and cmp,expression=f'{i} > 0'+(' && '+str(cmp).lower()+' [retorno de comparar]' if i>0 else ' [cortocircuito; comparar no se llama]'))
            if not (i>0 and cmp):break
            swapcall='intercambiar(&m->datos[indice], &m->datos[padre]);';emit('up',swapcall,'call')
            emit('swap','static void intercambiar(int *a, int *b) {','enter',lambda:enter('swap',{'a':f'&{reference}[{i}]','b':f'&{reference}[{p}]'}));swap=frames[-1];temp=values()[i]
            emit('swap','int temp = *a;','assignment',lambda:swap['locals'].update(temp=temp),indices=[i])
            emit('swap','*a = *b;','assignment',lambda:obj()['cells'][i].update(value=values()[p]),indices=[i,p],note='Lee *b y escribe *a. Temporalmente ambas celdas contienen el mismo entero; temp conserva el anterior *a.')
            emit('swap','*b = temp;','assignment',lambda:obj()['cells'][p].update(value=temp),indices=[p])
            emit('swap','}','return',leave)
            emit('up',swapcall,'resume')
            i=p;emit('up','indice = padre;','assignment',lambda:up['parameters'].update(indice=i))
            p=int((i-1)/2);emit('up','padre = (indice - 1) / 2;','assignment',lambda:up['locals'].update(padre=p))
        emit('up','}','return',leave)
        emit('insert','heapify_up(m, m->cantidad);','resume')
        def increment():
            nonlocal quantity
            quantity+=1
        emit('insert','m->cantidad++;','assignment',increment)
    emit('insert','return true;' if success else 'return false;','return',lambda:leave(success),result=success)
    emit('caller',call,'resume',lambda:caller['locals'].update(ok=success))
    emit('caller','return ok;','return',lambda:leave(success),result=success)
    steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    initial=deepcopy(steps[0]['pedagogy']);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={level:'Ninguna instruccion ejecutada: no hay nueva celda escrita, nueva reserva ni resultado booleano.' for level in ['basic','intermediate','advanced']};steps[0]['pedagogy']['initial_frame']=initial
    trace.update(source_code=source,steps=steps);return trace
