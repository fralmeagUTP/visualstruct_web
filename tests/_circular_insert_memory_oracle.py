"""Native lcir_insertar_final contract for the existing empty/one-node consumer."""
COMMON = ["bool lcir_insertar_final(ListaCircular *lista, int valor) {", "LCirNodo *nuevo;", "if (lista == NULL) {", "static LCirNodo *lcir_crear_nodo(int valor) {", "LCirNodo *nodo = (LCirNodo *)malloc(sizeof(LCirNodo));", "if (nodo == NULL) {", "nodo->valor = valor;", "nodo->sgte = NULL;", "return nodo;", "nuevo = lcir_crear_nodo(valor);", "if (nuevo == NULL) {", "if (lista->cabeza == NULL) {"]



def _assert_sequence_projection(state, values, size, identities=None):
    """Check public fields against a C-derived timeline, never candidate items."""
    assert state["items"] == [{"value": v} for v in values], "public items disagree with C links"
    assert type(state["size"]) is int and state["size"] == size
    assert state["empty"] is (not values)
    if identities is not None:
        assert state["node_ids"] == identities
        if "reachable_count" in state:
            assert state["reachable_count"] == len(identities)
def _assert_sequence_memory_projection(public, memory, heap):
    """Bind displayed identities/links to the already checked fixed C heap model."""
    objects={n["id"]:n for n in heap}
    expected_nodes=[{"id":n["id"],"value":n["fields"].get("valor",n["fields"].get("nro")),"next":n["fields"]["sgte"],"status":n["status"]} for n in heap]
    assert public["heap_nodes"]==expected_nodes
    root_field="cabeza" if "cabeza" in memory else "head"
    head=memory[root_field]; assert public[root_field]==head
    if root_field=="cabeza":
        tail=memory["cola"]
        assert public["cola"]==tail and public["cantidad"]==memory["cantidad"]
        pointer=head; visited=set()
        while pointer in objects and pointer not in visited:
            visited.add(pointer);pointer=objects[pointer]["fields"]["sgte"]
        assert public["cycle_target"]==pointer
        assert public["cola_sgte"]==("NULL" if tail=="NULL" else objects[tail]["fields"]["sgte"])


def assert_circular_insert_memory(body, initial_values, value):
    assert (initial_values, value) in [([],4),([4],9)]
    trace = body["execution_trace"]
    assert trace["structure_id"] == "circular_list" and trace["operation_name"] == "insertar_final"
    assert trace["payload"] == {"value":str(value)} and body["success"] is True
    steps = trace["steps"]
    empty = not initial_values
    ending = ["nuevo->sgte = nuevo;", "lista->cabeza = nuevo;", "lista->cola = nuevo;", "lista->cantidad = 1;", "return true;"] if empty else ["nuevo->sgte = lista->cabeza;", "lista->cola->sgte = nuevo;", "lista->cola = nuevo;", "lista->cantidad++;", "return true;"]
    lines = COMMON + ending
    assert len(steps) == 17 and [s["line_text"].strip() for s in steps] == lines
    initial = steps[0]["state_snapshot"]
    assert initial["items"] == [{"value":v} for v in initial_values]
    assert type(initial["size"]) is int and initial["size"] == len(initial_values)
    assert initial["empty"] is empty
    allocation = steps[4]["pedagogy"]["heap_objects"]
    assert len(allocation) == len(initial_values)+1 and len({n["id"] for n in allocation}) == len(allocation)
    temporary = [n for n in allocation if n["status"] == "temporary"]
    assert len(temporary) == 1
    identity = temporary[0]["id"]
    old_id = None if empty else next(n["id"] for n in allocation if n["status"] == "linked")
    assert identity != old_id
    source = trace["source_code"].replace("\r\n", "\n").split("\n")
    expected_values = initial_values[:]; expected_size = len(initial_values)
    previous_heap = None
    for i, step in enumerate(steps):
        assert step["step_index"] == i and source[step["line_index"]].strip() == lines[i]
        if i: assert step["state_snapshot"] == steps[i-1]["state_after"]
        if i >= 12:
            matches = [j for j,l in enumerate(source) if l.strip() == lines[i]]
            assert step["line_index"] == (matches[0] if empty else matches[-1])
        frame = step["pedagogy"]; m = frame["memory_state"]
        heap = frame["heap_objects"]
        count = len(initial_values) + (i >= 4)
        assert len(heap) == count and len({n["id"] for n in heap}) == count
        assert len({n["address"] for n in heap}) == count
        objects = {n["id"]:n for n in heap}
        assert set(objects) == ({old_id} if old_id else set()) | ({identity} if i >=4 else set())
        if i >=4:
            node = objects[identity]
            expected_next = "sin inicializar" if i<7 else "NULL" if i<12 else (identity if empty else old_id)
            assert node["fields"] == {"valor":"sin inicializar" if i<6 else value,"sgte":expected_next}
            assert node["status"] == ("temporary" if i<13 else "linked")
        if old_id:
            assert objects[old_id]["fields"] == {"valor":4,"sgte":old_id if i<13 else identity}
            assert objects[old_id]["status"] == "linked"
        assert all(n["allocated"] is True and n["freed"] is False for n in heap)
        transition = frame["heap_transition"]
        assert transition["after"] == heap and transition["freed"] == []
        assert len({n["id"] for n in transition["before"]}) == len(transition["before"])
        if previous_heap is not None: assert transition["before"] == previous_heap
        previous_heap = heap
        _assert_sequence_projection(step["state_snapshot"], expected_values, expected_size)
        expected_values = initial_values + ([value] if i>=13 else [])
        expected_size = len(initial_values)+(i>=15)
        expected_ids = ([old_id] if old_id else []) + ([identity] if i>=13 else [])
        _assert_sequence_projection(m, expected_values, expected_size, expected_ids)
        _assert_sequence_memory_projection(m, m, heap)
        if i<16:_assert_sequence_memory_projection(step["state_after"], m, heap)
        _assert_sequence_projection(step["state_after"], expected_values, expected_size, expected_ids if i<16 else None)
        assert m["items"] == [{"value":v} for v in expected_values]
        assert m["cabeza"] == (identity if empty and i>=13 else "NULL" if empty else old_id)
        assert m["cola"] == (identity if i>=14 else "NULL" if empty else old_id)
        assert m["cantidad"] == len(initial_values)+(i>=15)
        assert m["lista"] == "&lc"
        assert m.get("nodo") == (identity if 4<=i<=7 else None)
        assert m.get("nuevo") == (identity if 9<=i<=15 else None)
        calls = frame["call_stack"]
        assert len(calls) == (2 if 3<=i<=7 else 1)
        assert calls[0]["function"] == "lcir_insertar_final" and calls[0]["parameters"] == {"lista":"&lc","valor":value}
        assert calls[0]["return"] == (True if i==16 else None)
        if len(calls)==2:
            assert calls[1]["function"] == "lcir_crear_nodo" and calls[1]["parameters"] == {"valor":value}
        pointers = frame["pointers"]
        assert len({p["name"] for p in pointers}) == len(pointers)
        root = next(p for p in pointers if p["name"] == "lista")
        assert root["type"] == "ListaCircular *" and root["target"] == ("fuera de ámbito" if i==16 else "&lc")
        if i in (2,5,10,11): assert frame["condition"]["result"] is (empty if i==11 else False)
    _assert_sequence_projection(body["visual_state"], expected_values, expected_size)
    assert body["visual_state"]["items"] == [{"value":v} for v in initial_values+[value]]
    assert trace["final_state"] == body["visual_state"]
