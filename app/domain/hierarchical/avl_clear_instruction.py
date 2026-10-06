"""AVL clear: historical object identities survive as records, never usable pointers.

The highlighted instruction is at the recorded event boundary: entry to a call
suspends the parent; a later return event completes that same expression.
"""
from copy import deepcopy
from .pedagogy import build_hierarchical_frame, validate_hierarchical_frame


def build_avl_clear_trace(trace, before_state, after_state):
    source=trace['source_code'].rstrip()
    heap=[];frames=[];history=[];steps=[];caller=None;returned=None;caller_root_cleared=False;retired=[];live=set()
    def load(n,parent='NULL'):
        if n is None:return 'NULL'
        identity='N'+str(len(heap)+1);item={'id':identity,'value':n['value'],'left':'NULL','right':'NULL','status':'linked','parent':parent,'balance_factor':n['balance_factor']};heap.append(item)
        item['left'],item['right']=load(n['left'],identity),load(n['right'],identity);return identity
    head=load(before_state.get('root'));live.update(n['id'] for n in heap)
    def node(identity):return next(n for n in heap if n['id']==identity)
    def reference(identity):return identity if identity=='NULL' or identity in live else identity+' [valor indeterminado; identidad historica]'
    def projection(identity):
        if identity not in live:return None
        n=node(identity);left,right=projection(n['left']),projection(n['right']);return {'value':n['value'],'left':left,'right':right,'balance_factor':n['balance_factor'],'height':1+max(left['height'] if left else 0,right['height'] if right else 0)}
    # Breadth-first insertion reconstructs these valid initial AVL fixtures without
    # observing preparation as part of freeing. Native caller checks verify it.
    queue=[before_state.get('root')];values=[]
    while queue:
        n=queue.pop(0)
        if n is not None:values.append(n['value']);queue.extend([n['left'],n['right']])
    prep='\n'.join('    avl_insertar(&arbol, '+str(value)+');' for value in values)
    source+='\n\n/* Main equivalente: la preparacion ya ocurrio antes de esta traza. Se observan liberar, asignar NULL y retornar. */\nint main(void) {\n    AVL arbol = NULL;\n'+prep+'\n    avl_liberarAVL(arbol);\n    arbol = NULL;\n    return 0;\n}\n'
    lines=source.splitlines()
    def snapshot():
        state=deepcopy(before_state);active=deepcopy(frames)
        for f in active:f['parameters']['raiz']=reference(f['identity'])
        current=[{**deepcopy(n),'left':reference(n['left']),'right':reference(n['right']),'parent':reference(n['parent'])} for n in heap if n['id'] in live]
        call=None if caller is None else {'function':'main','parameters':{},'locals':{'arbol':reference(head)},'description':'arbol (AVL): '+reference(head)+'; asignacion NULL '+('completada' if caller_root_cleared else 'pendiente')+'. No se lee un valor indeterminado.'}
        state.update(abb_read_model=True,avl_read_model=True,abb_clear_model=True,avl_clear_model=True,head=reference(head),head_identity=head,heap_nodes=current,freed_nodes=deepcopy(retired),tree_frames=active,caller_frame=call,returned=returned,caller_root_cleared=caller_root_cleared,console_stdout='',root=projection(head),size=len(live),live_visual_projection=True)
        def height(n):return 0 if n is None else 1+max(height(n['left']),height(n['right']))
        def traversal(n,order):
            if n is None:return []
            left,right=traversal(n['left'],order),traversal(n['right'],order)
            return [n['value']]+left+right if order=='preorden' else left+right+[n['value']] if order=='postorden' else left+[n['value']]+right
        # Derived view metrics describe the live-object projection, not calls
        # to C height/traversal routines through unusable pointers.
        state.update(empty=state['root'] is None,height=height(state['root']),traversals={order:traversal(state['root'],order) for order in ['inorden','preorden','postorden']})
        if retired and head!='NULL':state['validation']=None
        return state
    def index(text):return next(i for i,l in enumerate(lines) if l.strip()==text)
    def emit(text,phase,mutate=None,condition=None,expression=None,result=None):
        old=snapshot();owner=frames[-1]['id'] if frames else 'caller'
        if mutate:mutate()
        new=snapshot();owner=new['tree_frames'][-1]['id'] if phase=='enter' else owner;idx=index(text);step={'step_index':len(steps),'line_index':idx,'line_text':lines[idx],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':old,'state_after':new,'debug':{'stage':phase}}
        if phase=='condition':step['condition_result']=condition
        ped=build_hierarchical_frame(structure_id='avl',operation_name='limpiar',payload=trace['payload'],step=step,source_lines=lines,success=True)
        ped['concept']='free' if phase=='free' else 'assignment' if phase=='caller_assign' else 'compare' if phase=='condition' else 'return' if phase in {'return','caller_exit'} else 'descend';ped['case']=phase;ped['phase']={'id':'limpiar-'+phase,'label':phase.title(),'goal':text};ped['condition']=None
        if phase=='condition':ped['condition']={'source':text,'substituted':expression,'result':condition,'consequence':'rama registrada con los valores de esta invocacion'};ped['executed_branch']='retornar void' if condition else 'seguir con los hijos'
        previous={(f['id'],name):value for f in old['tree_frames'] for name,value in {**f['parameters'],**f['locals']}.items()};current={(f['id'],name):value for f in new['tree_frames'] for name,value in {**f['parameters'],**f['locals']}.items()}
        variables=[]
        if old['caller_frame'] or new['caller_frame']:
            variables.append({'name':'arbol','scope':'main','frame_id':'caller','type':'AVL','previous':old['head'] if old['caller_frame'] else 'fuera de ámbito','value':new['head'] if new['caller_frame'] else 'fuera de ámbito','changed':old['head']!=new['head'] or bool(old['caller_frame'])!=bool(new['caller_frame']),'meaning':'Local arbol del main: su referente puede terminar sin asignacion; el valor indeterminado se representa con identidad guardada, nunca se lee. NULL se asigna solo en su propia instruccion.'})
        for f in history:
            for name in ['raiz']:
                key=(f['id'],name)
                if key not in previous and key not in current:continue
                a=previous.get(key,'fuera de ámbito');b=current.get(key,'fuera de ámbito')
                variables.append({'name':name,'scope':'avl_liberarAVL#'+f['id'],'frame_id':f['id'],'type':'AVL' if name=='raiz' else 'int','previous':a,'value':b,'changed':a!=b,'meaning':'Parametro por valor; tras terminar su referente se muestra identidad historica, sin leer el valor indeterminado. Invocacion '+f['id']+'; los llamadores suspendidos conservan sus propios parametros.'})
        ped['variables']=variables
        shown=old['tree_frames'] if phase=='return' else new['tree_frames'];stack=[]
        if old['caller_frame'] or new['caller_frame']:stack.append({'function':'main','frame_id':'caller','depth':-1,'parameters':{},'locals':{'arbol':new['head'] if new['caller_frame'] else old['head']},'local_root':new['head'] if new['caller_frame'] else old['head'],'local_root_address':new['head'] if new['caller_frame'] else old['head'],'return':0 if phase=='caller_exit' else None,'continuation':'Despues de avl_liberarAVL(arbol), asignar arbol=NULL sin leer el valor indeterminado; no se retorna un raiz.'})
        for f in shown:stack.append({'function':'avl_liberarAVL','frame_id':f['id'],'depth':f['depth'],'parameters':deepcopy(f['parameters']),'locals':deepcopy(f['locals']),'local_root':f['parameters']['raiz'],'local_root_address':f['parameters']['raiz'],'return':'void' if phase=='return' and f['id']==owner else None,'continuation':'retorno void de esta invocacion; los parametros de los padres conservan sus registros de identidad'})
        for entry in stack:
            if (phase=='return' and entry['frame_id']==owner) or (phase=='caller_exit' and entry['frame_id']=='caller'):
                entry['scope_status']='terminado (contexto del retorno)'
                entry['continuation']='Retorno completado: ambito terminado. Sus parametros son el contexto de la instruccion, no variables vivas despues del paso.'
            else:
                entry['scope_status']='activo' if (new['tree_frames'] and entry['frame_id']==new['tree_frames'][-1]['id']) or (not new['tree_frames'] and entry['frame_id']=='caller') else 'suspendido'
        ped['call_stack']=stack
        def objects(state):return [{'id':n['id'],'address':n['id'],'symbolic_identity':True,'value':n['value'],'left':n['left'],'right':n['right'],'allocated':True,'freed':False,'parent':n['parent'],'balance_factor':n['balance_factor']} for n in state['heap_nodes']]
        records=[]
        if new['caller_frame'] and new['head_identity']!='NULL' and new['head_identity'] not in live:records.append({'kind':'caller','name':'arbol','identity':new['head_identity'],'usable':False,'historical_identity':True})
        for f in new['tree_frames']:
            if f['identity']!='NULL' and f['identity'] not in live:records.append({'kind':'parameter','frame':f['id'],'name':'raiz','identity':f['identity'],'usable':False,'historical_identity':True})
        for n in heap:
            if n['id'] in live:
                for side in ['left','right','parent']:
                    if n[side]!='NULL' and n[side] not in live:records.append({'kind':'field','object':n['id'],'name':side,'identity':n[side],'usable':False,'historical_identity':True})
        freed=[x for x in objects(old) if x['id'] not in {n['id'] for n in new['heap_nodes']}]
        ped['memory']={'event':'free' if phase=='free' else 'none','objects_before':objects(old),'objects_after':objects(new),'allocated_objects':[],'freed_objects':freed,'dangling_references':[],'unusable_reference_records':records,'retired_objects':deepcopy(new['freed_nodes']),'stable_addresses':True,'symbolic_identities':True,'records_are_not_pointer_values':True}
        descriptions={'caller_enter':'Se observa el local arbol del main, preparado por el historial previo, y comienza la llamada a liberar. La preparacion no se reejecuta en esta traza.','enter':'Entra una invocacion con raiz por valor; cada llamada, incluso NULL, tiene su propio ambito.','condition':'Evalua !raiz. NULL retorna void sin liberar; un raiz vivo sigue con sus hijos.','call':'Comienza la llamada al hijo usando un enlace de raiz aun vivo. El padre conserva su parametro por valor y queda suspendido mientras el hijo ejecuta.','resume':'El hijo termino. Continúa este padre: sus enlaces no se asignaron a NULL. Una identidad cuyo referente termino es un registro historico inutilizable, no un puntero que se pueda leer.','free':'free termina la vida de esta reserva despues de sus hijos. Se guardan identidad y datos previos sin acceder al objeto liberado. Los alias a esa reserva tienen valor indeterminado; no se asignan ficticiamente a NULL. El SVG muestra solo reservas vivas y las tarjetas anotan enlaces inutilizables.','return':'Retorna void y termina solo este ambito; no devuelve un raiz ni un puntero liberado.','caller_resume':'La liberacion completa termino, pero arbol no se asigno a NULL dentro del TAD. El main conserva un registro historico inutilizable hasta su siguiente asignacion.','caller_assign':'El main asigna NULL a arbol sin leer su valor anterior. En vacio esta instruccion ocurre aunque no cambie el dibujo; no libera memoria otra vez.','caller_exit':'El main retorna 0 despues de la liberacion y asignacion NULL. El ambito termina.'}
        ped['narration']={level:descriptions[phase] for level in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase in {'return','caller_exit'},'value':'void' if phase=='return' else result,'reconnects_subtree':False};ped['state_before']=deepcopy(old);ped['state_after']=deepcopy(new);ped['memory_state']=deepcopy(new);ped['instruction_event']={'phase':phase,'frame_id':owner,'condition':condition,'return':'void' if phase=='return' else result}
        ped['invariant'].update(name='Vida de reservas y referencias',evidence_by_node_or_path=[{'identity':n['id'],'live':True} for n in new['heap_nodes']]+[{'identity':n['id'],'live':False,'historical_record':True} for n in new['freed_nodes']],explanation='Invariante de vida: liberar hijos antes del padre y no usar reservas terminadas. La proyeccion de reservas vivas no afirma que el C haya escrito NULL en enlaces ni que el arbol parcial sea recorrible.',holds=True,symbol='✓');validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
    def rec(identity):
        f={'id':'F'+str(len(history)+1),'function':'avl_liberarAVL','depth':len(frames),'identity':identity,'parameters':{'raiz':identity},'locals':{}};history.append(f)
        emit('void avl_liberarAVL(AVL raiz) {','enter',lambda:frames.append(f))
        terminal=identity=='NULL';emit('if (!raiz)','condition',condition=terminal,expression='if (!'+reference(identity)+')')
        if terminal:text='return;'
        else:
            for side,field in [('left','izq'),('right','der')]:
                assert identity in live
                text='avl_liberarAVL(raiz->'+field+');';child=node(identity)[side]
                assert child=='NULL' or child in live
                emit(text,'call');rec(child);emit(text,'resume')
            def release():
                assert identity in live
                n=node(identity);retired.append({'id':identity,'value':n['value'],'left':reference(n['left']),'right':reference(n['right']),'parent':reference(n['parent']),'balance_factor':n['balance_factor'],'status':'freed','historical_identity':True,'contents_are_historical':True});live.remove(identity)
            emit('free(raiz);','free',release);text='}'
        def leave():
            nonlocal returned
            frames.pop();returned='void'
        emit(text,'return',leave,result='void')
    def enter_caller():
        nonlocal caller
        caller=True
    emit('avl_liberarAVL(arbol);','caller_enter',enter_caller);rec(head);emit('avl_liberarAVL(arbol);','caller_resume')
    def assign_null():
        nonlocal head,caller_root_cleared
        head='NULL';caller_root_cleared=True
    emit('arbol = NULL;','caller_assign',assign_null)
    def exit_caller():
        nonlocal caller
        caller=None
    emit('return 0;','caller_exit',exit_caller,result=0)
    steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    initial=deepcopy(steps[0]['pedagogy']);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={level:'Ninguna instruccion ejecutada; arbol inicial, sin parametros ni retorno futuros.' for level in ['basic','intermediate','advanced']};steps[0]['pedagogy']['initial_frame']=initial
    trace.update(source_code=source,steps=steps);return trace
