"""Unit tests for the stable trace contract and strategy registry."""

from __future__ import annotations

import pytest

from app.services.trace.control_flow import ControlFlowPlanner
from app.services.trace import (
    LegacyTraceAdapter,
    TraceContractError,
    TraceEngine,
    TraceStep,
    TraceStrategyRegistry,
)


def test_control_flow_planner_filters_non_executable_c_lines() -> None:
    lines = ["#include <stdio.h>", "/* comentario */", "{", "valor = 1;", "}"]

    assert [
        index
        for index, line in enumerate(lines)
        if ControlFlowPlanner.is_executable_line(line, "Codigo C")
    ] == [3]


def test_control_flow_planner_skips_defensive_branch_on_success() -> None:
    lines = [
        "if (lista == NULL) {",
        'printf("Lista no inicializada");',
        "return false;",
        "}",
        "lista->cantidad++;",
    ]

    assert ControlFlowPlanner.filter_defensive_branches(
        lines, list(range(len(lines))), True, "Elemento insertado"
    ) == [0, 4]


def test_control_flow_planner_evaluates_position_and_tree_conditions() -> None:
    context = {
        "success": True,
        "message": "insertado",
        "before_state": {"root": {"value": 10, "left": None, "right": None}},
        "after_state": {},
    }

    assert ControlFlowPlanner.evaluate_condition(
        normalized_line="if (pos == 1)", payload={"position": "1"}, **context
    )
    assert ControlFlowPlanner.evaluate_condition(
        normalized_line="if (valor < nodo->valor)", payload={"value": "8"}, **context
    )


def test_control_flow_planner_estimates_clear_loop_from_state_size() -> None:
    assert ControlFlowPlanner.estimate_loop_iterations(
        normalized_line="while (actual != null)",
        operation_name="limpiar",
        before_state={"items": [1, 2, 3]},
        after_state={"items": []},
    ) == 3


def test_control_flow_planner_limits_steps_preserving_endpoints() -> None:
    limited = ControlFlowPlanner.limit_step_indexes(list(range(1000)), max_steps=5)

    assert limited == [0, 250, 500, 749, 999]


def test_control_flow_planner_counts_tree_nodes() -> None:
    state = {
        "root": {
            "value": 2,
            "left": {"value": 1, "left": None, "right": None},
            "right": {"value": 3, "left": None, "right": None},
        }
    }

    assert ControlFlowPlanner.state_size(state) == 3
from app.services.trace.strategies import (
    GraphTraceStrategy,
    HashTraceStrategy,
    SequentialTraceStrategy,
    TreeTraceStrategy,
)


def _step(after: dict[str, object] | None = None) -> TraceStep:
    return TraceStep(
        line_index=1,
        line_text="*p = aux;",
        event="assignment",
        stage="apply",
        before_state={"size": 0},
        after_state=after or {"size": 1},
    )


def test_trace_step_rejects_invalid_contract_fields() -> None:
    with pytest.raises(ValueError, match="line_index"):
        TraceStep(-1, "", "line", "progress", {}, {})
    with pytest.raises(ValueError, match="event"):
        TraceStep(0, "", "", "progress", {}, {})
    with pytest.raises(TypeError, match="before_state"):
        TraceStep(0, "", "line", "progress", [], {})  # type: ignore[arg-type]


def test_trace_engine_requires_final_state_equivalence() -> None:
    TraceEngine.validate_steps([_step()], {"size": 1})
    with pytest.raises(TraceContractError, match="último paso"):
        TraceEngine.validate_steps([_step()], {"size": 2})


def test_legacy_conversion_preserves_states_and_debug_metadata() -> None:
    legacy = {
        "step_index": 3,
        "line_index": 8,
        "line_text": "padre->FE--;",
        "event_type": "line",
        "phase": "progress",
        "delay_ms": 170,
        "state_snapshot": {"size": 2},
        "state_after": {"size": 3},
        "debug": {"stage": "rebalance", "note": "Actualizar FE"},
    }
    step = TraceStep.from_legacy(legacy)
    assert step.event == "line"
    assert step.stage == "rebalance"
    assert step.before_state == {"size": 2}
    assert step.after_state == {"size": 3}
    assert step.metadata["debug"]["note"] == "Actualizar FE"


