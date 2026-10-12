"""Causal raw-QuickSort contract for only the original [1,2,3] fixture."""
TOKENS="initial sort_entry valid_call valid_entry valid_ptr valid_n valid_return sort_guard rec_call rec_entry rec_init outer_test i_test i_increment i_test j_test j_decrement j_test cross_test swap_call swap_entry swap_declare swap_guard swap_temp swap_assign_a swap_assign_b swap_return swap_resume cross_i_increment cross_j_decrement outer_test left_test right_test rec_return rec_resume sort_return".split()

def assert_quicksort_comparison_consumer(result):
    steps=result["steps"]
    assert [s["line_token"] for s in steps]==TOKENS, "fixed reached C path including failed tests required"
    array=[1,2,3];ctx=dict(primero=None,ultimo=None,i=None,j=None,pivote=None,depth=0)
    counts=dict(comparisons=0,swaps=0,moves=0);evaluations=[];temporal=None
    for i,s in enumerate(steps):
        token=s["line_token"];event=s["instruction_event"]
        assert s["step"]==i+1 and event["token"]==token
        function=(None if token=="initial" else "arreglo_valido" if token in {"valid_entry","valid_ptr","valid_n","valid_return"} else "intercambiar" if token in {"swap_entry","swap_declare","swap_guard","swap_temp","swap_assign_a","swap_assign_b","swap_return"} else "ordenar_quicksort" if token in {"sort_entry","valid_call","sort_guard","rec_call","rec_resume","sort_return"} else "quicksort_recursivo")
        assert s["source_function"]==event["function"]==function
        if token=="rec_entry":ctx.update(primero=0,ultimo=2,depth=1)
        elif token=="rec_init":ctx.update(i=ctx["primero"],j=ctx["ultimo"],pivote=array[(ctx["primero"]+ctx["ultimo"])//2])
        elif token in {"i_increment","cross_i_increment"}:
            assert steps[i-1]["condition_result"] is True if token=="i_increment" else steps[i-1]["line_token"]=="swap_resume"
            ctx["i"]+=1
        elif token in {"j_decrement","cross_j_decrement"}:
            assert steps[i-1]["condition_result"] is True if token=="j_decrement" else steps[i-1]["line_token"]=="cross_i_increment"
            ctx["j"]-=1
        elif token=="rec_return":ctx=dict(primero=None,ultimo=None,i=None,j=None,pivote=None,depth=0)
        expected_expression="";expected_result=None
        if token in {"i_test","j_test"}:
            axis="i" if token=="i_test" else "j";index=ctx[axis];assert 0<=index<len(array)
            operand=array[index];pivot=ctx["pivote"];op="<" if axis=="i" else ">"
            expected_result=(operand<pivot if axis=="i" else operand>pivot);expected_expression=f"{operand} {op} {pivot}"
            counts["comparisons"]+=1
            assert s["comparing_indices"]==[index]
            evaluations.append((axis,index,pivot,expected_result))
        elif token in {"outer_test","cross_test"}:expected_expression=f'{ctx["i"]} <= {ctx["j"]}';expected_result=ctx["i"]<=ctx["j"]
        elif token=="left_test":expected_expression=f'{ctx["primero"]} < {ctx["j"]}';expected_result=ctx["primero"]<ctx["j"]
        elif token=="right_test":expected_expression=f'{ctx["i"]} < {ctx["ultimo"]}';expected_result=ctx["i"]<ctx["ultimo"]
        elif token=="valid_ptr":expected_expression="arreglo != NULL";expected_result=True
        elif token=="valid_n":expected_expression="3 > 0";expected_result=True
        elif token=="sort_guard":expected_expression="!arreglo_valido(arreglo,n)";expected_result=False
        elif token=="swap_guard":expected_expression="a == NULL || b == NULL";expected_result=False
        if token=="cross_test":counts["comparisons"]+=1
        assert s["condition_expression"]==expected_expression and s["condition_result"] is expected_result
        assert s["quick_context"]==ctx
        expected_frames=[] if ctx["depth"]==0 else [{k:ctx[k] for k in ("primero","ultimo","i","j","pivote")}]
        assert event["frames"]==expected_frames
        expected_variables={}
        if token not in {"initial","sort_return"}:expected_variables[("ordenar_quicksort","n")]=(3,True)
        if ctx["depth"]==1:
            for name in ("primero","ultimo"):expected_variables[("quicksort_recursivo[1]",name)]=(ctx[name],True)
            if ctx["i"] is not None:
                for name in ("i","j","pivote"):expected_variables[("quicksort_recursivo[1]",name)]=(ctx[name],True)
        if token in {"swap_declare","swap_guard","swap_temp","swap_assign_a","swap_assign_b"}:
            initialized=token in {"swap_temp","swap_assign_a","swap_assign_b"}
            expected_variables[("intercambiar","temporal")]=(array[1] if initialized else None,initialized)
        variables=s["instruction_variables"];keys=[(v["scope"],v["name"]) for v in variables];assert len(set(keys))==len(keys)
        assert {(v["scope"],v["name"]):(v["value"],v["initialized"]) for v in variables}==expected_variables
        stack=[] if token in {"initial","sort_return"} else ["ordenar_quicksort"]
        if ctx["depth"]==1:stack.append("quicksort_recursivo")
        if token in {"valid_entry","valid_ptr","valid_n"}:stack.append("arreglo_valido")
        if token in {"swap_entry","swap_declare","swap_guard","swap_temp","swap_assign_a","swap_assign_b"}:stack.append("intercambiar")
        assert s["instruction_stack"]==stack and s["console_output"]==""
        in_swap=token in {"swap_entry","swap_declare","swap_guard","swap_temp","swap_assign_a","swap_assign_b"}
        if in_swap:
            assert event["a"]==event["b"]==1
            pointers=s["instruction_pointers"]
            assert len(pointers)==2 and {p["name"] for p in pointers}=={"a","b"}
            for p in pointers:assert p["scope"]=="intercambiar" and p["target"]=="arreglo[1]" and p["index"]==1 and p["value"]==array[1]
        else:assert s["instruction_pointers"]==[] and event["a"] is None and event["b"] is None
        if token=="swap_temp":temporal=array[1];counts["moves"]+=1
        elif token=="swap_assign_a":array[1]=array[1];counts["moves"]+=1
        elif token=="swap_assign_b":assert temporal is not None;array[1]=temporal;counts["moves"]+=1;counts["swaps"]+=1
        if token in {"swap_temp","swap_assign_a","swap_assign_b"}:assert event["temporal"]==temporal
        else:assert event["temporal"] is None
        assert s["array_snapshot"]==array and s["metrics"]==counts
        assert {k:event[k] for k in counts}==counts
    assert evaluations==[("i",0,2,True),("i",1,2,False),("j",2,2,True),("j",1,2,False)]
    assert result["final_state"]["items"]==array==[1,2,3]
    assert result["metrics"]==result["final_state"]["metrics"]=={**counts,"steps":len(steps)}
    return evaluations
