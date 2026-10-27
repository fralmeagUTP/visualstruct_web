"""Readonly scalar queries of a borrowed struct Cola copied by value."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from .pedagogy import (
    SEQUENTIAL_FRAME_SCHEMA_VERSION,
    SEQUENTIAL_LEARNING_CATALOG,
    build_sequential_frame,
    sequential_frame_schema,
    validate_sequential_frame,
)


def build_queue_query_rejection_trace(*, operation_name: str, payload: dict[str, Any],
        source_code: str, code_title: str, before_state: dict[str, Any], message: str) -> dict[str, Any]:
    """Describe unsupported-query validation without invoking or tracing C."""
    if operation_name not in {"frente", "final"}:
        raise ValueError("Consulta de cola no reconocida.")
    return {"structure_id": "queue", "operation_name": operation_name, "payload": deepcopy(payload),
        "success": False, "message": message, "mutates": False, "source_code": source_code,
        "code_title": code_title, "steps": [], "final_state": deepcopy(before_state),
        "execution_started": False,
        "validation": {"stage": "supported_operations", "accepted": False, "message": message},
        "pedagogy_schema_version": SEQUENTIAL_FRAME_SCHEMA_VERSION,
        "pedagogy_schema": sequential_frame_schema(),
        "learning_profile": deepcopy(SEQUENTIAL_LEARNING_CATALOG["queue"])}


def build_queue_query_trace(*, operation_name: str, payload: dict[str, Any], source_code: str,
        code_title: str, before_state: dict[str, Any], after_state: dict[str, Any],
        success: bool, message: str, borrowed_memory: dict[str, Any] | None = None) -> dict[str, Any]:
    """Copy initialized struct fields; observe their live borrowed nodes without stores.

    borrowed_memory is a private fixture input for defined but inconsistent root
    pairs. It never accepts a NULL struct argument. Caller assignment is outside
    this function's source and remains pending independently of the int return.
    """
    if operation_name not in {"frente", "final"}:
        raise ValueError("Consulta de cola no reconocida.")
    function = "cola_" + operation_name
    lines = source_code.replace("\r\n", "\n").split("\n")
    entry = next(i for i, line in enumerate(lines) if f"int {function}(struct Cola q)" in line)
    items = before_state.get("items") or []
    if borrowed_memory is None:
        heap = [{"id": f"N{i+1}", "address": f"N{i+1}", "type": "struct NodoCola",
            "alive": True, "allocated": True, "freed": False, "status": "borrowed",
            "initialized_mask": 3, "fields_valid": True, "field_validity": {"nro": True, "sgte": True},
            "fields": {"nro": x["value"], "sgte": f"N{i+2}" if i+1 < len(items) else None}}
            for i, x in enumerate(items)]
        fields = {"delante": heap[0]["id"] if heap else None, "atras": heap[-1]["id"] if heap else None}
    else:
        heap = deepcopy(borrowed_memory["nodes"])
        fields = deepcopy(borrowed_memory["fields"])
        if set(fields) != {"delante", "atras"}:
            raise ValueError("La copia struct Cola requiere sus dos campos inicializados.")
        for node in heap:
            if (not node.get("alive") or node.get("initialized_mask") != 3
                    or set(node.get("fields", {})) != {"nro", "sgte"}):
                raise ValueError("La consulta requiere nodos prestados vivos e inicializados.")
    nodes = {node["id"]: node for node in heap}
    if len(nodes) != len(heap) or any(value is not None and value not in nodes for value in fields.values()):
        raise ValueError("Las raíces deben ser NULL o identidades de nodos vivos.")
    if any(n["fields"]["sgte"] is not None and n["fields"]["sgte"] not in nodes for n in heap):
        raise ValueError("Los enlaces deben referir sólo memoria prestada viva.")
    selected = fields["delante" if operation_name == "frente" else "atras"]
    value = -1 if selected is None else nodes[selected]["fields"]["nro"]
    condition = selected is not None if operation_name == "frente" else selected is None
    if operation_name == "frente":
        guard_index = next(i for i, line in enumerate(lines) if "if (q.delante != NULL)" in line)
        return_token = "return q.delante->nro;" if selected is not None else "return -1;"
        return_index = next(i for i, line in enumerate(lines) if return_token in line)
        expression = "q.delante != NULL"
        substituted = f"{selected or 'NULL'} != NULL"
    else:
        return_index = next(i for i, line in enumerate(lines) if "return q.atras == NULL ? -1 : q.atras->nro;" in line)
        guard_index = return_index
        expression = "q.atras == NULL"
        substituted = f"{selected or 'NULL'} == NULL"
    steps: list[dict[str, Any]] = []
    for event, index in [("entry", entry), ("condition", guard_index), ("return", return_index)]:
        active = event != "return"
        scope_state = "active" if active else "ended"
        caller = {"name": "cola", "type": "struct Cola", "value": deepcopy(fields), "address": "&cola",
            "initialized": True, "valid": True, "scope": "caller", "scope_state": "active"}
        parameter = {"name": "q", "type": "struct Cola", "value": deepcopy(fields), "address": "&q",
            "initialized": True, "valid": True, "scope": function, "scope_state": "active"}
        local = [parameter] if active else []
        storage = {"name": "caller_result", "type": "int", "address": "&caller_result", "value": None,
            "initialized": False, "written": False, "valid": False, "scope": "caller", "scope_state": "active",
            "meaning": "Almacenamiento independiente pendiente de una asignación fuera de esta función C."}
        variables = [caller, storage, *deepcopy(local)]
        if not active:
            variables.append({"name": "return", "type": "int", "value": value, "initialized": True,
                "valid": True, "scope": "return_value", "scope_state": "active",
                "meaning": "Expresión int retornada; no escribe nodos ni parámetros de salida."})
        pointers = [{"name": "cola." + name, "type": "struct NodoCola *", "target": target,
            "initialized": True, "valid": True, "scope": "caller", "scope_state": "active"}
            for name, target in fields.items()]
        if active:
            pointers.extend({"name": "q." + name, "type": "struct NodoCola *", "target": target,
                "initialized": True, "valid": True, "scope": function, "scope_state": "active",
                "alias": "cola." + name + "; copia de campo que apunta al mismo nodo prestado"}
                for name, target in fields.items())
        calls = [{"function": function, "parameters": {"q": deepcopy(fields)}, "return_type": "int",
            "return": None, "continuation": "El caller recibe el int; su asignación posterior no pertenece a esta fuente."}] if active else []
        scopes = [{"id": function, "kind": "function", "state": scope_state,
            "scope_state": scope_state, "variables": deepcopy(local)}]
        step = {"step_index": len(steps), "line_index": index, "line_text": lines[index],
            "event_type": event, "phase": "start" if event == "entry" else "end" if event == "return" else "progress",
            "delay_ms": 100, "condition_result": condition if event == "condition" else None,
            "function_name": function, "state_snapshot": deepcopy(before_state),
            "state_after": deepcopy(before_state), "console": []}
        frame = build_sequential_frame(structure_id="queue", operation_name=operation_name,
            payload=payload, step=step, success=success)
        frame.update(concept="call" if event == "entry" else event,
            variables=variables, pointers=pointers, heap_objects=deepcopy(heap),
            heap_transition={"kind": "stable", "before": deepcopy(heap), "after": deepcopy(heap),
                "freed": [], "dangling_references": []}, call_stack=calls, scopes=scopes, memory_state=None,
            condition={"source": expression, "substituted": substituted, "result": condition,
                "consequence": "Lee únicamente el campo nro del extremo elegido." if selected is not None else "Retorna -1 sin desreferenciar NULL."}
                if event == "condition" else None,
            query_memory={"caller_struct": deepcopy(caller), "parameter_struct": deepcopy(parameter) if active else None,
                "heap": deepcopy(heap), "fields": deepcopy(fields), "return_value": value if not active else None,
                "return_written": not active, "caller_storage": deepcopy(storage),
                "allocations": 0, "frees": 0, "function_scope": scope_state},
        )
        frame["source"]["function"] = function
        frame["phase"] = {"id": operation_name + "-" + event, "label": event,
            "goal": "Consulta readonly con copia struct por valor y enlaces prestados a memoria viva."}
        frame["invariant"] = {"text": "La copia de q observa sin modificar el struct del caller ni sus nodos.",
            "holds": True, "symbol": "✓", "evidence": "Campos inicializados; no malloc, free, escrituras a nodos ni printf."}
        narration = ("Copia struct Cola por valor: q y cola tienen identidades distintas y comparten nodos prestados." if event == "entry" else
            "Evalúa el valor del enlace, no la dirección de su celda; sólo lee la rama C seleccionada." if event == "condition" else
            "Retorna el int y termina el ámbito de q; raíces y nodos del caller continúan vivos.")
        for level in frame["narration"]:
            frame["narration"][level] = narration
        validate_sequential_frame(frame, source_code=source_code)
        step["pedagogy"] = frame
        step["debug"] = {"token": event, "function": function, "fields": deepcopy(fields), "heap": deepcopy(heap),
            "variables": deepcopy(variables), "pointers": deepcopy(pointers), "scopes": deepcopy(scopes),
            "call_stack": deepcopy(calls), "condition_result": condition if event == "condition" else None,
            "result": value if not active else None}
        steps.append(step)
    return {"structure_id": "queue", "operation_name": operation_name, "payload": deepcopy(payload),
        "success": success, "message": message, "mutates": False, "code_title": code_title, "source_code": source_code,
        "steps": steps, "final_state": deepcopy(before_state), "pedagogy_schema_version": SEQUENTIAL_FRAME_SCHEMA_VERSION,
        "pedagogy_schema": sequential_frame_schema(), "learning_profile": deepcopy(SEQUENTIAL_LEARNING_CATALOG["queue"]),
        "instruction_scope": "Consulta C privada por valor; asignación del caller y API/UI pública quedan excluidas."}
