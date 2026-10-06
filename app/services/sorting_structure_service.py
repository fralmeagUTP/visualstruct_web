"""Service layer for sorting module orchestration."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.adapters.sorting_adapter import SortingAdapter
from app.services.observability import observe_replay
from app.domain.sorting import SortingExecutionError
from app.services.c_code_service import CCodeService
from app.services.pseudocode_service import PseudocodeService
from app.services.sorting_main_program import build_sorting_main


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
    @observe_replay
    def _rebuild_adapter(structure_id: str, history: list[dict[str, Any]]) -> tuple[SortingAdapter, list[dict[str, Any]]]:
        adapter = SortingStructureService._new_adapter(structure_id)
        assert isinstance(adapter, SortingAdapter)
        valid_history: list[dict[str, Any]] = []
        for step in history if isinstance(history, list) else []:
            if not isinstance(step, dict):
                continue
            operation = step.get("operation")
            payload = step.get("payload", {})
            if not isinstance(operation, str) or not isinstance(payload, dict):
                continue
            try:
                if operation == "generate_random_array":
                    materialized = step.get("materialized_values")
                    if materialized is None:
                        # Earlier accepted entries store an effective seed. Materialize
                        # them once for the returned history; never invent a new seed.
                        if payload.get("seed") is None or str(payload["seed"]).strip() == "":
                            continue
                        adapter.execute(operation, payload)
                        materialized = adapter.to_visual_state()["items"]
                    else:
                        if not isinstance(materialized, list) or any(type(v) is not int for v in materialized):
                            continue
                        size = adapter._require_int(payload, "size", "tamano")
                        low = adapter._require_int(payload, "min_value", "minimo")
                        high = adapter._require_int(payload, "max_value", "maximo")
                        adapter._validate_values([low, high])
                        if len(materialized) != size or low > high or any(not low <= v <= high for v in materialized):
                            continue
                        adapter.create_array(list(materialized))
                        adapter._set_operation(operation, f"Arreglo aleatorio generado con {size} elementos.")
                    valid_history.append({"operation": operation, "payload": deepcopy(payload), "materialized_values": list(materialized)})
                    continue
                elif operation in {"create_array", "select_algorithm"}:
                    adapter.execute(operation, payload)
                    if operation == "create_array":
                        payload = {"values": adapter.to_visual_state()["items"]}
                elif operation == "run":
                    effect = step.get("array_effect")
                    algorithm = payload.get("algorithm_id")
                    if not isinstance(effect, dict) or effect.get("schema") != 1:
                        continue
                    original, ordered = effect.get("input"), effect.get("output")
                    if not isinstance(original, list) or not isinstance(ordered, list):
                        continue
                    if any(type(v) is not int for v in original + ordered):
                        continue
                    adapter._validate_values(original)
                    adapter._validate_values(ordered)
                    if original != adapter.to_visual_state()["items"] or ordered != sorted(original):
                        continue
                    if payload.get("mode") not in {"fast", "step_by_step"}:
                        continue
                    if algorithm in {"counting_sort", "binsort"} and max(original) - min(original) + 1 > 1_000_000:
                        continue
                    adapter.select_algorithm(str(algorithm))
                    adapter.create_array(list(ordered))
                    adapter._set_operation("run", f"Ordenamiento ejecutado con {algorithm}.")
                    valid_history.append({"operation": operation, "payload": deepcopy(payload), "array_effect": deepcopy(effect)})
                    continue
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
            "main_c": build_sorting_main(valid_history),
        }

    @staticmethod
    def execute_operation(
        *,
        structure_id: str,
        operation_name: str,
        payload: dict[str, Any],
        history: list[dict[str, Any]],
        counting_allocator=None,
        radix_allocator=None,
    ) -> dict[str, Any]:
        adapter, valid_history = SortingStructureService._rebuild_adapter(structure_id, history)
        adapter._counting_allocator = counting_allocator
        adapter._radix_allocator = radix_allocator
        didactic_data = SortingStructureService._didactic_content(structure_id)
        # Legacy step API reconstructs the last execution from its actual input.
        # GET/topology reconstruction itself never dispatches a historical run.
        if operation_name == "step" and valid_history and valid_history[-1]["operation"] == "run":
            previous = valid_history[-1]
            if not payload.get("algorithm_id") or payload["algorithm_id"] == previous["payload"]["algorithm_id"]:
                adapter.create_array(list(previous["array_effect"]["input"]))
        before_state = adapter.to_visual_state()
        adapter._counting_accepted_state = deepcopy(before_state)
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
            source_algorithm = str(active_algorithm or adapter.to_visual_state().get("algorithm") or "")
            source_code = str(
                didactic_data.get("operations", {}).get(
                    source_algorithm,
                    didactic_data.get("default_operation", ""),
                )
            )
            payload = dict(payload)
            payload["source_code"] = source_code

        try:
            result = adapter.execute(operation_name, payload)
        except (SortingExecutionError, ValueError, TypeError) as error:
            message = SortingStructureService._didactic_error(error)
            response = {
                "success": False,
                "message": message,
                "visual_state": before_state if (
                    getattr(error, "execution_trace", None)
                    or (operation_name == "run" and (payload.get("algorithm_id") or before_state.get("algorithm")) in {"binsort", "radixsort"})
                ) else adapter.to_visual_state(),
                "history": valid_history,
            }
            if getattr(error, "execution_trace", None):
                response["execution_trace"] = error.execution_trace
            return response

        if operation_meta.get("mutates", False) and operation_name in {"create_array", "generate_random_array", "select_algorithm"}:
            if operation_name == "generate_random_array":
                effective_seed = result.get("result", {}).get("seed")
                if effective_seed is not None:
                    payload = {**payload, "seed": effective_seed}
            if operation_name == "create_array":
                payload = {"values": list(result["result"]["array"])}
            entry = {"operation": operation_name, "payload": deepcopy(payload)}
            if operation_name == "generate_random_array":
                entry["materialized_values"] = list(result["result"]["array"])
            valid_history.append(entry)

        if operation_name == "run":
            valid_history.append({
                "operation": "run",
                "payload": {"mode": payload["mode"], "algorithm_id": result["result"]["algorithm"]},
                "array_effect": {"schema": 1, "input": list(before_state["items"]), "output": list(result["result"]["array"])},
            })

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

    @staticmethod
    def compare_algorithms(*, values: Any, left_algorithm: str, right_algorithm: str) -> dict[str, Any]:
        """Execute two isolated traces over defensive copies of one immutable input."""
        parser = SortingAdapter()
        parsed = parser._parse_manual_values({"values": values})
        parser._validate_values(parsed)
        didactic = SortingStructureService._didactic_content("sorting_array")

        def execute(algorithm_id: str) -> dict[str, Any]:
            adapter = SortingAdapter()
            adapter.create_array(list(parsed))
            adapter.select_algorithm(algorithm_id)
            source = str(didactic.get("operations", {}).get(algorithm_id, ""))
            result = adapter.run("step_by_step", source_code=source)
            return {"algorithm": algorithm_id, "trace": result["execution_trace"], "result": result["result"]}

        return {"success": True, "input": list(parsed), "left": execute(left_algorithm), "right": execute(right_algorithm)}
