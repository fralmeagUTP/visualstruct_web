"""Canonical pedagogical contract for the fixed-capacity C hash table."""
from __future__ import annotations

from typing import Any, Mapping
import re

HASH_FRAME_SCHEMA_VERSION = 1
HASH_LEARNING_CATALOG = {
    "objective": "Explicar cómo índice, cadena, punteros y memoria producen cada estado de la tabla hash.",
    "prior": ["módulo entero", "arreglos", "punteros", "listas enlazadas", "malloc/free"],
    "mastery": ["predice el bucket", "explica colisiones", "traza búsqueda/eliminación", "verifica invariantes"],
    "capacity_policy": "fixed",
    "key_type": "int",
    "value_type": "int",
}
HASH_GUIDED_EXAMPLES = [
    {"id": "empty", "label": "Tabla vacía", "capacity": 5, "entries": [], "operation": "get", "payload": {"key": 1}, "lesson": "Una búsqueda vacía termina sin comparar nodos."},
    {"id": "capacity-one", "label": "Capacidad 1", "capacity": 1, "entries": [[2, 20], [5, 50]], "operation": "get", "payload": {"key": 5}, "lesson": "Con capacidad 1, toda clave comparte el bucket 0."},
    {"id": "no-collision", "label": "Sin colisión", "capacity": 7, "entries": [[1, 10], [2, 20]], "operation": "insert", "payload": {"key": 3, "value": 30}, "lesson": "Una buena distribución mantiene cadenas cortas."},
    {"id": "collision", "label": "Colisión múltiple", "capacity": 3, "entries": [[1, 10], [4, 40]], "operation": "insert", "payload": {"key": 7, "value": 70}, "lesson": "1, 4 y 7 comparten bucket porque son congruentes módulo 3."},
    {"id": "update", "label": "Actualizar sin reservar", "capacity": 3, "entries": [[1, 10], [4, 40]], "operation": "insert", "payload": {"key": 4, "value": 99}, "lesson": "Actualizar conserva cantidad, dirección y colisiones."},
    {"id": "search-head", "label": "Buscar en cabecera", "capacity": 3, "entries": [[1, 10], [4, 40], [7, 70]], "operation": "get", "payload": {"key": 7}, "lesson": "La clave más reciente queda en la cabecera de la cadena."},
    {"id": "search-middle", "label": "Buscar en medio", "capacity": 3, "entries": [[1, 10], [4, 40], [7, 70]], "operation": "get", "payload": {"key": 4}, "lesson": "La búsqueda avanza por siguiente hasta encontrar la clave."},
    {"id": "search-tail", "label": "Buscar al final", "capacity": 3, "entries": [[1, 10], [4, 40], [7, 70]], "operation": "get", "payload": {"key": 1}, "lesson": "La cola de la cadena exige visitar todos los nodos anteriores."},
    {"id": "search-absent", "label": "Buscar ausente", "capacity": 3, "entries": [[1, 10], [4, 40], [7, 70]], "operation": "get", "payload": {"key": 10}, "lesson": "Una clave ausente recorre toda su cadena y retorna false."},
    {"id": "remove-head", "label": "Eliminar cabecera", "capacity": 3, "entries": [[1, 10], [4, 40], [7, 70]], "operation": "remove", "payload": {"key": 7}, "lesson": "La cabecera se sustituye por actual->siguiente."},
    {"id": "remove-middle", "label": "Eliminar intermedio", "capacity": 3, "entries": [[1, 10], [4, 40], [7, 70]], "operation": "remove", "payload": {"key": 4}, "lesson": "anterior->siguiente evita perder el resto de la cadena."},
    {"id": "remove-absent", "label": "Eliminar ausente", "capacity": 3, "entries": [[1, 10], [4, 40]], "operation": "remove", "payload": {"key": 10}, "lesson": "Sin coincidencia no hay unlink, free ni cambio de cantidad."},
    {"id": "zero", "label": "Clave cero", "capacity": 5, "entries": [], "operation": "insert", "payload": {"key": 0, "value": 0}, "lesson": "0 % capacidad siempre selecciona el bucket 0."},
    {"id": "negative", "label": "Clave negativa", "capacity": 3, "entries": [[1, 10]], "operation": "insert", "payload": {"key": -2, "value": 20}, "lesson": "El residuo negativo de C se normaliza a un índice válido."},
    {"id": "int-max", "label": "Límite INT_MAX", "capacity": 7, "entries": [], "operation": "insert", "payload": {"key": 2147483647, "value": 1}, "lesson": "Las claves de int C se mantienen exactas en la visualización."},
    {"id": "low-load", "label": "Factor de carga bajo", "capacity": 17, "entries": [[1, 10]], "operation": "get", "payload": {"key": 1}, "lesson": "Un α bajo suele reducir las comparaciones observadas."},
    {"id": "high-load", "label": "Factor de carga alto", "capacity": 3, "entries": [[1, 10], [4, 40], [7, 70]], "operation": "get", "payload": {"key": 1}, "lesson": "Un α alto no garantiza, pero puede aumentar cadenas y costo."},
    {"id": "malloc-failure", "label": "Fallo de memoria", "capacity": 3, "entries": [[1, 10]], "operation": "insert", "payload": {"key": 4, "value": 40, "simulate_allocation_failure": True}, "lesson": "Si malloc devuelve NULL, se retorna false sin modificar la tabla."},
]
INT_MIN = -(2**31)
INT_MAX = 2**31 - 1


