"""Versioned pedagogical contract for sorting execution frames."""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any, Mapping


PEDAGOGICAL_FRAME_SCHEMA_VERSION = 1
PEDAGOGICAL_LEVELS = ("basic", "intermediate", "advanced")


SORTING_LEARNING_CATALOG: dict[str, dict[str, Any]] = {
    "intercambio": {"objective": "Ordenar comparando cada posición con las posteriores.", "prior": ["arreglos", "ciclos anidados", "comparaciones"], "mastery": ["predice cada intercambio", "explica el prefijo confirmado"]},
    "seleccion": {"objective": "Seleccionar el mínimo del segmento pendiente en cada pasada.", "prior": ["arreglos", "índices", "mínimo"], "mastery": ["identifica el mínimo provisional", "justifica el prefijo ordenado"]},
    "insercion": {"objective": "Insertar cada clave en un prefijo previamente ordenado.", "prior": ["arreglos", "desplazamientos", "ciclos"], "mastery": ["ubica el hueco", "explica la estabilidad"]},
    "burbuja": {"objective": "Desplazar el mayor elemento hacia el final mediante comparaciones adyacentes.", "prior": ["arreglos", "comparaciones", "banderas booleanas"], "mastery": ["predice la frontera de pasada", "explica la terminación temprana"]},
    "shell": {"objective": "Ordenar subsecuencias separadas por intervalos decrecientes.", "prior": ["inserción", "división entera", "índices"], "mastery": ["forma los grupos por intervalo", "explica el paso final con intervalo uno"]},
    "quicksort": {"objective": "Particionar alrededor de un pivote y resolver recursivamente los subrangos.", "prior": ["recursión", "punteros o índices", "particiones"], "mastery": ["sigue i y j", "reconstruye el árbol de llamadas"]},
    "mergesort": {"objective": "Dividir el arreglo y fusionar segmentos ordenados mediante memoria auxiliar.", "prior": ["recursión", "arreglos auxiliares", "intervalos"], "mastery": ["reconstruye divisiones", "explica una fusión estable"]},
    "heapsort": {"objective": "Construir un max-heap y extraer repetidamente su raíz.", "prior": ["árbol binario", "representación en arreglo", "recursión"], "mastery": ["verifica la propiedad de heap", "distingue heap y sufijo ordenado"]},
    "counting_sort": {"objective": "Ordenar reconstruyendo el arreglo desde frecuencias de valores.", "prior": ["frecuencias", "rango mínimo-máximo", "memoria dinámica"], "mastery": ["calcula una urna", "explica el coste dependiente del rango"]},
    "binsort": {"objective": "Relacionar la distribución en urnas con la implementación C basada en conteos.", "prior": ["frecuencias", "delegación de funciones", "rangos"], "mastery": ["explica la delegación", "reconstruye desde urnas"]},
    "radixsort": {"objective": "Ordenar por dígitos estables y recombinar correctamente los signos.", "prior": ["valor posicional", "módulo y división", "estabilidad"], "mastery": ["identifica el dígito activo", "explica el tratamiento de negativos"]},
}

SORTING_THEORY_CATALOG: dict[str, dict[str, Any]] = {
    "intercambio": {"best": "O(n²)", "average": "O(n²)", "worst": "O(n²)", "memory": "O(1)", "stable": False, "in_place": True},
    "seleccion": {"best": "O(n²)", "average": "O(n²)", "worst": "O(n²)", "memory": "O(1)", "stable": False, "in_place": True},
    "insercion": {"best": "O(n)", "average": "O(n²)", "worst": "O(n²)", "memory": "O(1)", "stable": True, "in_place": True},
    "burbuja": {"best": "O(n)", "average": "O(n²)", "worst": "O(n²)", "memory": "O(1)", "stable": True, "in_place": True},
    "shell": {"best": "depende de gaps", "average": "depende de gaps", "worst": "O(n²)", "memory": "O(1)", "stable": False, "in_place": True},
    "quicksort": {"best": "O(n log n)", "average": "O(n log n)", "worst": "O(n²)", "memory": "O(log n) promedio", "stable": False, "in_place": True},
    "mergesort": {"best": "O(n log n)", "average": "O(n log n)", "worst": "O(n log n)", "memory": "O(n)", "stable": True, "in_place": False},
    "heapsort": {"best": "O(n log n)", "average": "O(n log n)", "worst": "O(n log n)", "memory": "O(1)", "stable": False, "in_place": True},
    "counting_sort": {"best": "O(n+k)", "average": "O(n+k)", "worst": "O(n+k)", "memory": "O(k)", "stable": False, "in_place": False},
    "binsort": {"best": "O(n+k)", "average": "O(n+k)", "worst": "O(n+k)", "memory": "O(k)", "stable": False, "in_place": False},
    "radixsort": {"best": "O(d(n+b))", "average": "O(d(n+b))", "worst": "O(d(n+b))", "memory": "O(n+b)", "stable": True, "in_place": False},
}

