"""Independent focal cp_frente candidate projection contract; no producer invariants."""
EXPECTED_LINES = ["bool cp_frente(const ColaPrioridad *cola, int *valor, int *prioridad) {", "const CPNodo *actual;", "const CPNodo *objetivo;", "if (cola == NULL || cola->delante == NULL || valor == NULL || prioridad == NULL) {", "objetivo = cola->delante;", "actual = cola->delante->sgte;", "while (actual != NULL) {", "if (actual->prioridad < objetivo->prioridad) {", "objetivo = actual;", "actual = actual->sgte;", "while (actual != NULL) {", "if (actual->prioridad < objetivo->prioridad) {", "objetivo = actual;", "actual = actual->sgte;", "while (actual != NULL) {", "*valor = objetivo->valor;", "*prioridad = objetivo->prioridad;", "return true;"]
EXPECTED_INDEX = [-1]*4 + [0]*4 + [1]*4 + [2]*6

def assert_priority_front_candidate(body):
    trace = body["execution_trace"]
    assert trace["structure_id"] == "priority_queue" and trace["operation_name"] == "frente"
    assert body["success"] is True and body["result"] == 30
    steps = trace["steps"]
    assert len(steps) == 18 and [s["line_text"].strip() for s in steps] == EXPECTED_LINES
    original = [{"value":10,"priority":8},{"value":20,"priority":5},{"value":30,"priority":2}]
    assert steps[0]["state_snapshot"]["items"] == original
    initial_heap = steps[0]["pedagogy"]["front_memory"]["heap"]
    assert len(initial_heap) == 3 and len({n["id"] for n in initial_heap}) == 3
    assert len({n["fields"]["valor"] for n in initial_heap}) == 3
    ids = {n["fields"]["valor"]: n["id"] for n in initial_heap}
    assert set(ids) == {10,20,30}
    for node, value, priority, following in zip(initial_heap,[10,20,30],[8,5,2],[ids[20],ids[30],None]):
        assert node["fields"] == {"valor":value,"prioridad":priority,"sgte":following}
        assert node["alive"] is True and node["allocated"] is True and node["freed"] is False
    source = trace["source_code"].replace("\r\n", "\n").split("\n")
    for i, step in enumerate(steps):
        assert step["step_index"] == i and source[step["line_index"]].strip() == EXPECTED_LINES[i]
        if i: assert step["state_snapshot"] == steps[i-1]["state_after"]
        assert step["state_after"]["items"] == original and step["state_after"]["size"] == 3
        assert step["state_after"]["out_index"] == EXPECTED_INDEX[i]
        m = step["pedagogy"]["front_memory"]
        assert len(m["heap"]) == 3 and len({n["id"] for n in m["heap"]}) == 3 and m["heap"] == initial_heap
        assert step["pedagogy"]["heap_objects"] == initial_heap
        assert m["root"]["front"] == ids[10] and m["root"]["rear"] == ids[30] and m["root"]["quantity"] == 3
        pointers = m["pointers"]
        assert len({(p["scope"],p["name"]) for p in pointers}) == len(pointers)
        for name, target, typ in [("cola","&cp","const ColaPrioridad *"),("valor","&caller_valor","int *"),("prioridad","&caller_prioridad","int *")]:
            p = next(p for p in pointers if p["name"] == name)
            assert p["target"] == target and p["type"] == typ and p["initialized"] is True
            assert p["valid"] is (i < 17) and p["scope_state"] == ("active" if i < 17 else "ended")
        candidates = [p for p in pointers if p["name"] == "objetivo"]
        if i < 4: assert not candidates
        else:
            assert len(candidates) == 1
            assert candidates[0]["target"] == ids[[10,20,30][EXPECTED_INDEX[i]]]
        assert m["outputs"] == {"value":30 if i >= 15 else 0,"priority":2 if i >= 16 else 0,"value_written":i >= 15,"priority_written":i >= 16}
    assert trace["final_state"] == body["visual_state"]
