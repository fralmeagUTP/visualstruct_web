"""Only original duplicate-parent7 and mergesort[3,1,3,1] focal C memory."""
from copy import deepcopy
import hashlib
from _sorting_source_oracle import assert_sorting_source_trace

def assert_duplicate_sublist(body):
    t=body["execution_trace"];steps=t["steps"]
    assert body["success"] is True and t["operation_name"]=="insertar_padre"
    assert hashlib.sha256(t["source_code"].encode()).hexdigest()=="2db43db109a02fec7496e730515113872b7020256d946c53b442fb95b3d564c7"
    expected_lines=["Nodo *sublista_insertar_padre_final(Nodo **lista, int valor_padre) {","Nodo *nuevo;","Nodo *actual;","if (lista == NULL) {","nuevo = crear_padre(valor_padre);","static Nodo *crear_padre(int valor) {","Nodo *nuevo = (Nodo *)malloc(sizeof(Nodo));","if (nuevo == NULL) {","nuevo->nro = valor;","nuevo->sgte = NULL;","nuevo->sub = NULL;","return nuevo;","nuevo = crear_padre(valor_padre);","if (nuevo == NULL) {","if (*lista == NULL) {","actual = *lista;","while (actual->sgte != NULL) {","actual->sgte = nuevo;","return nuevo;"]
    assert len(steps)==19 and [s["line_text"].strip() for s in steps]==expected_lines
    initial=steps[0]["state_snapshot"];assert len(initial["heap_nodes"])==1 and initial["items"][0]["parent"]==7
    old_id=initial["heap_nodes"][0]["id"];assert initial["head"]==old_id
    allocated=steps[6]["pedagogy"]["memory_state"]["heap_nodes"];new_ids={n["id"] for n in allocated}-{old_id};assert len(new_ids)==1;new_id=new_ids.pop()
    assert old_id!=new_id
    def cards(nodes):return [{"id":n["id"],"address":"0x"+n["id"],"status":n["status"],"allocated":True,"freed":False,"fields":{"nro":n["value"],"sgte":n["next"],"sub":n["sub"]}} for n in nodes]
    previous=initial["heap_nodes"]
    source=t["source_code"].splitlines()
    for i,s in enumerate(steps):
        m=s["pedagogy"]["memory_state"]
        assert s["state_after"]==(m if i<18 else body["visual_state"])
        assert s["state_after"]["items"]==m["items"]
        assert s["step_index"]==i and source[s["line_index"]]==s["line_text"]
        if i:assert s["state_snapshot"]==steps[i-1]["state_after"]
        expected=[{"id":old_id,"kind":"parent","value":7,"next":new_id if i>=17 else "NULL","sub":"NULL","status":"linked"}]
        if i>=6:expected.append({"id":new_id,"kind":"parent","value":7 if i>=8 else "sin inicializar","next":"NULL" if i>=9 else "sin inicializar","sub":"NULL" if i>=10 else "sin inicializar","status":"linked" if i>=17 else "detached"})
        assert m["heap_nodes"]==expected and m["head"]==old_id
        assert m["node_ids"]==([old_id,new_id] if i>=17 else [old_id]) and m["size"]==(2 if i>=17 else 1)
        assert [x["parent"] for x in m["items"]]==([7,7] if i>=17 else [7])
        ids=[x["id"] for x in m["items"]];assert len(set(ids))==len(ids) and ids[0]==initial["items"][0]["id"]
        transition=s["pedagogy"]["heap_transition"]
        assert transition["before"]==cards(previous) and transition["after"]==cards(expected)
        assert transition["freed"]==[] and transition["dangling_references"]==[];previous=expected
        frames=m["sublist_frames"]
        if i<18:
            caller=frames[0];assert caller["parameters"]=={"lista":"&sublista","valor_padre":7}
            if i>=1:assert caller["locals"]["nuevo"]==(new_id if i>=12 else "sin inicializar")
            if i>=2:assert caller["locals"]["actual"]==(old_id if i>=15 else "sin inicializar")
        else:assert frames==[] and m["returned"]==new_id and m["scope_ended"] is True
        if 5<=i<=10:
            helper=frames[-1];assert helper["function"]=="crear_padre" and helper["parameters"]=={"valor":7}
            if i>=6:assert helper["locals"]["nuevo"]==new_id
        if i==11:assert len(frames)==1 and m["returned"]==new_id
    assert t["final_state"]==body["visual_state"] and len(body["visual_state"]["items"])==2

