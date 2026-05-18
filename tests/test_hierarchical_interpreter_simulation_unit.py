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
    """Duplicate red-black insert should return before allocation and re-balance calls."""
    history: list[dict] = []
    first = _run_hier_op("red_black", history, "insertar", {"value": "10"})
    history = first["history"]

    duplicate = _run_hier_op("red_black", history, "insertar", {"value": "10"})
    assert duplicate["success"] is False

    lines = _trace_lines(duplicate)
    idx_if_actual = lines.index(_norm("if (actual != NULL)"))
    idx_return = lines.index(_norm("return;"), idx_if_actual)
    tail = lines[idx_return + 1 :]

    assert _norm("actual = malloc(sizeof(struct nodorbt));") not in tail
    assert _norm("rbt_insercion_caso1(actual, arbol);") not in tail


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

    changed_indexes = [
        idx
        for idx, step in enumerate(steps)
        if (step.get("state_snapshot") or {}) != (step.get("state_after") or {})
    ]
    assert changed_indexes, "La traza no refleja ningun cambio de estado."
    first_changed = steps[changed_indexes[0]]
    changed_line = _norm(first_changed.get("line_text", ""))

    assert changed_line in {
        _norm("*arbol = actual;"),
        _norm("padre->izq = actual;"),
        _norm("padre->der = actual;"),
    }

def test_abb_empty_insert_keeps_tree_empty_until_value_assignment_step() -> None:
    """Root insertion must appear only when value assignment executes, not before."""
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
    assert values_from_state(assignment_after) == [55]


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

    changed_indexes = [
        idx for idx, step in enumerate(steps)
        if (step.get("state_snapshot") or {}) != (step.get("state_after") or {})
    ]
    assert changed_indexes, "La traza no refleja ningun cambio de estado."
    first_changed_step = steps[changed_indexes[0]]
    line = _norm(first_changed_step.get("line_text", ""))

    # La mutacion visible debe ocurrir al enlazar el nuevo nodo al arbol.
    assert line in {
        _norm("padre->izq = nuevo;"),
        _norm("padre->der = nuevo;"),
        _norm("*raiz = nuevo;"),
    }


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

    changed_indexes = [
        idx for idx, step in enumerate(steps)
        if (step.get("state_snapshot") or {}) != (step.get("state_after") or {})
    ]
    assert len(changed_indexes) == 1


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
    assert any(dbg.get("stage") == "result" for dbg in debug_steps)


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
    left_call = _norm("rbt_inorden(nodo->rbt_izq);")
    right_call = _norm("rbt_inorden(nodo->rbt_der);")
    visit = _norm('printf("%d ", nodo->rbt_dato);')

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
    left_call = _norm("if (!rbt_validar(raiz->rbt_izq)) {")
    right_call = _norm("if (!rbt_validar(raiz->rbt_der)) {")

    assert lines.count(header) > 1
    assert left_call in lines
    assert right_call in lines


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

    header = _norm("int abb_validar_rango(ABBNodo* nodo, int minimo, int maximo) {")
    left_call = _norm("if (!abb_validar_rango(nodo->izquierdo, minimo, nodo->valor)) {")
    right_call = _norm("if (!abb_validar_rango(nodo->derecho, nodo->valor, maximo)) {")

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
