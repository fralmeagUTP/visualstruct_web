"""Service layer for graph structures orchestration."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.adapters.graph_adapter import GraphAdapter
from app.domain.graph.educational_capacity import MAX_VERTICES, GraphCapacityError
from app.services.observability import observe_replay
from app.domain.graph import PesoNegativoError, TADError, VerticeNoEncontradoError
from app.services.c_code_service import CCodeService
from app.services.execution_trace_service import ExecutionTraceService
from app.services.pseudocode_service import PseudocodeService
from app.domain.graph.pedagogy import GRAPH_EDGE_POLICY, GRAPH_GUIDED_EXAMPLES
from app.services.graph_main_service import build_graph_main
from app.services.graph_mark_effects import capture_mark_effect, restore_mark_effect


class GraphStructureService:
    """Coordinate graph adapter and transform errors into didactic messages."""

    _REGISTRY: dict[str, dict[str, Any]] = {
        "graph": {
            "name": "Grafo",
            "description": "Grafo dirigido o no dirigido con recorridos y algoritmos clásicos.",
            "adapter": GraphAdapter,
        }
    }
    _C_FIRST_STRUCTURES: set[str] = {"graph"}

    @staticmethod
    def _didactic_content(structure_id: str) -> dict[str, Any]:
        """Return didactic content, prioritizing real C-code when available."""
        c_data = CCodeService.get_structure_data(structure_id)
        if c_data is not None:
            return c_data
        if structure_id in GraphStructureService._C_FIRST_STRUCTURES:
            return {
                "record": "/* Estructura en C no disponible temporalmente. */",
                "operations": {},
                "default_operation": (
                    "/* Código C no disponible para esta operación en docs/tads_C. */"
                ),
                "code_title": "Código C",
            }
        return PseudocodeService.get_structure_data(structure_id)

    @staticmethod
    def list_structures() -> list[dict[str, str]]:
        """Return metadata for graph structures."""
        items: list[dict[str, str]] = []
        for structure_id, data in GraphStructureService._REGISTRY.items():
            items.append(
                {
                    "id": structure_id,
                    "name": data["name"],
                    "description": data["description"],
                }
            )
        return items

    @staticmethod
    def get_structure(structure_id: str) -> dict[str, Any]:
        """Return one graph structure metadata dictionary."""
        structure = GraphStructureService._REGISTRY.get(structure_id)
        if structure is None:
            raise KeyError(f"Estructura no registrada: {structure_id}.")
        return structure

    @staticmethod
    def _new_adapter(structure_id: str) -> BaseAdapter:
        structure = GraphStructureService.get_structure(structure_id)
        adapter_class: type[BaseAdapter] = structure["adapter"]
        return adapter_class()

    SOURCE_CONTRACT = "graph-book/v1"

    @staticmethod
    def main_issue(history):
        issue = GraphStructureService.history_issue(history)
        if issue:
            return issue
        if any(entry["payload"].get("fail_allocation") is not None for entry in history):
            return ("Este historial contiene una inyección de fallo del diagnóstico. Un main con malloc "
                    "ordinario no reproduce ese fallo; exporta el historial y usa el harness de pruebas. "
                    "No se ofrece un main que aparente reproducir un estado distinto.")
        return None

    @staticmethod
    def _main(history):
        return "" if GraphStructureService.main_issue(history) else build_graph_main(history)

    @staticmethod
    def history_issue(history):
        if not isinstance(history, list) or any(
            not isinstance(entry, dict)
            or entry.get("source_contract") != GraphStructureService.SOURCE_CONTRACT
            or not isinstance(entry.get("operation"), str)
            or not isinstance(entry.get("payload"), dict)
            for entry in history
        ):
            return ("Este historial pertenece a otra versión del código C. Está suspendido, no vacío. "
                    "Puedes exportarlo sin cambios y abrirlo en la copia anterior. "
                    "Para trabajar con el código del libro, confirma Restablecer datos.")
        if any(entry["operation"] == "generate_random_graph" and
               type(entry["payload"].get("seed")) is not int for entry in history):
            return "El historial aleatorio no conserva su semilla. Está suspendido para no inventar otro grafo; expórtalo o confirma Restablecer."
        return None

    @staticmethod
    @observe_replay
    def _rebuild_adapter(structure_id, history):
        """Replay only explicitly canonical commands, never reinterpret legacy history."""
        if GraphStructureService.history_issue(history):
            raise ValueError(GraphStructureService.history_issue(history))
        adapter = GraphStructureService._new_adapter(structure_id)
        adapter._console_history_stdout = ''
        for step in history:
            adapter.execute(step["operation"], deepcopy(step["payload"]))
            adapter._console_history_stdout += adapter._last_book_execution.get('stdout', '')
        return adapter, deepcopy(history)

    @staticmethod
    def _didactic_error(error: Exception) -> str:
        """Translate technical exceptions to didactic messages."""
        if isinstance(error, PesoNegativoError):
            return (
                "Dijkstra no se puede ejecutar con pesos negativos. "
                "Usa Bellman-Ford para este caso."
            )
        if isinstance(error, VerticeNoEncontradoError):
            return str(error)
        if isinstance(error, ValueError):
            message = str(error)
            if "Prim requiere un grafo no dirigido" in message:
                return "Prim solo esta disponible para grafos no dirigidos."
            if "Kruskal requiere un grafo no dirigido" in message:
                return "Kruskal solo esta disponible para grafos no dirigidos."
            return message
        if isinstance(error, TADError):
            return str(error)
        return "Ocurrió un error inesperado durante la operación."

    @staticmethod
    def get_view_model(structure_id, history):
        structure = GraphStructureService.get_structure(structure_id)
        issue = GraphStructureService.history_issue(history)
        adapter = GraphStructureService._new_adapter(structure_id)
        if not issue:
            try:
                adapter, _ = GraphStructureService._rebuild_adapter(structure_id, history)
            except (TADError, ValueError, TypeError, KeyError):
                issue = "Este historial no se puede reconstruir con el contrato del libro. Está suspendido y conservado; expórtalo o confirma Restablecer."

        visual = ({"type": "graph", "suspended": True, "suspension_reason": issue,
                   "source_contract": GraphStructureService.SOURCE_CONTRACT}
                  if issue else adapter.to_visual_state())
        return {"id": structure_id, "name": structure["name"],
                "description": structure["description"],
                "operations": adapter.get_supported_operations(), "visual_state": visual,
                "didactic": GraphStructureService._didactic_content(structure_id),
                "history": deepcopy(history), "main_c": "" if issue else GraphStructureService._main(history),
                "console_stdout": getattr(adapter, '_console_history_stdout', ''),
                "main_unavailable_reason": issue or GraphStructureService.main_issue(history), "suspended": bool(issue),
                "source_contract": GraphStructureService.SOURCE_CONTRACT,
                "guided_examples": deepcopy(GRAPH_GUIDED_EXAMPLES),
                "edge_policy": deepcopy(GRAPH_EDGE_POLICY), "max_vertices": MAX_VERTICES}

    @staticmethod
    def execute_operation(structure_id, operation_name, payload, history, execution_mode="step"):
        """Execute once in the canonical interpreter and stream its real recorded events."""
        from app.domain.graph.book_trace import BookTraceCollector
        issue = GraphStructureService.history_issue(history)
        if issue:
            model = GraphStructureService.get_view_model(structure_id, history)
            return {"success": False, "message": issue, "preserve_session": True,
                    "history": deepcopy(history), "visual_state": model["visual_state"],
                    "suspended": True, "main_c": "", "execution_trace": None,
                    "source_contract": GraphStructureService.SOURCE_CONTRACT}
        try:
            adapter, valid_history = GraphStructureService._rebuild_adapter(structure_id, history)
        except (TADError, ValueError, TypeError, KeyError):
            model = GraphStructureService.get_view_model(structure_id, history)
            return {"success": False, "message": model["main_unavailable_reason"],
                    "preserve_session": True, "suspended": True, "history": deepcopy(history),
                    "visual_state": model["visual_state"], "main_c": "", "execution_trace": None,
                    "source_contract": GraphStructureService.SOURCE_CONTRACT}
        before = adapter.to_visual_state()
        from app.domain.graph.trace_budget import MAX_TRACE_EVENTS, trace_budget_message, normal_trace_notice
        from app.domain.graph.book_c_subset import BookEventLimitExceeded
        planned_payload = deepcopy(payload)
        probe = deepcopy(adapter)
        probe._book_event_limit = MAX_TRACE_EVENTS
        over_budget = False
        try:
            probe.execute(operation_name, planned_payload)
        except BookEventLimitExceeded:
            over_budget = True
        except (TADError, ValueError, TypeError, KeyError):
            pass  # The actual validation path below returns the precise pre-C error.
        if over_budget and execution_mode != "normal":
            return {"success": False, "message": trace_budget_message(), "preserve_session": True,
                    "history": valid_history, "visual_state": before, "main_c": GraphStructureService._main(valid_history),
                    "execution_trace": None, "trace_available": False,
                    "trace_unavailable_reason": trace_budget_message(), "trace_event_limit": MAX_TRACE_EVENTS,
                    "source_contract": GraphStructureService.SOURCE_CONTRACT}
        payload = planned_payload  # Keep the exact random seed prepared by the probe.
        collector = BookTraceCollector(operation_name=operation_name, payload=payload, before_state=before)
        adapter._book_callback = None if over_budget else collector.callback
        try:
            result = adapter.execute(operation_name, payload)
        except (TADError, ValueError, TypeError, KeyError) as error:
            message = GraphStructureService._didactic_error(error)
            trace = collector.finish(after_state=adapter.to_visual_state(), success=False, message=message)
            return {"success": False, "message": message, "preserve_session": True,
                    "history": valid_history, "visual_state": adapter.to_visual_state(),
                    "main_c": GraphStructureService._main(valid_history), "execution_trace": trace,
                    "source_contract": GraphStructureService.SOURCE_CONTRACT}
        # Failed C calls remain real history too: they can have observable partial
        # caller effects (two independent calls for an undirected edge).
        valid_history.append({"operation": operation_name, "payload": deepcopy(payload),
                              "source_contract": GraphStructureService.SOURCE_CONTRACT})
        after = adapter.to_visual_state()
        success = bool(result.get("success", True))
        message = result.get("message", "Operación ejecutada.")
        trace = None if over_budget else collector.finish(after_state=after, success=success, message=message,
                                 result=result.get("result"))
        return {**result, "success": success, "message": message, "visual_state": after,
                "console_stdout": adapter._last_book_execution.get("stdout", ""),
                 "console_prefix": adapter._console_history_stdout,
                "execution_started": bool(adapter._last_book_execution.get("calls")),
                "history": valid_history, "main_c": GraphStructureService._main(valid_history),
                "main_unavailable_reason": GraphStructureService.main_issue(valid_history),
                "execution_trace": trace, "trace_available": not over_budget,
                "trace_unavailable_reason": normal_trace_notice() if over_budget else None,
                "trace_event_limit": MAX_TRACE_EVENTS,
                "source_contract": GraphStructureService.SOURCE_CONTRACT}

    @staticmethod
    def compare_algorithms(kind: str, graph_state: Any, start: Any = None, end: Any = None) -> dict[str, Any]:
        """Run two algorithms on independent copies of one immutable graph snapshot."""
        pairs = {
            "bfs-dfs": ("run_bfs", "run_dfs"),
            "dijkstra-bellman-ford": ("run_dijkstra", "run_bellman_ford"),
            "prim-kruskal": ("run_prim", "run_kruskal"),
        }
        if kind not in pairs or not isinstance(graph_state, dict):
            raise ValueError("Comparación de grafos no soportada.")
        if graph_state.get("asymmetric_pairs"):
            raise ValueError("La comparación requiere un grafo sin pares incompletos; revisa las inserciones que fallaron.")
        nodes = graph_state.get("nodes") or []
        edges = graph_state.get("edges") or []
        if not nodes or len(nodes) > MAX_VERTICES or len(edges) > 300:
            raise ValueError(f"La comparación requiere entre 1 y {MAX_VERTICES} vértices y máximo 300 aristas.")
        immutable = deepcopy({"directed": bool(graph_state.get("directed", False)), "nodes": nodes, "edges": edges})

        def execute_copy(operation: str) -> dict[str, Any]:
            adapter = GraphAdapter()
            adapter.execute("create_graph", {"directed": immutable["directed"]})
            for node in immutable["nodes"]:
                adapter.execute("insert_vertex", {"vertex": node.get("id")})
            for edge in immutable["edges"]:
                adapter.execute("insert_edge", {"origin": edge.get("source"), "target": edge.get("target"), "weight": edge.get("weight", 1)})
            payload: dict[str, Any] = {}
            if operation in {"run_bfs", "run_dfs", "run_dijkstra", "run_bellman_ford", "run_prim"}:
                payload["start"] = start if start not in (None, "") else immutable["nodes"][0].get("id")
            if operation in {"run_dijkstra", "run_bellman_ford"}:
                payload["end"] = end if end not in (None, "") else immutable["nodes"][-1].get("id")
            answer = adapter.execute(operation, payload)
            outcome = answer.get("result")
            if isinstance(outcome, list):
                summary = {"order": outcome, "visited_count": len(outcome), "auxiliary": "FIFO" if operation == "run_bfs" else "pila/recursión"}
            else:
                summary = deepcopy(outcome or {})
            return {"algorithm": operation, "payload": payload, "summary": summary, "success": answer.get("success", True), "c_status": answer.get("c_status"), "c_status_name": answer.get("c_status_name"), "c_return": answer.get("c_return"), "message": answer.get("message"), "final_state": deepcopy(adapter.to_visual_state())}

        left_name, right_name = pairs[kind]
        left, right = execute_copy(left_name), execute_copy(right_name)
        conclusions = {
            "bfs-dfs": "BFS usa FIFO y visita por niveles; DFS usa pila/recursión y profundiza antes de retroceder.",
            "dijkstra-bellman-ford": "Dijkstra cierra mínimos con pesos no negativos; Bellman-Ford relaja por pasadas y admite pesos negativos.",
            "prim-kruskal": "Prim crece desde una frontera; Kruskal ordena aristas y evita ciclos mediante Union-Find.",
        }
        return {"kind": kind, "input": immutable, "left": left, "right": right, "conclusion": conclusions[kind], "isolated": True}
