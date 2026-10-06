"""Exclusive instruction models of four retained List API methods; unchanged C contracts."""
from copy import deepcopy
import hashlib,re
from .pedagogy import build_sequential_frame,validate_sequential_frame,sequential_frame_schema,SEQUENTIAL_FRAME_SCHEMA_VERSION
FUNCTIONS={'eliminar_inicio': 'lista_eliminar_inicio', 'eliminar_final': 'lista_eliminar_final', 'mostrar': 'lista_mostrar', 'primero': 'lista_primero'}
EXPECTED_BODIES={'lista_eliminar_inicio': 'c2aff4347c9092b6fea7eb780057dc14a0f8767961d0168ef7991cb1cdb89590', 'lista_eliminar_final': '4e2eb2570ba43d590124edfc34b55edc8bac88422d3b754e55c05c200492dbed', 'lista_mostrar': '115e404ca421fad1391c51573b9c6d55079ba0016037f6e6f7aa0d5e638135bd', 'lista_primero': '382394394c74e1a820522b0ab9e202c04fa85554e1459d8841627f602bcb5350'}

def build_hidden_terminal_trace(*,operation_name,payload,source_code,code_title,before_state,after_state,success,message):
    fn=FUNCTIONS[operation_name];start=source_code.index(('void ' if fn=='lista_mostrar' else 'int ')+fn+'(')
    body=source_code[start:source_code.index('\n}',start)+2]
    if hashlib.sha256(' '.join(re.sub(r'/\*.*?\*/|//[^\n]*','',body,flags=re.S).split()).encode()).hexdigest()!=EXPECTED_BODIES[fn]:
        raise ValueError('List terminal C body changed: instruction model requires review')
    lines=source_code.splitlines();steps=[];deleting=operation_name.startswith('eliminar')
    trace=dict(structure_id='linked_list',operation_name=operation_name,payload=deepcopy(payload),success=success,
        mutates=deleting,message=message,source_code=source_code,code_title=code_title,steps=steps,
        final_state=deepcopy(after_state),hidden_terminal_instruction_model=True,
        pedagogy_schema_version=SEQUENTIAL_FRAME_SCHEMA_VERSION,pedagogy_schema=sequential_frame_schema())
    if not success:
        trace.update(execution_started=False,validation=dict(stage='API',accepted=False,message=message));return trace
    nodes=[dict(id=f'N{i+1}',value=n['value'],next=f'N{i+2}' if i+1<len(before_state['items']) else 'NULL') for i,n in enumerate(before_state['items'])]
    head=nodes[0]['id'] if nodes else 'NULL';args={'lista':'&cabeza' if deleting else head}
    if operation_name!='mostrar':args['valor']='&resultado'
    locals={};freed=[];output='sin inicializar';console=[];ended=False
    def node(ptr):return next(n for n in nodes if n['id']==ptr)
    def snapshot():
        reachable=[];p=head
        while p!='NULL':reachable.append(p);p=node(p)['next']
        state=deepcopy(before_state)
        # insert_model is the existing generic rich-node renderer switch, not a C operation claim.
        state.update(insert_model=True,search_model=not deleting,hidden_terminal_model=operation_name,
            head=head,lista='&cabeza' if ended else args['lista'],node_ids=reachable,items=[{'value':node(p)['value']} for p in reachable],
            size=len(reachable),empty=not reachable,heap_nodes=[dict(n,status='linked' if n['id'] in reachable else 'detached') for n in nodes],
            local_pointer_names=[n for n in locals if n!='i'],scope_ended=ended,output=output,free_count=len(freed),**deepcopy(locals))
        if freed:state['freed_p']=freed[-1];state['freed_nodes']=list(freed)
        return state
    last=snapshot()
    def emit(token,event='statement',condition=None,ret=None):
        nonlocal last,ended
        if event in {'return','scope_exit'}:ended=True
        index=next(i for i,l in enumerate(lines) if token in l) if token!='}' else next(i for i in range(start_line+1,len(lines)) if lines[i]=='}')
        after=snapshot();before=deepcopy(last)
        step=dict(step_index=len(steps),line_index=index,line_text=lines[index],function_name=fn,event_type=event,
            phase='end' if ended else 'start' if event=='entry' else 'progress',delay_ms=100,
            condition_result=condition,state_snapshot=before,state_after=after,console=list(console))
        frame=build_sequential_frame(structure_id='linked_list',operation_name=operation_name,payload=payload,step=step,success=True)
        scope='ended' if ended else 'active';ptrs=[];variables=[]
        for name,value in {**args,**locals}.items():
            ctype='int' if name=='i' else 'Tlista *' if name=='lista' and deleting else 'int *' if name=='valor' else 'Tlista'
            previous=before.get(name,args.get(name,'sin inicializar'));dangling=str(value).startswith('indeterminado (liberado')
            if ctype=='int':variables.append(dict(name=name,type=ctype,value=value,scope=fn,scope_state=scope,initialized=value!='sin inicializar',valid=True))
            else:ptrs.append(dict(name=name,type=ctype,target=value,previous_target=previous,changed=previous!=value,scope=fn,scope_state=scope,initialized=value!='sin inicializar',valid=not dangling and value!='sin inicializar',dangling=dangling,historical_id=freed[-1] if dangling else None))
        if operation_name!='mostrar':variables.append(dict(name='resultado',type='int',value=output,scope='caller',scope_state='active',initialized=output!='sin inicializar',valid=True))
        expression=None;substituted=None
        if condition is not None:
            expression=lines[index][lines[index].index('(')+1:lines[index].index(')')]
            if token.startswith('if (lista'):substituted=(f'&cabeza == NULL || {head} == NULL || &resultado == NULL' if deleting else f'{head} == NULL || &resultado == NULL')
            elif token.startswith('while (actual'):substituted=f"{locals['actual']}->sgte != NULL"
            elif token.startswith('while (aux'):substituted=f"{locals['aux']} != NULL"
            else:substituted=f"{locals['anterior']} == NULL"
        heap_before=before['heap_nodes'];heap_after=after['heap_nodes'];new_frees=[n['id'] for n in heap_before if n['id'] not in {v['id'] for v in heap_after}]
        frame.update(memory_state=deepcopy(after),concept=event,variables=variables,pointers=ptrs,
            heap_objects=deepcopy(heap_after),heap_transition=dict(kind='free' if new_frees else 'link' if before['head']!=after['head'] else 'stable',before=deepcopy(heap_before),after=deepcopy(heap_after),freed=new_frees,dangling_references=[]),
            call_stack=[] if ended else [dict(function=fn,parameters=deepcopy(args))],
            scopes=[dict(id=fn,kind='function',state=scope,variables=deepcopy({**args,**locals}))],
            condition=dict(source=expression,result=condition,substituted=substituted) if condition is not None else None)
        frame['source']['function']=fn;frame['narration']={level:token+('; termina el ambito; no se leen aliases liberados.' if ended else '') for level in ['basic','intermediate','advanced']}
        validate_sequential_frame(frame,source_code=source_code);step['pedagogy']=frame
        step['debug']=dict(head=head,locals=deepcopy(locals),output=output,return_value=ret,free_count=len(freed))
        steps.append(step);last=deepcopy(after)
    start_line=next(i for i,l in enumerate(lines) if (fn+'(') in l and l.strip().startswith(('int ','void ')))
    emit(('void ' if operation_name=='mostrar' else 'int ')+fn+'(','entry')
    if operation_name=='mostrar':
        locals['i']=1;emit('int i = 1;');locals['aux']=head;emit('Tlista aux = lista;')
        while True:
            present=locals['aux']!='NULL';emit('while (aux != NULL)','condition',present)
            if not present:break
            console.append(f" {locals['i']}) {node(locals['aux'])['value']}");emit('printf(')
            locals['aux']=node(locals['aux'])['next'];emit('aux = aux->sgte;');locals['i']+=1;emit('i++;')
        emit('}','scope_exit')
    else:
        if operation_name=='eliminar_inicio':locals['eliminado']='sin inicializar';emit('Tlista eliminado;')
        elif operation_name=='eliminar_final':locals.update(actual='sin inicializar',anterior='NULL');emit('Tlista actual, anterior = NULL;')
        emit('if (lista == NULL','condition',False)
        if operation_name=='primero':output=node(head)['value'];emit('*valor = lista->nro;')
        elif operation_name=='eliminar_inicio':
            locals['eliminado']=head;emit('eliminado = *lista;');output=node(locals['eliminado'])['value'];emit('*valor = eliminado->nro;')
            head=node(locals['eliminado'])['next'];emit('*lista = eliminado->sgte;')
            victim=locals['eliminado'];nodes[:]=[n for n in nodes if n['id']!=victim];freed.append(victim);locals['eliminado']='indeterminado (liberado '+victim+')';emit('free(eliminado);')
        else:
            locals['actual']=head;emit('actual = *lista;')
            while True:
                more=node(locals['actual'])['next']!='NULL';emit('while (actual->sgte','condition',more)
                if not more:break
                locals['anterior']=locals['actual'];locals['actual']=node(locals['actual'])['next'];emit('while (actual->sgte','statement')
            output=node(locals['actual'])['value'];emit('*valor = actual->nro;');first=locals['anterior']=='NULL';emit('if (anterior == NULL)','condition',first)
            if first:head='NULL'
            else:node(locals['anterior'])['next']='NULL'
            emit('if (anterior == NULL)','statement');victim=locals['actual'];nodes[:]=[n for n in nodes if n['id']!=victim];freed.append(victim);locals['actual']='indeterminado (liberado '+victim+')';emit('free(actual);')
        emit('return 1;','return',ret=1)
    assert after_state['items']==steps[-1]['pedagogy']['memory_state']['items'],'C model/API terminal disagreement'
    steps[-1]['state_after']=deepcopy(after_state)
    return trace
