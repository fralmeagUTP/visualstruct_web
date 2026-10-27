"""Borrowed lista_ultimo instruction model; unchanged C body and API result."""
from copy import deepcopy
from .pedagogy import build_sequential_frame, validate_sequential_frame, sequential_frame_schema, SEQUENTIAL_FRAME_SCHEMA_VERSION
import hashlib,re
EXPECTED_BODY = 'a39a4fb2454630be774bfa17a53941a64b3a85ac2fe5b29af59ad01666f881b5'

def build_linked_last_trace(*,payload,source_code,code_title,before_state,after_state,success,message):
    body=source_code[source_code.index('int lista_ultimo('):];body=body[:body.index('\n}')+2]
    normalized=' '.join(re.sub(r'/\*.*?\*/|//[^\n]*','',body,flags=re.S).split())
    if hashlib.sha256(normalized.encode()).hexdigest()!=EXPECTED_BODY:
        raise ValueError('lista_ultimo C changed: review instruction model')
    lines=source_code.splitlines();steps=[]
    trace=dict(structure_id='linked_list',operation_name='ultimo',payload=deepcopy(payload),success=success,
        mutates=False,message=message,source_code=source_code,code_title=code_title,steps=steps,
        final_state=deepcopy(after_state),pedagogy_schema_version=SEQUENTIAL_FRAME_SCHEMA_VERSION,
        pedagogy_schema=sequential_frame_schema(),linked_last_instruction_model=True)
    if not success:
        trace.update(execution_started=False,validation=dict(stage='API',accepted=False,message=message));return trace
    nodes=[dict(id=f'N{i+1}',value=x['value'],next=f'N{i+2}' if i+1<len(before_state['items']) else 'NULL') for i,x in enumerate(before_state['items'])]
    head=nodes[0]['id'] if nodes else 'NULL';current=head;output='sin inicializar'
    def snapshot():
        state=deepcopy(before_state);state.update(head=head,node_ids=[n['id'] for n in nodes],heap_nodes=deepcopy(nodes),lista=current,valor='&resultado',output=output,local_pointer_names=['lista','valor']);return state
    last=snapshot()
    def emit(token,event,condition=None,ret=None):
        nonlocal last
        idx=next(i for i,l in enumerate(lines) if token in l);state=snapshot()
        step=dict(step_index=len(steps),line_index=idx,line_text=lines[idx],function_name='lista_ultimo',event_type=event,
            phase='end' if event=='return' else 'start' if event=='entry' else 'progress',delay_ms=100,
            condition_result=condition,state_snapshot=deepcopy(last),state_after=state,console=[])
        frame=build_sequential_frame(structure_id='linked_list',operation_name='ultimo',payload=payload,step=step,success=success)
        ended=event=='return';scope='ended' if ended else 'active'
        frame.update(memory_state=deepcopy(state),concept=event,heap_objects=deepcopy(nodes),
            variables=[dict(name='resultado',type='int',value=output,initialized=output!='sin inicializar',scope='caller',scope_state='active',valid=True)],
            pointers=[dict(name=n,type=t,target=v,previous_target=last.get(n,v),scope='lista_ultimo',scope_state=scope,changed=last.get(n,v)!=v,valid=True,dangling=False) for n,t,v in [('lista','Tlista',current),('valor','int *','&resultado')]],
            call_stack=[] if ended else [dict(function='lista_ultimo',parameters=dict(lista=current,valor='&resultado'))],
            scopes=[dict(id='lista_ultimo',kind='function',state=scope,variables=dict(lista=current,valor='&resultado'))],
            condition=dict(source=token,result=condition,substitution=f'{current}->sgte != NULL' if token.startswith('while') else f'{current} == NULL || &resultado == NULL') if condition is not None else None,
            heap_transition=dict(kind='stable',before=deepcopy(nodes),after=deepcopy(nodes),freed=[],dangling_references=[]))
        frame['source']['function']='lista_ultimo';frame['narration']={level:token for level in ['basic','intermediate','advanced']}
        validate_sequential_frame(frame,source_code=source_code);step['pedagogy']=frame
        step['debug']=dict(head=head,lista=current,output=output,return_value=ret);steps.append(step);last=deepcopy(state)
    emit('int lista_ultimo(','entry')
    invalid=current=='NULL';emit('if (lista == NULL','condition',invalid)
    if invalid:emit('if (lista == NULL','return',ret=0)
    else:
        while True:
            node=next(n for n in nodes if n['id']==current);more=node['next']!='NULL'
            emit('while (lista->sgte','condition',more)
            if not more:break
            current=node['next'];emit('while (lista->sgte','statement')
        output=node['value'];emit('*valor = lista->nro;','statement');emit('return 1;','return',ret=1)
    steps[-1]['state_after']=deepcopy(after_state)
    return trace
