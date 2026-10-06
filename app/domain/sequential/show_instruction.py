"""Private readonly void Mostrar traces following the actual C print traversal."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from .pedagogy import (SEQUENTIAL_FRAME_SCHEMA_VERSION, SEQUENTIAL_LEARNING_CATALOG,
    build_sequential_frame, sequential_frame_schema, validate_sequential_frame)


def build_show_rejection_trace(*, structure_id: str, payload: dict[str, Any],
        source_code: str, code_title: str, before_state: dict[str, Any], message: str) -> dict[str, Any]:
    """Unsupported validation has no C invocation or printf events."""
    return {"structure_id": structure_id, "operation_name": "mostrar", "payload": deepcopy(payload),
        "success": False, "message": message, "mutates": False, "source_code": source_code,
        "code_title": code_title, "steps": [], "final_state": deepcopy(before_state),
        "execution_started": False, "validation": {"stage": "supported_operations", "accepted": False, "message": message},
        "pedagogy_schema_version": SEQUENTIAL_FRAME_SCHEMA_VERSION, "pedagogy_schema": sequential_frame_schema(),
        "learning_profile": deepcopy(SEQUENTIAL_LEARNING_CATALOG[structure_id])}


def build_show_trace(*, structure_id: str, payload: dict[str, Any], source_code: str,
        code_title: str, before_state: dict[str, Any], after_state: dict[str, Any], success: bool,
        message: str, borrowed_memory: dict[str, Any] | None = None) -> dict[str, Any]:
    """Walk initialized borrowed nodes, observe each printf, and return void.

    Private queue fixtures may supply independently initialized roots. They do
    not register a method, accept a NULL struct argument, or persist a query.
    """
    if structure_id not in {"stack", "queue"}:
        raise ValueError("Mostrar requiere Pila o Cola.")
    stack = structure_id == "stack"
    function = "pila_mostrar" if stack else "cola_mostrar"
    node_type = "struct NodoPila" if stack else "struct NodoCola"
    parameter_name = "p" if stack else "q"
    caller_name = "pila" if stack else "cola"
    pointer_type = "ptrPila" if stack else "struct NodoCola *"
    lines = source_code.replace("\r\n", "\n").split("\n")
    def index(token: str) -> int:
        return next(i for i, line in enumerate(lines) if token in line)
    entry_index = index("void " + function + "(")
    declare_index = index("ptrPila aux = p;" if stack else "struct NodoCola *aux = q.delante;")
    while_index = index("while (aux != NULL)")
    value_index = next(i for i, line in enumerate(lines) if "printf(" in line and "aux->nro" in line)
    advance_index = index("aux = aux->sgte;")
    end_index = max(i for i, line in enumerate(lines) if line.strip() == "}")
    items = before_state.get("items") or []
    if borrowed_memory is None:
        heap = [{"id": f"N{i+1}", "address": f"N{i+1}", "type": node_type, "alive": True,
            "allocated": True, "freed": False, "status": "borrowed", "initialized_mask": 3,
            "fields_valid": True, "field_validity": {"nro": True, "sgte": True},
            "fields": {"nro": item["value"], "sgte": f"N{i+2}" if i+1 < len(items) else None}}
            for i, item in enumerate(items)]
        fields = {"delante": heap[0]["id"] if heap else None, "atras": heap[-1]["id"] if heap else None}
    else:
        if stack:
            raise ValueError("El override de raíces es privado de struct Cola.")
        heap, fields = deepcopy(borrowed_memory["nodes"]), deepcopy(borrowed_memory["fields"])
    nodes = {node["id"]: node for node in heap}
    if set(fields) != {"delante", "atras"} or len(nodes) != len(heap):
        raise ValueError("Se requieren identidades y ambos campos de struct Cola inicializados.")
    for node in heap:
        if (node["type"] != node_type or not node.get("alive") or node.get("initialized_mask") != 3
                or set(node.get("fields", {})) != {"nro", "sgte"}
                or (node["fields"]["sgte"] is not None and node["fields"]["sgte"] not in nodes)):
            raise ValueError("Mostrar requiere enlaces a nodos prestados vivos e inicializados.")
    if any(root is not None and root not in nodes for root in fields.values()):
        raise ValueError("Las raíces deben referir nodos vivos o NULL.")
    head = fields["delante"]
    parameter_value: Any = head if stack else deepcopy(fields)
    console: list[str] = []
    steps: list[dict[str, Any]] = []
    aux: str | None = None
    declared = False

    def emit(event: str, line_index: int, *, condition: bool | None = None, ended: bool = False) -> None:
        caller = {"name": caller_name, "type": "ptrPila" if stack else "struct Cola", "value": deepcopy(parameter_value),
            "address": "&" + caller_name, "initialized": True, "valid": True, "scope": "caller", "scope_state": "active"}
        parameter = {"name": parameter_name, "type": "ptrPila" if stack else "struct Cola", "value": deepcopy(parameter_value),
            "address": "&" + parameter_name, "initialized": True, "valid": True, "scope": function, "scope_state": "active"}
        local = [parameter] if not ended else []
        if declared and not ended:
            local.append({"name": "aux", "type": pointer_type, "value": aux, "address": "&aux",
                "initialized": True, "valid": True, "scope": function, "scope_state": "active"})
        pointers = [{"name": caller_name, "type": "ptrPila", "target": head,
            "initialized": True, "valid": True, "scope": "caller", "scope_state": "active"}] if stack else [
            {"name": "cola."+field, "type": pointer_type, "target": root, "initialized": True,
                "valid": True, "scope": "caller", "scope_state": "active"} for field, root in fields.items()]
        if not ended:
            if stack:
                pointers.append({"name": "p", "type": "ptrPila", "target": head, "alias": "pila",
                    "initialized": True, "valid": True, "scope": function, "scope_state": "active"})
            else:
                pointers.extend({"name": "q."+field, "type": pointer_type, "target": root, "alias": "cola."+field,
                    "initialized": True, "valid": True, "scope": function, "scope_state": "active"} for field, root in fields.items())
            if declared:
                pointers.append({"name": "aux", "type": pointer_type, "target": aux,
                    "initialized": True, "valid": True, "scope": function, "scope_state": "active"})
        expression = "aux == NULL" if event == "if" else "aux != NULL"
        condition_data = {"source": expression, "substituted": (aux or "NULL") + (" == NULL" if event == "if" else " != NULL"),
            "result": condition, "consequence": "Selecciona sólo la rama o iteración evaluada."} if condition is not None else None
        calls = [] if ended else [{"function": function, "parameters": {parameter_name: deepcopy(parameter_value)},
            "return_type": "void", "return": None, "continuation": "Regresa sin valor ni asignación escalar del caller."}]
        scope_state = "ended" if ended else "active"
        step = {"step_index": len(steps), "line_index": line_index, "line_text": lines[line_index],
            "event_type": event, "function_name": function, "phase": "start" if event == "entry" else "end" if ended else "progress",
            "delay_ms": 100, "condition_result": condition, "state_snapshot": deepcopy(before_state),
            "state_after": deepcopy(before_state), "console": list(console)}
        frame = build_sequential_frame(structure_id=structure_id, operation_name="mostrar", payload=payload, step=step, success=success)
        frame.update(concept="call" if event == "entry" else "return" if ended else "condition" if condition is not None else "console" if event == "printf" else "assignment",
            variables=[caller, *deepcopy(local)], pointers=pointers, heap_objects=deepcopy(heap),
            heap_transition={"kind": "stable", "before": deepcopy(heap), "after": deepcopy(heap), "freed": [], "dangling_references": []},
            call_stack=calls, scopes=[{"id": function, "kind": "function", "state": scope_state, "scope_state": scope_state, "variables": deepcopy(local)}],
            condition=condition_data, memory_state=None,
            show_memory={"caller": deepcopy(caller), "parameter": deepcopy(parameter) if not ended else None,
                "fields": deepcopy(fields) if not stack else None, "head": head, "heap": deepcopy(heap),
                "aux": aux if declared else None, "aux_initialized": declared, "return_type": "void",
                "scope": scope_state, "allocations": 0, "frees": 0, "console": list(console)})
        frame["source"]["function"] = function
        frame["phase"] = {"id": "mostrar-"+event, "label": event, "goal": "Recorrido readonly y salida printf causal del C real."}
        frame["invariant"] = {"text": "Raíces y nodos prestados permanecen intactos.", "holds": True, "symbol": "V",
            "evidence": "Sólo aux y la consola avanzan; no malloc, free ni escritura estructural."}
        narration = ("Copia el parámetro por valor y comparte nodos vivos con el caller." if event == "entry" else
            "Inicializa aux con el enlace recibido." if event == "declare" else
            "Evalúa la guarda con el valor actual de aux, antes de leer el nodo." if condition is not None else
            "printf añade únicamente la salida de esta instrucción." if event == "printf" else
            "aux recibe el enlace sgte ya inicializado; la estructura no cambia." if event == "advance" else
            "Termina el ámbito de los locales y regresa void; el caller conserva sus nodos.")
        for level in frame["narration"]:
            frame["narration"][level] = narration
        validate_sequential_frame(frame, source_code=source_code)
        step["pedagogy"] = frame
        step["debug"] = {"function": function, "token": event, "aux": aux if declared else None,
            "aux_initialized": declared, "condition_result": condition, "scope": scope_state, "return_type": "void"}
        steps.append(step)

    emit("entry", entry_index)
    aux, declared = head, True
    emit("declare", declare_index)
    if stack:
        emit("if", index("if (aux == NULL)"), condition=aux is None)
        if aux is None:
            console.append("Pila vacia.\n")
            emit("printf", index('printf("Pila vacia.'))
            emit("return", index("return;"), ended=True)
    else:
        console.append("Cola: ")
        emit("printf", index('printf("Cola: ");'))
    if not stack or aux is not None:
        visited: set[str] = set()
        while True:
            emit("while", while_index, condition=aux is not None)
            if aux is None:
                break
            if aux in visited:
                raise ValueError("La fixture privada de Mostrar debe ser acíclica.")
            visited.add(aux)
            console.append(("\t"+str(nodes[aux]["fields"]["nro"])+"\n") if stack else str(nodes[aux]["fields"]["nro"])+" ")
            emit("printf", value_index)
            aux = nodes[aux]["fields"]["sgte"]
            emit("advance", advance_index)
        if not stack:
            console.append("\n")
            emit("printf", index('printf("\\n");'))
        emit("end", end_index, ended=True)
    return {"structure_id": structure_id, "operation_name": "mostrar", "payload": deepcopy(payload),
        "success": success, "message": message, "mutates": False, "source_code": source_code, "code_title": code_title,
        "steps": steps, "final_state": deepcopy(before_state), "pedagogy_schema_version": SEQUENTIAL_FRAME_SCHEMA_VERSION,
        "pedagogy_schema": sequential_frame_schema(), "learning_profile": deepcopy(SEQUENTIAL_LEARNING_CATALOG[structure_id]),
        "instruction_scope": "Mostrar C void privado; API/UI aceptada y persistencia de queries excluidas."}
