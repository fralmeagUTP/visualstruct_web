"""Unit tests focused on hierarchical interpreter simulation behavior."""

from __future__ import annotations

from app.services.hierarchical_structure_service import HierarchicalStructureService


def _run_hier_op(structure_id: str, history: list[dict], operation: str, payload: dict) -> dict:
    return HierarchicalStructureService.execute_operation(
        structure_id=structure_id,
        operation_name=operation,
        payload=payload,
        history=history,
    )


def _norm(line: str) -> str:
    return " ".join(str(line).strip().lower().split())


def _trace_lines(result: dict) -> list[str]:
    return [_norm(step.get("line_text", "")) for step in result["execution_trace"]["steps"]]


def _tree_shape(state: dict) -> tuple | None:
    """Project only reachable node values and child links, not scope/heap metadata."""
    def walk(node):
        if node is None:
            return None
        return (node["value"], walk(node["left"]), walk(node["right"]))
    return walk(state.get("root"))


def _structural_change_indexes(trace: dict) -> list[int]:
    for step in trace["steps"]:
        assert step["line_text"] == trace["source_code"].splitlines()[step["line_index"]]
    return [index for index, step in enumerate(trace["steps"])
            if _tree_shape(step["state_snapshot"]) != _tree_shape(step["state_after"])]


def _assert_single_reservation_no_free(trace: dict) -> None:
    memories = [step["pedagogy"]["memory"] for step in trace["steps"]]
    assert sum(len(memory["allocated_objects"]) for memory in memories) == 1
    assert all(memory["freed_objects"] == [] for memory in memories)
    assert _tree_shape(trace["steps"][-1]["state_after"]) == _tree_shape(trace["final_state"])


def test_hierarchical_trace_contract_for_mutating_insert_abb() -> None:
    """Mutating ABB operation should expose trace and final state consistency."""
    history: list[dict] = []
    result = _run_hier_op("abb", history, "insertar", {"value": "10"})

    assert result["success"] is True
    trace = result["execution_trace"]
    assert trace["steps"]
    assert trace["final_state"] == result["visual_state"]
    assert result["visual_state"]["size"] == 1


def test_abb_insert_empty_tree_stops_after_return_nuevo() -> None:
    """When ABB root is NULL, trace should return new node and exit subroutine."""
    history: list[dict] = []
    result = _run_hier_op("abb", history, "insertar", {"value": "10"})
    assert result["success"] is True

    lines = _trace_lines(result)
    idx_return_new = lines.index(_norm("return nuevo;"))
    tail = lines[idx_return_new + 1 :]

    assert _norm("if (valor < nodo->valor)") not in tail
    assert _norm("nodo->izquierdo = abb_insertar(nodo->izquierdo, valor);") not in tail
    assert _norm("nodo->derecho = abb_insertar(nodo->derecho, valor);") not in tail
    assert _norm("return nodo;") not in tail


def test_abb_insert_left_branch_does_not_execute_right_branch() -> None:
    """In `if / else if`, inserting left should not execute right assignment line."""
    history: list[dict] = []
    first = _run_hier_op("abb", history, "insertar", {"value": "10"})
    history = first["history"]

    second = _run_hier_op("abb", history, "insertar", {"value": "5"})
    assert second["success"] is True
    lines = _trace_lines(second)

    assert _norm("nodo->izquierdo = abb_insertar(nodo->izquierdo, valor);") in lines
    assert _norm("nodo->derecho = abb_insertar(nodo->derecho, valor);") not in lines


def test_avl_duplicate_insert_returns_before_malloc() -> None:
    """Duplicate AVL insert should hit early return and skip node allocation block."""
    history: list[dict] = []
    first = _run_hier_op("avl", history, "insertar", {"value": "10"})
    history = first["history"]

    duplicate = _run_hier_op("avl", history, "insertar", {"value": "10"})
    assert duplicate["success"] is False

    lines = _trace_lines(duplicate)
    idx_dup_return = lines.index(_norm("return; // no duplicados"))
    tail = lines[idx_dup_return + 1 :]

    assert _norm("avl nuevo = malloc(sizeof(*nuevo));") not in tail
    assert _norm("if (padre == NULL) {") not in tail
    assert _norm("while (padre != NULL) {") not in tail


