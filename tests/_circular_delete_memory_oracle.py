"""Native head-match timeline: predecessor bypass, root move, count store, free."""
LINES = ["bool lcir_eliminar_primero(ListaCircular *lista, int valor) {", "LCirNodo *actual;", "LCirNodo *anterior;", "if (lista == NULL || lista->cabeza == NULL) {", "actual = lista->cabeza;", "anterior = lista->cola;", "do {", "if (actual->valor == valor) {", "if (actual == lista->cabeza && actual == lista->cola) {", "anterior->sgte = actual->sgte;", "if (actual == lista->cabeza) {", "lista->cabeza = actual->sgte;", "if (actual == lista->cola) {", "if (lista->cantidad > 0) {", "lista->cantidad--;", "free(actual);", "return true;"]

from _circular_insert_memory_oracle import _assert_sequence_projection, _assert_sequence_memory_projection

def assert_circular_delete_memory(body):
    trace = body["execution_trace"]
    assert trace["structure_id"] == "circular_list" and trace["operation_name"] == "eliminar_primero"
    assert trace["payload"] == {"value":"7"} and body["success"] is True
    steps = trace["steps"]
    assert len(steps) == 17 and [s["line_text"].strip() for s in steps] == LINES
    initial = steps[0]["state_snapshot"]
    assert initial["items"] == [{"value":7},{"value":4},{"value":7}]
    assert type(initial["size"]) is int and initial["size"] == 3 and initial["empty"] is False
    original = steps[0]["pedagogy"]["heap_objects"]
    assert len(original)==3 and len({n["id"] for n in original})==3
    first,middle,last = [n["id"] for n in original]
    source = trace["source_code"].replace("\r\n","\n").split("\n")
    expected_values=[7,4,7]; expected_size=3
    previous_heap = None
    for i,step in enumerate(steps):
        assert step["step_index"]==i and source[step["line_index"]].strip()==LINES[i]
        if i: assert step["state_snapshot"]==steps[i-1]["state_after"]
        if i in (15,16): assert step["line_index"]==max(j for j,l in enumerate(source) if l.strip()==LINES[i])
        _assert_sequence_projection(step["state_snapshot"], expected_values, expected_size)
        expected_values=[7,4,7] if i<11 else [4,7]; expected_size=3 if i<14 else 2
        f=step["pedagogy"];m=f["memory_state"];heap=f["heap_objects"]
        count=3 if i<15 else 2
        assert len(heap)==count and len({n["id"] for n in heap})==count and len({n["address"] for n in heap})==count
        objects={n["id"]:n for n in heap}
        assert set(objects)==({first,middle,last} if i<15 else {middle,last})
        for identity,value,following in [(first,7,middle),(middle,4,last),(last,7,first if i<9 else middle)]:
            if identity not in objects:continue
            node=objects[identity]
            assert node["fields"]=={"valor":value,"sgte":following}
            assert node["allocated"] is True and node["freed"] is False
            assert node["status"]==("detached" if identity==first and i>=11 else "linked")
        t=f["heap_transition"]
        assert t["after"]==heap
        assert len({n["id"] for n in t["before"]})==len(t["before"])
        if previous_heap is not None:assert t["before"]==previous_heap
        previous_heap=heap
        if i==15:
            assert len(t["freed"])==1
            retired=t["freed"][0]
            assert retired["id"]==first and retired["fields"]=={"valor":7,"sgte":middle}
            assert retired["allocated"] is False and retired["freed"] is True and retired["status"]=="freed"
        else:assert t["freed"]==[]
        assert m["lista"]=="&lc" and m["cabeza"]==(first if i<11 else middle) and m["cola"]==last
        assert m["cantidad"]==(3 if i<14 else 2)
        expected_ids=[first,middle,last] if i<11 else [middle,last]
        _assert_sequence_projection(m, expected_values, expected_size, expected_ids)
        _assert_sequence_memory_projection(m, m, heap)
        if i<16:_assert_sequence_memory_projection(step["state_after"], m, heap)
        _assert_sequence_projection(step["state_after"], expected_values, expected_size, expected_ids if i<16 else None)
        assert m["items"]==([{"value":7},{"value":4},{"value":7}] if i<11 else [{"value":4},{"value":7}])
        assert m.get("actual")== (None if i<4 or i==16 else "indeterminado (liberado)" if i==15 else first)
        assert m.get("anterior")== (last if 5<=i<=15 else None)
        calls=f["call_stack"]
        assert len(calls)==1 and calls[0]["function"]=="lcir_eliminar_primero"
        assert calls[0]["parameters"]=={"lista":"&lc","valor":7} and calls[0]["return"]==(True if i==16 else None)
        pointers=f["pointers"]
        assert len({p["name"] for p in pointers})==len(pointers)
        root=next(p for p in pointers if p["name"]=="lista")
        assert root["type"]=="ListaCircular *" and root["target"]==("fuera de ámbito" if i==16 else "&lc")
        conditions={3:False,7:True,8:False,10:True,12:False,13:True}
        if i in conditions:assert f["condition"]["result"] is conditions[i]
    _assert_sequence_projection(body["visual_state"], expected_values, expected_size)
    assert body["visual_state"]["items"]==[{"value":4},{"value":7}] and trace["final_state"]==body["visual_state"]