@pytest.mark.parametrize(
    ("structure_id", "family"),
    [
        ("stack", "sequential"),
        ("avl", "tree"),
        ("graph", "graph"),
        ("hash_table", "hash"),
        ("sorting_array", "sorting"),
    ],
)
def test_registry_resolves_each_family(structure_id: str, family: str) -> None:
    assert TraceStrategyRegistry.resolve(structure_id).family == family


def test_registry_rejects_unknown_structure() -> None:
    with pytest.raises(KeyError, match="No existe estrategia"):
        TraceStrategyRegistry.resolve("unknown")


def test_validate_legacy_trace_does_not_mutate_public_shape() -> None:
    trace = {
        "structure_id": "stack",
        "steps": [
            {
                "step_index": 0,
                "line_index": 0,
                "line_text": "*p = aux;",
                "event_type": "line",
                "phase": "single",
                "delay_ms": 170,
                "state_snapshot": {"size": 0},
                "state_after": {"size": 1},
            }
        ],
        "final_state": {"size": 1},
    }
    original_keys = set(trace["steps"][0])
    semantic = TraceEngine.validate_legacy_trace(trace)
    assert semantic[-1].after_state == trace["final_state"]
    assert set(trace["steps"][0]) == original_keys


def test_compatibility_adapter_round_trip_preserves_extensions() -> None:
    raw = [{
        "step_index": 4,
        "line_index": 12,
        "line_text": "rotar(raiz);",
        "event_type": "line",
        "phase": "progress",
        "delay_ms": 200,
        "state_snapshot": {"root": 30},
        "state_after": {"root": 20},
        "debug": {"stage": "rebalance", "rotation_hint": {"type": "LL"}},
        "frontend_extension": {"active_keys": ["30", "20"]},
    }]
    projected = LegacyTraceAdapter.round_trip(raw)
    assert projected == raw
    assert projected is not raw
    projected[0]["debug"]["stage"] = "changed"
    assert raw[0]["debug"]["stage"] == "rebalance"


def test_compatibility_adapter_projects_native_semantic_step() -> None:
    step = _step()
    public = LegacyTraceAdapter.to_public(step, step_index=2)
    assert public["step_index"] == 2
    assert public["event_type"] == "assignment"
    assert public["phase"] == "apply"
    assert public["state_snapshot"] == {"size": 0}
    assert public["state_after"] == {"size": 1}


def test_sequential_strategy_aligns_insertion_with_assignment() -> None:
    strategy = SequentialTraceStrategy()
    before = {"kind": "linear", "title": "Pila", "items": [], "size": 0, "empty": True}
    after = {"kind": "linear", "title": "Pila", "items": [{"value": 7}], "size": 1, "empty": False}
    boundaries = strategy.build_boundaries(
        before,
        after,
        total_steps=4,
        step_lines=["void apilar() {", "aux = malloc(...);", "aux->nro = valor;", "*p = aux;"],
    )
    assert len(boundaries) == 5
    assert boundaries[0] == before
    assert boundaries[1]["items"] == []
    assert boundaries[-1] == after


def test_sequential_strategy_handles_deletion_and_updates_metadata() -> None:
    strategy = SequentialTraceStrategy()
    before = {"kind": "circular", "title": "Lista", "items": [{"value": 1}, {"value": 2}], "size": 2, "empty": False}
    after = {"kind": "circular", "title": "Lista", "items": [{"value": 2}], "size": 1, "empty": False}
    boundaries = strategy.build_boundaries(before, after, 3, ["if (x == NULL)", "aux = *lista;", "free(aux);"])
    assert boundaries[-1] == after
    assert all(state["size"] == len(state["items"]) for state in boundaries)


