"""The actual iterative ABB extrema functions: one scope, borrowed return."""
from copy import deepcopy
from .pedagogy import build_hierarchical_frame, validate_hierarchical_frame


def build_abb_extreme_trace(trace, before_state, after_state):
    op=trace['operation_name'];assert op in {'minimo','maximo'}
    fn='abb_encontrarMinimo' if op=='minimo' else 'abb_encontrarMaximo'
    source=trace['source_code'];lines=source.splitlines();heap=[];frames=[];steps=[];returned=None
    def load(n):
        if n is None:return 'NULL'
        identity='N'+str(len(heap)+1);item={'id':identity,'value':n['value'],'left':'NULL','right':'NULL','status':'linked'};heap.append(item)
        item['left'],item['right']=load(n['left']),load(n['right']);return identity
    head=load(before_state.get('root'))
    def node(identity):return next(n for n in heap if n['id']==identity)
    def snap():
        state=deepcopy(before_state);state.update(abb_read_model=True,head=head,heap_nodes=deepcopy(heap),tree_frames=deepcopy(frames),caller_frame=None,returned=returned,console_stdout='');return state
    f={'id':'F1','function':fn,'depth':0,'parameters':{'nodo':head},'locals':{}}
    def emit(text,phase,mutate=None,condition=None,expression=None):
        old=snap()
        if mutate:mutate()
        new=snap();idx=next(i for i,l in enumerate(lines) if l.strip()==text)
        step={'step_index':len(steps),'line_index':idx,'line_text':lines[idx],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':old,'state_after':new,'debug':{'stage':phase}}
        if phase=='condition':step['condition_result']=condition
        ped=build_hierarchical_frame(structure_id='abb',operation_name=op,payload=trace['payload'],step=step,source_lines=lines,success=True)
        ped['concept']='compare' if phase=='condition' else 'return' if phase=='return' else 'assignment';ped['case']=phase;ped['phase']={'id':op+'-'+phase,'label':phase.title(),'goal':text};ped['condition']=None
        if phase=='condition':ped['condition']={'source':text,'substituted':expression,'result':condition,'consequence':'continuar cuerpo' if condition else 'salir; cortocircuito si nodo es NULL'};ped['executed_branch']='cuerpo' if condition else 'salida'
        a=old['tree_frames'][0]['parameters']['nodo'] if old['tree_frames'] else 'fuera de ámbito';b=new['tree_frames'][0]['parameters']['nodo'] if new['tree_frames'] else 'fuera de ámbito'
        ped['variables']=[{'name':'nodo','scope':fn+'#F1','frame_id':'F1','type':'ABBNodo *','previous':a,'value':b,'changed':a!=b,'meaning':'Unico parametro local por valor; cambiar su alias no cambia la raiz ni los enlaces.'}]
        shown=old['tree_frames'] if phase=='return' else new['tree_frames']
        ped['call_stack']=[{'function':fn,'frame_id':'F1','depth':0,'parameters':deepcopy(x['parameters']),'locals':{},'local_root':x['parameters']['nodo'],'local_root_address':x['parameters']['nodo'],'return':returned if phase=='return' else None,'continuation':'un solo ambito iterativo; el retorno es un alias prestado, no una reserva nueva'} for x in shown]
        objects=[{'id':n['id'],'address':n['id'],'symbolic_identity':True,'value':n['value'],'left':n['left'],'right':n['right'],'allocated':True,'freed':False} for n in heap]
        ped['memory']={'event':'none','objects_before':deepcopy(objects),'objects_after':deepcopy(objects),'allocated_objects':[],'freed_objects':[],'dangling_references':[],'stable_addresses':True,'symbolic_identities':True}
        explanation={'enter':'Entra una unica invocacion. nodo es un parametro por valor; el llamador conserva su raiz.','condition':'Evalua la condicion real del C. En &&, si nodo es NULL no evalua nodo->derecho. No cambia el arbol.','assignment':'El while cambia solo el alias local nodo al hijo indicado. Es la misma invocacion; no crea una pila recursiva ni escribe enlaces.','return':'Retorna NULL o el puntero prestado a una reserva ya existente. Termina el unico ambito sin liberar memoria ni cambiar la raiz.'}[phase]
        ped['narration']={level:explanation for level in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase=='return','value':returned if phase=='return' else None,'reconnects_subtree':False};ped['state_before']=deepcopy(old);ped['state_after']=deepcopy(new);ped['memory_state']=deepcopy(new);ped['instruction_event']={'phase':phase,'frame_id':'F1','condition':condition,'return':returned if phase=='return' else None}
        ped['invariant'].update(explanation='El recorrido iterativo conserva todas las identidades y enlaces. El alias prestado retornado pertenece al arbol del llamador.',holds=True,symbol='✓');validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
    emit('ABBNodo* '+fn+'(ABBNodo* nodo) {','enter',lambda:frames.append(f))
    cursor=head
    if op=='minimo':emit('if (nodo == NULL) {','condition',condition=cursor=='NULL',expression='if ('+cursor+' == NULL)')
    if not (op=='minimo' and cursor=='NULL'):
        side='left' if op=='minimo' else 'right';field='izquierdo' if op=='minimo' else 'derecho'
        while True:
            child=node(cursor)[side] if cursor!='NULL' else None
            condition=cursor!='NULL' and child!='NULL'
            text='while (nodo->izquierdo != NULL)' if op=='minimo' else 'while (nodo != NULL && nodo->derecho != NULL)'
            expression='while ('+str(child)+' != NULL)' if op=='minimo' else ('while (NULL != NULL && nodo->derecho != NULL) [segundo operando no evaluado]' if cursor=='NULL' else 'while ('+cursor+' != NULL && '+child+' != NULL)')
            emit(text,'condition',condition=condition,expression=expression)
            if not condition:break
            cursor=child
            emit('nodo = nodo->'+field+';','assignment',lambda:f['parameters'].update(nodo=cursor))
    def leave():
        nonlocal returned
        returned=cursor;frames.pop()
    emit('return NULL;' if op=='minimo' and cursor=='NULL' else 'return nodo;','return',leave)
    steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    initial=deepcopy(steps[0]['pedagogy']);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={level:'Ninguna instruccion ejecutada; sin parametros ni retorno futuros.' for level in ['basic','intermediate','advanced']};steps[0]['pedagogy']['initial_frame']=initial
    trace.update(steps=steps);return trace
