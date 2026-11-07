"""Original all-visible Hash consumer: strict C mapping plus explicit recreation caller."""
import hashlib
CREATE_SHA="918b415b10bde5aa826a95584ee74bea9145945e01a96d93f82a47b71316bfa5"
def assert_hash_visible_contract(result):
    trace=result.get("execution_trace");assert isinstance(trace,dict)
    source=trace.get("source_code");assert isinstance(source,str)
    steps=trace.get("steps");assert isinstance(steps,list) and steps
    assert trace["final_state"]==result["visual_state"]
    lines=source.replace("\r\n","\n").split("\n")
    boundaries=[]
    for i,s in enumerate(steps):
        index=s.get("line_index");text=s.get("line_text")
        assert type(index) is int and isinstance(text,str)
        assert isinstance(s.get("state_snapshot"),dict) and isinstance(s.get("state_after"),dict)
        if index>=0:
            assert index<len(lines) and lines[index].strip()==text.strip()
            assert s.get("event_type")!="caller_recreate"
        else:
            boundaries.append(i)
            assert index==-1 and i==0 and trace["operation_name"]=="create_table"
            assert result["success"] is True and text=="" and s["phase"]=="start"
            assert hashlib.sha256(source.encode()).hexdigest()==CREATE_SHA
            assert s["step_index"]==0 and s["event_type"]=="caller_recreate"
            assert s["instruction_event"]=={"token":"caller_recreate","function":"caller","condition":None}
            debug=s["debug"];ped=s["pedagogy"];memory=ped["memory"]
            assert debug["token"]=="caller_recreate" and debug["function"]=="caller"
            assert ped["source"]=={"line_index":-1,"line_text":"","function":"caller"}
            before=s["state_snapshot"];after=s["state_after"]
            old_objects=[entry for bucket in before["buckets"] for entry in bucket["entries"]]
            expected_freed=[entry["address"] for entry in old_objects]+(["bucket-array"] if before["metadata"]["capacity"] else [])
            assert len(expected_freed)==len(set(expected_freed))
            assert debug["freed"]==expected_freed and memory["freed"]==expected_freed
            assert after["buckets"]==[] and after["metadata"]["capacity"]==after["metadata"]["size"]==0
            assert after["metadata"]["capacity_policy"]=="fixed"
            assert debug["root"]=={"capacity":0,"size":0,"bucket_pointer":None}
            assert debug["heap"]==memory["heap"]==[]
            assert debug["call_stack"]==memory["call_stack"]==[] and debug["scopes"]==memory["scopes"]==[]
            assert debug["variables"]==memory["variables"]=={}
            assert debug["allocated"]==memory["allocated"]==[] and memory["objects_after"]==[]
            assert memory["bucket_array_is_null"] is True
            assert memory["struct_fields"]=={"tabla":{"identity":"&tabla","capacidad":0,"cantidad":0,"buckets":None}}
            for field in ("allocation_attempts","allocations","comparisons","hash_calls","link_writes","value_writes","key_writes","count_writes"):assert debug[field]==0
            assert debug["bucket_initialization"]==memory["bucket_initialization"]==[]
            assert s["console"]==[]
            assert steps[1]["event_type"]=="init_entry" and steps[1]["debug"]["function"]=="th_inicializar"
            assert steps[1]["debug"]["freed"]==[] and steps[1]["state_snapshot"]==after
    assert boundaries==([0] if trace["operation_name"]=="create_table" else [])


