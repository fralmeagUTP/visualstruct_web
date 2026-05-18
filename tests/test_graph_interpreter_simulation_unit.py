"""Unit tests focused on graph interpreter simulation behavior."""

from __future__ import annotations

from app.services.graph_structure_service import GraphStructureService


def _run_graph_op(history: list[dict], operation: str, payload: dict) -> dict:
    return GraphStructureService.execute_operation(
        structure_id="graph",
        operation_name=operation,
        payload=payload,
        history=history,
    )


def _norm(line: str) -> str:
    return " ".join(str(line).strip().lower().split())


def _trace_lines(result: dict) -> list[str]:
    return [_norm(step.get("line_text", "")) for step in result["execution_trace"]["steps"]]


def test_graph_trace_contract_for_mutating_operation_insert_edge() -> None:
    """Trace for a mutating graph op must expose state transitions and final consistency."""
    history: list[dict] = []

    create = _run_graph_op(history, "create_graph", {"directed": "false"})
    history = create["history"]

    result = _run_graph_op(history, "insert_edge", {"origin": "1", "target": "2", "weight": "7"})

    assert result["success"] is True
    trace = result["execution_trace"]
    steps = trace["steps"]
    assert steps
    assert trace["final_state"] == result["visual_state"]

    # Must show at least one state change across the trace for a mutating op.
    snapshots = [step["state_snapshot"]["metadata"]["edges_count"] for step in steps]
    afters = [step["state_after"]["metadata"]["edges_count"] for step in steps]
    assert max(afters) >= max(snapshots)
    assert result["visual_state"]["metadata"]["edges_count"] == 1


def test_graph_trace_bfs_keeps_statement_order_before_condition_checks() -> None:
    """Interpreter trace should preserve C statement order inside BFS loop."""
    history: list[dict] = []
    history = _run_graph_op(history, "create_graph", {"directed": "false"})["history"]
    history = _run_graph_op(history, "insert_edge", {"origin": "1", "target": "2", "weight": "1"})["history"]

    bfs = _run_graph_op(history, "run_bfs", {"start": "1"})
    assert bfs["success"] is True

    lines = _trace_lines(bfs)
    idx_decl_actual = lines.index(_norm("int actual = cola_desencolar(&cola);"))
    idx_if_actual = lines.index(_norm("if (actual == -1) {"))
    idx_decl_tmp = lines.index(_norm("ListaVertice tmp = (ListaVertice) malloc(sizeof(struct NodoV));"))
    idx_if_tmp = lines.index(_norm("if (tmp == NULL) continue;"))

    assert idx_decl_actual < idx_if_actual, "Se evalua 'actual' antes de asignarlo en la traza."
    assert idx_decl_tmp < idx_if_tmp, "Se evalua 'tmp' antes de reservar memoria en la traza."


def test_graph_trace_bfs_repeats_loop_blocks_for_multiple_visits() -> None:
    """BFS interpreter must iterate queue/successor loops, not just show them once."""
    history: list[dict] = []
    history = _run_graph_op(history, "create_graph", {"directed": "false"})["history"]
    history = _run_graph_op(history, "insert_edge", {"origin": "1", "target": "2", "weight": "1"})["history"]
    history = _run_graph_op(history, "insert_edge", {"origin": "1", "target": "3", "weight": "1"})["history"]
    history = _run_graph_op(history, "insert_edge", {"origin": "2", "target": "4", "weight": "1"})["history"]

    bfs = _run_graph_op(history, "run_bfs", {"start": "1"})
    assert bfs["success"] is True
    lines = _trace_lines(bfs)

    assert lines.count(_norm("while (cola.delante != NULL) {")) > 1
    assert lines.count(_norm("while (suces != NULL) {")) > 1
    assert lines.count(_norm("if (!grafo_marcado_vertice(g, suces->dato)) {")) > 1


def test_graph_trace_bfs_stops_after_return_when_start_vertex_does_not_exist() -> None:
    """If BFS hits `if (!existe) return NULL;` trace must stop the subroutine there."""
    history: list[dict] = []
    history = _run_graph_op(history, "create_graph", {"directed": "false"})["history"]

    bfs = _run_graph_op(history, "run_bfs", {"start": "99"})
    assert bfs["success"] is False

    lines = _trace_lines(bfs)
    return_idx = lines.index(_norm("if (!existe) return NULL;"))
    tail = lines[return_idx + 1 :]

    assert _norm("cola_encolar(&cola, inicio);") not in tail
    assert _norm("while (cola.delante != NULL) {") not in tail