def c_remainder(dividend: int, divisor: int) -> int:
    """Return C17 integer remainder without overflowing on INT_MIN."""
    if divisor <= 0:
        raise ValueError("La capacidad debe ser positiva.")
    quotient = abs(dividend) // divisor
    if dividend < 0:
        quotient = -quotient
    return dividend - quotient * divisor


class HashFrameValidationError(ValueError):
    pass


def _function_at(lines: list[str], index: int, default: str) -> str:
    for row in reversed(lines[: index + 1]):
        match = re.search(r"\b([A-Za-z_]\w*)\s*\([^;]*\)\s*\{\s*$", row)
        if match and match.group(1) not in {"if", "while", "for", "switch"}:
            return match.group(1)
    return default


def _concept(line: str) -> str:
    text = line.strip().lower()
    if "th_indice" in text or "indice =" in text:
        return "hash"
    if "malloc" in text:
        return "allocate"
    if "free(" in text:
        return "free"
    if "actual->clave" in text:
        return "compare"
    if "actual = actual->siguiente" in text:
        return "advance"
    if "anterior->siguiente" in text or "buckets[indice]" in text or "nuevo->siguiente" in text:
        return "link"
    if "actual->valor" in text:
        return "update"
    if text.startswith("return"):
        return "return"
    if text.startswith(("if ", "if(", "while ", "while(", "for ", "for(")):
        return "condition"
    return "assignment"


def _entries(state: Mapping[str, Any]) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    for bucket in state.get("buckets") or []:
        if not isinstance(bucket, Mapping):
            continue
        for position, entry in enumerate(bucket.get("entries") or []):
            if isinstance(entry, Mapping):
                key = int(entry.get("key"))
                result[key] = {"key": key, "value": entry.get("value"), "bucket": int(bucket.get("index", 0)), "position": position, "address": f"0xHASH-{key}"}
    return result


def _chain(state: Mapping[str, Any], bucket_index: int | None) -> list[dict[str, Any]]:
    if bucket_index is None:
        return []
    for bucket in state.get("buckets") or []:
        if isinstance(bucket, Mapping) and int(bucket.get("index", -1)) == bucket_index:
            return [dict(item) for item in bucket.get("entries") or [] if isinstance(item, Mapping)]
    return []


