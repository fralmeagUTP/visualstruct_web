"""Service layer for hash-table structure orchestration."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.adapters.hash_table_adapter import HashTableAdapter
from app.services.c_code_service import CCodeService
from app.services.execution_trace_service import ExecutionTraceService
from app.services.pseudocode_service import PseudocodeService


class HashStructureService:
    """Coordinate hash adapter and transform errors into didactic messages."""

    _REGISTRY: dict[str, dict[str, Any]] = {
        "hash_table": {
            "name": "Tabla Hash",
            "description": "Tabla hash con encadenamiento separado y redimensionamiento automatico.",
            "adapter": HashTableAdapter,
        }
    }

    @staticmethod
    def _didactic_content(structure_id: str) -> dict[str, Any]:
        """Return didactic content, prioritizing real C-code when available."""
        c_data = CCodeService.get_structure_data(structure_id)
        if c_data is not None:
            return c_data
        return PseudocodeService.get_structure_data(structure_id)

    @staticmethod
    def list_structures() -> list[dict[str, str]]:
        """Return metadata for hash structures."""
        items: list[dict[str, str]] = []
        for structure_id, data in HashStructureService._REGISTRY.items():
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
        """Return one hash structure metadata dictionary."""
        structure = HashStructureService._REGISTRY.get(structure_id)
        if structure is None:
            raise KeyError(f"Estructura no registrada: {structure_id}.")
        return structure

    @staticmethod
    def _new_adapter(structure_id: str) -> BaseAdapter:
        structure = HashStructureService.get_structure(structure_id)
        adapter_class: type[BaseAdapter] = structure["adapter"]
        return adapter_class()

    @staticmethod
    def _rebuild_adapter(
        structure_id: str,
        history: list[dict[str, Any]],
    ) -> tuple[BaseAdapter, list[dict[str, Any]]]:
        """Replay mutating history and return adapter with valid history."""
        adapter = HashStructureService._new_adapter(structure_id)
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
        if isinstance(error, ValueError):
            return str(error)
        return "Ocurrio un error inesperado durante la operacion."

    @staticmethod
    def get_view_model(structure_id: str, history: list[dict[str, Any]]) -> dict[str, Any]:
        """Build data needed to render hash structure page."""
        structure = HashStructureService.get_structure(structure_id)
        adapter, valid_history = HashStructureService._rebuild_adapter(structure_id, history)
        return {
            "id": structure_id,
            "name": structure["name"],
            "description": structure["description"],
            "operations": adapter.get_supported_operations(),
            "visual_state": adapter.to_visual_state(),
            "didactic": HashStructureService._didactic_content(structure_id),
            "history": valid_history,
        }

    @staticmethod
    def execute_operation(
        structure_id: str,
        operation_name: str,
        payload: dict[str, Any],
        history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Execute one operation over rebuilt hash-table state."""
        adapter, valid_history = HashStructureService._rebuild_adapter(structure_id, history)
        didactic_data = HashStructureService._didactic_content(structure_id)
        before_state = adapter.to_visual_state()
        operations = adapter.get_supported_operations()
        operation_meta = next((item for item in operations if item["name"] == operation_name), None)

        if operation_meta is None:
            message = "La operacion solicitada no esta soportada por esta estructura."
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
        except (ValueError, TypeError) as error:
            message = HashStructureService._didactic_error(error)
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
        message = result.get("message", "Operacion ejecutada correctamente.")
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
        )
        return {
            "success": True,
            "message": message,
            "result": result.get("result"),
            "visual_state": after_state,
            "history": valid_history,
            "execution_trace": trace,
        }
