"""Service layer for hierarchical structures orchestration."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.adapters.abb_adapter import ABBAdapter
from app.adapters.avl_adapter import AVLAdapter
from app.adapters.binary_heap_adapter import BinaryHeapAdapter
from app.adapters.red_black_adapter import RedBlackAdapter
from app.services.c_code_service import CCodeService
from app.services.execution_trace_service import ExecutionTraceService
from app.services.pseudocode_service import PseudocodeService
from app.domain.hierarchical import (
    ElementoDuplicadoError,
    ElementoNoEncontradoError,
    EstructuraVaciaError,
    TADError,
)


class HierarchicalStructureService:
    """Coordinate adapters and transform errors into didactic messages."""

    _REGISTRY: dict[str, dict[str, Any]] = {
        "abb": {
            "name": "ABB",
            "description": "Árbol Binario de Búsqueda sin duplicados.",
            "adapter": ABBAdapter,
        },
        "avl": {
            "name": "AVL",
            "description": "Árbol AVL auto-balanceado.",
            "adapter": AVLAdapter,
        },
        "red_black": {
            "name": "Rojo-Negro",
            "description": "Árbol rojo-negro auto-balanceado.",
            "adapter": RedBlackAdapter,
        },
        "binary_heap": {
            "name": "Montículo Binario",
            "description": "Montículo min-heap representado en arreglo y árbol.",
            "adapter": BinaryHeapAdapter,
        },
    }
    _C_FIRST_STRUCTURES: set[str] = {
        "abb",
        "avl",
        "red_black",
        "binary_heap",
    }

    @staticmethod
    def list_structures() -> list[dict[str, str]]:
        """Return metadata for all hierarchical structures."""
        items: list[dict[str, str]] = []
        for structure_id, data in HierarchicalStructureService._REGISTRY.items():
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
        """Return one structure metadata dictionary."""
        structure = HierarchicalStructureService._REGISTRY.get(structure_id)
        if structure is None:
            raise KeyError(f"Estructura no registrada: {structure_id}.")
        return structure

    @staticmethod
    def _new_adapter(structure_id: str) -> BaseAdapter:
        structure = HierarchicalStructureService.get_structure(structure_id)
        adapter_class: type[BaseAdapter] = structure["adapter"]
        return adapter_class()

    @staticmethod
    def _rebuild_adapter(
        structure_id: str,
        history: list[dict[str, Any]],
    ) -> tuple[BaseAdapter, list[dict[str, Any]]]:
        """Replay mutating history and return a ready adapter and valid history."""
        adapter = HierarchicalStructureService._new_adapter(structure_id)
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
        if isinstance(error, EstructuraVaciaError):
            return "No se puede ejecutar la operación porque la estructura está vacía."
        if isinstance(error, ElementoDuplicadoError):
            return str(error)
        if isinstance(error, ElementoNoEncontradoError):
            return str(error)
        if isinstance(error, ValueError):
            return str(error)
        if isinstance(error, TADError):
            return str(error)
        return "Ocurrió un error inesperado durante la operación."

    @staticmethod
    def _didactic_content(structure_id: str) -> dict[str, Any]:
        """Return didactic content, prioritizing real C-code when available."""
        c_data = CCodeService.get_structure_data(structure_id)
        if c_data is not None:
            return c_data
        if structure_id in HierarchicalStructureService._C_FIRST_STRUCTURES:
            return {
                "record": "/* Estructura en C no disponible temporalmente. */",
                "operations": {},
                "default_operation": (
                    "/* Codigo C no disponible para esta operacion en docs/tads_C. */"
                ),
                "code_title": "Codigo C",
            }
        return PseudocodeService.get_structure_data(structure_id)

    @staticmethod
    def get_view_model(structure_id: str, history: list[dict[str, Any]]) -> dict[str, Any]:
        """Build data needed to render one hierarchical structure page."""
        structure = HierarchicalStructureService.get_structure(structure_id)
        adapter, valid_history = HierarchicalStructureService._rebuild_adapter(structure_id, history)
        return {
            "id": structure_id,
            "name": structure["name"],
            "description": structure["description"],
            "operations": adapter.get_supported_operations(),
            "visual_state": adapter.to_visual_state(),
            "didactic": HierarchicalStructureService._didactic_content(structure_id),
            "history": valid_history,
        }

    @staticmethod
    def execute_operation(
        structure_id: str,
        operation_name: str,
        payload: dict[str, Any],
        history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Execute an operation over a rebuilt hierarchical structure state."""
        adapter, valid_history = HierarchicalStructureService._rebuild_adapter(structure_id, history)
        didactic_data = HierarchicalStructureService._didactic_content(structure_id)
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
        except (TADError, ValueError, TypeError) as error:
            message = HierarchicalStructureService._didactic_error(error)
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

        visual_state = adapter.to_visual_state()
        message = result.get("message", "Operación ejecutada correctamente.")
        if "validation" in visual_state:
            message += f" Validación: {'OK' if visual_state['validation'] else 'ERROR'}."
        trace = ExecutionTraceService.build_trace(
            structure_id=structure_id,
            operation_name=operation_name,
            payload=payload,
            didactic_data=didactic_data,
            before_state=before_state,
            after_state=visual_state,
            success=True,
            message=message,
            mutates=bool(operation_meta.get("mutates", False)),
        )

        return {
            "success": True,
            "message": message,
            "result": result.get("result"),
            "visual_state": visual_state,
            "history": valid_history,
            "execution_trace": trace,
        }
