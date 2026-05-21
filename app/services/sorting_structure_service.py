"""Service layer for sorting module orchestration."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.adapters.sorting_adapter import SortingAdapter
from app.domain.sorting import SortingExecutionError
from app.services.c_code_service import CCodeService
from app.services.pseudocode_service import PseudocodeService


class SortingStructureService:
    """Coordinate sorting adapter and transform errors into didactic messages."""

    _REGISTRY: dict[str, dict[str, Any]] = {
        "sorting_array": {
            "name": "Metodos de Ordenamiento",
            "description": "Visualizador didactico de algoritmos de ordenamiento sobre arreglos.",
            "adapter": SortingAdapter,
        }
    }

    @staticmethod
    def list_structures() -> list[dict[str, str]]:
        """Return metadata for sorting module cards."""
        return [
            {
                "id": structure_id,
                "name": data["name"],
                "description": data["description"],
            }
            for structure_id, data in SortingStructureService._REGISTRY.items()
        ]

    @staticmethod
    def get_structure(structure_id: str) -> dict[str, Any]:
        """Return one structure metadata dictionary."""
        structure = SortingStructureService._REGISTRY.get(structure_id)
        if structure is None:
            raise KeyError(f"Estructura no registrada: {structure_id}.")
        return structure

    @staticmethod
    def _new_adapter(structure_id: str) -> BaseAdapter:
        structure = SortingStructureService.get_structure(structure_id)
        adapter_class: type[BaseAdapter] = structure["adapter"]
        return adapter_class()

    @staticmethod
    def _rebuild_adapter(structure_id: str, history: list[dict[str, Any]]) -> tuple[SortingAdapter, list[dict[str, Any]]]:
        adapter = SortingStructureService._new_adapter(structure_id)
        assert isinstance(adapter, SortingAdapter)
        valid_history: list[dict[str, Any]] = []
        for step in history:
            operation = step.get("operation")
            payload = step.get("payload", {})
            if not isinstance(operation, str) or not isinstance(payload, dict):
                continue
            try:
                if operation in {"create_array", "generate_random_array", "select_algorithm"}:
                    adapter.execute(operation, payload)
                else:
                    continue
            except Exception:
                continue
            valid_history.append({"operation": operation, "payload": deepcopy(payload)})
        return adapter, valid_history

    @staticmethod
    def _didactic_error(error: Exception) -> str:
        if isinstance(error, SortingExecutionError):
            return str(error)
        if isinstance(error, ValueError):
            return str(error)
        return "Ocurrio un error inesperado durante la simulacion de ordenamiento."

    @staticmethod
    def _didactic_content(structure_id: str) -> dict[str, Any]:
        c_data = CCodeService.get_structure_data(structure_id)
        if c_data is not None:
            return c_data
        return PseudocodeService.get_structure_data(structure_id)

    @staticmethod
    def get_view_model(structure_id: str, history: list[dict[str, Any]]) -> dict[str, Any]:
        structure = SortingStructureService.get_structure(structure_id)
        adapter, valid_history = SortingStructureService._rebuild_adapter(structure_id, history)
        return {
            "id": structure_id,
            "name": structure["name"],
            "description": structure["description"],
            "operations": adapter.get_supported_operations(),
            "algorithms": adapter.get_supported_algorithms(),
            "visual_state": adapter.to_visual_state(),
            "didactic": SortingStructureService._didactic_content(structure_id),
            "history": valid_history,
        }

    @staticmethod
    def execute_operation(
        *,
        structure_id: str,
        operation_name: str,
        payload: dict[str, Any],
        history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        adapter, valid_history = SortingStructureService._rebuild_adapter(structure_id, history)
        didactic_data = SortingStructureService._didactic_content(structure_id)
        before_state = adapter.to_visual_state()
        operations = adapter.get_supported_operations()
        operation_meta = next((item for item in operations if item["name"] == operation_name), None)

        if operation_meta is None:
            message = "La operacion solicitada no esta soportada por el modulo de ordenamiento."
            return {
                "success": False,
                "message": message,
                "visual_state": before_state,
                "history": valid_history,
            }

        if operation_name in {"run", "step"}:
            active_algorithm = payload.get("algorithm_id") or before_state.get("algorithm")
            if active_algorithm:
                adapter.select_algorithm(str(active_algorithm))
            source_code = str(
                didactic_data.get("operations", {}).get(
                    str(before_state.get("algorithm") or adapter.to_visual_state().get("algorithm")),
                    didactic_data.get("default_operation", ""),
                )
            )
            payload = dict(payload)
            payload["source_code"] = source_code

        try:
            result = adapter.execute(operation_name, payload)
        except (SortingExecutionError, ValueError, TypeError) as error:
            message = SortingStructureService._didactic_error(error)
            return {
                "success": False,
                "message": message,
                "visual_state": adapter.to_visual_state(),
                "history": valid_history,
            }

        if operation_meta.get("mutates", False) and operation_name in {"create_array", "generate_random_array", "select_algorithm"}:
            valid_history.append({"operation": operation_name, "payload": deepcopy(payload)})

        response: dict[str, Any] = {
            "success": True,
            "message": result.get("message", "Operacion ejecutada correctamente."),
            "result": result.get("result"),
            "visual_state": result.get("visual_state", adapter.to_visual_state()),
            "history": valid_history,
        }
        if result.get("execution_trace"):
            response["execution_trace"] = result["execution_trace"]
        if result.get("cursor") is not None:
            response["cursor"] = result["cursor"]
            response["total_steps"] = result.get("total_steps")
            response["step"] = result.get("step")
        return response

