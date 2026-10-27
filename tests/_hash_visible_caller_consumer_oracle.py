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
