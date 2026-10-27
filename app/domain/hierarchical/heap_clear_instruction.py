"""Executed C statements for visible Heap clear; allocation internals are opaque."""
from copy import deepcopy
from pathlib import Path
from app.services.c_code_service import CCodeService
from .pedagogy import build_hierarchical_frame,validate_hierarchical_frame


def heap_clear_source():
    raw=(Path(__file__).resolve().parents[3]/'docs/tads_C/tad_monticulo_binario.c').read_text(encoding='utf-8-sig')
    blocks={scope:CCodeService._extract_function_with_comment(raw,name) for scope,name in [('reserve','asegurar_capacidad'),('destroy','monticulo_destruir'),('init','monticulo_inicializar')]}
    blocks['caller']='''/**
 * @brief Limpia mediante destruccion y nueva inicializacion del monticulo visible.
 * @param m Monticulo prestado; su buffer previo termina su vida.
 * @note Equivale al llamador descargado MIN/16; no es una nueva API del TAD.
 * @note El retorno void no indica exito de reserva; observar capacidad y datos.
 */
void ejecutar_limpiar(MonticuloBinario *m) {
    monticulo_destruir(m);
    monticulo_inicializar(m, MONTICULO_MIN, 16);
}'''
    return '\n\n'.join(blocks.values())+'\n',blocks