def test_graph_trace_dijkstra_unreachable_stops_before_path_reconstruction() -> None:
    """When there is no route, Dijkstra trace should not execute path reconstruction block."""
    history: list[dict] = []
    history = _run_graph_op(history, "create_graph", {"directed": "false"})["history"]
    history = _run_graph_op(history, "insert_vertex", {"vertex": "1"})["history"]
    history = _run_graph_op(history, "insert_vertex", {"vertex": "2"})["history"]

    dij = _run_graph_op(history, "run_dijkstra", {"start": "1", "end": "2"})
    assert dij["success"] is True
    assert "no existe ruta" in str(dij["message"]).lower()

    lines = _trace_lines(dij)
    assert _norm("return NULL;") in lines

    # This block belongs to successful path reconstruction and must not run on unreachable cases.
    assert _norm("while (prev[destino] != -1) {") not in lines
    assert _norm("nuevo->origen = vertices[prev[destino]];") not in lines


def test_graph_trace_dijkstra_keeps_for_loop_order_before_j_condition() -> None:
    """Interpreter should not evaluate `if (!visitado[j]...)` before `for (j...)` exists."""
    history: list[dict] = []
    history = _run_graph_op(history, "create_graph", {"directed": "false"})["history"]
    history = _run_graph_op(history, "insert_edge", {"origin": "1", "target": "2", "weight": "3"})["history"]

    dij = _run_graph_op(history, "run_dijkstra", {"start": "1", "end": "2"})
    assert dij["success"] is True

    lines = _trace_lines(dij)
    idx_for_j = lines.index(_norm("for (j = 0; j < n; j++) {"))
    idx_if_j = lines.index(_norm("if (!visitado[j] && dist[j] < min) {"))

    assert idx_for_j < idx_if_j, "La condicion de j aparece antes del for(j) en la traza."


def test_graph_trace_dfs_expands_recursive_subroutine_and_uses_real_edges() -> None:
    """DFS trace must include recursive helper calls and only valid traversal-tree edges."""
    history: list[dict] = []
    history = _run_graph_op(history, "create_graph", {"directed": "false"})["history"]
    history = _run_graph_op(history, "insert_edge", {"origin": "1", "target": "2", "weight": "1"})["history"]
    history = _run_graph_op(history, "insert_edge", {"origin": "2", "target": "4", "weight": "1"})["history"]
    history = _run_graph_op(history, "insert_edge", {"origin": "1", "target": "3", "weight": "1"})["history"]

    dfs = _run_graph_op(history, "run_dfs", {"start": "1"})
    assert dfs["success"] is True

    trace = dfs["execution_trace"]
    lines = _trace_lines(dfs)
    assert "void grafo_dfs_recursivo(grafo g, int actual, listavertice *recorrido) {" in lines
    assert lines.count(_norm("grafo_dfs_recursivo(g, suces->dato, recorrido);")) >= 2
    assert "grafo_dfs_recursivo(g, inicio, &recorrido);" in lines

    state_edges = dfs["visual_state"]["edges"]
    valid_edges: set[tuple[str, str]] = set()
    for edge in state_edges:
        source = str(edge["source"])
        target = str(edge["target"])
        valid_edges.add((source, target))
        valid_edges.add((target, source))

    for step in trace["steps"]:
        debug = step.get("debug")
        if not isinstance(debug, dict):
            continue
        progress = debug.get("graph_progress")
        if not isinstance(progress, dict):
            continue
        for edge in progress.get("edges", []):
            assert isinstance(edge, list) and len(edge) == 2
            src = str(edge[0])
            dst = str(edge[1])
            assert (src, dst) in valid_edges, f"DFS destaca arista inexistente: {src}->{dst}"


def test_graph_trace_bfs_uses_existing_edges_in_progress() -> None:
    """BFS graph_progress must highlight only edges that exist in the current graph."""
    history: list[dict] = []
    history = _run_graph_op(history, "create_graph", {"directed": "false"})["history"]
    history = _run_graph_op(history, "generate_random_graph", {"vertices_count": "7", "seed": "484589473"})["history"]

    bfs = _run_graph_op(history, "run_bfs", {"start": "1"})
    assert bfs["success"] is True

    valid_edges: set[tuple[str, str]] = set()
    for edge in bfs["visual_state"]["edges"]:
        source = str(edge["source"])
        target = str(edge["target"])
        valid_edges.add((source, target))
        valid_edges.add((target, source))

    for step in bfs["execution_trace"]["steps"]:
        debug = step.get("debug")
        if not isinstance(debug, dict):
            continue
        progress = debug.get("graph_progress")
        if not isinstance(progress, dict):
            continue
        for edge in progress.get("edges", []):
            assert isinstance(edge, list) and len(edge) == 2
            src = str(edge[0])
            dst = str(edge[1])
            assert (src, dst) in valid_edges, f"BFS destaca arista inexistente: {src}->{dst}"