def build_hash_frame(*, operation_name: str, payload: Mapping[str, Any], step: Mapping[str, Any], source_lines: list[str], success: bool) -> dict[str, Any]:
    before = step.get("state_snapshot") if isinstance(step.get("state_snapshot"), Mapping) else {}
    after = step.get("state_after") if isinstance(step.get("state_after"), Mapping) else {}
    initial = step.get("hash_initial_state") if isinstance(step.get("hash_initial_state"), Mapping) else before
    line = str(step.get("line_text") or "")
    line_index = int(step.get("line_index") or 0)
    concept = _concept(line)
    capacity = int((initial.get("metadata") or after.get("metadata") or before.get("metadata") or {}).get("capacity", 0))
    key_value = payload.get("key", step.get("hash_lifecycle_free_key"))
    try:
        key = int(key_value) if key_value not in (None, "") else None
    except (TypeError, ValueError):
        key = None
    raw = None if key is None or capacity <= 0 else c_remainder(key, capacity)
    index = None if raw is None else (raw + capacity if raw < 0 else raw)
    before_chain, after_chain = _chain(initial, index), _chain(after, index)
    before_entries, after_entries = _entries(before), _entries(after)
    allocated = [after_entries[item] for item in after_entries.keys() - before_entries.keys()]
    freed = [before_entries[item] for item in before_entries.keys() - after_entries.keys()]
    match_position = next((position for position, item in enumerate(before_chain) if item.get("key") == key), None)
    visit_index = step.get("hash_visit_index")
    natural_limit = len(before_chain) if match_position is None else match_position + 1
    visit_limit = min(natural_limit, int(visit_index) + 1) if isinstance(visit_index, int) else natural_limit
    examined = [item.get("key") for item in before_chain[:visit_limit]]
    active_index = min(int(visit_index), len(before_chain) - 1) if isinstance(visit_index, int) and before_chain else match_position
    active = before_chain[active_index] if active_index is not None and before_chain else (before_chain[-1] if before_chain else None)
    if concept == "free" and active is not None:
        freed = [{"key": int(active.get("key")), "value": active.get("value"), "bucket": index, "address": f"0xHASH-{active.get('key')}"}]
    actual_address = active and f"0xHASH-{active.get('key')}"
    previous_address = None
    if active and before_chain.index(active) > 0:
        previous_address = f"0xHASH-{before_chain[before_chain.index(active)-1].get('key')}"
    condition = None
    if concept in {"condition", "compare"}:
        result = bool(active and active.get("key") == key) if "clave" in line else step.get("condition_result")
        condition = {"source": line.strip(), "substituted": line.strip().replace("clave", str(key)), "result": result, "consequence": "Solo se representa la rama ejecutada."}
    metadata = after.get("metadata") if isinstance(after.get("metadata"), Mapping) else {}
    all_entries = list(after_entries.values())
    keys = [item["key"] for item in all_entries]
    located = all(item["bucket"] == (c_remainder(item["key"], capacity) + capacity) % capacity for item in all_entries) if capacity else not all_entries
    invariant_holds = len(keys) == len(set(keys)) and int(metadata.get("size", len(keys))) == len(keys) and located
    chain_lengths = [len(bucket.get("entries") or []) for bucket in after.get("buckets") or [] if isinstance(bucket, Mapping)]
    occupied = sum(length > 0 for length in chain_lengths)
    allocation_failed = payload.get("simulate_allocation_failure") in (True, "true", "1", 1) and key not in before_entries
    found = match_position is not None
    position = "absent"
    if found:
        position = "head" if match_position == 0 else "tail" if match_position == len(before_chain) - 1 else "middle"
    return {
        "schema_version": HASH_FRAME_SCHEMA_VERSION,
        "operation": operation_name,
        "concept": concept,
        "phase": {"id": f"{operation_name}-{concept}", "label": concept.replace("_", " ").title()},
        "source": {"line_index": line_index, "line_text": line, "function": _function_at(source_lines, line_index, operation_name)},
        "hash": {"key": key, "capacity": capacity, "raw_remainder": raw, "normalization_applied": bool(raw is not None and raw < 0), "normalization_expression": None if raw is None else (f"{raw} + {capacity} = {index}" if raw < 0 else f"{raw} ya es no negativo"), "normalized_index": index, "expression": None if key is None else f"{key} % {capacity} = {raw}"},
        "condition": condition,
        "variables": {"indice": index, "cantidad": metadata.get("size", 0), "capacidad": capacity, "clave": key, "valor": payload.get("value"), "valor_salida": active.get("value") if found and active else None, "retorno": found if operation_name in {"get", "contains"} else success},
        "pointers": {"actual": actual_address or "NULL", "anterior": previous_address or "NULL", "nuevo": allocated[0]["address"] if allocated else "NULL", "bucket_head": f"bucket[{index}]" if index is not None else "NULL"},
        "chain": {"bucket": index, "before": before_chain, "after": after_chain, "examined": examined, "current_index": active_index, "found": found, "match_position": match_position, "position_kind": position, "contains_equivalence": "th_contiene llama th_buscar con &dummy_valor" if operation_name == "contains" else None},
        "distribution": {"occupied_buckets": occupied, "empty_buckets": max(0, capacity - occupied), "chain_lengths": chain_lengths, "max_chain_length": max(chain_lengths, default=0), "load_factor": (len(all_entries) / capacity) if capacity else 0.0, "collisions": sum(max(0, length - 1) for length in chain_lengths)},
        "cost": {"hash_evaluations": 1 if key is not None else 0, "comparisons": len(examined), "nodes_visited": len(examined), "unit": "evaluaciones discretas, no tiempo real", "best_case": "Θ(1): bucket vacío o coincidencia en cabecera", "average_case": "Θ(1 + α) bajo distribución aproximadamente uniforme", "worst_case": "Θ(n): todas las claves en una cadena", "depends_on": "distribución de claves y factor de carga α = cantidad/capacidad"},
        "memory": {"objects_before": list(before_entries.values()), "objects_after": list(after_entries.values()), "allocated": allocated, "freed": freed, "bucket_array_freed": "free(tabla->buckets)" in line, "bucket_array_is_null": "tabla->buckets = NULL" in line or capacity == 0, "allocation_attempted": operation_name == "insert" and not found, "allocation_failed": allocation_failed, "null_checked": operation_name == "insert" and not found, "state_unchanged_on_failure": allocation_failed and before == after, "initialized_fields": ["clave", "valor", "siguiente"] if allocated else [], "transition": "free_bucket_array" if "free(tabla->buckets)" in line else "free" if concept == "free" else "unlink" if concept == "link" and operation_name == "remove" else "decrement" if "cantidad--" in line else "stable", "links_changed": before_chain != after_chain or (operation_name == "remove" and concept == "link"), "dangling_references": []},
        "state_before": before,
        "state_after": after,
        "invariant": {"name": "ubicación, unicidad, cantidad, aciclicidad y memoria segura", "holds": invariant_holds, "symbol": "✓" if invariant_holds else "✗", "evidence": f"nodos={len(keys)}, cantidad={metadata.get('size', 0)}, bucket={index}"},
        "narration": {"basic": f"Observa el concepto {concept} en el bucket {index}.", "intermediate": f"La operación {operation_name} usa encadenamiento separado y capacidad fija.", "advanced": f"La función {_function_at(source_lines, line_index, operation_name)} ejecuta «{line.strip()}» con punteros y memoria explícitos."},
        "success": bool(success),
    }