# Ordinary visible callers are separately checked against their exact C source.
# The original historical TAD/recreation consumer above remains unchanged.
_CALLER_SOURCE_SHA = {'create_table': '2a30c27f3de3d4269adbad2592637b14441a1b911cab0256102dbc7d2b12c740', 'insert': '7bc68cfd8923c29ddcefbef73e17339722db70b1dc23c72a2ed97cfa96cf3a98', 'get': '3ea44c93541b3d43b783809272208d79f82f41dcdceae50731d73d0d1ee1b513', 'contains': '4a0a1f46c5ba4694232f8672966735e2c0c4ea7287b2318a78f4c4bebaaf4a96', 'remove': '1846c0f9a5607723479cf46d2f17e0988283e5fbf92702e969b3c87385c425c9', 'stats': 'b3696b96c9b83d3736568806426a6c883cb701d4f332c0e122499a1c96d7bdeb', 'keys': 'd832d74f0d0e51e578e197141596625f99af69a05e067a25ac392470ab3211a3', 'values': 'f640a92057fbcfb27e53b523e8182c80cc57c1ebb0dc26d9e0caf4730c284497', 'items': '0e90dffae8c70bd7506226fa32be5f7f574e0c3077c1c165bdb29797ebeee5ac'}
_RETURN_TOKENS = {'create_table':'init_return','insert':'insert_return',
                  'get':'search_return','contains':'contains_return','remove':'remove_return',
                  'stats':'formatter_return','keys':'formatter_return',
                  'values':'formatter_return','items':'formatter_return'}

def assert_hash_current_visible_contract(result):
    """Check caller structure/continuity, then every original TAD obligation.

    Independent native C17 tests validate formatted output bytes and cardinality;
    this consumer alone is not an independent printf formatting oracle.
    """
    from copy import deepcopy
    trace=result['execution_trace'];steps=trace['steps'];operation=trace['operation_name']
    diagnostic=trace.get('payload',{}).get('simulate_allocation_failure') in (True,'true','1',1)
    positions=[i for i,step in enumerate(steps) if step.get('event_type')=='caller_printf']
    if positions:
        assert not diagnostic
        first=positions[0]
        assert first>0 and positions==list(range(first,len(steps)))
        assert operation in _CALLER_SOURCE_SHA
        caller_source=trace['caller_source_code']
        assert hashlib.sha256(caller_source.encode()).hexdigest()==_CALLER_SOURCE_SHA[operation]
        assert steps[first-1]['debug']['token']==_RETURN_TOKENS[operation]
        caller_lines={line.strip() for line in caller_source.splitlines() if line.strip().startswith('printf(')}
        stdout=''
        for i in positions:
            step=steps[i];event=step['instruction_event'];line=event['caller_line_text']
            assert step['line_index']==-1 and step['line_text']=='' and step['step_index']==i
            assert event=={'token':'caller_printf','function':'main','source_role':'caller',
                           'C_executed':True,'caller_line_text':line}
            assert line in caller_lines
            assert step['debug']['token']=='caller_printf' and step['debug']['function']=='main'
            assert step['debug']['caller_line_text']==line and step['debug']['source_role']=='caller'
            assert step['pedagogy']['source']=={'line_index':None,'line_text':line,'function':'main','source_role':'caller'}
            assert step['state_snapshot']==step['state_after']==steps[i-1]['state_after']
            assert step['pedagogy']['state_before']==step['state_snapshot']
            assert step['pedagogy']['state_after']==step['state_after']
            caller_fields={'token','function','caller_line_text','source_role','caller_variables'}
            assert {key:value for key,value in step['debug'].items() if key not in caller_fields} == {key:value for key,value in steps[first-1]['debug'].items() if key not in caller_fields}
            assert step['pedagogy'].get('memory')==steps[first-1]['pedagogy'].get('memory')
            assert len(step['console'])==1 and isinstance(step['console'][0],str) and step['console'][0]
            stdout+=step['console'][0]
            assert step['console_stdout']==stdout
        assert trace['console_stdout']==result['console_stdout']==stdout
        assert all(not step['console'] and step['console_stdout']=='' for step in steps[:first])
    else:
        first=len(steps)
        assert diagnostic or steps[-1].get('debug',{}).get('token')!=_RETURN_TOKENS.get(operation)
        assert trace.get('console_stdout','')==result.get('console_stdout','')==''
        assert all(not step['console'] and step['console_stdout']=='' for step in steps)
    original=deepcopy(result)
    original['execution_trace']['steps']=original['execution_trace']['steps'][:first]
    assert_hash_visible_contract(original)
