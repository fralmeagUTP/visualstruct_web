"""Contract tests for interpreter execution traces across all modules."""

from __future__ import annotations

import json

from app.services.execution_trace_service import ExecutionTraceService


def _assert_execution_trace_payload(data: dict) -> None:
    trace = data.get("execution_trace")
    assert isinstance(trace, dict)
    assert isinstance(trace.get("operation_name"), str)
    assert isinstance(trace.get("code_title"), str)
    assert isinstance(trace.get("source_code"), str)
    assert isinstance(trace.get("steps"), list)
    assert len(trace["steps"]) >= 1
    assert isinstance(trace.get("final_state"), dict)

    first = trace["steps"][0]
    assert isinstance(first.get("step_index"), int)
    assert isinstance(first.get("line_index"), int)
    assert isinstance(first.get("line_text"), str)
    assert "state_snapshot" in first

    last = trace["steps"][-1]
    assert "state_after" in last
    assert trace["final_state"] == data["visual_state"]


def _assert_step_debug_progression(data: dict) -> None:
    trace = data["execution_trace"]
    steps = trace["steps"]
    assert steps, "La traza debe contener pasos."

    state_markers = []
    for step in steps:
        assert "state_snapshot" in step
        assert "state_after" in step
        state_markers.append(json.dumps(step["state_after"], sort_keys=True, ensure_ascii=False))

    unique_state_count = len(set(state_markers))
    assert unique_state_count >= 2, "La simulacion paso a paso debe incluir cambios de estado durante la traza."


