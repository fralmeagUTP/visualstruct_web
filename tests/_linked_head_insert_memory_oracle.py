"""Focal caller-level C contract: constructor postcondition then private link/publication."""
LINES = ["void lista_insertar_inicio(Tlista *lista, int valor) {", "if (lista == NULL) {", "Tlista q = CrearNodoLista(valor);", "if (q == NULL) {", "q->sgte = *lista;", "*lista = q;", "}"]

from _circular_insert_memory_oracle import _assert_sequence_projection, _assert_sequence_memory_projection

def assert_linked_head_insert_memory(body):
    trace = body["execution_trace"]
    assert trace["structure_id"] == "linked_list" and trace["operation_name"] == "insertar_inicio"
    assert trace["payload"] == {"value":"20"} and body["success"] is True
    steps = trace["steps"]
    assert len(steps) == 7 and [s["line_text"].strip() for s in steps] == LINES
    initial = steps[0]["state_snapshot"]
    assert initial["items"] == [{"value":10}] and type(initial["size"]) is int and initial["size"] == 1 and initial["empty"] is False
    initial_heap = steps[0]["pedagogy"]["heap_objects"]
    assert len(initial_heap) == 1
    old_id = initial_heap[0]["id"]
    allocated = steps[2]["pedagogy"]["heap_objects"]
    assert len(allocated) == 2 and len({n["id"] for n in allocated}) == 2
    new_nodes = [n for n in allocated if n["id"] != old_id]
    assert len(new_nodes) == 1
    identity = new_nodes[0]["id"]
    source = trace["source_code"].replace("\r\n","\n").split("\n")
    expected_values=[10]; expected_size=1
    previous_heap = None
    for i, step in enumerate(steps):
        assert step["step_index"] == i and source[step["line_index"]].strip() == LINES[i]
        if i: assert step["state_snapshot"] == steps[i-1]["state_after"]
        if i==6: assert step["line_index"] == max(j for j,l in enumerate(source) if l.strip()=="}")
        _assert_sequence_projection(step["state_snapshot"], expected_values, expected_size)
        expected_values=[10] if i<5 else [20,10]; expected_size=1 if i<5 else 2
        frame = step["pedagogy"]; m = frame["memory_state"]
        heap = frame["heap_objects"]
        count = 1+(i>=2)
        assert len(heap) == count and len({n["id"] for n in heap}) == count and len({n["address"] for n in heap}) == count
        objects = {n["id"]:n for n in heap}
        assert set(objects) == ({old_id,identity} if i>=2 else {old_id})
        assert objects[old_id]["fields"] == {"nro":10,"sgte":"NULL"} and objects[old_id]["status"] == "linked"
        if i>=2:
            assert objects[identity]["fields"] == {"nro":20,"sgte":"NULL" if i<4 else old_id}
            assert objects[identity]["status"] == ("temporary" if i<5 else "linked")
        assert all(n["allocated"] is True and n["freed"] is False for n in heap)
        transition = frame["heap_transition"]
        assert transition["after"] == heap and transition["freed"] == []
        assert len({n["id"] for n in transition["before"]}) == len(transition["before"])
        if previous_heap is not None: assert transition["before"] == previous_heap
        previous_heap = heap
        assert m["head"] == (old_id if i<5 else identity)
        expected_ids=[old_id] if i<5 else [identity,old_id]
        _assert_sequence_projection(m, expected_values, expected_size, expected_ids)
        _assert_sequence_memory_projection(m, m, heap)
        if i<6:_assert_sequence_memory_projection(step["state_after"], m, heap)
        _assert_sequence_projection(step["state_after"], expected_values, expected_size, expected_ids if i<6 else None)
        assert m["items"] == ([{"value":10}] if i<5 else [{"value":20},{"value":10}])
        assert m["size"] == (1 if i<5 else 2)
        assert m["lista"] == "&cabeza" and m.get("q") == (identity if 2<=i<=5 else None)
        calls = frame["call_stack"]
        assert len(calls) == 1 and calls[0]["function"] == "lista_insertar_inicio"
        assert calls[0]["parameters"] == {"lista":"&cabeza","valor":20}
        pointers = frame["pointers"]
        assert len({p["name"] for p in pointers}) == len(pointers)
        root = next(p for p in pointers if p["name"] == "lista")
        assert root["type"] == "Tlista *" and root["target"] == ("fuera de ámbito" if i==6 else "&cabeza")
        if i in (1,3): assert frame["condition"]["result"] is False
    _assert_sequence_projection(body["visual_state"], expected_values, expected_size)
    assert body["visual_state"]["items"] == [{"value":20},{"value":10}]
    assert trace["final_state"] == body["visual_state"]
