"""Readonly statement boundaries of int pila_cima(ptrPila p)."""
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


def build_stack_top_rejection_trace(*, payload: dict[str, Any], source_code: str,
        code_title: str, before_state: dict[str, Any], message: str) -> dict[str, Any]:
    """Report unregistered-operation validation without claiming a C call."""
    return {
        "structure_id": "stack", "operation_name": "cima", "payload": deepcopy(payload),
        "success": False, "message": message, "mutates": False,
        "source_code": source_code, "code_title": code_title, "steps": [],
        "final_state": deepcopy(before_state), "execution_started": False,
        "validation": {"stage": "supported_operations", "accepted": False, "message": message},
        "pedagogy_schema_version": SEQUENTIAL_FRAME_SCHEMA_VERSION,
        "pedagogy_schema": sequential_frame_schema(),
        "learning_profile": deepcopy(SEQUENTIAL_LEARNING_CATALOG["stack"]),
    }


def build_stack_top_trace(*, payload: dict[str, Any], source_code: str, code_title: str,
        before_state: dict[str, Any], after_state: dict[str, Any], success: bool,
        message: str) -> dict[str, Any]:
    """Observe initialized borrowed nodes; the ternary reads nro only if p is non-NULL.

    The int return value is separate from caller storage. Caller assignment has
    no source statement in this function and is therefore left pending here.
    Wrapper success/error metadata does not change the C NULL return of -1.
    """
    lines = source_code.replace("\r\n", "\n").split("\n")
    entry_index = next(i for i, line in enumerate(lines) if "int pila_cima(ptrPila p)" in line)
    return_index = next(i for i, line in enumerate(lines) if "return p == NULL ? -1 : p->nro;" in line)
    items = before_state.get("items") or []
    heap = [{
        "id": f"N{i+1}", "address": f"N{i+1}", "type": "struct NodoPila",
        "alive": True, "allocated": True, "freed": False, "status": "linked",
        "initialized_mask": 3, "fields_valid": True,
        "field_validity": {"nro": True, "sgte": True},
        "fields": {"nro": item["value"], "sgte": f"N{i+2}" if i+1 < len(items) else None},
    } for i, item in enumerate(items)]
    head = heap[0]["id"] if heap else None
    null = head is None
    value = -1 if null else heap[0]["fields"]["nro"]
    steps: list[dict[str, Any]] = []

    for event, index, active, condition in [
        ("entry", entry_index, True, None),
        ("conditional", return_index, True, null),
        ("return", return_index, False, None),
    ]:
        scope = "active" if active else "ended"
        root = {"identity": "&caller_pila", "type": "ptrPila", "value": head,
            "initialized": True, "valid": True, "alive": True, "scope": "caller"}
        caller_pointer = {"name": "pila", "type": "ptrPila", "target": head,
            "initialized": True, "valid": True, "scope": "caller", "scope_state": "active"}
        parameter = {"name": "p", "type": "ptrPila", "value": head,
            "initialized": True, "valid": active, "scope": "pila_cima", "scope_state": scope}
        pointers = [caller_pointer]
        local = [parameter] if active else []
        if active:
            pointers.append({"name": "p", "type": "ptrPila", "target": head,
                "initialized": True, "valid": True, "scope": "pila_cima", "scope_state": scope,
                "alias": "pila; misma identidad de nodo vivo y copia independiente del puntero"})
        variables = [{"name": "pila", "type": "ptrPila", "value": head,
            "initialized": True, "valid": True, "scope": "caller", "scope_state": "active"},
            {"name": "caller_result", "type": "int", "address": "&caller_result",
                "value": None, "initialized": False, "written": False, "valid": False,
                "scope": "caller", "scope_state": "active",
                "meaning": "El almacenamiento del caller espera su propia asignación; no es un parámetro de salida C."},
            *deepcopy(local)]
        if not active:
            variables.append({"name": "return", "type": "int", "value": value,
                "initialized": True, "valid": True, "scope": "return_value", "scope_state": "active",
                "meaning": "Valor de la expresión C retornada; no escribe nodos ni parámetros de salida."})
        calls = [{"function": "pila_cima", "parameters": {"p": head},
            "return_type": "int", "return": None,
            "continuation": "El caller recibe el int; su posterior asignación queda fuera de esta función."}] if active else []
        scopes = [{"id": "pila_cima", "kind": "function", "state": scope,
            "scope_state": scope, "variables": deepcopy(local)}]
        step = {"step_index": len(steps), "line_index": index, "line_text": lines[index],
            "event_type": event, "phase": "start" if event == "entry" else "end" if event == "return" else "progress",
            "delay_ms": 100, "function_name": "pila_cima", "condition_result": condition,
            "state_snapshot": deepcopy(before_state), "state_after": deepcopy(before_state), "console": []}
        frame = build_sequential_frame(structure_id="stack", operation_name="cima",
            payload=payload, step=step, success=success)
        frame.update(
            concept="call" if active and event == "entry" else "condition" if condition is not None else "return",
            variables=variables, pointers=pointers, heap_objects=deepcopy(heap),
            heap_transition={"kind": "stable", "before": deepcopy(heap), "after": deepcopy(heap),
                "freed": [], "dangling_references": []},
            call_stack=calls, scopes=scopes, memory_state=None,
            condition=None if condition is None else {"source": "p == NULL",
                "substituted": f"{head or 'NULL'} == NULL", "result": condition,
                "consequence": "Selecciona -1 sin desreferenciar" if null else "Lee el campo inicializado p->nro"},
            top_memory={"root": root, "heap": deepcopy(heap), "parameter": deepcopy(parameter) if active else None,
                "return_value": value if not active else None, "return_written": not active,
                "caller_storage": deepcopy(variables[1]), "call_stack": deepcopy(calls), "scopes": deepcopy(scopes),
                "allocations": 0, "frees": 0},
        )
        frame["source"]["function"] = "pila_cima"
        frame["phase"] = {"id": "cima-" + event, "label": event,
            "goal": "Observa la cima prestada sin modificar raíz, enlaces, campos ni almacenamiento del caller."}
        frame["invariant"] = {"text": "La raíz del caller y todos los nodos inicializados permanecen idénticos.",
            "holds": True, "symbol": "✓", "evidence": "Sin reserva, escritura en nodos, liberación ni printf."}
        narration = ("Entra en pila_cima con un ptrPila inicializado prestado por valor." if event == "entry" else
            "Evalúa p == NULL; no lee la rama no seleccionada de la expresión condicional." if condition is not None else
            "Retorna la expresión int y termina el ámbito de la función; raíz y nodos del caller siguen vivos.")
        for level in frame["narration"]:
            frame["narration"][level] = narration
        validate_sequential_frame(frame, source_code=source_code)
        step["pedagogy"] = frame
        step["debug"] = {"token": event, "function": "pila_cima", "root": deepcopy(root),
            "heap": deepcopy(heap), "pointers": deepcopy(pointers), "variables": deepcopy(variables),
            "call_stack": deepcopy(calls), "scopes": deepcopy(scopes), "condition_result": condition,
            "result": value if not active else None}
        steps.append(step)
    return {"structure_id": "stack", "operation_name": "cima", "payload": deepcopy(payload),
        "success": success, "message": message, "mutates": False, "code_title": code_title,
        "source_code": source_code, "steps": steps, "final_state": deepcopy(before_state),
        "pedagogy_schema_version": SEQUENTIAL_FRAME_SCHEMA_VERSION, "pedagogy_schema": sequential_frame_schema(),
        "learning_profile": deepcopy(SEQUENTIAL_LEARNING_CATALOG["stack"]),
        "instruction_scope": "Private Cima C query; caller assignment and public API/UI are outside this trace."}