def test_red_black_duplicate_insert_returns_before_malloc_and_fixup() -> None:
    """The application rejects a duplicate without C calls, allocation, output or history."""
    history: list[dict] = []
    first = _run_hier_op("red_black", history, "insertar", {"value": "10"})
    history = first["history"]

    duplicate = _run_hier_op("red_black", history, "insertar", {"value": "10"})
    assert duplicate["success"] is False

    trace = duplicate["execution_trace"]
    assert trace["application_precondition_rejected"] is True
    assert duplicate["history"] == history
    assert duplicate["visual_state"] == first["visual_state"]
    assert trace["final_state"] == first["visual_state"]
    assert len(trace["steps"]) == 1
    step = trace["steps"][0]
    frame = step["pedagogy"]
    assert frame["instruction_event"]["C_invoked"] is False
    assert frame["instruction_event"]["return"] is None
    assert frame["call_stack"] == [] and frame["condition"] is None
    assert frame["memory"]["allocated_objects"] == []
    assert frame["memory"]["freed_objects"] == []
    assert step["console"] == []
    assert step["state_snapshot"] == step["state_after"] == first["visual_state"]
    assert "rbt_insertar NO fue invocado" in step["line_text"]
    assert step["line_text"] == trace["source_code"].splitlines()[step["line_index"]]