def test_graph_trace_kruskal_respects_loops_conditions_and_taken_branches() -> None:
    """Kruskal trace must reflect iterative control-flow and executed branch lines."""
    history: list[dict] = []
    history = _run_graph_op(history, "create_graph", {"directed": "false"})["history"]
    history = _run_graph_op(history, "generate_random_graph", {"vertices_count": "7", "seed": "484589473"})["history"]

    kr = _run_graph_op(history, "run_kruskal", {})
    assert kr["success"] is True

    lines = _trace_lines(kr)
    mst_edges = kr["result"].get("mst_edges", [])
    mst_count = len(mst_edges) if isinstance(mst_edges, list) else 0

    assert lines.count(_norm("for (int j = 0; j < i; j++) {")) > 1
    assert lines.count(_norm("if (u != -1 && v != -1 && grafo_encontrar_conjunto(&conjuntos, u) != grafo_encontrar_conjunto(&conjuntos, v)) {")) >= 1
    assert lines.count(_norm("grafo_unir_conjuntos(&conjuntos, u, v);")) >= max(1, mst_count // 2)
    assert _norm("return mst;") in lines


def test_graph_trace_dijkstra_respects_main_loops_and_returns() -> None:
    """Dijkstra trace must show iterative control-flow and final return path."""
    history: list[dict] = []
    history = _run_graph_op(history, "create_graph", {"directed": "false"})["history"]
    history = _run_graph_op(history, "generate_random_graph", {"vertices_count": "7", "seed": "484589473"})["history"]

    dij = _run_graph_op(history, "run_dijkstra", {"start": "1", "end": "4"})
    assert dij["success"] is True

    lines = _trace_lines(dij)
    assert lines.count(_norm("for (i = 0; i < n; i++) {")) >= 2
    assert lines.count(_norm("for (j = 0; j < n; j++) {")) >= 2
    assert lines.count(_norm("if (!visitado[j] && dist[j] < min) {")) >= 2
    assert lines.count(_norm("while (suces != NULL) {")) >= 2
    assert lines.count(_norm("if (v != -1 && !visitado[v]) {")) >= 2
    assert _norm("return camino;") in lines


def test_graph_trace_bellman_ford_respects_relax_passes_and_cycle_detection_branch() -> None:
    """Bellman-Ford trace must reflect pass loops and negative-cycle return branch."""
    history: list[dict] = []
    history = _run_graph_op(history, "create_graph", {"directed": "false"})["history"]
    history = _run_graph_op(history, "generate_random_graph", {"vertices_count": "7", "seed": "484589473"})["history"]

    bf = _run_graph_op(history, "run_bellman_ford", {"start": "1", "end": "4"})
    assert bf["success"] is True
    lines = _trace_lines(bf)
    assert lines.count(_norm("for (i = 0; i < n - 1; i++) {")) >= 2
    assert lines.count(_norm("while (a != NULL) {")) >= 2
    assert lines.count(_norm("if (u != -1 && v != -1 && dist[u] != INT_MAX) {")) >= 2
    assert _norm("return camino;") in lines

    # Caso dirigido con ciclo negativo para validar rama de retorno temprano.
    history = []
    history = _run_graph_op(history, "create_graph", {"directed": "true"})["history"]
    for vertex in ("1", "2", "3"):
        history = _run_graph_op(history, "insert_vertex", {"vertex": vertex})["history"]
    for payload in (
        {"origin": "1", "target": "2", "weight": "1"},
        {"origin": "2", "target": "3", "weight": "-3"},
        {"origin": "3", "target": "1", "weight": "1"},
    ):
        history = _run_graph_op(history, "insert_edge", payload)["history"]

    bf_neg = _run_graph_op(history, "run_bellman_ford", {"start": "1", "end": "3"})
    assert bf_neg["success"] is True
    neg_lines = _trace_lines(bf_neg)
    assert _norm("printf(\"Se detecto un ciclo negativo.\\n\");") in neg_lines
    assert _norm("return NULL;") in neg_lines