def assert_duplicate_mergesort(body):
    t=body["execution_trace"];assert body["success"] is True
    assert hashlib.sha256(t["source_code"].encode()).hexdigest()=="eddfaad857bb33d6ea954fcfa0d04943190341dc1335699fc75cd0198b1e6426"
    assert_sorting_source_trace(t,[3,1,3,1])
    steps=t["steps"];assert len(steps)==147
    items=[3,1,3,1];aux=None;allocations=frees=moves=0;active=False
    write_tokens={"aux_left_write","aux_right_write","left_tail_write","right_tail_write"}
    for pos,s in enumerate(steps):
        old=s["state_snapshot"];new=s["state_after"];token=s["pedagogy"]["source"]["line_token"]
        assert old["items"]==items and old["auxiliary_array"]==aux
        expected_items=items[:];expected_aux=None if aux is None else aux[:];ctx=old.get("merge_context",{})
        if token=="aux_reserve":assert not active;active=True;allocations+=1;expected_aux=[None]*4
        elif token in write_tokens:
            assert active and aux is not None
            side="i" if token in {"aux_left_write","left_tail_write"} else "j";idx=ctx[side];k=ctx["k"]
            assert 0<=idx<4 and 0<=k<4;expected_aux[k]=items[idx];moves+=1
            assert new["merge_context"][side]==idx+1 and new["merge_context"]["k"]==k+1
            if token in {"aux_left_write","aux_right_write"}:assert (items[ctx["i"]]<=items[ctx["j"]])==(side=="i")
        elif token=="copy_write":
            idx=ctx["i"];assert active and aux[idx] is not None;expected_items[idx]=aux[idx];moves+=1
        elif token=="aux_free":assert active;active=False;frees+=1;expected_aux=None
        assert new["items"]==expected_items and new["auxiliary_array"]==expected_aux
        items=expected_items;aux=expected_aux
        assert new["metrics"]["moves"]==moves
        nc=new.get("merge_context")
        if nc is not None:
            assert nc["allocations"]==allocations and nc["frees"]==frees and nc["aux_live"] is active
            bounds=[nc["izquierda"],nc["derecha"]]
            assert new["active_range"]==(bounds if all(v is not None for v in bounds) else None)
        for pointer in s["pedagogy"]["pointers"]:
            if pointer["name"]=="auxiliar":
                assert active
                assert pointer["target"]==("reserva int[n]" if pointer["scope"]=="ordenar_mergesort" else "misma reserva del wrapper")
        if token=="aux_free":
            aliases=[v for v in s["pedagogy"]["variables"] if v["name"]=="auxiliar"]
            assert len(aliases)==1 and aliases[0]["value"]=="memoria liberada; sin lectura"
    assert (allocations,frees,moves)==(1,1,16) and items==[1,1,3,3]
    assert t["final_state"]==body["visual_state"] and body["visual_state"]["items"]==items

def assert_duplicate_RN(body):
    from _rbt_legacy_consumer_oracle import assert_rbt_consumer
    from _tree_intermediate_consumer_oracle import _assert_tree_public_projection
    assert_rbt_consumer(body,"rotation")
    for step in body["execution_trace"]["steps"]:
        _assert_tree_public_projection(step["state_after"],step["pedagogy"]["memory_state"],"red_black")
        for frame in step["pedagogy"]["memory_state"].get("tree_frames",[]):
            if frame["function"]=="rbt_rotar_dcha":assert frame["parameters"]=={"r":"&raiz","nodoRBT":"N1"}