def test_red_black_insert_non_duplicate_skips_duplicate_return_branch() -> None:
    """Successful red-black insert must not execute duplicate early return."""
    history: list[dict] = []
    for value in (40, 20, 60, 8, 30, 50, 70):
        out = _run_hier_op("red_black", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("red_black", history, "insertar", {"value": "80"})
    assert result["success"] is True
    lines = _trace_lines(result)

    idx_if_actual = lines.index(_norm("if (actual != null)"))
    # Si no es duplicado, la siguiente instruccion NO debe ser el return
    # inmediato de esa rama, sino la reserva de memoria del nuevo nodo.
    next_line = lines[idx_if_actual + 1] if idx_if_actual + 1 < len(lines) else ""
    assert next_line != _norm("return;")
    assert _norm("actual = malloc(sizeof(struct nodorbt));") in lines
    assert _norm("rbt_insercion_caso1(actual, arbol);") in lines


def test_red_black_insert_state_changes_on_link_line_not_during_search() -> None:
    """Tree must remain unchanged during search; first visible mutation is link line."""
    history: list[dict] = []
    for value in (40, 20, 60, 8, 30, 50, 70):
        out = _run_hier_op("red_black", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("red_black", history, "insertar", {"value": "80"})
    assert result["success"] is True
    steps = result["execution_trace"]["steps"]
    assert steps

    changed_indexes = _structural_change_indexes(result["execution_trace"])
    assert changed_indexes, "La traza no refleja ningun cambio de estado."
    first_changed = steps[changed_indexes[0]]
    changed_line = _norm(first_changed.get("line_text", ""))

    assert changed_line in {
        _norm("*arbol = actual;"),
        _norm("padre->izq = actual;"),
        _norm("padre->der = actual;"),
    }
    assert all(_tree_shape(step["state_snapshot"]) == _tree_shape(step["state_after"])
               for step in steps[:changed_indexes[0]])
    _assert_single_reservation_no_free(result["execution_trace"])

def test_abb_empty_insert_keeps_root_null_until_caller_publication() -> None:
    """The allocated local initializes before the by-value caller publishes root."""
    history: list[dict] = []
    result = _run_hier_op("abb", history, "insertar", {"value": "55"})
    assert result["success"] is True

    steps = result["execution_trace"]["steps"]
    assert len(steps) >= 5

    def values_from_state(state: dict) -> list[int]:
        out: list[int] = []

        def walk(node: dict | None) -> None:
            if not isinstance(node, dict):
                return
            value = node.get("value")
            if isinstance(value, int):
                out.append(value)
            walk(node.get("left"))
            walk(node.get("right"))

        walk(state.get("root"))
        return sorted(out)

    assignment_index = None
    for idx, step in enumerate(steps):
        line = _norm(step.get("line_text", ""))
        if line == _norm("nuevo->valor = valor;"):
            assignment_index = idx
            break

    assert assignment_index is not None

    for step in steps[:assignment_index]:
        after_state = step.get("state_after") or {}
        assert values_from_state(after_state) == []
        traversals = after_state.get("traversals") or {}
        assert traversals.get("inorden") == []
        assert traversals.get("preorden") == []
        assert traversals.get("postorden") == []

    assignment_after = steps[assignment_index].get("state_after") or {}
    assert values_from_state(assignment_after) == []
    assert assignment_after["head"] == "NULL"
    assert assignment_after["heap_nodes"] == [{"id": "N1", "value": 55,
        "left": "sin inicializar", "right": "sin inicializar", "status": "detached"}]
    publication_index = next(idx for idx, step in enumerate(steps)
        if step["pedagogy"]["instruction_event"]["phase"] == "caller")
    assert publication_index > assignment_index
    for step in steps[assignment_index:publication_index]:
        assert values_from_state(step["state_after"]) == []
        assert step["state_after"]["head"] == "NULL"
    published = steps[publication_index]["pedagogy"]["memory_state"]
    assert values_from_state(published) == [55] and published["head"] == "N1"
    assert published["heap_nodes"] == [{"id": "N1", "value": 55,
        "left": "NULL", "right": "NULL", "status": "linked"}]


def test_abb_inorden_trace_expands_recursive_calls() -> None:
    """Inorden must expand recursive calls, not execute method body only once."""
    history: list[dict] = []
    for value in (63, 50, 75, 55):
        out = _run_hier_op("abb", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("abb", history, "inorden", {})
    assert result["success"] is True

    lines = _trace_lines(result)
    func_line = _norm("void abb_inorden(ABBNodo* nodo) {")
    if_line = _norm("if (nodo != NULL) {")
    left_call = _norm("abb_inorden(nodo->izquierdo);")
    right_call = _norm("abb_inorden(nodo->derecho);")
    visit_line = _norm('printf("%d ", nodo->valor);')

    # Debe haber multiples entradas recursivas (nodos + ramas NULL), no 1 sola pasada.
    assert lines.count(func_line) > 1
    assert lines.count(if_line) > 1

    # En nodos reales se visitan ambas ramas recursivas.
    assert lines.count(left_call) >= 4
    assert lines.count(right_call) >= 4

    # Debe imprimirse una vez por nodo visitado en inorden.
    expected_visits = len(result.get("result") or [])
    assert expected_visits == 4
    assert lines.count(visit_line) == expected_visits


def test_abb_insert_trace_expands_recursive_calls_along_path() -> None:
    """ABB insertar should expand recursive subroutine calls for each level traversed."""
    history: list[dict] = []
    for value in (63, 50, 75, 55, 70, 80):
        out = _run_hier_op("abb", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("abb", history, "insertar", {"value": "65"})
    assert result["success"] is True
    lines = _trace_lines(result)

    header = _norm("ABBNodo* abb_insertar(ABBNodo* nodo, int valor) {")
    left_call = _norm("nodo->izquierdo = abb_insertar(nodo->izquierdo, valor);")
    right_call = _norm("nodo->derecho = abb_insertar(nodo->derecho, valor);")
    assign = _norm("nuevo->valor = valor;")

    assert lines.count(header) > 1
    assert lines.count(right_call) >= 1
    assert lines.count(left_call) >= 1
    assert lines.count(assign) == 1


def test_abb_delete_trace_expands_recursive_calls_and_successor_delete() -> None:
    """ABB eliminar with two children should recurse to delete in-order successor."""
    history: list[dict] = []
    for value in (63, 50, 75, 55, 70, 80):
        out = _run_hier_op("abb", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("abb", history, "eliminar", {"value": "63"})
    assert result["success"] is True
    lines = _trace_lines(result)

    header = _norm("ABBNodo* abb_eliminar(ABBNodo* nodo, int valor) {")
    recurse_successor = _norm("nodo->derecho = abb_eliminar(nodo->derecho, temp->valor);")
    min_line = _norm("ABBNodo* temp = abb_encontrarMinimo(nodo->derecho);")

    assert lines.count(header) > 1
    assert recurse_successor in lines
    assert min_line in lines


def test_avl_insert_trace_does_not_take_duplicate_return_for_new_value() -> None:
    """AVL insert with a new key must not execute the duplicate early return line."""
    history: list[dict] = []
    for value in (10, 8, 30, 40):
        out = _run_hier_op("avl", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("avl", history, "insertar", {"value": "50"})
    assert result["success"] is True
    lines = _trace_lines(result)

    assert _norm("else return; // no duplicados") not in lines
    assert _norm("else if (x > actual->nro)") in lines
    assert _norm("actual = actual->der;") in lines


def test_avl_insert_state_changes_on_link_line_not_local_assignment() -> None:
    """Visual tree should change when linking new node, not on local pointer assignments."""
    history: list[dict] = []
    for value in (10, 8, 30, 40):
        out = _run_hier_op("avl", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("avl", history, "insertar", {"value": "50"})
    assert result["success"] is True
    steps = result["execution_trace"]["steps"]

    changed_indexes = _structural_change_indexes(result["execution_trace"])
    assert changed_indexes, "La traza no refleja ningun cambio de estado."
    first_changed_step = steps[changed_indexes[0]]
    line = _norm(first_changed_step.get("line_text", ""))

    # La mutacion visible debe ocurrir al enlazar el nuevo nodo al arbol.
    assert line in {
        _norm("padre->izq = nuevo;"),
        _norm("padre->der = nuevo;"),
        _norm("*raiz = nuevo;"),
    }
    assert all(_tree_shape(step["state_snapshot"]) == _tree_shape(step["state_after"])
               for step in steps[:changed_indexes[0]])
    _assert_single_reservation_no_free(result["execution_trace"])


def test_avl_rotation_debug_marks_unbalanced_node_and_rotation_message() -> None:
    """AVL rotation steps should expose unbalanced pivot and human-readable rotation message."""
    history: list[dict] = []
    for value in (30, 20):
        out = _run_hier_op("avl", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("avl", history, "insertar", {"value": "10"})
    assert result["success"] is True

    debug_steps = [
        step.get("debug")
        for step in result["execution_trace"]["steps"]
        if isinstance(step.get("debug"), dict)
    ]
    rebalance_steps = [dbg for dbg in debug_steps if dbg.get("stage") in {"pre_rebalance", "rebalance"}]
    assert rebalance_steps
    assert any(str(step.get("unbalanced_key", "")) == "30" for step in rebalance_steps)
    assert any("Rotacion AVL LL" in str(step.get("rotation_message", "")) for step in rebalance_steps)


def test_avl_insert_without_rotation_does_not_emit_rotation_hint() -> None:
    """Insertion that keeps AVL balanced must not show fake rotation metadata."""
    history: list[dict] = []
    for value in (60, 50, 70):
        out = _run_hier_op("avl", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("avl", history, "insertar", {"value": "80"})
    assert result["success"] is True

    steps = result["execution_trace"]["steps"]
    debug_steps = [step.get("debug") for step in steps if isinstance(step.get("debug"), dict)]
    assert not any(isinstance(dbg.get("rotation_hint"), dict) for dbg in debug_steps)
    assert not any(str(dbg.get("rotation_message", "")).strip() for dbg in debug_steps)

    changed_indexes = _structural_change_indexes(result["execution_trace"])
    assert len(changed_indexes) == 1
    assert _norm(steps[changed_indexes[0]]["line_text"]) == _norm("padre->der = nuevo;")
    assert _tree_shape(steps[changed_indexes[0]]["state_snapshot"]) != _tree_shape(steps[changed_indexes[0]]["state_after"])
    _assert_single_reservation_no_free(result["execution_trace"])


def test_avl_minimo_trace_expands_while_by_left_depth() -> None:
    """AVL minimo should iterate while-loop according to real left-depth path."""
    history: list[dict] = []
    for value in (60, 50, 70, 40, 55):
        out = _run_hier_op("avl", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("avl", history, "minimo", {})
    assert result["success"] is True
    assert result["result"] == 40

    lines = _trace_lines(result)
    assert lines.count(_norm("while (nodo->izq)")) >= 2
    assert lines.count(_norm("nodo = nodo->izq;")) >= 2
    assert _norm("return nodo;") in lines

    debug_steps = [
        step.get("debug")
        for step in result["execution_trace"]["steps"]
        if isinstance(step.get("debug"), dict)
    ]
    assert debug_steps
    returning = [step for step in result["execution_trace"]["steps"]
                 if _norm(step["line_text"]) == _norm("return nodo;")]
    assert len(returning) == 1
    returned = returning[0]["pedagogy"]["instruction_event"]
    assert returned["phase"] == "return" and returned["return"] not in (None, "NULL")
    identity = returned["return"]
    assert next(node for node in returning[0]["state_snapshot"]["heap_nodes"]
                if node["id"] == identity)["value"] == 40
    all_steps = result["execution_trace"]["steps"]
    stages = [step["pedagogy"]["instruction_event"]["phase"] for step in all_steps]
    assert stages.index("return") < stages.index("caller_assignment") < stages.index("caller_store") < stages.index("caller_result")
    store = all_steps[stages.index("caller_store")]
    assert store["state_snapshot"]["caller_output"]["initialized"] is False
    assert store["state_after"]["caller_output"] == {"identity": "salida", "type": "int", "initialized": True, "value": 40}
    assert all_steps[-1]["pedagogy"]["instruction_event"]["return"] == 1
    for step in all_steps:
        memory = step["pedagogy"]["memory"]
        assert memory["objects_before"] == memory["objects_after"]
        assert memory["allocated_objects"] == memory["freed_objects"] == []
        assert _tree_shape(step["state_snapshot"]) == _tree_shape(step["state_after"])
        assert step["line_text"] == result["execution_trace"]["source_code"].splitlines()[step["line_index"]]


def test_abb_minimo_trace_repeats_while_per_left_depth() -> None:
    """ABB minimo should evaluate while-loop once per level plus final false check."""
    history: list[dict] = []
    for value in (6, 5, 10):
        out = _run_hier_op("abb", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("abb", history, "minimo", {})
    assert result["success"] is True
    assert result["result"] == 5
    lines = _trace_lines(result)

    while_line = _norm("while (nodo->izquierdo != NULL)")
    move_line = _norm("nodo = nodo->izquierdo;")
    return_line = _norm("return nodo;")

    assert lines.count(while_line) >= 2
    assert lines.count(move_line) >= 1
    assert return_line in lines


def test_abb_maximo_trace_repeats_while_per_right_depth() -> None:
    """ABB maximo should evaluate while-loop once per level plus final false check."""
    history: list[dict] = []
    for value in (8, 7, 9, 10):
        out = _run_hier_op("abb", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("abb", history, "maximo", {})
    assert result["success"] is True
    assert result["result"] == 10
    lines = _trace_lines(result)

    while_line = _norm("while (nodo != NULL && nodo->derecho != NULL)")
    move_line = _norm("nodo = nodo->derecho;")
    return_line = _norm("return nodo;")

    assert lines.count(while_line) >= 2
    assert lines.count(move_line) >= 1
    assert return_line in lines


def test_avl_inorden_trace_expands_recursive_calls() -> None:
    """AVL inorden must execute recursive subroutine calls for each branch."""
    history: list[dict] = []
    for value in (60, 50, 70, 40, 55):
        out = _run_hier_op("avl", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("avl", history, "inorden", {})
    assert result["success"] is True
    lines = _trace_lines(result)

    header = _norm("void avl_inorden(AVL nodo) {")
    left_call = _norm("avl_inorden(nodo->izq);")
    right_call = _norm("avl_inorden(nodo->der);")
    visit = _norm('printf("%d ", nodo->nro);')

    assert lines.count(header) > 1
    assert lines.count(left_call) >= 5
    assert lines.count(right_call) >= 5
    assert lines.count(visit) == len(result.get("result") or [])


def test_red_black_inorden_trace_expands_recursive_calls() -> None:
    """Rojo-Negro inorden must expand recursive calls, not single linear pass."""
    history: list[dict] = []
    for value in (60, 50, 70, 40, 55):
        out = _run_hier_op("red_black", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("red_black", history, "inorden", {})
    assert result["success"] is True
    lines = _trace_lines(result)

    header = _norm("void rbt_inorden(RBT nodo) {")
    left_call = _norm("rbt_inorden(nodo->izq);")
    right_call = _norm("rbt_inorden(nodo->der);")
    visit = _norm('printf("%d ", nodo->nro);')

    assert lines.count(header) > 1
    assert lines.count(left_call) >= 5
    assert lines.count(right_call) >= 5
    assert lines.count(visit) == len(result.get("result") or [])


def test_avl_altura_trace_expands_recursive_calls() -> None:
    """AVL altura should recurse over left and right subtrees."""
    history: list[dict] = []
    for value in (60, 50, 70, 40, 55):
        out = _run_hier_op("avl", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("avl", history, "altura", {})
    assert result["success"] is True
    lines = _trace_lines(result)

    header = _norm("int avl_altura(AVL arbol) {")
    left_call = _norm("int altizq = avl_altura(arbol->izq);")
    right_call = _norm("int altder = avl_altura(arbol->der);")
    base_return = _norm("return 0;")
    final_return = _norm("return (altizq > altder ? altizq : altder) + 1;")

    assert lines.count(header) > 1
    assert lines.count(left_call) >= 1
    assert lines.count(right_call) >= 1
    assert base_return in lines
    assert final_return in lines


def test_red_black_validar_trace_expands_recursive_calls() -> None:
    """Rojo-Negro validar should recurse through both branches before returning."""
    history: list[dict] = []
    for value in (60, 50, 70, 40, 55):
        out = _run_hier_op("red_black", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("red_black", history, "validar", {})
    assert result["success"] is True
    lines = _trace_lines(result)

    header = _norm("int rbt_validar(RBT raiz) {")
    helper_header = _norm("static int rbt_validar_altura_negra(RBT nodo, RBT padreEsperado, int tieneMin, int minimo, int tieneMax, int maximo) {")
    delegate = _norm("return rbt_validar_altura_negra(raiz, NULL, 0, 0, 0, 0) != 0;")
    left_call = _norm("int bhIzq = rbt_validar_altura_negra(nodo->izq, nodo, tieneMin, minimo, 1, nodo->nro);")
    right_call = _norm("int bhDer = rbt_validar_altura_negra(nodo->der, nodo, 1, nodo->nro, tieneMax, maximo);")

    assert lines.count(header) == 1
    delegate_steps = [step for step in result["execution_trace"]["steps"]
                      if _norm(step["line_text"]) == delegate]
    assert [step["debug"]["stage"] for step in delegate_steps] == ["call", "resume", "return"]
    assert lines.count(helper_header) > 1
    assert lines.count(left_call) >= 5
    assert lines.count(right_call) >= 5
    assert result.get("result") is True


def test_abb_contar_hojas_trace_expands_recursive_calls() -> None:
    """ABB contar_hojas should recurse on both branches before final aggregation."""
    history: list[dict] = []
    for value in (60, 50, 70, 40, 55):
        out = _run_hier_op("abb", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("abb", history, "contar_hojas", {})
    assert result["success"] is True
    lines = _trace_lines(result)

    header = _norm("int abb_contarHojas(ABBNodo* nodo) {")
    aggregate = _norm("return abb_contarHojas(nodo->izquierdo) + abb_contarHojas(nodo->derecho);")

    assert lines.count(header) > 1
    assert lines.count(aggregate) >= 1


def test_abb_validar_trace_expands_recursive_calls() -> None:
    """ABB validar should recurse in both branches with early-return guards."""
    history: list[dict] = []
    for value in (60, 50, 70, 40, 55):
        out = _run_hier_op("abb", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("abb", history, "validar", {})
    assert result["success"] is True
    lines = _trace_lines(result)

    header = _norm("int abb_validar_rango(ABBNodo* nodo, int hay_minimo, int minimo, int hay_maximo, int maximo) {")
    left_call = _norm("if (!abb_validar_rango(nodo->izquierdo, hay_minimo, minimo, 1, nodo->valor)) {")
    right_call = _norm("if (!abb_validar_rango(nodo->derecho, 1, nodo->valor, hay_maximo, maximo)) {")

    assert lines.count(header) > 1
    assert left_call in lines
    assert right_call in lines


def test_abb_limpiar_trace_expands_recursive_postorder_free() -> None:
    """ABB limpiar should recurse postorder and execute one free per node."""
    history: list[dict] = []
    values = (8, 7, 9, 6, 10, 5)
    for value in values:
        out = _run_hier_op("abb", history, "insertar", {"value": str(value)})
        history = out["history"]

    result = _run_hier_op("abb", history, "limpiar", {})
    assert result["success"] is True
    lines = _trace_lines(result)

    header = _norm("void abb_liberarArbol(ABBNodo* nodo) {")
    left_call = _norm("abb_liberarArbol(nodo->izquierdo);")
    right_call = _norm("abb_liberarArbol(nodo->derecho);")
    free_line = _norm("free(nodo);")

    assert lines.count(header) > 1
    assert left_call in lines
    assert right_call in lines
    assert lines.count(free_line) == len(values)
