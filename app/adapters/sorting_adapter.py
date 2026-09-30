"""Adapter for the sorting module."""

from __future__ import annotations

import random
from typing import Any

from app.services.trace.engine import TraceEngine

from app.adapters.base_adapter import BaseAdapter
from app.domain.sorting import SORTING_ALGORITHMS, SortingExecutionError, SortingInterpreter
from app.domain.sorting.pedagogy import (
    PEDAGOGICAL_FRAME_SCHEMA_VERSION,
    build_pedagogical_frame,
    learning_profile,
    pedagogical_frame_schema,
    theory_profile,
    validate_pedagogical_frame,
)


class SortingAdapter(BaseAdapter):
    """Adapt sorting simulation to the common visualizer contract."""

    _MAX_SIZE = 80
    _C_INT_MIN = -(2**31)
    _C_INT_MAX = 2**31 - 1
    _LINE_PATTERNS: dict[str, dict[str, str]] = {
        "intercambio": {"compare": "if (arreglo[i] > arreglo[j])", "swap": "intercambiar(&arreglo[i], &arreglo[j])"},
        "seleccion": {"init_min": "indice_menor = i;", "compare_min": "if (arreglo[j] < arreglo[indice_menor])", "set_min": "indice_menor = j;", "swap": "intercambiar(&arreglo[i], &arreglo[indice_menor])"},
        "insercion": {"take_key": "int clave = arreglo[i];", "while_compare": "while (j > 0 && arreglo[j - 1] > clave)", "shift": "arreglo[j] = arreglo[j - 1];", "insert_key": "arreglo[j] = clave;"},
        "burbuja": {"compare": "if (arreglo[j] > arreglo[j + 1])", "swap": "intercambiar(&arreglo[j], &arreglo[j + 1])", "break": "if (!hubo_intercambio) break;"},
        "shell": {"gap": "for (intervalo = n / 2; intervalo > 0; intervalo /= 2)", "take_temp": "int temporal = arreglo[i];", "gap_compare": "while (j >= intervalo && arreglo[j - intervalo] > temporal)", "gap_shift": "arreglo[j] = arreglo[j - intervalo];", "gap_insert": "arreglo[j] = temporal;"},
        "quicksort": {"pivot": "int i = primero, j = ultimo, pivote =", "move_i": "while (arreglo[i] < pivote)", "move_j": "while (arreglo[j] > pivote)", "partition_swap": "intercambiar(&arreglo[i], &arreglo[j]);"},
        "mergesort": {"split": "mergesort_recursivo(arreglo, auxiliar, izquierda, medio);", "merge_compare": "if (arreglo[i] <= arreglo[j])", "merge_copy_back": "for (i = izquierda; i <= derecha; ++i) arreglo[i] = auxiliar[i];"},
        "heapsort": {"heap_compare_left": "if (izquierdo < n && arreglo[izquierdo] > arreglo[mayor])", "heap_compare_right": "if (derecho < n && arreglo[derecho] > arreglo[mayor])", "heap_swap": "intercambiar(&arreglo[raiz], &arreglo[mayor]);", "heap_extract": "intercambiar(&arreglo[0], &arreglo[i - 1]);"},
        "counting_sort": {"count_init": "conteo = (int *)calloc(rango, sizeof(int));", "count_fill": "++conteo[arreglo[i] - minimo];", "count_write": "while (conteo[i] > 0)"},
        "binsort": {"count_init": "conteo = (int *)calloc(rango, sizeof(int));", "count_fill": "++conteo[arreglo[i] - minimo];", "count_write": "while (conteo[i] > 0)", "binsort_delegate": "return ordenar_counting_sort(arreglo, n);"},
        "radixsort": {"radix_split": "if (arreglo[i] < 0) negativos[cant_negativos++] = 0U - (uint32_t)arreglo[i];", "radix_digit": "counting_por_digito", "radix_merge": "uint32_t magnitud = negativos[i - 1];"},
    }

    def __init__(self) -> None:
        self._array: list[int] = []
        self._algorithm_id: str = "burbuja"
        self._last_operation: dict[str, Any] = {"name": "create", "status": "success", "message": "Modulo inicializado."}
        self._last_result: dict[str, Any] | None = None
        self._last_trace: dict[str, Any] | None = None
        self.create()

    def create(self) -> None:
        """Create or recreate the sorting state."""
        self._array = []
        self._algorithm_id = "burbuja"
        self._last_result = None
        self._last_trace = None
        self._last_operation = {
            "name": "create",
            "status": "success",
            "message": "Modulo de ordenamiento listo.",
        }

    def _set_operation(self, name: str, message: str, success: bool = True) -> None:
        self._last_operation = {
            "name": name,
            "status": "success" if success else "error",
            "message": message,
        }

    @staticmethod
    def _parse_manual_values(payload: dict[str, Any]) -> list[int]:
        raw = payload.get("values")
        if isinstance(raw, list):
            out: list[int] = []
            try:
                for value in raw:
                    out.append(int(str(value).strip()))
            except (TypeError, ValueError) as error:
                raise ValueError("Cada posicion del arreglo debe contener un entero.") from error
            return out
        text = BaseAdapter._require_text(payload, "values", "valores")
        raw_items = text.split(",")
        if any(not item.strip() for item in raw_items):
            raise ValueError("Cada posicion del arreglo debe contener un entero.")
        items = [item.strip() for item in raw_items]
        if not items:
            raise ValueError("Debes ingresar al menos un numero en el arreglo.")
        try:
            return [int(item) for item in items]
        except ValueError as error:
            raise ValueError("Cada posicion del arreglo debe contener un entero.") from error

    @staticmethod
    def _validate_values(values: list[int]) -> None:
        if not values:
            raise ValueError("El arreglo no puede estar vacio.")
        if len(values) > SortingAdapter._MAX_SIZE:
            raise ValueError(f"El arreglo no puede superar {SortingAdapter._MAX_SIZE} elementos.")
        if any(value < SortingAdapter._C_INT_MIN or value > SortingAdapter._C_INT_MAX for value in values):
            raise ValueError("Cada valor debe pertenecer al rango de int C (-2147483648 a 2147483647).")

    def create_array(self, values: list[int]) -> dict[str, Any]:
        """Create array from user values."""
        self._validate_values(values)
        self._array = list(values)
        self._last_result = {"array": list(self._array)}
        self._last_trace = None
        self._set_operation("create_array", f"Arreglo creado con {len(values)} elementos.")
        return {"message": self._last_operation["message"], "result": self._last_result}

    def generate_random_array(
        self,
        size: int,
        min_value: int,
        max_value: int,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """Generate didactic random array."""
        if size <= 0:
            raise ValueError("El tamano del arreglo debe ser mayor a 0.")
        if size > self._MAX_SIZE:
            raise ValueError(f"El tamano maximo permitido es {self._MAX_SIZE}.")
        if min_value > max_value:
            raise ValueError("El valor minimo no puede ser mayor al maximo.")
        self._validate_values([min_value, max_value])
        effective_seed = seed if seed is not None else random.randint(1, 1_000_000_000)
        rng = random.Random(effective_seed)
        self._array = [rng.randint(min_value, max_value) for _ in range(size)]
        self._last_trace = None
        self._last_result = {"array": list(self._array)}
        self._set_operation("generate_random_array", f"Arreglo aleatorio generado con {size} elementos.")
        return {
            "message": self._last_operation["message"],
            "result": {**self._last_result, "seed": effective_seed},
        }

    def select_algorithm(self, algorithm_id: str) -> dict[str, Any]:
        """Select algorithm for next execution."""
        valid = {item["id"] for item in SORTING_ALGORITHMS}
        if algorithm_id not in valid:
            raise ValueError("El algoritmo seleccionado no existe en el TAD.")
        self._algorithm_id = algorithm_id
        self._last_trace = None
        self._set_operation("select_algorithm", f"Algoritmo seleccionado: {algorithm_id}.")
        return {"message": self._last_operation["message"], "result": {"algorithm": algorithm_id}}

    def _build_visual_state_from_step(
        self,
        step: dict[str, Any],
        *,
        algorithm_id: str,
    ) -> dict[str, Any]:
        return {
            "structure": "sorting_array",
            "kind": "sorting_array",
            "title": "Arreglo de ordenamiento",
            "algorithm": algorithm_id,
            "items": list(step.get("array_snapshot", [])),
            "highlighted_indices": list(step.get("comparing_indices", [])),
            "comparing_indices": list(step.get("comparing_indices", [])),
            "swapping_indices": list(step.get("swapping_indices", [])),
            "sorted_indices": list(step.get("sorted_indices", [])),
            "active_range": step.get("active_range"),
            "pivot_index": step.get("pivot_index"),
            "auxiliary_array": step.get("auxiliary_snapshot"),
            "temporaries": dict(step.get("temporaries", {})),
            "trace_token": str(step.get("line_token") or ""),
            "trace_action": str(step.get("action") or ""),
            "metrics": {
                "comparisons": int(step.get("metrics", {}).get("comparisons", 0)),
                "swaps": int(step.get("metrics", {}).get("swaps", 0)),
                "moves": int(step.get("metrics", {}).get("moves", 0)),
                "steps": int(step.get("step", 0)),
            },
            "last_operation": {
                "name": algorithm_id,
                "status": "running",
                "message": str(step.get("action", "")),
            },
        }

    @staticmethod
    def _build_line_lookup(source_code: str, patterns: dict[str, str]) -> dict[str, int | None]:
        rows = str(source_code or "").replace("\r\n", "\n").split("\n")
        lookup: dict[str, int | None] = {}
        for token, pattern in patterns.items():
            line_index: int | None = None
            for idx, row in enumerate(rows):
                if pattern in row:
                    line_index = idx
                    break
            lookup[token] = line_index
        return lookup

    def run(self, mode: str, *, source_code: str = "") -> dict[str, Any]:
        """Run sorting simulation in fast or step mode."""
        if mode not in {"fast", "step_by_step"}:
            raise ValueError("El modo debe ser 'fast' o 'step_by_step'.")
        if not self._array:
            raise ValueError("Debes crear primero un arreglo para ordenar.")

        interpreter = SortingInterpreter(self._array, self._algorithm_id)
        run_result = interpreter.run()
        raw_steps = run_result["steps"]
        patterns = {
            **self._LINE_PATTERNS.get(self._algorithm_id, {}),
            "validate_array": "return arreglo != NULL && n > 0;",
            "swap_guard": "if (a == NULL || b == NULL) return;",
            "swap_temp": "temporal = *a;",
            "swap_assign_a": "*a = *b;",
            "swap_assign_b": "*b = temporal;",
        }
        line_lookup = self._build_line_lookup(source_code, patterns)
        source_lines = str(source_code or "").replace("\r\n", "\n").split("\n")
        line_lookup["entry"] = next(
            (index for index, line in enumerate(source_lines) if f"ordenar_{self._algorithm_id}(" in line),
            next((index for index, line in enumerate(source_lines) if "ordenar_" in line and "(" in line), None),
        )
        line_lookup["return"] = next(
            (index for index in range(len(source_lines) - 1, -1, -1) if "return ORDENAMIENTO_OK" in source_lines[index]),
            next((index for index in range(len(source_lines) - 1, -1, -1) if source_lines[index].strip()), line_lookup.get("entry")),
        )

        execution_steps: list[dict[str, Any]] = []
        for idx, raw_step in enumerate(raw_steps):
            prev = raw_steps[idx - 1] if idx > 0 else raw_steps[0]
            state_snapshot = self._build_visual_state_from_step(prev, algorithm_id=self._algorithm_id)
            state_after = self._build_visual_state_from_step(raw_step, algorithm_id=self._algorithm_id)
            token = str(raw_step.get("line_token") or "")
            line_index = line_lookup.get(token, None)
            line_text = ""
            if isinstance(line_index, int) and 0 <= line_index < len(source_lines):
                line_text = source_lines[line_index]
            execution_steps.append(
                {
                    "step_index": idx,
                    "line_index": line_index,
                    "line_text": line_text,
                    "event_type": "line",
                    "phase": "single" if len(raw_steps) == 1 else "start" if idx == 0 else "end" if idx == len(raw_steps) - 1 else "progress",
                    "delay_ms": 160,
                    "state_snapshot": state_snapshot,
                    "state_after": state_after,
                    "debug": {"stage": "sorting", "note": str(raw_step.get("action", ""))},
                }
            )
            pedagogical = build_pedagogical_frame(
                algorithm_id=self._algorithm_id,
                raw_step=raw_step,
                line_index=line_index,
                line_text=line_text,
            )
            validate_pedagogical_frame(pedagogical, source_code=source_code)
            execution_steps[-1]["pedagogy"] = pedagogical

        final_state = self._build_visual_state_from_step(raw_steps[-1], algorithm_id=self._algorithm_id)
        final_state["last_operation"] = {
            "name": self._algorithm_id,
            "status": "success",
            "message": "Ordenamiento finalizado.",
        }
        execution_steps[-1]["state_after"] = final_state
        self._array = list(final_state["items"])
        self._last_trace = {
            "structure_id": "sorting",
            "operation_name": self._algorithm_id,
            "payload": {},
            "success": True,
            "mutates": True,
            "message": "Ordenamiento ejecutado correctamente.",
            "code_title": "Codigo C",
            "source_code": source_code,
            "steps": execution_steps,
            "final_state": final_state,
            "pedagogy_schema_version": PEDAGOGICAL_FRAME_SCHEMA_VERSION,
            "pedagogy_schema": pedagogical_frame_schema(),
            "learning_profile": learning_profile(self._algorithm_id),
            "theory_profile": theory_profile(self._algorithm_id),
        }
        TraceEngine.validate_legacy_trace(self._last_trace)
        self._last_result = {
            "mode": mode,
            "algorithm": self._algorithm_id,
            "metrics": run_result["metrics"],
            "array": list(self._array),
        }
        self._set_operation("run", f"Ordenamiento ejecutado con {self._algorithm_id}.")
        return {
            "message": self._last_operation["message"],
            "result": self._last_result,
            "execution_trace": self._last_trace,
            "visual_state": final_state,
        }

    def step(self, direction: str, cursor: int, *, source_code: str = "") -> dict[str, Any]:
        """Move one step in the execution trace."""
        if direction == "prev":
            direction = "previous"
        if direction not in {"next", "previous"}:
            raise ValueError("La direccion del paso debe ser 'next' o 'previous'.")
        trace_result = self.run("step_by_step", source_code=source_code)
        trace = trace_result["execution_trace"]
        steps = trace.get("steps", [])
        if not steps:
            raise ValueError("No hay pasos disponibles para esta ejecucion.")
        next_cursor = cursor + 1 if direction == "next" else cursor - 1
        next_cursor = max(0, min(next_cursor, len(steps) - 1))
        current = steps[next_cursor]
        return {
            "message": f"Paso {next_cursor + 1}/{len(steps)}.",
            "cursor": next_cursor,
            "total_steps": len(steps),
            "step": current,
            "visual_state": current["state_after"],
            "execution_trace": trace,
        }

    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute one supported operation."""
        if operation_name == "create_array":
            return self.create_array(self._parse_manual_values(payload))
        if operation_name == "generate_random_array":
            size = self._require_int(payload, "size", "tamano")
            min_value = self._require_int(payload, "min_value", "minimo")
            max_value = self._require_int(payload, "max_value", "maximo")
            seed = payload.get("seed")
            seed_value = int(seed) if seed is not None and str(seed).strip() != "" else None
            return self.generate_random_array(size=size, min_value=min_value, max_value=max_value, seed=seed_value)
        if operation_name == "select_algorithm":
            algorithm_id = self._require_text(payload, "algorithm_id", "algoritmo")
            return self.select_algorithm(algorithm_id)
        if operation_name == "run":
            mode = self._require_text(payload, "mode", "modo")
            source_code = str(payload.get("source_code") or "")
            return self.run(mode=mode, source_code=source_code)
        if operation_name == "step":
            direction = self._require_text(payload, "direction", "direccion")
            cursor = int(payload.get("cursor", -1))
            source_code = str(payload.get("source_code") or "")
            return self.step(direction=direction, cursor=cursor, source_code=source_code)
        if operation_name == "reset":
            self.reset()
            return {"message": "Estado de ordenamiento reiniciado correctamente."}
        raise SortingExecutionError(f"Operacion no soportada: {operation_name}.")

    def to_visual_state(self) -> dict[str, Any]:
        """Return visual state for frontend."""
        return {
            "structure": "sorting_array",
            "kind": "sorting_array",
            "title": "Arreglo de ordenamiento",
            "algorithm": self._algorithm_id,
            "items": list(self._array),
            "highlighted_indices": [],
            "comparing_indices": [],
            "swapping_indices": [],
            "sorted_indices": [],
            "active_range": [0, len(self._array) - 1] if self._array else None,
            "pivot_index": None,
            "auxiliary_array": None,
            "metrics": {
                "comparisons": int(self._last_result.get("metrics", {}).get("comparisons", 0)) if self._last_result else 0,
                "swaps": int(self._last_result.get("metrics", {}).get("swaps", 0)) if self._last_result else 0,
                "moves": int(self._last_result.get("metrics", {}).get("moves", 0)) if self._last_result else 0,
                "steps": int(self._last_result.get("metrics", {}).get("steps", 0)) if self._last_result else 0,
            },
            "metadata": {"size": len(self._array), "max_size": self._MAX_SIZE, "is_empty": len(self._array) == 0},
            "last_operation": self._last_operation,
            "last_result": self._last_result,
        }

    def reset(self) -> None:
        """Reset adapter state."""
        self.create()

    def get_supported_algorithms(self) -> list[dict[str, str]]:
        """Return algorithm metadata."""
        return list(SORTING_ALGORITHMS)

    def get_supported_operations(self) -> list[dict[str, Any]]:
        """Return operation metadata."""
        return [
            {
                "name": "create_array",
                "label": "Crear arreglo",
                "mutates": True,
                "inputs": [{"name": "values", "label": "Valores (csv)", "type": "text"}],
            },
            {
                "name": "generate_random_array",
                "label": "Generar arreglo aleatorio",
                "mutates": True,
                "inputs": [
                    {"name": "size", "label": "Tamano", "type": "number"},
                    {"name": "min_value", "label": "Minimo", "type": "number"},
                    {"name": "max_value", "label": "Maximo", "type": "number"},
                ],
            },
            {
                "name": "select_algorithm",
                "label": "Seleccionar algoritmo",
                "mutates": True,
                "inputs": [{"name": "algorithm_id", "label": "Algoritmo", "type": "text"}],
            },
            {
                "name": "run",
                "label": "Ejecutar ordenamiento",
                "mutates": True,
                "inputs": [{"name": "mode", "label": "Modo", "type": "text"}],
            },
            {
                "name": "step",
                "label": "Paso de ejecucion",
                "mutates": False,
                "inputs": [
                    {"name": "direction", "label": "Direccion", "type": "text"},
                    {"name": "cursor", "label": "Cursor", "type": "number"},
                ],
            },
            {"name": "reset", "label": "Reiniciar", "mutates": True, "inputs": []},
        ]
