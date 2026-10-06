"""Service layer for sequential structure orchestration."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.adapters.circular_list_adapter import CircularListAdapter
from app.adapters.linked_list_adapter import LinkedListAdapter
from app.adapters.priority_queue_adapter import PriorityQueueAdapter
from app.adapters.queue_adapter import QueueAdapter
from app.adapters.stack_adapter import StackAdapter
from app.adapters.sublist_adapter import SublistAdapter
from app.services.observability import observe_replay
from app.services.c_code_service import CCodeService
from app.services.execution_trace_service import ExecutionTraceService
from app.services.pseudocode_service import PseudocodeService
from app.domain.sequential.pedagogy import SEQUENTIAL_GUIDED_EXAMPLES
from app.domain.sequential import (
    ElementoNoEncontradoError,
    EstructuraVaciaError,
    PosicionInvalidaError,
    TADError,
)


class StructureService:
    """Coordinate adapters and transform errors into didactic messages."""

    _REGISTRY: dict[str, dict[str, Any]] = {
        "stack": {
            "name": "Pila",
            "description": "Estructura LIFO para apilar y desapilar elementos.",
            "adapter": StackAdapter,
        },
        "queue": {
            "name": "Cola",
            "description": "Estructura FIFO para encolar y desencolar elementos.",
            "adapter": QueueAdapter,
        },
        "priority_queue": {
            "name": "Cola de Prioridad",
            "description": "Los elementos se atienden por prioridad numérica.",
            "adapter": PriorityQueueAdapter,
        },
        "linked_list": {
            "name": "Lista Enlazada",
            "description": "Secuencia de nodos con operaciones por posición y valor.",
            "adapter": LinkedListAdapter,
        },
        "circular_list": {
            "name": "Lista Circular",
            "description": "Lista donde el último nodo vuelve al primero.",
            "adapter": CircularListAdapter,
        },
        "sublist": {
            "name": "Sublista",
            "description": "Padres con sublistas de hijos.",
            "adapter": SublistAdapter,
        },
    }
    _C_FIRST_STRUCTURES: set[str] = {
        "stack",
        "queue",
        "priority_queue",
        "linked_list",
        "circular_list",
        "sublist",
    }

    @staticmethod
    def list_structures() -> list[dict[str, str]]:
        """Return metadata for all sequential structures."""
        items: list[dict[str, str]] = []
        for structure_id, data in StructureService._REGISTRY.items():
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
        structure = StructureService._REGISTRY.get(structure_id)
        if structure is None:
            raise KeyError(f"Estructura no registrada: {structure_id}.")
        return structure

    @staticmethod
    def _new_adapter(structure_id: str) -> BaseAdapter:
        structure = StructureService.get_structure(structure_id)
        adapter_class: type[BaseAdapter] = structure["adapter"]
        return adapter_class()

    @staticmethod
    @observe_replay
    def _rebuild_adapter(
        structure_id: str,
        history: list[dict[str, Any]],
    ) -> tuple[BaseAdapter, list[dict[str, Any]]]:
        """Replay mutations; retain recorded successful searches without executing them again."""
        adapter = StructureService._new_adapter(structure_id)
        valid_history: list[dict[str, Any]] = []

        for step in history:
            operation = step.get("operation")
            payload = step.get("payload", {})
            if not isinstance(operation, str) or not isinstance(payload, dict):
                continue
            # Successful hidden readonly queries are journal entries, never replayed mutations.
            if structure_id == "priority_queue" and operation == "frente":
                valid_history.append({"operation": operation, "payload": deepcopy(payload)})
                continue
            # Search records describe completed actions, not state reconstruction.
            if (structure_id, operation) in {
                ("linked_list", "buscar_elemento"),
                ("circular_list", "buscar_posiciones"),
                ("sublist", "hijos_de"),
            }:
                try:
                    BaseAdapter._require_int(payload, "parent", "padre") if structure_id == "sublist" else BaseAdapter._require_int(payload, "value", "valor")
                except (ValueError, TypeError):
                    continue
                valid_history.append({"operation": operation, "payload": deepcopy(payload)})
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
        if isinstance(error, PosicionInvalidaError):
            return "La posición ingresada es inválida para el estado actual."
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
        if structure_id in StructureService._C_FIRST_STRUCTURES:
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
        """Build the data needed to render one structure page."""
        structure = StructureService.get_structure(structure_id)
        adapter, valid_history = StructureService._rebuild_adapter(structure_id, history)
        return {
            "id": structure_id,
            "name": structure["name"],
            "description": structure["description"],
            "operations": adapter.get_supported_operations(),
            "visual_state": adapter.to_visual_state(),
            "didactic": StructureService._didactic_content(structure_id),
            "history": valid_history,
            "guided_examples": deepcopy(SEQUENTIAL_GUIDED_EXAMPLES.get(structure_id, [])),
        }

    @staticmethod
    def execute_operation(
        structure_id: str,
        operation_name: str,
        payload: dict[str, Any],
        history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Execute an operation over a rebuilt structure state."""
        adapter, valid_history = StructureService._rebuild_adapter(structure_id, history)
        didactic_data = StructureService._didactic_content(structure_id)
        before_state = adapter.to_visual_state()
        operations = adapter.get_supported_operations()
        operation_meta = next((item for item in operations if item["name"] == operation_name), None)

        if operation_meta is None:
            message = "La operación solicitada no está soportada por esta estructura."
            if structure_id == "stack" and operation_name == "cima":
                from app.domain.sequential.stack_top_instruction import build_stack_top_rejection_trace
                source_code, code_title = ExecutionTraceService._get_operation_source(
                    didactic_data=didactic_data, operation_name=operation_name)
                trace = build_stack_top_rejection_trace(payload=payload, source_code=source_code,
                    code_title=code_title, before_state=before_state, message=message)
            elif structure_id == "queue" and operation_name in {"frente", "final"}:
                from app.domain.sequential.queue_query_instruction import build_queue_query_rejection_trace
                source_code, code_title = ExecutionTraceService._get_operation_source(
                    didactic_data=didactic_data, operation_name=operation_name)
                trace = build_queue_query_rejection_trace(operation_name=operation_name, payload=payload,
                    source_code=source_code, code_title=code_title, before_state=before_state, message=message)
            elif structure_id == "priority_queue" and operation_name.removeprefix("cp_") in {
                    "inicializar", "vacia", "contar", "copiar_items", "formatear"}:
                from app.domain.sequential.priority_queue_helpers_instruction import build_priority_helper_rejection_trace
                source_code, code_title = ExecutionTraceService._get_operation_source(
                    didactic_data=didactic_data, operation_name=operation_name.removeprefix("cp_"))
                trace = build_priority_helper_rejection_trace(operation_name=operation_name, payload=payload,
                    source_code=source_code, code_title=code_title, before_state=before_state, message=message)
            elif structure_id in {"stack", "queue"} and operation_name == "mostrar":
                from app.domain.sequential.show_instruction import build_show_rejection_trace
                source_code, code_title = ExecutionTraceService._get_operation_source(
                    didactic_data=didactic_data, operation_name=operation_name)
                trace = build_show_rejection_trace(structure_id=structure_id, payload=payload, source_code=source_code,
                    code_title=code_title, before_state=before_state, message=message)
            else:
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
            message = StructureService._didactic_error(error)
            after_state = adapter.to_visual_state()
            if structure_id == "sublist" and operation_name in {"insertar_padre", "insertar_hijo", "eliminar_padre", "eliminar_hijo", "hijos_de"}:
                try:
                    adapter._require_int(payload, "parent", "padre")
                    if operation_name in {"insertar_hijo", "eliminar_hijo"}:
                        adapter._require_int(payload, "child", "hijo")
                except (ValueError, TypeError):
                    source_code, code_title = ExecutionTraceService._get_operation_source(
                        didactic_data=didactic_data, operation_name=operation_name)
                    trace = {"structure_id": structure_id, "operation_name": operation_name,
                        "payload": deepcopy(payload), "success": False, "mutates": False,
                        "message": message, "source_code": source_code, "code_title": code_title,
                        "steps": [], "final_state": deepcopy(after_state), "execution_started": False,
                        "validation": {"stage": "API", "accepted": False, "message": message}}
                    return {"success": False, "message": message, "visual_state": after_state,
                        "history": valid_history, "execution_trace": trace}
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

        successful_search = (structure_id, operation_name) in {
            ("priority_queue", "frente"),
            ("linked_list", "buscar_elemento"),
            ("circular_list", "buscar_posiciones"),
                ("sublist", "hijos_de"),
        }
        if operation_meta.get("mutates", False) or successful_search:
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