_INVARIANTS = {
    "intercambio": "Las posiciones anteriores al rango activo contienen sus valores definitivos.",
    "seleccion": "El prefijo confirmado contiene los menores valores en orden.",
    "insercion": "El prefijo hasta la clave actual permanece ordenado.",
    "burbuja": "El sufijo confirmado contiene los mayores valores en posición definitiva.",
    "shell": "Cada grupo separado por el intervalo actual queda ordenado por inserción.",
    "quicksort": "Fuera de los índices de exploración, los valores respetan la partición respecto al pivote.",
    "mergesort": "Cada segmento ya fusionado está ordenado y conserva todos sus elementos.",
    "heapsort": "La zona heap mantiene padre mayor o igual que sus hijos; el sufijo está ordenado.",
    "counting_sort": "La suma de frecuencias procesadas coincide con los elementos reconstruidos.",
    "binsort": "Cada urna representa exactamente la frecuencia de su valor.",
    "radixsort": "Tras cada dígito, el grupo queda establemente ordenado por los dígitos procesados.",
}


_CONCEPT_BY_TOKEN = {
    "entry": "call", "return": "return", "validate_array": "call",
    "compare": "comparison", "compare_min": "comparison", "while_compare": "condition",
    "gap_compare": "condition", "move_i": "condition", "move_j": "condition",
    "merge_compare": "comparison", "heap_compare_left": "condition",
    "heap_compare_right": "condition", "swap": "call", "partition_swap": "call",
    "heap_swap": "call", "heap_extract": "call", "swap_guard": "condition",
    "swap_temp": "assignment", "swap_assign_a": "assignment", "swap_assign_b": "assignment",
    "break": "branch", "split": "call", "binsort_delegate": "call",
}

_CONCEPT_EXPLANATIONS = {
    "call": "La ejecución entra en una función y conserva el punto al que deberá regresar.",
    "return": "La función termina y devuelve el control a quien la llamó.",
    "comparison": "Se comparan valores sin modificar todavía el arreglo.",
    "condition": "La expresión de C decide cuál será la siguiente rama ejecutada.",
    "branch": "El resultado de la condición selecciona una única ruta de ejecución.",
    "assignment": "Una asignación cambia el estado; los demás valores permanecen iguales.",
    "phase": "Comienza una nueva fase lógica del método de ordenamiento.",
}


class PedagogicalFrameValidationError(ValueError):
    """Raised when a pedagogical frame violates its published contract."""


def learning_profile(algorithm_id: str) -> dict[str, Any]:
    """Return a defensive copy of the learning profile for an algorithm."""
    try:
        return deepcopy(SORTING_LEARNING_CATALOG[algorithm_id])
    except KeyError as error:
        raise PedagogicalFrameValidationError(f"Algoritmo pedagógico desconocido: {algorithm_id}.") from error


def theory_profile(algorithm_id: str) -> dict[str, Any]:
    """Return theoretical properties, kept separate from observed metrics."""
    try:
        return deepcopy(SORTING_THEORY_CATALOG[algorithm_id])
    except KeyError as error:
        raise PedagogicalFrameValidationError(f"Algoritmo teórico desconocido: {algorithm_id}.") from error