def build_heap_clear_trace(trace,before_state,after_state):
    source,blocks=heap_clear_source();lines=source.splitlines();frames=[];steps=[]
    quantity=before_state['size'];capacity=before_state['capacity'];original=list(before_state['array'])
    allocated=capacity>0;reference='A1' if allocated else 'NULL';retired=[]
    objects=[{'id':'A1','capacity':capacity,'live':True,'cells':[{'index':i,'initialized':True if i<quantity else None,'value':original[i] if i<quantity else None} for i in range(capacity)]}] if allocated else []
    reserve_ok=after_state['capacity']>0;last_return=None
    names={'caller':'ejecutar_limpiar','destroy':'monticulo_destruir','init':'monticulo_inicializar','reserve':'asegurar_capacidad'}
    types={'m':'MonticuloBinario *','tipo':'TipoMonticulo','capacidad_inicial':'int','capacidad_objetivo':'int','nueva_capacidad':'int','nuevos_datos':'int *'}
    def snapshot():
        data=deepcopy(before_state);logical=original if reference=='A1' and any(o['id']=='A1' and o['live'] for o in objects) else []
        data.update(heap_query_model=True,heap_clear_model=True,query_operation='limpiar',query_frames=deepcopy(frames),array=list(logical),size=quantity,capacity=capacity,empty=quantity==0,root=None,console_stdout='',active_copy_index=None,heap_data_reference=reference,heap_allocations=deepcopy(objects),heap_retired=deepcopy(retired),last_return=deepcopy(last_return))
        # Existing heap renderer derives both views from array. No dereference of a dead/NULL buffer.
        return data
    def locate(scope,text,phase):
        start=source.index(blocks[scope]);base=source[:start].count('\n');local=blocks[scope].splitlines()
        if text=='}' and phase=='return':return base+len(local)-1
        indices=[i for i,l in enumerate(local) if l.strip()==text]
        return base+(indices[-1] if scope=='reserve' and text.startswith('return ') else indices[0])
    def enter(scope,parameters):frames.append({'id':scope,'function':names[scope],'parameters':parameters,'locals':{}})
    def leave(value=None):
        nonlocal last_return
        last_return={'function':frames[-1]['function'],'type':'bool' if frames[-1]['id']=='reserve' else 'void','value':value};frames.pop()
    def emit(scope,text,phase,mutate=None,condition=None,expression=None,result=None,note=None):
        previous=snapshot()
        if mutate:mutate()
        current=snapshot();idx=locate(scope,text,phase)
        step={'step_index':len(steps),'line_index':idx,'line_text':lines[idx],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':previous,'state_after':current,'debug':{'stage':phase}}
        if condition is not None:step['condition_result']=condition
        ped=build_hierarchical_frame(structure_id='binary_heap',operation_name='limpiar',payload=trace['payload'],step=step,source_lines=lines,success=trace['success'])
        ped.update(concept='compare' if condition is not None else 'return' if phase=='return' else 'free' if phase=='free' else 'allocation' if phase=='allocation' else 'assignment',case=phase,phase={'id':scope+'-'+phase,'label':phase.replace('_',' ').title(),'goal':text})
        ped['condition']={'source':text,'substituted':expression,'result':condition,'consequence':'cuerpo' if condition else 'salida/siguiente'} if condition is not None else None
        ped['executed_branch']=('cuerpo' if condition else 'salida/siguiente') if condition is not None else None
        old={f['id']:f for f in previous['query_frames']};new={f['id']:f for f in current['query_frames']};variables=[]
        for ident in dict.fromkeys([*old,*new]):
            a=old.get(ident,{});b=new.get(ident,{});prev={**a.get('parameters',{}),**a.get('locals',{})};now={**b.get('parameters',{}),**b.get('locals',{})}
            for name in dict.fromkeys([*prev,*now]):variables.append({'name':name,'frame_id':ident,'scope':names[ident]+'#'+ident,'type':types[name],'previous':prev.get(name,'fuera de ambito'),'value':now.get(name,'fuera de ambito'),'changed':prev.get(name)!=now.get(name),'meaning':'Local/parametro C real; sin inicializar hasta completar asignacion. Identidades simbolicas de vidas distintas.'})
        for name,typ,field in [('m->datos','int *','heap_data_reference'),('m->cantidad','int','size'),('m->capacidad','int','capacity')]:variables.append({'name':name,'frame_id':'external','scope':'M1 compartido','type':typ,'previous':previous[field],'value':current[field],'changed':previous[field]!=current[field],'meaning':'Campos reales de M1. Contadores pueden conservar valores hasta su asignacion; nunca se leen datos liberados.'})
        ped['variables']=variables;shown=previous['query_frames'] if phase=='return' else current['query_frames']
        ped['call_stack']=[{'function':f['function'],'frame_id':f['id'],'depth':i,'parameters':deepcopy(f['parameters']),'locals':deepcopy(f['locals']),'local_root':'M1','local_root_address':'M1','return':result if phase=='return' and i==len(shown)-1 else None,'scope_status':'terminado (contexto del retorno)' if phase=='return' and i==len(shown)-1 else 'suspendido' if i<len(shown)-1 else 'activo','continuation':'Retornar reanuda el llamador; void no es un estado de reserva.'} for i,f in enumerate(shown)]
        def memory(state):return [dict(o,address=o['id'],allocated=o['live'],freed=not o['live'],symbolic_identity=True) for o in state['heap_allocations']]
        ped['memory']={'event':phase if phase in {'free','allocation'} else 'none','objects_before':memory(previous),'objects_after':memory(current),'allocated_objects':[{'id':o['id'],'address':o['id']} for o in current['heap_allocations'] if o['live'] and not any(a['id']==o['id'] and a['live'] for a in previous['heap_allocations'])],'freed_objects':[{'id':o['id'],'address':o['id']} for o in previous['heap_allocations'] if o['live'] and not any(a['id']==o['id'] and a['live'] for a in current['heap_allocations'])],'dangling_references':[],'stable_addresses':False,'symbolic_identities':True,'historical_objects':deepcopy(retired)}
        ped['array'].update(active_index=None,parent_index=None)
        explanation=note or {'enter':'Entra un ambito con parametros por valor; todos los m designan M1.','declaration':'Declara un local sin inicializar, sin cambiar el monticulo.','call':'Llama al C real; el llamador queda suspendido hasta el retorno.','resume':'La llamada termina; void no representa true/false. No hay mutacion adicional.','condition':'Evalua la condicion real, respetando cortocircuito; no modifica memoria.','assignment':'Solo cambia el campo o local indicado por esta instruccion.','free':'Termina la vida de A1, incluso si cantidad es cero. datos queda indeterminado hasta la siguiente asignacion NULL. Valores previos son registros historicos, no memoria accesible.','allocation':'realloc(NULL, ...) devuelve una reserva independiente sin enteros inicializados. A2 es una nueva vida, aunque la direccion fisica se reutilice. Internos del asignador no se simulan.','return':'Termina el ambito. Retorno void no tiene valor; el bool privado controla la rama del inicializador.'}[phase]
        ped['narration']={level:explanation for level in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase=='return','value':result,'reconnects_subtree':False}
        ped.update(state_before=deepcopy(previous),state_after=deepcopy(current),memory_state=deepcopy(current),instruction_event={'scope':scope,'phase':phase,'condition':condition,'return':result})
        ped['invariant'].update(name='Estado intermedio de vida de memoria',holds=None,symbol='—',evidence_by_node_or_path=[],explanation='La vida y los campos cambian solo en la instruccion indicada. Durante free/NULL y la reinicializacion no se afirma un monticulo listo para operar. No hay borrado gradual ni lectura de memoria liberada.')
        validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
    emit('caller','void ejecutar_limpiar(MonticuloBinario *m) {','enter',lambda:enter('caller',{'m':'M1'}))
    emit('caller','monticulo_destruir(m);','call')
    emit('destroy','void monticulo_destruir(MonticuloBinario *m) {','enter',lambda:enter('destroy',{'m':'M1'}))
    emit('destroy','if (m != NULL) {','condition',condition=True,expression='M1 != NULL')
    emit('destroy','if (m->datos) {','condition',condition=allocated,expression='A1 != NULL' if allocated else 'NULL != NULL')
    if allocated:
        def release():
            nonlocal reference
            obj=objects[0];retired.append({'id':'A1','capacity':obj['capacity'],'cells':deepcopy(obj['cells']),'status':'registro previo a free; no memoria viva'});obj.update(live=False,cells=[]);reference='indeterminado (A1 historico)'
        emit('destroy','free(m->datos);','free',release)
        def nullify():
            nonlocal reference
            reference='NULL'
        emit('destroy','m->datos = NULL;','assignment',nullify)
    def set_quantity():
        nonlocal quantity
        quantity=0
    emit('destroy','m->cantidad = 0;','assignment',set_quantity)
    def set_capacity():
        nonlocal capacity
        capacity=0
    emit('destroy','m->capacidad = 0;','assignment',set_capacity)
    emit('destroy','}','return',leave)
    emit('caller','monticulo_destruir(m);','resume')
    emit('caller','monticulo_inicializar(m, MONTICULO_MIN, 16);','call')
    emit('init','void monticulo_inicializar(MonticuloBinario *m, TipoMonticulo tipo, int capacidad_inicial) {','enter',lambda:enter('init',{'m':'M1','tipo':0,'capacidad_inicial':16}));init=frames[-1]
    emit('init','int capacidad_objetivo;','declaration',lambda:init['locals'].update(capacidad_objetivo='sin inicializar'))
    emit('init','if (m == NULL) return;','condition',condition=False,expression='M1 == NULL')
    emit('init','m->tipo = tipo;','assignment',note='M1.tipo toma MONTICULO_MIN (0). No hay cambio de valores del arreglo.')
    emit('init','m->cantidad = 0;','assignment',set_quantity)
    emit('init','m->capacidad = 0;','assignment',set_capacity)
    def nullify():
        nonlocal reference
        reference='NULL'
    emit('init','m->datos = NULL;','assignment',nullify)
    emit('init','capacidad_objetivo = (capacidad_inicial > 0) ? capacidad_inicial : MONTICULO_CAPACIDAD_POR_DEFECTO;','assignment',lambda:init['locals'].update(capacidad_objetivo=16),condition=True,expression='16 > 0 ? 16 : 10')
    guard='if (!asegurar_capacidad(m, capacidad_objetivo)) {';emit('init',guard,'call')
    emit('reserve','static bool asegurar_capacidad(MonticuloBinario *m, int capacidad_objetivo) {','enter',lambda:enter('reserve',{'m':'M1','capacidad_objetivo':16}));reserve=frames[-1]
    emit('reserve','int nueva_capacidad;','declaration',lambda:reserve['locals'].update(nueva_capacidad='sin inicializar'))
    emit('reserve','int *nuevos_datos;','declaration',lambda:reserve['locals'].update(nuevos_datos='sin inicializar'))
    emit('reserve','if (m == NULL || capacidad_objetivo <= 0) {','condition',condition=False,expression='M1 == NULL || 16 <= 0')
    emit('reserve','if (m->capacidad >= capacidad_objetivo && m->datos != NULL) {','condition',condition=False,expression='0 >= 16 [cortocircuito; datos no se evalua]')
    emit('reserve','nueva_capacidad = (m->capacidad > 0) ? m->capacidad : MONTICULO_CAPACIDAD_POR_DEFECTO;','assignment',lambda:reserve['locals'].update(nueva_capacidad=10),condition=False,expression='0 > 0 ? 0 : 10')
    emit('reserve','while (nueva_capacidad < capacidad_objetivo) {','condition',condition=True,expression='10 < 16')
    emit('reserve','if (nueva_capacidad > INT_MAX / 2) {','condition',condition=False,expression='10 > INT_MAX / 2')
    emit('reserve','nueva_capacidad *= 2;','assignment',lambda:reserve['locals'].update(nueva_capacidad=20))
    emit('reserve','while (nueva_capacidad < capacidad_objetivo) {','condition',condition=False,expression='20 < 16')
    def allocate():
        reserve['locals']['nuevos_datos']='A2' if reserve_ok else 'NULL'
        if reserve_ok:objects.append({'id':'A2','capacity':20,'live':True,'cells':[{'index':i,'initialized':False,'value':None} for i in range(20)]})
    emit('reserve','nuevos_datos = (int *)realloc(m->datos, sizeof(int) * (size_t)nueva_capacidad);','allocation',allocate,note=None if reserve_ok else 'La reserva inyectada falla: realloc(NULL, ...) devuelve NULL. No existe A2 ni se publica un buffer; el monticulo queda vacio y capacidad 0.')
    emit('reserve','if (nuevos_datos == NULL) {','condition',condition=not reserve_ok,expression=('A2' if reserve_ok else 'NULL')+' == NULL')
    if reserve_ok:
        def publish():
            nonlocal reference
            reference='A2'
        emit('reserve','m->datos = nuevos_datos;','assignment',publish)
        def grow():
            nonlocal capacity
            capacity=20
        emit('reserve','m->capacidad = nueva_capacidad;','assignment',grow)
    emit('reserve','return true;' if reserve_ok else 'return false;','return',lambda:leave(reserve_ok),result=reserve_ok)
    emit('init',guard,'condition',condition=not reserve_ok,expression='!'+str(reserve_ok).lower())
    if not reserve_ok:emit('init','m->capacidad = 0;','assignment',set_capacity)
    emit('init','}','return',leave)
    emit('caller','monticulo_inicializar(m, MONTICULO_MIN, 16);','resume')
    emit('caller','}','return',leave)
    steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    initial=deepcopy(steps[0]['pedagogy']);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={level:'Ninguna instruccion ejecutada; buffer original vivo, sin liberacion ni reserva futura.' for level in ['basic','intermediate','advanced']};steps[0]['pedagogy']['initial_frame']=initial
    trace.update(source_code=source,steps=steps);return trace