def test_tree_strategy_exposes_pre_rotation_avl_state() -> None:
    strategy = TreeTraceStrategy()
    before = {
        "kind": "binary_tree",
        "title": "Árbol AVL",
        "root": {"value": 30, "left": {"value": 20, "left": None, "right": None}, "right": None},
        "size": 2,
    }
    after = {
        "kind": "binary_tree",
        "title": "Árbol AVL",
        "root": {
            "value": 20,
            "left": {"value": 10, "left": None, "right": None},
            "right": {"value": 30, "left": None, "right": None},
        },
        "size": 3,
    }
    boundaries = strategy.build_boundaries(
        before,
        after,
        total_steps=5,
        operation_name="insertar",
        payload={"value": 10},
        step_lines=["void avl_insertar() {", "padre->izq = nuevo;", "while (padre != NULL)", "avl_RSD(raiz, padre);", "return;"],
    )
    assert boundaries[0] == before
    assert boundaries[2]["root"]["value"] == 30
    assert boundaries[2]["root"]["left"]["left"]["value"] == 10
    assert boundaries[-1] == after


def test_tree_strategy_builds_heap_boundaries() -> None:
    strategy = TreeTraceStrategy()
    before = {"kind": "heap", "title": "Montículo", "array": [2, 5], "root": {}, "size": 2, "empty": False}
    after = {"kind": "heap", "title": "Montículo", "array": [1, 5, 2], "root": {"value": 1}, "size": 3, "empty": False}
    boundaries = strategy.build_heap_boundaries(before, after, 3, ["nuevo = valor;", "array[n] = nuevo;", "flotar();"])
    assert boundaries[0] == before
    assert boundaries[-1] == after
    for state in boundaries[1:-1]:
        assert state["size"] == len(state["array"])
        if state["array"]:
            assert state["root"]["value"] == state["array"][0]


def test_tree_strategy_switches_abb_state_at_mutation_boundary() -> None:
    strategy = TreeTraceStrategy()
    before = {"kind": "binary_tree", "title": "ABB", "root": None, "size": 0}
    after = {"kind": "binary_tree", "title": "ABB", "root": {"value": 5, "left": None, "right": None}, "size": 1}
    boundaries = strategy.build_boundaries(
        before,
        after,
        total_steps=3,
        operation_name="insertar",
        payload={"value": 5},
        step_lines=["ABB abb_insertar(...) {", "nuevo->valor = valor;", "return nuevo;"],
    )
    assert boundaries[:2] == [before, before]
    assert boundaries[2:] == [after, after]


def test_tree_debug_strategy_labels_avl_rotation() -> None:
    strategy = TreeTraceStrategy()
    before = {"title": "Árbol AVL", "root": {"value": 30, "left": {"value": 20, "left": None, "right": None}, "right": None}}
    after = {"title": "Árbol AVL", "root": {"value": 20, "left": {"value": 10, "left": None, "right": None}, "right": {"value": 30, "left": None, "right": None}}}
    steps = strategy.build_debug_steps(
        "insertar", {"value": 10}, before, after, True, True, 3,
        ["while (padre != NULL) {", "avl_RSD(raiz, padre);", "printf(\"ok\");"],
    )
    assert steps[0]["stage"] == "pre_rebalance"
    assert steps[1]["stage"] == "rebalance"
    assert steps[1]["rotation_hint"]["type"] == "LL"


def test_tree_debug_strategy_labels_red_black_fixup() -> None:
    strategy = TreeTraceStrategy()
    before = {"title": "Árbol Rojo-Negro", "root": {"value": 10, "left": None, "right": None}}
    after = {"title": "Árbol Rojo-Negro", "root": {"value": 10, "left": {"value": 5, "color": "RED"}, "right": None}}
    steps = strategy.build_debug_steps(
        "insertar", {"value": 5}, before, after, True, True, 3,
        ["padre->izq = actual;", "actual->rbt_color = ROJO;", "rbt_insercion_caso1(arbol, actual);"],
    )
    assert [step["stage"] for step in steps] == ["apply", "pre_fixup", "fixup"]


def test_tree_debug_strategy_tracks_extreme_search() -> None:
    strategy = TreeTraceStrategy()
    state = {"title": "ABB", "root": {"value": 8, "left": {"value": 3, "left": {"value": 1}, "right": None}, "right": None}}
    steps = strategy.build_debug_steps("minimo", {}, state, state, True, False, 3, ["while", "nodo = nodo->izq;", "return nodo;"])
    assert steps[-1]["stage"] == "result"
    assert steps[-1]["active_keys"] == ["1"]
    assert steps[-1]["note"] == "Minimo encontrado en 1."