def build_pedagogical_frame(
    *, algorithm_id: str, raw_step: Mapping[str, Any], line_index: int | None, line_text: str
) -> dict[str, Any]:
    """Build presentation-neutral pedagogy from an interpreter event."""
    token = str(raw_step.get("line_token") or "")
    action = str(raw_step.get("action") or "")
    concept = _CONCEPT_BY_TOKEN.get(token, "phase" if token in {"entry", "return", "gap", "pivot", "split"} else "assignment")
    temporaries = dict(raw_step.get("temporaries") or {})
    array = list(raw_step.get("array_snapshot") or [])
    comparing = list(raw_step.get("comparing_indices") or raw_step.get("swapping_indices") or [])
    active_range = list(raw_step.get("active_range") or [])
    variables = [
        {"name": name, "value": value, "type": "int", "changed": True, "meaning": "Variable temporal del algoritmo."}
        for name, value in temporaries.items()
    ]
    index_names = {
        "burbuja": ("j", "j + 1"), "intercambio": ("i", "j"), "seleccion": ("j", "indice_menor"),
        "insercion": ("j - 1", "j"), "shell": ("j - intervalo", "j"),
        "quicksort": ("i/j", "pivote"), "mergesort": ("i", "j"), "heapsort": ("hijo", "mayor"),
    }
    for name, index in zip(index_names.get(algorithm_id, ("i", "j")), comparing):
        variables.append({"name": name, "value": index, "type": "size_t", "changed": False, "meaning": "Índice activo en el arreglo."})
    if active_range:
        variables.extend([
            {"name": "limite_inferior", "value": active_range[0], "type": "size_t", "changed": False, "meaning": "Inicio del rango activo."},
            {"name": "limite_superior", "value": active_range[-1], "type": "size_t", "changed": False, "meaning": "Fin del rango activo."},
        ])
    stack = [{"function": f"ordenar_{algorithm_id}", "parameters": {"n": len(array)}, "continuation": "retornar al llamador"}]
    if token.startswith("swap_"):
        stack.append({"function": "intercambiar", "parameters": {"a": comparing[0] if comparing else None, "b": comparing[1] if len(comparing) > 1 else None}, "continuation": "instrucción posterior a intercambiar"})
    elif algorithm_id in {"quicksort", "mergesort"} and active_range:
        recursive_name = "quicksort_recursivo" if algorithm_id == "quicksort" else "mergesort_recursivo"
        stack.append({"function": recursive_name, "parameters": {"inicio": active_range[0], "fin": active_range[-1]}, "continuation": "continuar el subrango pendiente"})
    elif algorithm_id == "heapsort" and token.startswith("heap_"):
        stack.append({"function": "hundir", "parameters": {"n": active_range[-1] + 1 if active_range else len(array)}, "continuation": "continuar construcción o extracción"})
    condition = None
    if concept in {"condition", "comparison", "branch"}:
        result = None
        expression = action.rstrip(".")
        boolean_match = re.search(r":\s*(True|False)$", expression)
        insertion_match = re.search(r"Comparar clave (-?\d+) con arreglo\[\d+\]=(-?\d+)", expression)
        shell_match = re.search(r"Comparar arreglo\[\d+\] con temporal (-?\d+)", expression)
        if boolean_match:
            result = boolean_match.group(1) == "True"
        elif insertion_match:
            key, previous = map(int, insertion_match.groups())
            expression, result = f"{previous} > {key}", previous > key
        elif shell_match and comparing:
            temporal = int(shell_match.group(1))
            previous = array[comparing[0]]
            expression, result = f"{previous} > {temporal}", previous > temporal
        elif len(comparing) >= 2 and all(isinstance(index, int) and 0 <= index < len(array) for index in comparing[:2]):
            left, right = array[comparing[0]], array[comparing[1]]
            if token in {"compare", "gap_compare", "while_compare", "heap_compare_left", "heap_compare_right"}:
                result = left > right
            elif token == "compare_min":
                result = left < right
            elif token == "merge_compare":
                result = left <= right
            expression = f"{left} {'<' if token == 'compare_min' else '<=' if token == 'merge_compare' else '>'} {right}"
        elif token == "swap_guard":
            expression, result = "a == NULL || b == NULL", False
        condition = {"expression": expression, "result": result, "consequence": "Se ejecuta la rama verdadera." if result is True else "Se continúa por la rama falsa." if result is False else "El resultado se muestra al evaluar la instrucción."}
    loop_tokens = {"compare", "compare_min", "while_compare", "gap", "gap_compare", "move_i", "move_j", "merge_compare", "heap_compare_left", "heap_compare_right", "count_fill", "count_write", "radix_digit"}
    loop = None
    if token in loop_tokens:
        loop = {"kind": "while" if token in {"while_compare", "gap_compare", "move_i", "move_j", "merge_compare", "count_write"} else "for", "iteration": int(raw_step.get("step") or 1), "bounds": active_range or [0, max(len(array) - 1, 0)], "exit": condition is not None and condition.get("result") is False}
    pointers = []
    if token.startswith("swap_"):
        pointer_indices = list(raw_step.get("pointer_indices") or comparing)
        pointers = [
            {"name": "a", "target": f"arreglo[{pointer_indices[0]}]" if pointer_indices else "NULL", "value": array[pointer_indices[0]] if pointer_indices else None},
            {"name": "b", "target": f"arreglo[{pointer_indices[1]}]" if len(pointer_indices) > 1 else "NULL", "value": array[pointer_indices[1]] if len(pointer_indices) > 1 else None},
        ]
    profile = learning_profile(algorithm_id)
    concept_explanation = _CONCEPT_EXPLANATIONS[concept]
    return {
        "schema_version": PEDAGOGICAL_FRAME_SCHEMA_VERSION,
        "concept": concept,
        "phase": {"id": token or "execution", "label": token.replace("_", " ").title() or "Ejecución", "goal": action},
        "condition": condition,
        "variables": variables,
        "call_stack": stack,
        "loop": loop,
        "pointers": pointers,
        "invariant": {"text": _INVARIANTS[algorithm_id], "indices": list(raw_step.get("sorted_indices") or []), "holds": True},
        "narration": {
            "basic": f"{profile['objective']} Ahora: {action}",
            "intermediate": f"{concept_explanation} {action}",
            "advanced": f"{concept_explanation} {action} Línea C: {line_text.strip() or 'no disponible'}.",
        },
        "source": {"line_token": token, "line_index": line_index, "line_text": line_text},
    }