def validate_hash_frame(frame: Mapping[str, Any], *, source_code: str = "") -> None:
    required = {"schema_version", "operation", "concept", "source", "hash", "condition", "variables", "pointers", "chain", "distribution", "cost", "memory", "state_before", "state_after", "invariant", "narration"}
    missing = required.difference(frame)
    if missing:
        raise HashFrameValidationError(f"Campos faltantes: {sorted(missing)}")
    if frame["schema_version"] != HASH_FRAME_SCHEMA_VERSION:
        raise HashFrameValidationError("Versión hash no soportada")
    if frame["memory"].get("dangling_references"):
        raise HashFrameValidationError("Referencia colgante")
    key = frame["hash"].get("key")
    if key is not None and not INT_MIN <= int(key) <= INT_MAX:
        raise HashFrameValidationError("Clave fuera del rango int C")
    if source_code and frame["source"].get("line_text"):
        rows = source_code.replace("\r\n", "\n").split("\n")
        index = frame["source"].get("line_index")
        if not isinstance(index, int) or not 0 <= index < len(rows) or rows[index] != frame["source"]["line_text"]:
            raise HashFrameValidationError("Línea C inconsistente")


def hash_frame_schema() -> dict[str, Any]:
    return {"$id": "visualestruct://hash/pedagogical-frame/v1", "version": HASH_FRAME_SCHEMA_VERSION, "levels": ["basic", "intermediate", "advanced"], "capacity_policy": "fixed", "types": {"key": "int", "value": "int"}}
