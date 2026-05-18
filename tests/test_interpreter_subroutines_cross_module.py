"""Cross-module tests for C-code interpretation traces across TAD methods."""

from __future__ import annotations

from typing import Any, Callable

from app.services.graph_structure_service import GraphStructureService
from app.services.hash_structure_service import HashStructureService
from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.services.structure_service import StructureService


ServiceExec = Callable[[str, str, dict[str, Any], list[dict[str, Any]]], dict[str, Any]]


def _exec(
    service_exec: ServiceExec,
    structure_id: str,
    operation: str,
    payload: dict[str, Any],
    history: list[dict[str, Any]],
) -> dict[str, Any]:
    return service_exec(structure_id, operation, payload, history)


def _assert_trace_contract(result: dict[str, Any], *, context: str) -> None:
    trace = result.get("execution_trace")
    assert isinstance(trace, dict), f"{context}: execution_trace ausente."
    assert isinstance(trace.get("source_code"), str), f"{context}: source_code ausente."
    assert isinstance(trace.get("steps"), list), f"{context}: steps ausente."
    steps = trace["steps"]
    assert steps, f"{context}: traza vacia."
    assert trace.get("final_state") == result.get("visual_state"), f"{context}: final_state != visual_state."

    source_lines = trace.get("source_code", "").replace("\r\n", "\n").split("\n")
    for idx, step in enumerate(steps):
        assert isinstance(step.get("line_text"), str), f"{context}: step[{idx}] sin line_text string."
        assert isinstance(step.get("line_index"), int), f"{context}: step[{idx}] sin line_index entero."
        assert isinstance(step.get("state_snapshot"), dict), f"{context}: step[{idx}] sin state_snapshot."
        assert isinstance(step.get("state_after"), dict), f"{context}: step[{idx}] sin state_after."
        line_index = step["line_index"]
        assert 0 <= line_index < len(source_lines), f"{context}: line_index fuera de rango ({line_index})."
        assert source_lines[line_index].strip() == step["line_text"].strip(), (
            f"{context}: line_text no coincide con source_code en line_index={line_index}."
        )


def _visible_operations(view_model: dict[str, Any]) -> list[dict[str, Any]]:
    ops = view_model.get("operations") or []
    return [op for op in ops if not bool(op.get("hidden"))]


