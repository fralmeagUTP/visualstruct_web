"""Observe the executed sequential renderer and its backend memory projection."""
OBSERVER = """() => {
    window.auditRenderedState=null; window.auditRenderEvent=null;
    for(const name of ['renderVisualState','renderStackPushState','renderStackCleanupState',
        'renderQueueDequeueState','renderQueueEnqueueState','renderQueueCleanupState',
        'renderPriorityQueueDequeueState','renderPriorityQueueEnqueueState','renderPriorityQueueCleanupState']) {
        const real=window[name]; if(typeof real!=='function') throw new Error('Missing renderer: '+name);
        window[name]=function(...args) {
            const generic=name==='renderVisualState';
            window.auditRenderedState=structuredClone(args[generic?1:0]);
            window.auditRenderEvent={renderer:name,state:window.auditRenderedState,
                memory:generic?null:structuredClone(args[1])};
            return real(...args);
        };
    }
}"""


def _assert_retained_singleton_dequeue_index(trace, cursor, family, projected, canonical):
    """One documented representation difference, not a general omitted key.

    At the successful final return of a singleton cp_desencolar, structural
    out_index becomes -1 while the closed-scope projection retains index 0
    identifying the one retired node. Require the exact preceding snapshot,
    ownership transition and copied outputs; every other mismatch still fails.
    """
    steps=trace['steps']
    assert family==trace['structure_id']=='priority_queue'
    assert trace['operation_name']=='desencolar' and cursor==len(steps)-1 and cursor>0
    step=steps[cursor]
    assert step['event_type']=='return' and step['function_name']=='cp_desencolar'
    assert step['line_text'].strip()=='return true;'
    assert type(canonical['out_index']) is int and canonical['out_index']==-1
    assert type(projected['out_index']) is int and projected['out_index']==0
    assert canonical['empty'] is True and canonical['size']==0 and canonical['items']==[]
    assert projected==step['state_snapshot']==steps[cursor-1]['state_after']
    initial=steps[0]['state_snapshot']
    assert initial['size']==1 and len(initial['items'])==1 and initial['out_index']==0
    memory=step['pedagogy']['dequeue_memory']
    first_memory=steps[0]['pedagogy']['dequeue_memory']
    assert memory['kind']=='priority_queue_dequeue' and memory['scope_state']=='ended'
    assert memory['result'] is True and memory['call_stack']==[] and memory['heap']==[]
    assert memory['root']=={**first_memory['root'],'front':None,'rear':None,'quantity':0}
    assert len(first_memory['heap'])==len(memory['retired'])==1
    original=first_memory['heap'][0];retired=memory['retired'][0]
    assert original['alive'] is True and original['freed'] is False
    assert retired['alive'] is False and retired['freed'] is True
    assert projected['objetivo']==retired['id']==original['id']
    assert first_memory['root']['front']==first_memory['root']['rear']==original['id']
    assert retired['historical_fields']==original['fields']
    item=initial['items'][0]
    assert original['fields']=={'valor':item['value'],'prioridad':item['priority'],'sgte':None}
    assert memory['outputs']=={'value':item['value'],'priority':item['priority'],
                               'value_written':True,'priority_written':True}


def assert_causal_render(event, trace, cursor, family):
    """Preserve exact projection AND independently require causal TAD contents.

    Memory projections retain retired identities/scope markers after the final
    structural snapshot drops them. They must not change reachable contents.
    The specialized renderers also receive the exact scoped memory record.
    """
    assert event is not None, 'The observer must have seen a real renderer call'
    step=trace['steps'][max(cursor,0)]
    canonical=step['state_snapshot'] if cursor<0 else step['state_after']
    before_sublist=family=='sublist' and cursor<0 and canonical.get('sublist_delete_model')
    expected=canonical if before_sublist else step['pedagogy'].get('memory_state') or canonical
    assert event['state']==expected, (family,cursor,event['renderer'])
    # Compare every canonical field, including roots, links, counts and flags.
    # Extra memory fields remain intact; they do not exempt shared fields.
    for key,value in canonical.items():
        assert key in event['state'], (family,cursor,'missing canonical field',key)
        if event['state'][key]!=value:
            assert key=='out_index', (family,cursor,key)
            _assert_retained_singleton_dequeue_index(trace,cursor,family,event['state'],canonical)
    choices={'stack':['push_memory','cleanup_memory'],
             'queue':['dequeue_memory','enqueue_memory','cleanup_memory'],
             'priority_queue':['dequeue_memory','enqueue_memory','cleanup_memory']}
    selected=next((key for key in choices.get(family,[]) if step['pedagogy'].get(key)),None)
    if selected:
        memory=step['pedagogy'][selected]
        suffix={'push_memory':'Push','enqueue_memory':'Enqueue','dequeue_memory':'Dequeue','cleanup_memory':'Cleanup'}[selected]
        prefix={'stack':'Stack','queue':'Queue','priority_queue':'PriorityQueue'}[family]
        assert event['renderer']=='render'+prefix+suffix+'State'
        if cursor<0:memory={**memory,'variables':[],'aux':None,'next':None,'call_stack':[]}
        assert event['memory']==memory, (family,cursor,'exact scoped memory')
    else:
        assert event['renderer']=='renderVisualState' and event['memory'] is None
    return expected