def validate_pedagogical_frame(frame: Mapping[str, Any], *, source_code: str = "") -> None:
    """Validate completeness and, when source exists, C-line consistency."""
    required = {"schema_version", "concept", "phase", "condition", "variables", "call_stack", "loop", "pointers", "invariant", "narration", "source"}
    missing = sorted(required.difference(frame))
    if missing:
        raise PedagogicalFrameValidationError(f"Frame pedagógico incompleto: {', '.join(missing)}.")
    if frame["schema_version"] != PEDAGOGICAL_FRAME_SCHEMA_VERSION:
        raise PedagogicalFrameValidationError("Versión de frame pedagógico no soportada.")
    narration = frame["narration"]
    if not isinstance(narration, Mapping) or any(not str(narration.get(level, "")).strip() for level in PEDAGOGICAL_LEVELS):
        raise PedagogicalFrameValidationError("La narración debe existir en los tres niveles pedagógicos.")
    for key in ("phase", "invariant", "source"):
        if not isinstance(frame[key], Mapping):
            raise PedagogicalFrameValidationError(f"El campo {key} debe ser un objeto.")
    source = frame["source"]
    if source_code:
        rows = source_code.replace("\r\n", "\n").split("\n")
        index = source.get("line_index")
        text = str(source.get("line_text") or "")
        unresolved = index is None and not text
        inconsistent = not isinstance(index, int) or not 0 <= index < len(rows) or rows[index] != text
        if not unresolved and inconsistent:
            raise PedagogicalFrameValidationError("La línea C del frame no coincide con el código fuente.")


def pedagogical_frame_schema() -> dict[str, Any]:
    """Publish the lightweight JSON-compatible schema used by clients."""
    return {
        "$id": "visualestruct://sorting/pedagogical-frame/v1",
        "version": PEDAGOGICAL_FRAME_SCHEMA_VERSION,
        "required": ["schema_version", "concept", "phase", "condition", "variables", "call_stack", "loop", "pointers", "invariant", "narration", "source"],
        "levels": list(PEDAGOGICAL_LEVELS),
    }
