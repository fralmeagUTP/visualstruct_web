"""Unit tests focused on graph interpreter simulation behavior."""

from __future__ import annotations

from app.services.graph_structure_service import GraphStructureService


def _run_graph_op(history: list[dict], operation: str, payload: dict, *, trace=False) -> dict:
    return GraphStructureService.execute_operation(
        structure_id="graph",
        operation_name=operation,
        payload=payload,
        history=history,
        execution_mode='step' if trace or operation.startswith('run_') else 'normal',
    )


def _norm(line: str) -> str:
    return " ".join(str(line).strip().lower().split())


def _trace_lines(result: dict) -> list[str]:
    return [_norm(step.get("line_text", "")) for step in result["execution_trace"]["steps"]]


def _dense_budget_and_sparse_trace(history, operation, payload):
    """Keep the dense seven-vertex fixture as a real budget regression, then
    inspect complete control flow on a seven-vertex sparse connected graph.
    """
    rejected = _run_graph_op(history, operation, payload)
    assert rejected['success'] is False and rejected['trace_available'] is False
    assert rejected['preserve_session'] is True and rejected['execution_trace'] is None
    assert rejected['history'] == history and rejected['trace_event_limit'] == 4000
    normal = GraphStructureService.execute_operation('graph',operation,payload,history,execution_mode='normal')
    assert normal['success'] is True and normal['execution_trace'] is None
    assert normal['visual_state']['metadata']['vertices_count'] == 7
    assert normal['history'][:-1] == history
    # Bellman-Ford needs a directed chain to keep the complete seven-vertex
    # control-flow trace inside the same public event budget.
    sparse = _run_graph_op([], 'create_graph', {'directed':operation == 'run_bellman_ford'})['history']
    for vertex in range(1,8):
        sparse = _run_graph_op(sparse, 'insert_vertex', {'vertex':vertex})['history']
    for vertex in range(1,7):
        sparse = _run_graph_op(sparse, 'insert_edge', {'origin':vertex,'target':vertex+1,'weight':1})['history']
    result = _run_graph_op(sparse, operation, payload)
    assert result['success'] is True and result['trace_available'] is True
    assert result['visual_state']['metadata']['vertices_count'] == 7
    return result


def test_graph_trace_contract_for_mutating_operation_insert_edge() -> None:
    """Trace for a mutating graph op must expose state transitions and final consistency."""
    history: list[dict] = []

    create = _run_graph_op(history, "create_graph", {"directed": "false"})
    history = create["history"]

    result = _run_graph_op(history, "insert_edge", {"origin": "1", "target": "2", "weight": "7"}, trace=True)

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
    steps = bfs["execution_trace"]["steps"]
    actual = lines.index(_norm('int u = t.prev[frente++];'))
    idx_decl_tmp = lines.index(_norm('correcto = agregar_visita(&lista, &ultimo, t.vertices[u]);'))
    idx_if_tmp = lines.index(_norm('if (!correcto) break;'))
    idx_queue_guard = lines.index(_norm('while (frente < final && correcto) {'))
    assert idx_queue_guard < actual < idx_decl_tmp < idx_if_tmp
    assert _norm("if (actual == -1) {") not in lines
    condition=next(step for step in steps if _norm(step['line_text'])==_norm('if (!correcto) break;') and step['pedagogy']['instruction_event']['phase']=='condition')
    assert condition['pedagogy']['condition']['result'] is False


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

    assert lines.count(_norm('while (frente < final && correcto) {')) > 1
    assert lines.count(_norm('for (ListaVertice p = suces; p != NULL; p = p->sig) {')) > 1
    assert lines.count(_norm('if (v >= 0 && !t.usado[v]) {')) > 1


def test_graph_trace_bfs_stops_after_return_when_start_vertex_does_not_exist() -> None:
    """Absent starts execute C and report status without traversing fictitious nodes."""
    history: list[dict] = []
    history = _run_graph_op(history, "create_graph", {"directed": "false"})["history"]

    bfs = _run_graph_op(history, "run_bfs", {"start": "99"})
    assert bfs["success"] is False

    lines = _trace_lines(bfs)
    assert bfs['c_status']==2 and bfs['execution_trace']['execution_started'] is True
    assert bfs['history'][:-1]==history and bfs['history'][-1]['source_contract']=='graph-book/v1'
    assert any(step['pedagogy']['instruction_event']['function']=='grafo_bfs' for step in bfs['execution_trace']['steps'])
    assert bfs['execution_trace']['steps'][-1]['pedagogy']['memory_state']['frames']==[]
    assert not any(_norm("cola_encolar(&cola, inicio);")==line for line in lines)
    assert _norm("while (cola.delante != NULL) {") not in lines


