"""Service layer for graph structures orchestration."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.adapters.graph_adapter import GraphAdapter
from app.services.observability import observe_replay
from app.domain.graph import PesoNegativoError, TADError, VerticeNoEncontradoError
from app.services.c_code_service import CCodeService
from app.services.execution_trace_service import ExecutionTraceService
from app.services.pseudocode_service import PseudocodeService


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

    @staticmethod
    @observe_replay
    def _rebuild_adapter(
        structure_id: str,
        history: list[dict[str, Any]],
    ) -> tuple[BaseAdapter, list[dict[str, Any]]]:
        """Replay mutating history and return adapter with valid history."""
        adapter = GraphStructureService._new_adapter(structure_id)
        valid_history: list[dict[str, Any]] = []

        for step in history:
            operation = step.get("operation")
            payload = step.get("payload", {})
            if not isinstance(operation, str) or not isinstance(payload, dict):
                continue
            try:
                adapter.execute(operation, payload)
            except Exception:
                continue
            valid_history.append({"operation": operation, "payload": deepcopy(payload)})

        return adapter, valid_history

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
    def get_view_model(structure_id: str, history: list[dict[str, Any]]) -> dict[str, Any]:
        """Build data needed to render graph structure page."""
        structure = GraphStructureService.get_structure(structure_id)
        adapter, valid_history = GraphStructureService._rebuild_adapter(structure_id, history)
        didactic_data = GraphStructureService._didactic_content(structure_id)
        return {
            "id": structure_id,
            "name": structure["name"],
            "description": structure["description"],
            "operations": adapter.get_supported_operations(),
            "visual_state": adapter.to_visual_state(),
            "didactic": didactic_data,
            "history": valid_history,
        }

    @staticmethod
    def execute_operation(
        structure_id: str,
        operation_name: str,
        payload: dict[str, Any],
        history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Execute operation over rebuilt graph state."""
        adapter, valid_history = GraphStructureService._rebuild_adapter(structure_id, history)
        didactic_data = GraphStructureService._didactic_content(structure_id)
        before_state = adapter.to_visual_state()
        operations = adapter.get_supported_operations()
        operation_meta = next((item for item in operations if item["name"] == operation_name), None)

        if operation_meta is None:
            message = "La operación solicitada no está soportada por esta estructura."
            trace = ExecutionTraceService.build_trace(
                structure_id=structure_id,
                operation_name=operation_name,
                payload=payload,
                didactic_data=didactic_data,
                before_state=before_state,
                after_state=before_state,
                success=False,
                message=message,
                mutates=False,
            )
            return {
                "success": False,
                "message": message,
                "visual_state": before_state,
                "history": valid_history,
                "execution_trace": trace,
            }

        try:
            result = adapter.execute(operation_name, payload)
        except (TADError, ValueError, TypeError, KeyError) as error:
            message = GraphStructureService._didactic_error(error)
            if hasattr(adapter, "record_failed_operation"):
                adapter.record_failed_operation(operation_name, message)
            after_state = adapter.to_visual_state()
            trace = ExecutionTraceService.build_trace(
                structure_id=structure_id,
                operation_name=operation_name,
                payload=payload,
                didactic_data=didactic_data,
                before_state=before_state,
                after_state=after_state,
                success=False,
                message=message,
                mutates=bool(operation_meta.get("mutates", False)),
            )
            return {
                "success": False,
                "message": message,
                "visual_state": after_state,
                "history": valid_history,
                "execution_trace": trace,
            }

        if operation_meta.get("mutates", False):
            valid_history.append({"operation": operation_name, "payload": deepcopy(payload)})

        after_state = adapter.to_visual_state()
        message = result.get("message", "Operación ejecutada correctamente.")
        trace = ExecutionTraceService.build_trace(
            structure_id=structure_id,
            operation_name=operation_name,
            payload=payload,
            didactic_data=didactic_data,
            before_state=before_state,
            after_state=after_state,
            success=True,
            message=message,
            mutates=bool(operation_meta.get("mutates", False)),
            console_events=result.get("console") if isinstance(result.get("console"), list) else [],
        )
        return {
            "success": True,
            "message": message,
            "result": result.get("result"),
            "visual_state": after_state,
            "history": valid_history,
            "execution_trace": trace,
        }