def test_sequential_operation_includes_execution_trace(client) -> None:
    response = client.post(
        "/sequential/stack/operate",
        json={"operation": "apilar", "payload": {"value": "42"}},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    _assert_execution_trace_payload(data)
    _assert_step_debug_progression(data)


def test_hierarchical_operation_includes_execution_trace(client) -> None:
    warmup = client.post(
        "/hierarchical/abb/operate",
        json={"operation": "insertar", "payload": {"value": "42"}},
    )
    assert warmup.status_code == 200
    assert warmup.get_json()["success"] is True

    response = client.post(
        "/hierarchical/abb/operate",
        json={"operation": "insertar", "payload": {"value": "21"}},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    _assert_execution_trace_payload(data)
    _assert_step_debug_progression(data)
    debug_steps = [step for step in data["execution_trace"]["steps"] if isinstance(step.get("debug"), dict)]
    assert debug_steps
    assert isinstance(debug_steps[0]["debug"].get("path_keys"), list)


def test_graph_operation_includes_execution_trace(client) -> None:
    response = client.post(
        "/graph/graph/operate",
        json={"operation": "insert_vertex", "payload": {"vertex": "7"}},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    _assert_execution_trace_payload(data)
    _assert_step_debug_progression(data)


def test_hash_operation_includes_execution_trace(client) -> None:
    response = client.post(
        "/hash/hash_table/operate",
        json={"operation": "insert", "payload": {"key": "A", "value": "1"}},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    _assert_execution_trace_payload(data)
    _assert_step_debug_progression(data)


def test_avl_trace_includes_rebalance_debug_metadata(client) -> None:
    for value in ("30", "20"):
        warmup = client.post(
            "/hierarchical/avl/operate",
            json={"operation": "insertar", "payload": {"value": value}},
        )
        assert warmup.status_code == 200
        assert warmup.get_json()["success"] is True

    response = client.post(
        "/hierarchical/avl/operate",
        json={"operation": "insertar", "payload": {"value": "10"}},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    trace = data["execution_trace"]
    stages = [
        step.get("debug", {}).get("stage")
        for step in trace["steps"]
        if isinstance(step.get("debug"), dict)
    ]
    assert "rebalance" in stages or "post_rebalance" in stages
    has_rotation_hint = any(
        isinstance(step.get("debug"), dict) and isinstance(step["debug"].get("rotation_hint"), dict)
        for step in trace["steps"]
    )
    assert has_rotation_hint


def test_graph_algorithm_trace_includes_semantic_debug_steps(client) -> None:
    for vertex in ("1", "2", "3"):
        response = client.post(
            "/graph/graph/operate",
            json={"operation": "insert_vertex", "payload": {"vertex": vertex}},
        )
        assert response.status_code == 200
        assert response.get_json()["success"] is True

    edge_payloads = (
        {"origin": "1", "target": "2", "weight": "1"},
        {"origin": "2", "target": "3", "weight": "1"},
    )
    for payload in edge_payloads:
        response = client.post(
            "/graph/graph/operate",
            json={"operation": "insert_edge", "payload": payload},
        )
        assert response.status_code == 200
        assert response.get_json()["success"] is True

    response = client.post(
        "/graph/graph/operate",
        json={"operation": "run_bfs", "payload": {"start": "1"}},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

    steps = data["execution_trace"]["steps"]
    debug_steps = [step for step in steps if isinstance(step.get("debug"), dict)]
    assert debug_steps
    assert any(step["debug"].get("stage") in {"visit", "complete"} for step in debug_steps)
    assert any(
        isinstance(step["debug"].get("graph_progress"), dict)
        and step["debug"]["graph_progress"].get("mode") == "traversal"
        for step in debug_steps
    )
    assert "grafo_bfs" in data["execution_trace"]["source_code"]
    normalized_lines = [str(step.get("line_text", "")).strip().lower() for step in steps]
    assert "while (cola.delante != null) {" in normalized_lines
    assert "while (suces != null) {" in normalized_lines


def test_graph_dfs_trace_includes_recursive_subroutine_source_and_calls(client) -> None:
    for vertex in ("1", "2", "3", "4"):
        response = client.post(
            "/graph/graph/operate",
            json={"operation": "insert_vertex", "payload": {"vertex": vertex}},
        )
        assert response.status_code == 200
        assert response.get_json()["success"] is True

    for payload in (
        {"origin": "1", "target": "2", "weight": "1"},
        {"origin": "2", "target": "4", "weight": "1"},
        {"origin": "1", "target": "3", "weight": "1"},
    ):
        response = client.post(
            "/graph/graph/operate",
            json={"operation": "insert_edge", "payload": payload},
        )
        assert response.status_code == 200
        assert response.get_json()["success"] is True

    response = client.post(
        "/graph/graph/operate",
        json={"operation": "run_dfs", "payload": {"start": "1"}},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "grafo_dfs_recursivo" in data["execution_trace"]["source_code"]

    normalized_lines = [str(step.get("line_text", "")).strip().lower() for step in data["execution_trace"]["steps"]]
    assert "grafo_dfs_recursivo(g, inicio, &recorrido);" in normalized_lines
    assert normalized_lines.count("grafo_dfs_recursivo(g, suces->dato, recorrido);") >= 2

def test_stack_stepwise_change_happens_on_mutation_line(client) -> None:
    response = client.post(
        "/sequential/stack/operate",
        json={"operation": "apilar", "payload": {"value": "9"}},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

    steps = data["execution_trace"]["steps"]
    assert steps
    previous_size = steps[0]["state_snapshot"].get("size", 0)
    first_change = None
    for step in steps:
        current_size = step["state_after"].get("size", previous_size)
        if current_size != previous_size:
            first_change = step
            break
        previous_size = current_size

    assert first_change is not None
    trace = data["execution_trace"]
    assert "pila_apilar" in trace["source_code"]
    normalized_lines = [str(step.get("line_text", "")).strip().lower() for step in steps]
    assert "*p = aux;" in normalized_lines
    assert any("aux->nro = valor;" in line for line in normalized_lines)
    assert "*" not in normalized_lines
    assert not any(line == "return false;" for line in normalized_lines)


def test_stack_success_trace_skips_defensive_return_false_lines(client) -> None:
    response = client.post(
        "/sequential/stack/operate",
        json={"operation": "apilar", "payload": {"value": "11"}},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    lines = [str(step.get("line_text", "")).strip().lower() for step in data["execution_trace"]["steps"]]
    assert "return false;" not in lines
    assert not any("error: pila no inicializada" in line for line in lines)
    assert not any("error: no se pudo asignar memoria" in line for line in lines)


def test_linked_list_trace_stops_after_return_in_insertar_elemento(client) -> None:
    warmup = client.post(
        "/sequential/linked_list/operate",
        json={"operation": "insertar_final", "payload": {"value": "10"}},
    )
    assert warmup.status_code == 200
    assert warmup.get_json()["success"] is True

    response = client.post(
        "/sequential/linked_list/operate",
        json={"operation": "lista_insertar_elemento", "payload": {"value": "8", "position": "1"}},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

    lines = [str(step.get("line_text", "")).strip().lower() for step in data["execution_trace"]["steps"]]
    assert not any("error...posicion no encontrada" in line for line in lines)
    assert "free(q);" not in lines


def test_control_flow_filter_keeps_only_taken_error_branch() -> None:
    lines = [
        "int cola_desencolar(struct Cola *q) {",
        "if (q == NULL || q->delante == NULL) {",
        '    printf("Cola vacía. No se puede desencolar.\\n");',
        "    return -1;  // Valor de error",
        "}",
        "struct NodoCola *aux = q->delante;",
        "int num = aux->nro;",
        "q->delante = aux->sgte;",
    ]
    executable = list(range(len(lines)))
    filtered = ExecutionTraceService._filter_trace_lines_by_control_flow(
        lines=lines,
        executable_indexes=executable,
        success=False,
        message="Cola vacía. No se puede desencolar.",
    )
    filtered_lines = [lines[idx].strip().lower() for idx in filtered]
    assert 'printf("cola vacía. no se puede desencolar.\\n");' in filtered_lines
    assert "return -1;  // valor de error" in filtered_lines
    assert "int num = aux->nro;" not in filtered_lines
    assert "q->delante = aux->sgte;" not in filtered_lines


def test_dijkstra_trace_includes_fine_grained_debug_stages(client) -> None:
    for vertex in ("1", "2", "3"):
        response = client.post(
            "/graph/graph/operate",
            json={"operation": "insert_vertex", "payload": {"vertex": vertex}},
        )
        assert response.status_code == 200
        assert response.get_json()["success"] is True

    for payload in (
        {"origin": "1", "target": "2", "weight": "2"},
        {"origin": "2", "target": "3", "weight": "3"},
    ):
        response = client.post(
            "/graph/graph/operate",
            json={"operation": "insert_edge", "payload": payload},
        )
        assert response.status_code == 200
        assert response.get_json()["success"] is True

    response = client.post(
        "/graph/graph/operate",
        json={"operation": "run_dijkstra", "payload": {"start": "1", "end": "3"}},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    stages = [
        step.get("debug", {}).get("stage")
        for step in data["execution_trace"]["steps"]
        if isinstance(step.get("debug"), dict)
    ]
    assert "extract_min" in stages
    assert "relax_edge" in stages
    assert "update_distance" in stages
    assert "grafo_dijkstra" in data["execution_trace"]["source_code"]
    normalized_lines = [str(step.get("line_text", "")).strip().lower() for step in data["execution_trace"]["steps"]]
    outer_for_count = normalized_lines.count("for (i = 0; i < n; i++) {")
    inner_for_count = normalized_lines.count("for (j = 0; j < n; j++) {")
    assert outer_for_count >= 2
    assert inner_for_count >= 1


def test_bellman_ford_negative_cycle_trace_includes_detection_stage(client) -> None:
    create_response = client.post(
        "/graph/graph/operate",
        json={"operation": "create_graph", "payload": {"directed": "true"}},
    )
    assert create_response.status_code == 200
    assert create_response.get_json()["success"] is True

    for vertex in ("1", "2", "3"):
        response = client.post(
            "/graph/graph/operate",
            json={"operation": "insert_vertex", "payload": {"vertex": vertex}},
        )
        assert response.status_code == 200
        assert response.get_json()["success"] is True

    for payload in (
        {"origin": "1", "target": "2", "weight": "1"},
        {"origin": "2", "target": "3", "weight": "-3"},
        {"origin": "3", "target": "1", "weight": "1"},
    ):
        response = client.post(
            "/graph/graph/operate",
            json={"operation": "insert_edge", "payload": payload},
        )
        assert response.status_code == 200
        assert response.get_json()["success"] is True

    response = client.post(
        "/graph/graph/operate",
        json={"operation": "run_bellman_ford", "payload": {"start": "1", "end": "3"}},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    stages = [
        step.get("debug", {}).get("stage")
        for step in data["execution_trace"]["steps"]
        if isinstance(step.get("debug"), dict)
    ]
    assert "detect_negative_cycle" in stages