def test_graph_trace_dijkstra_unreachable_stops_before_path_reconstruction() -> None:
    """When there is no route, Dijkstra trace should not execute path reconstruction block."""
    history: list[dict] = []
    history = _run_graph_op(history, "create_graph", {"directed": "false"})["history"]
    history = _run_graph_op(history, "insert_vertex", {"vertex": "1"})["history"]
    history = _run_graph_op(history, "insert_vertex", {"vertex": "2"})["history"]

    dij = _run_graph_op(history, "run_dijkstra", {"start": "1", "end": "2"})
    assert dij["success"] is False and dij['c_status']==2

    lines = _trace_lines(dij)
    assert any('grafo_no_existe' in line for line in lines)

    # This block belongs to successful path reconstruction and must not run on unreachable cases.
    assert _norm('while (d != s) {') not in lines
    assert not any(step['pedagogy']['instruction_event']['function']=='reconstruir' and step['pedagogy']['instruction_event']['phase']=='allocate' for step in dij['execution_trace']['steps'])


def test_graph_trace_dijkstra_keeps_for_loop_order_before_j_condition() -> None:
    """Interpreter should not evaluate `if (!visitado[j]...)` before `for (j...)` exists."""
    history: list[dict] = []
    history = _run_graph_op(history, "create_graph", {"directed": "false"})["history"]
    history = _run_graph_op(history, "insert_edge", {"origin": "1", "target": "2", "weight": "3"})["history"]

    dij = _run_graph_op(history, "run_dijkstra", {"start": "1", "end": "2"})
    assert dij["success"] is True

    lines = _trace_lines(dij)
    idx_for_j = lines.index(_norm('for (int j = 0; j < t.n; j++)'))
    idx_if_j = next(i for i,line in enumerate(lines) if line.startswith('if (!t.usado[j] && t.alcanzable[j] &&'))

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
    assert any(step['pedagogy']['instruction_event']['function']=='grafo_dfs_recursivo' and step['pedagogy']['instruction_event']['phase']=='enter' for step in trace['steps'])
    assert lines.count(_norm('correcto = grafo_dfs_recursivo(g, t, v, lista, ultimo);')) >= 2
    assert _norm('int correcto = grafo_dfs_recursivo(g, &t, s, &lista, &ultimo);') in lines

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

    bfs = _dense_budget_and_sparse_trace(history, "run_bfs", {"start": "1"})
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

    kr = _dense_budget_and_sparse_trace(history, "run_kruskal", {})
    assert kr["success"] is True

    lines = _trace_lines(kr)
    mst_edges = kr["result"].get("mst_edges", [])
    mst_count = len(mst_edges) if isinstance(mst_edges, list) else 0

    assert lines.count(_norm('for (int j = 0; j < cantidad - i - 1; j++)')) > 1
    assert lines.count(_norm('if (grafo_encontrar_conjunto(&c, u) ==')) >= 1
    assert lines.count(_norm('grafo_unir_conjuntos(&c, u, v);')) >= mst_count
    assert _norm('return arbol;') in lines


def test_graph_trace_dijkstra_respects_main_loops_and_returns() -> None:
    """Dijkstra trace must show iterative control-flow and final return path."""
    history: list[dict] = []
    history = _run_graph_op(history, "create_graph", {"directed": "false"})["history"]
    history = _run_graph_op(history, "generate_random_graph", {"vertices_count": "7", "seed": "484589473"})["history"]

    dij = _run_graph_op(history, "run_dijkstra", {"start": "1", "end": "4"})
    assert dij["success"] is True

    lines = _trace_lines(dij)
    assert lines.count(_norm('for (int k = 0; k < t.n && e == GRAFO_OK; k++) {')) >= 2
    assert lines.count(_norm('for (int j = 0; j < t.n; j++)')) >= 2
    assert lines.count(_norm('if (!t.usado[j] && t.alcanzable[j] &&')) >= 2
    assert lines.count(_norm('for (ListaArco a = g.a; a != NULL; a = a->sig) {')) >= 2
    assert lines.count(_norm('if (t.usado[v]) continue;')) >= 2
    assert _norm("return camino;") in lines


def test_graph_trace_bellman_ford_respects_relax_passes_and_cycle_detection_branch() -> None:
    """Bellman-Ford trace must reflect pass loops and negative-cycle return branch."""
    from _book_frame_oracle import assert_book_body
    history: list[dict] = []
    history = _run_graph_op(history, "create_graph", {"directed": "false"})["history"]
    history = _run_graph_op(history, "generate_random_graph", {"vertices_count": "7", "seed": "484589473"})["history"]

    bf = _dense_budget_and_sparse_trace(history, "run_bellman_ford", {"start": "1", "end": "4"})
    assert bf["success"] is True
    lines = _trace_lines(bf)
    assert lines.count(_norm('for (int k = 0; k < t.n && e == GRAFO_OK; k++) {')) >= 2
    assert lines.count(_norm('for (ListaArco a = g.a; a != NULL; a = a->sig) {')) >= 2
    assert lines.count(_norm('if (!t.alcanzable[u]) continue;')) >= 2
    assert _norm("return camino;") in lines
    assert_book_body(bf)

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
    assert bf_neg["success"] is False
    assert bf_neg['c_status']==4 and bf_neg["history"][:-1] == history
    neg_lines = _trace_lines(bf_neg)
    assert any('e = grafo_ciclo_negativo' in line for line in neg_lines)
    assert not any(step['pedagogy']['instruction_event']['function']=='reconstruir' for step in bf_neg['execution_trace']['steps'])
    assert_book_body(bf_neg)