def _default_payload(operation_name: str, inputs: list[dict[str, Any]]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for field in inputs:
        name = str(field.get("name", ""))
        if name in {"value", "vertex", "start", "origin", "position", "parent"}:
            payload[name] = "1"
        elif name in {"target", "end", "child"}:
            payload[name] = "2"
        elif name == "priority":
            payload[name] = "1"
        elif name == "weight":
            payload[name] = "1"
        elif name == "relative":
            payload[name] = "0"
        elif name == "capacity":
            payload[name] = "17"
        elif name == "directed":
            payload[name] = "false"
        elif name == "key":
            payload[name] = "k1"
        elif name == "value" and field.get("type") == "text":
            payload[name] = "v1"
        elif field.get("type") == "text":
            payload[name] = "txt"
        else:
            payload[name] = "1"
    return payload


def _seed_history_sequential(structure_id: str) -> list[dict[str, Any]]:
    history: list[dict[str, Any]] = []
    seed_ops: dict[str, list[tuple[str, dict[str, Any]]]] = {
        "stack": [("apilar", {"value": "5"}), ("apilar", {"value": "10"})],
        "queue": [("encolar", {"value": "5"}), ("encolar", {"value": "10"})],
        "priority_queue": [
            ("encolar", {"value": "5", "priority": "2"}),
            ("encolar", {"value": "10", "priority": "1"}),
        ],
        "linked_list": [
            ("insertar_final", {"value": "5"}),
            ("insertar_final", {"value": "10"}),
            ("insertar_final", {"value": "15"}),
        ],
        "circular_list": [("insertar_final", {"value": "5"}), ("insertar_final", {"value": "10"})],
        "sublist": [("insertar_padre", {"parent": "1"}), ("insertar_hijo", {"parent": "1", "child": "2"})],
    }
    for op, payload in seed_ops.get(structure_id, []):
        result = _exec(StructureService.execute_operation, structure_id, op, payload, history)
        history = result["history"]
    return history


def _seed_history_hierarchical(structure_id: str) -> list[dict[str, Any]]:
    history: list[dict[str, Any]] = []
    seed_ops: dict[str, list[tuple[str, dict[str, Any]]]] = {
        "abb": [("insertar", {"value": "40"}), ("insertar", {"value": "20"}), ("insertar", {"value": "60"})],
        "avl": [("insertar", {"value": "40"}), ("insertar", {"value": "20"}), ("insertar", {"value": "60"})],
        "red_black": [("insertar", {"value": "40"}), ("insertar", {"value": "20"}), ("insertar", {"value": "60"})],
        "binary_heap": [("insertar", {"value": "40"}), ("insertar", {"value": "20"}), ("insertar", {"value": "60"})],
    }
    for op, payload in seed_ops.get(structure_id, []):
        result = _exec(HierarchicalStructureService.execute_operation, structure_id, op, payload, history)
        history = result["history"]
    return history


def _seed_history_graph() -> list[dict[str, Any]]:
    history: list[dict[str, Any]] = []
    seed = [
        ("create_graph", {"directed": "false"}),
        ("insert_vertex", {"vertex": "1"}),
        ("insert_vertex", {"vertex": "2"}),
        ("insert_vertex", {"vertex": "3"}),
        ("insert_edge", {"origin": "1", "target": "2", "weight": "1"}),
        ("insert_edge", {"origin": "2", "target": "3", "weight": "2"}),
    ]
    for op, payload in seed:
        result = _exec(GraphStructureService.execute_operation, "graph", op, payload, history)
        history = result["history"]
    return history


def _seed_history_hash() -> list[dict[str, Any]]:
    history: list[dict[str, Any]] = []
    seed = [
        ("create_table", {"capacity": "17"}),
        ("insert", {"key": "k1", "value": "v1"}),
        ("insert", {"key": "k2", "value": "v2"}),
    ]
    for op, payload in seed:
        result = _exec(HashStructureService.execute_operation, "hash_table", op, payload, history)
        history = result["history"]
    return history


def test_trace_contract_all_visible_sequential_methods() -> None:
    for structure_id in ("stack", "queue", "priority_queue", "linked_list", "circular_list", "sublist"):
        history = _seed_history_sequential(structure_id)
        vm = StructureService.get_view_model(structure_id, history)
        for op in _visible_operations(vm):
            op_name = op["name"]
            payload = _default_payload(op_name, op.get("inputs", []))
            if structure_id == "linked_list":
                if op_name in {"buscar_elemento", "eliminar_elemento", "eliminar_repetidos"}:
                    payload["value"] = "10"
                if op_name == "lista_insertar_elemento":
                    payload["position"] = "1"
            if structure_id == "circular_list" and op_name in {"eliminar_primero", "buscar_posiciones"}:
                payload["value"] = "10"
            if structure_id == "sublist":
                if op_name in {"insertar_hijo", "eliminar_hijo"}:
                    payload["parent"] = "1"
                    payload["child"] = "2"
                if op_name in {"eliminar_padre", "hijos_de"}:
                    payload["parent"] = "1"

            result = _exec(StructureService.execute_operation, structure_id, op_name, payload, history)
            _assert_trace_contract(result, context=f"sequential::{structure_id}::{op_name}")
            history = result["history"]


def test_trace_contract_all_visible_hierarchical_methods() -> None:
    for structure_id in ("abb", "avl", "red_black", "binary_heap"):
        history = _seed_history_hierarchical(structure_id)
        vm = HierarchicalStructureService.get_view_model(structure_id, history)
        for op in _visible_operations(vm):
            op_name = op["name"]
            payload = _default_payload(op_name, op.get("inputs", []))
            if op_name in {"buscar", "eliminar"}:
                payload["value"] = "20"
            if op_name == "insertar":
                payload["value"] = "55"

            result = _exec(HierarchicalStructureService.execute_operation, structure_id, op_name, payload, history)
            _assert_trace_contract(result, context=f"hierarchical::{structure_id}::{op_name}")
            history = result["history"]


def test_trace_contract_all_visible_graph_methods() -> None:
    history = _seed_history_graph()
    vm = GraphStructureService.get_view_model("graph", history)
    for op in _visible_operations(vm):
        op_name = op["name"]
        payload = _default_payload(op_name, op.get("inputs", []))
        if op_name in {"insert_vertex", "remove_vertex", "exists_vertex", "neighbors"}:
            payload["vertex"] = "2"
        if op_name == "generate_random_graph":
            payload["vertices_count"] = "6"
        if op_name in {"insert_edge", "remove_edge", "exists_edge", "edge_weight"}:
            payload["origin"] = "1"
            payload["target"] = "2"
        if op_name in {"run_bfs", "run_dfs", "run_prim"}:
            payload["start"] = "1"
        if op_name in {"run_dijkstra", "run_bellman_ford"}:
            payload["start"] = "1"
            payload["end"] = "3"
        if op_name == "create_graph":
            payload["directed"] = "false"

        result = _exec(GraphStructureService.execute_operation, "graph", op_name, payload, history)
        _assert_trace_contract(result, context=f"graph::graph::{op_name}")
        history = result["history"]


def test_trace_contract_all_visible_hash_methods() -> None:
    history = _seed_history_hash()
    vm = HashStructureService.get_view_model("hash_table", history)
    for op in _visible_operations(vm):
        op_name = op["name"]
        payload = _default_payload(op_name, op.get("inputs", []))
        if op_name in {"get", "contains", "remove"}:
            payload["key"] = "k1"
        if op_name == "insert":
            payload["key"] = "k3"
            payload["value"] = "v3"
        if op_name == "create_table":
            payload["capacity"] = "17"

        result = _exec(HashStructureService.execute_operation, "hash_table", op_name, payload, history)
        _assert_trace_contract(result, context=f"hash::hash_table::{op_name}")
        history = result["history"]


def test_recursive_abb_traversals_expand_subroutine_calls() -> None:
    history: list[dict[str, Any]] = []
    for value in (63, 50, 75, 55):
        result = _exec(
            HierarchicalStructureService.execute_operation,
            "abb",
            "insertar",
            {"value": str(value)},
            history,
        )
        history = result["history"]

    def _norm(text: str) -> str:
        return " ".join(str(text).strip().lower().split())

    for operation_name, fn_name in (
        ("inorden", "abb_inorden"),
        ("preorden", "abb_preorden"),
        ("postorden", "abb_postorden"),
    ):
        result = _exec(HierarchicalStructureService.execute_operation, "abb", operation_name, {}, history)
        _assert_trace_contract(result, context=f"abb::{operation_name}")
        lines = [_norm(step.get("line_text", "")) for step in result["execution_trace"]["steps"]]

        header_line = _norm(f"void {fn_name}(ABBNodo* nodo) {{")
        left_call = _norm(f"{fn_name}(nodo->izquierdo);")
        right_call = _norm(f"{fn_name}(nodo->derecho);")
        print_line = _norm('printf("%d ", nodo->valor);')
        expected_visits = len(result.get("result") or [])

        assert lines.count(header_line) > 1
        assert lines.count(left_call) >= expected_visits
        assert lines.count(right_call) >= expected_visits
        assert lines.count(print_line) == expected_visits