def test_hash_strategy_derives_bucket_metadata_during_collision() -> None:
    strategy = HashTraceStrategy()
    empty_bucket = lambda index: {"index": index, "entries": [], "size": 0, "collisions": 0}
    before = {
        "structure": "hash_table",
        "buckets": [empty_bucket(0), empty_bucket(1), empty_bucket(2)],
        "metadata": {"size": 0, "capacity": 3, "load_factor": 0.0, "collisions": 0, "is_empty": True},
    }
    after = {
        "structure": "hash_table",
        "buckets": [
            {"index": 0, "entries": [{"key": "A", "value": "1"}, {"key": "B", "value": "2"}], "size": 2, "collisions": 1},
            empty_bucket(1),
            empty_bucket(2),
        ],
        "metadata": {"size": 2, "capacity": 3, "load_factor": 0.666667, "collisions": 1, "is_empty": False, "resized": False, "resize_event": None},
    }
    boundaries = strategy.build_boundaries(before, after, 4, ["int indice = 0;", "nuevo->valor = valor;", "tabla->buckets[indice] = nuevo;", "tabla->cantidad++;"])
    assert boundaries[0] == before
    assert boundaries[-1] == after
    for state in boundaries[1:-1]:
        entries = sum(len(bucket["entries"]) for bucket in state["buckets"])
        collisions = sum(max(0, len(bucket["entries"]) - 1) for bucket in state["buckets"])
        assert state["metadata"]["size"] == entries
        assert state["metadata"]["collisions"] == collisions


def test_hash_strategy_preserves_resize_event_in_final_state() -> None:
    strategy = HashTraceStrategy()
    before = {"structure": "hash_table", "buckets": [], "metadata": {"capacity": 0, "size": 0}}
    after = {
        "structure": "hash_table",
        "buckets": [{"index": 0, "entries": [], "size": 0, "collisions": 0}],
        "metadata": {"capacity": 1, "size": 0, "load_factor": 0.0, "collisions": 0, "is_empty": True, "resized": True, "resize_event": {"old_capacity": 0, "new_capacity": 1}},
    }
    assert strategy.build_boundaries(before, after, 1, ["tabla->buckets = nuevos;"])[-1] == after


def test_graph_strategy_progresses_nodes_edges_and_metadata() -> None:
    strategy = GraphTraceStrategy()
    node_1 = {"id": "1", "label": "1", "value": "1"}
    node_2 = {"id": "2", "label": "2", "value": "2"}
    before = {
        "structure": "graph",
        "directed": False,
        "weighted": False,
        "nodes": [node_1, node_2],
        "edges": [],
        "metadata": {"vertices_count": 2, "edges_count": 0, "is_empty": False},
    }
    after = {
        **before,
        "weighted": True,
        "edges": [{"source": "1", "target": "2", "weight": 3.0}],
        "metadata": {"vertices_count": 2, "edges_count": 1, "is_empty": False},
    }
    boundaries = strategy.build_boundaries(
        before,
        after,
        4,
        ["nuevo = malloc(...);", "nuevo->origen = x;", "nuevo->destino = y;", "g.a = nuevo;"],
    )
    assert boundaries[0] == before
    assert boundaries[-1] == after
    for state in boundaries[1:-1]:
        assert state["metadata"]["vertices_count"] == len(state["nodes"])
        assert state["metadata"]["edges_count"] == len(state["edges"])
        assert state["weighted"] is GraphTraceStrategy._is_weighted(state["edges"])


def test_graph_strategy_handles_vertex_removal() -> None:
    strategy = GraphTraceStrategy()
    before = {
        "structure": "graph",
        "directed": True,
        "nodes": [{"id": "1"}, {"id": "2"}],
        "edges": [{"source": "1", "target": "2", "weight": 1.0}],
        "metadata": {"vertices_count": 2, "edges_count": 1, "is_empty": False},
    }
    after = {
        "structure": "graph",
        "directed": True,
        "weighted": False,
        "nodes": [{"id": "1"}],
        "edges": [],
        "metadata": {"vertices_count": 1, "edges_count": 0, "is_empty": False},
    }
    boundaries = strategy.build_boundaries(before, after, 3, ["actual = g.v;", "free(eliminar);", "return g;"])
    assert boundaries[-1] == after
    assert all(state["directed"] is True for state in boundaries)
