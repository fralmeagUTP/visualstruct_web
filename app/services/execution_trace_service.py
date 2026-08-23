"""Build interpreter-like execution traces for didactic operation playback."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.trace.control_flow import ControlFlowPlanner
from app.services.trace.graph_planner import GraphAlgorithmPlanner
from app.services.trace.graph_trace_planner import GraphTracePlanner
from app.services.trace.tree_planner import TreeAlgorithmPlanner
from app.services.trace.tree_query_planner import TreeQueryPlanner
from app.services.trace.engine import TraceEngine
from app.services.trace.strategies import (
    GraphTraceStrategy,
    HashTraceStrategy,
    SequentialTraceStrategy,
    TraceStrategyRegistry,
    TreeTraceStrategy,
)


class ExecutionTraceService:
    """Create a normalized execution trace from didactic operation code."""

    # Aliases retained for callers of the former private API while the service
    # becomes an orchestration-only facade.
    _is_executable_line = staticmethod(ControlFlowPlanner.is_executable_line)
    _next_nonempty_line_index = staticmethod(ControlFlowPlanner.next_nonempty_line_index)
    _find_matching_brace_line = staticmethod(ControlFlowPlanner.find_matching_brace_line)
    _filter_trace_lines_by_control_flow = staticmethod(ControlFlowPlanner.filter_defensive_branches)
    _normalized_line_text = staticmethod(ControlFlowPlanner.normalize_line)
    _expand_generic_control_flow_indexes = staticmethod(ControlFlowPlanner.expand_generic)

    @staticmethod
    def _get_operation_source(
        didactic_data: dict[str, Any],
        operation_name: str,
    ) -> tuple[str, str]:
        code_title = str(didactic_data.get("code_title", "Codigo C"))
        operation_map = didactic_data.get("operations", {})
        if not isinstance(operation_map, dict):
            operation_map = {}
        source = str(
            operation_map.get(
                operation_name,
                didactic_data.get(
                    "default_operation",
                    "/* Codigo no disponible para esta operacion. */",
                ),
            )
        )
        return source, code_title

    @staticmethod
    def _state_kind(state: dict[str, Any]) -> str:
        return str(state.get("kind") or state.get("structure") or "").strip().lower()

    @staticmethod
    def _tree_family(state: dict[str, Any]) -> str:
        title = str(state.get("title", "")).lower()
        if "avl" in title:
            return "avl"
        if "rojo" in title or "red-black" in title or "negro" in title:
            return "red_black"
        return "abb"


    _build_graph_debug_steps = staticmethod(GraphTracePlanner._build_graph_debug_steps)
    _expand_graph_control_flow_indexes = staticmethod(GraphTracePlanner._expand_graph_control_flow_indexes)
    _expand_graph_kruskal_indexes = staticmethod(GraphAlgorithmPlanner.expand_kruskal)
    _expand_graph_dijkstra_indexes = staticmethod(GraphAlgorithmPlanner.expand_dijkstra)
    _expand_graph_bfs_indexes = staticmethod(GraphAlgorithmPlanner.expand_bfs)
    _expand_graph_bellman_ford_indexes = staticmethod(GraphAlgorithmPlanner.expand_bellman_ford)
    _expand_recursive_graph_dfs_indexes = staticmethod(GraphAlgorithmPlanner.expand_dfs)
    _extract_tree_node_value = staticmethod(TreeAlgorithmPlanner.node_value)
    _tree_child = staticmethod(TreeAlgorithmPlanner.child)
    _find_line_index_by_contains = staticmethod(GraphAlgorithmPlanner.find_line)
    _expand_recursive_abb_insert_indexes = staticmethod(TreeAlgorithmPlanner.expand_abb_insert)
    _expand_recursive_abb_delete_indexes = staticmethod(TreeAlgorithmPlanner.expand_abb_delete)
    _expand_avl_insert_indexes = staticmethod(TreeAlgorithmPlanner.expand_avl_insert)
    _expand_rbt_insert_indexes = staticmethod(TreeAlgorithmPlanner.expand_rbt_insert)
    _expand_rbt_delete_indexes = staticmethod(TreeAlgorithmPlanner.expand_rbt_delete)
    _expand_tree_extreme_indexes = staticmethod(TreeQueryPlanner.expand_extreme)
    _expand_recursive_bst_traversal_indexes = staticmethod(TreeQueryPlanner.expand_traversal)
    _expand_recursive_tree_metrics_indexes = staticmethod(TreeQueryPlanner.expand_metrics)
    _expand_recursive_tree_clear_indexes = staticmethod(TreeQueryPlanner.expand_clear)

    @staticmethod
    def _expand_recursive_abb_indexes(
        *,
        operation_name: str,
        lines: list[str],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        payload: dict[str, Any],
        success: bool,
    ) -> list[int] | None:
        if operation_name == "limpiar":
            expanded_clear = ExecutionTraceService._expand_recursive_tree_clear_indexes(
                lines=lines,
                before_state=before_state,
                after_state=after_state,
            )
            if expanded_clear is not None:
                return expanded_clear

        if operation_name in {"minimo", "maximo"}:
            return ExecutionTraceService._expand_tree_extreme_indexes(
                operation_name=operation_name,
                lines=lines,
                before_state=before_state,
                after_state=after_state,
            )

        normalized_join = "\n".join(ExecutionTraceService._normalized_line_text(line) for line in lines)
        if (
            "abb_insertar(" not in normalized_join
            and "abb_eliminar(" not in normalized_join
            and "_inorden(" not in normalized_join
            and "_preorden(" not in normalized_join
            and "_postorden(" not in normalized_join
            and "abb_altura(" not in normalized_join
            and "avl_altura(" not in normalized_join
            and "rbt_altura(" not in normalized_join
            and "abb_contarhojas(" not in normalized_join
            and "avl_validar_fes(" not in normalized_join
            and "rbt_validar(" not in normalized_join
            and "abb_validar_" not in normalized_join
            and "void avl_insertar(" not in normalized_join
            and "void rbt_insertar(" not in normalized_join
            and "void rbt_eliminar(" not in normalized_join
        ):
            return None

        if operation_name == "insertar" and "void avl_insertar(" in normalized_join:
            return ExecutionTraceService._expand_avl_insert_indexes(
                lines=lines,
                before_state=before_state,
                after_state=after_state,
                payload=payload,
                success=success,
            )
        if operation_name == "insertar" and "void rbt_insertar(" in normalized_join:
            return ExecutionTraceService._expand_rbt_insert_indexes(
                lines=lines,
                before_state=before_state,
                payload=payload,
                success=success,
            )
        if operation_name == "eliminar" and "void rbt_eliminar(" in normalized_join:
            return ExecutionTraceService._expand_rbt_delete_indexes(
                lines=lines,
                before_state=before_state,
                payload=payload,
            )
        if operation_name == "insertar" and "abb_insertar(" in normalized_join:
            return ExecutionTraceService._expand_recursive_abb_insert_indexes(
                lines=lines,
                before_state=before_state,
                payload=payload,
                success=success,
            )
        if operation_name == "eliminar" and "abb_eliminar(" in normalized_join:
            return ExecutionTraceService._expand_recursive_abb_delete_indexes(
                lines=lines,
                before_state=before_state,
                payload=payload,
            )
        if operation_name in {"altura", "contar_hojas", "validar"}:
            expanded_metrics = ExecutionTraceService._expand_recursive_tree_metrics_indexes(
                operation_name=operation_name,
                lines=lines,
                before_state=before_state,
                after_state=after_state,
            )
            if expanded_metrics is not None:
                return expanded_metrics
        return ExecutionTraceService._expand_recursive_bst_traversal_indexes(
            operation_name=operation_name,
            lines=lines,
            before_state=before_state,
            after_state=after_state,
        )

    _expand_tree_extreme_indexes = staticmethod(TreeQueryPlanner.expand_extreme)
    _expand_recursive_bst_traversal_indexes = staticmethod(TreeQueryPlanner.expand_traversal)
    _expand_recursive_tree_metrics_indexes = staticmethod(TreeQueryPlanner.expand_metrics)
    _expand_recursive_tree_clear_indexes = staticmethod(TreeQueryPlanner.expand_clear)

    @staticmethod
    def _build_boundaries(
        structure_id: str,
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        total_steps: int,
        mutates: bool,
        operation_name: str,
        payload: dict[str, Any],
        step_lines: list[str],
    ) -> list[dict[str, Any]]:
        boundaries = total_steps + 1
        if boundaries <= 1:
            return [deepcopy(before_state), deepcopy(after_state)]
        if not mutates or before_state == after_state:
            states = [deepcopy(before_state) for _ in range(boundaries)]
            states[-1] = deepcopy(after_state)
            return states

        state_kind = ExecutionTraceService._state_kind(after_state)
        if state_kind in {"linear", "circular", "sublist"}:
            strategy = TraceStrategyRegistry.resolve(structure_id)
            if not isinstance(strategy, SequentialTraceStrategy):
                raise TypeError(f"La estrategia de '{structure_id}' no es secuencial.")
            return strategy.build_boundaries(before_state, after_state, total_steps, step_lines)
        if state_kind == "heap":
            strategy = TraceStrategyRegistry.resolve(structure_id)
            if not isinstance(strategy, TreeTraceStrategy):
                raise TypeError(f"La estrategia de '{structure_id}' no es de árbol.")
            return strategy.build_heap_boundaries(before_state, after_state, total_steps, step_lines)
        if state_kind == "binary_tree":
            strategy = TraceStrategyRegistry.resolve(structure_id)
            if not isinstance(strategy, TreeTraceStrategy):
                raise TypeError(f"La estrategia de '{structure_id}' no es de árbol.")
            return strategy.build_boundaries(
                before_state,
                after_state,
                total_steps,
                operation_name,
                payload,
                step_lines,
            )
        if state_kind == "graph":
            strategy = TraceStrategyRegistry.resolve(structure_id)
            if not isinstance(strategy, GraphTraceStrategy):
                raise TypeError(f"La estrategia de '{structure_id}' no es de grafo.")
            return strategy.build_boundaries(before_state, after_state, total_steps, step_lines)
        if state_kind == "hash_table":
            strategy = TraceStrategyRegistry.resolve(structure_id)
            if not isinstance(strategy, HashTraceStrategy):
                raise TypeError(f"La estrategia de '{structure_id}' no es hash.")
            return strategy.build_boundaries(before_state, after_state, total_steps, step_lines)

        states = [deepcopy(before_state) for _ in range(boundaries)]
        switch_index = max(1, int(boundaries * 0.7))
        for index in range(switch_index, boundaries):
            states[index] = deepcopy(after_state)
        states[0] = deepcopy(before_state)
        states[-1] = deepcopy(after_state)
        return states

    @staticmethod
    def build_trace(
        *,
        structure_id: str,
        operation_name: str,
        payload: dict[str, Any],
        didactic_data: dict[str, Any],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        success: bool,
        message: str,
        mutates: bool,
        console_events: list[str] | None = None,
    ) -> dict[str, Any]:
        """Build one execution trace consumable by frontend animation runtimes."""
        source_code, code_title = ExecutionTraceService._get_operation_source(
            didactic_data=didactic_data,
            operation_name=operation_name,
        )
        lines = source_code.replace("\r\n", "\n").split("\n")
        state_kind = ExecutionTraceService._state_kind(after_state)
        executable_line_indexes = [
            index
            for index, line in enumerate(lines)
            if ExecutionTraceService._is_executable_line(line, code_title)
        ]
        executable_line_indexes = ExecutionTraceService._filter_trace_lines_by_control_flow(
            lines,
            executable_line_indexes,
            bool(success),
            str(message),
            state_kind,
        )
        recursive_tree_indexes = None
        if state_kind == "binary_tree":
            recursive_tree_indexes = ExecutionTraceService._expand_recursive_abb_indexes(
                operation_name=operation_name,
                lines=lines,
                before_state=before_state,
                after_state=after_state,
                payload=payload,
                success=bool(success),
            )
        if recursive_tree_indexes is not None:
            executable_line_indexes = recursive_tree_indexes
        elif state_kind != "graph":
            executable_line_indexes = ExecutionTraceService._expand_generic_control_flow_indexes(
                operation_name=operation_name,
                lines=lines,
                executable_line_indexes=executable_line_indexes,
                before_state=before_state,
                after_state=after_state,
                success=bool(success),
                message=str(message),
                payload=payload,
            )
        elif state_kind == "graph":
            executable_line_indexes = ExecutionTraceService._expand_graph_control_flow_indexes(
                operation_name=operation_name,
                lines=lines,
                executable_line_indexes=executable_line_indexes,
                before_state=before_state,
                after_state=after_state,
                success=bool(success),
                message=str(message),
                payload=payload,
            )

        if not executable_line_indexes and lines:
            executable_line_indexes = [0]
        step_lines = [lines[index] if 0 <= index < len(lines) else "" for index in executable_line_indexes]

        steps: list[dict[str, Any]] = []
        total_steps = len(executable_line_indexes)
        boundary_states = ExecutionTraceService._build_boundaries(
            structure_id=structure_id,
            before_state=before_state,
            after_state=after_state,
            total_steps=total_steps,
            mutates=bool(mutates and success),
            operation_name=operation_name,
            payload=payload,
            step_lines=step_lines,
        )
        if state_kind == "binary_tree":
            strategy = TraceStrategyRegistry.resolve(structure_id)
            if not isinstance(strategy, TreeTraceStrategy):
                raise TypeError(f"La estrategia de '{structure_id}' no es de árbol.")
            debug_steps = strategy.build_debug_steps(
                operation_name=operation_name,
                payload=payload,
                before_state=before_state,
                after_state=after_state,
                success=bool(success),
                mutates=bool(mutates),
                total_steps=total_steps,
                step_lines=step_lines,
            )
        elif state_kind == "graph":
            debug_steps = ExecutionTraceService._build_graph_debug_steps(
                operation_name=operation_name,
                after_state=after_state,
                total_steps=total_steps,
            )
        else:
            debug_steps = [None for _ in range(total_steps)]
        for step_index, line_index in enumerate(executable_line_indexes):
            line_text = lines[line_index] if 0 <= line_index < len(lines) else ""
            is_first = step_index == 0
            is_last = step_index == total_steps - 1

            step: dict[str, Any] = {
                "step_index": step_index,
                "line_index": line_index,
                "line_text": line_text,
                "event_type": "line",
                "phase": (
                    "start"
                    if is_first and not is_last
                    else "end"
                    if is_last and not is_first
                    else "single"
                    if is_first and is_last
                    else "progress"
                ),
                "delay_ms": 170,
                "state_snapshot": deepcopy(boundary_states[step_index]),
                "state_after": deepcopy(boundary_states[step_index + 1]),
            }
            if not is_first:
                step.pop("phase", None)
                step["phase"] = "progress" if not is_last else "end"
            if step_index < len(debug_steps) and isinstance(debug_steps[step_index], dict):
                step["debug"] = debug_steps[step_index]
            step["console"] = list(console_events or []) if is_last else []
            steps.append(step)

        if not steps:
            steps = [
                {
                    "step_index": 0,
                    "line_index": 0,
                    "line_text": "",
                    "event_type": "noop",
                    "phase": "single",
                    "delay_ms": 100,
                    "state_snapshot": deepcopy(before_state),
                    "state_after": deepcopy(after_state),
                }
            ]

        trace = {
            "structure_id": structure_id,
            "operation_name": operation_name,
            "payload": deepcopy(payload),
            "success": bool(success),
            "mutates": bool(mutates),
            "message": str(message),
            "code_title": code_title,
            "source_code": source_code,
            "steps": steps,
            "final_state": deepcopy(after_state),
        }
        TraceEngine.validate_legacy_trace(trace)
        return trace
