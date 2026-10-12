"""Three original Bubble consumers; reached C branches, operands and physical stores."""
from copy import deepcopy
import hashlib
from _sorting_source_oracle import assert_sorting_source_trace
SOURCE_SHA="e42e4dfd6930479aaf40b8d387e3abd92644f9baa3c632811e7aebc2945ab1c8"
ALLOWED=((3,1,2),(3,1,2,1),(2,1))

def _expected(values):
    a=list(values);n=len(a);pasada=j=flag=temp=None;aliases=None
    counts=dict(comparisons=0,swaps=0,moves=0);indices=flag_declared=swap_declared=False;stack=[];rows=[]
    def emit(token,function="ordenar_burbuja",condition=None):
        variables={}
        if stack:variables[("ordenar_burbuja","n")]=(n,True)
        if indices and stack:
            for name,value in [("pasada",pasada),("j",j)]:variables[("ordenar_burbuja",name)]=(value,value is not None)
        if flag_declared and stack:variables[("ordenar_burbuja","hubo_intercambio")]=(flag,flag is not None)
        if swap_declared:variables[("intercambiar","temporal")]=(temp,temp is not None)
        event=dict(token=token,function=function,pasada=pasada,j=j,hubo_intercambio=flag,temporal=temp,a=aliases[0] if aliases else None,b=aliases[1] if aliases else None,**counts)
        pointers=[] if aliases is None else [dict(name=name,target=f"arreglo[{index}]",index=index,value=a[index],type="int *",scope="intercambiar") for name,index in zip(("a","b"),aliases)]
        rows.append(dict(token=token,event=event,array=list(a),metrics=dict(counts),variables=variables,stack=list(stack),pointers=pointers,condition=condition,temporaries={} if temp is None or not swap_declared else {"temporal":temp}))
    emit("initial",None);stack=["ordenar_burbuja"];emit("sort_entry")
    indices=True;emit("sort_declare_indices");flag_declared=True;emit("sort_declare_flag");emit("valid_call")
    stack.append("arreglo_valido");emit("valid_entry","arreglo_valido");emit("valid_ptr","arreglo_valido",("arreglo != NULL",True));emit("valid_n","arreglo_valido",(f"{n} > 0",True));stack.pop();emit("valid_return","arreglo_valido");emit("sort_guard",condition=("!arreglo_valido(arreglo,n)",False))
    pasada=0;emit("outer_init")
    while True:
        entered=pasada+1<n;emit("outer_test",condition=(f"{pasada} + 1 < {n}",entered))
        if not entered:break
        flag=0;emit("flag_reset");j=0;emit("inner_init")
        while True:
            entered=j+1<n-pasada;emit("inner_test",condition=(f"{j} + 1 < {n} - {pasada}",entered))
            if not entered:break
            greater=a[j]>a[j+1];counts["comparisons"]+=1;emit("compare",condition=(f"{a[j]} > {a[j+1]}",greater))
            if greater:
                emit("swap_call");aliases=(j,j+1);stack.append("intercambiar");emit("swap_entry","intercambiar")
                swap_declared=True;emit("swap_declare","intercambiar");emit("swap_guard","intercambiar",("a == NULL || b == NULL",False))
                temp=a[j];counts["moves"]+=1;emit("swap_temp","intercambiar")
                a[j]=a[j+1];counts["moves"]+=1;emit("swap_assign_a","intercambiar")
                a[j+1]=temp;counts["moves"]+=1;counts["swaps"]+=1;emit("swap_assign_b","intercambiar")
                temp=None;aliases=None;swap_declared=False;stack.pop();emit("swap_return","intercambiar");emit("swap_resume")
                flag=1;emit("flag_set")
            j+=1;emit("inner_increment")
        stop=not flag;emit("stop_test",condition=(f"!{flag}",stop))
        if stop:emit("early_break");break
        emit("outer_complete");pasada+=1;emit("outer_increment")
    stack=[];emit("sort_return")
    return rows

def assert_bubble_canonical_consumer(body,values):
    assert tuple(values) in ALLOWED
    trace=body["execution_trace"];assert trace["structure_id"]=="sorting" and trace["operation_name"]=="burbuja" and trace["payload"]=={}
    assert hashlib.sha256(trace["source_code"].encode()).hexdigest()==SOURCE_SHA
    assert_sorting_source_trace(trace,list(values))
    expected=_expected(values);steps=trace["steps"];assert len(steps)==len(expected)
    for i,(s,want) in enumerate(zip(steps,expected)):
        p=s["pedagogy"];assert p["source"]["line_token"]==want["token"] and p["source"]["function"]==want["event"]["function"]
        assert s["debug"]["instruction_event"]==want["event"]
        if i:assert s["state_snapshot"]==steps[i-1]["state_after"]
        assert s["state_after"]["items"]==want["array"] and s["state_after"]["temporaries"]==want["temporaries"]
        assert {k:s["state_after"]["metrics"][k] for k in want["metrics"]}==want["metrics"]
        variables=p["variables"];keys=[(v["scope"],v["name"]) for v in variables];assert len(set(keys))==len(keys)
        assert {(v["scope"],v["name"]):(v["value"],v["initialized"]) for v in variables}==want["variables"]
        assert [f["function"] for f in p["call_stack"]]==want["stack"]
        for f in p["call_stack"]:
            if f["function"]=="ordenar_burbuja":assert f["parameters"]=={"arreglo":"arreglo del caller","n":len(values)}
            if f["function"]=="intercambiar":assert f["parameters"]=={"a":f'arreglo[{want["event"]["a"]}]',"b":f'arreglo[{want["event"]["b"]}]'}
        assert p["pointers"]==want["pointers"]
        condition=p["condition"]
        if want["condition"] is None:assert condition is None
        else:assert condition["expression"]==want["condition"][0] and condition["result"] is want["condition"][1]
    assert trace["final_state"]==body["visual_state"]==steps[-1]["state_after"]
    assert body["visual_state"]["items"]==sorted(values)
    return steps
