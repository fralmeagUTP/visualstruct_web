"""Private C statement traces for five Priority helpers and bounded caller buffers."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from .pedagogy import (SEQUENTIAL_FRAME_SCHEMA_VERSION, SEQUENTIAL_LEARNING_CATALOG,
    build_sequential_frame, sequential_frame_schema, validate_sequential_frame)

HELPERS = {"inicializar": "cp_inicializar", "vacia": "cp_vacia", "contar": "cp_contar",
    "copiar_items": "cp_copiar_items", "formatear": "cp_formatear"}


def build_priority_helper_rejection_trace(*, operation_name: str, payload: dict[str, Any],
        source_code: str, code_title: str, before_state: dict[str, Any], message: str) -> dict[str, Any]:
    return {"structure_id": "priority_queue", "operation_name": operation_name, "payload": deepcopy(payload),
        "success": False, "message": message, "mutates": False, "source_code": source_code,
        "code_title": code_title, "steps": [], "final_state": deepcopy(before_state), "execution_started": False,
        "validation": {"stage": "supported_operations", "accepted": False, "message": message},
        "pedagogy_schema_version": SEQUENTIAL_FRAME_SCHEMA_VERSION, "pedagogy_schema": sequential_frame_schema(),
        "learning_profile": deepcopy(SEQUENTIAL_LEARNING_CATALOG["priority_queue"])}


def build_priority_helper_trace(*, operation_name: str, payload: dict[str, Any], source_code: str,
        code_title: str, before_state: dict[str, Any], after_state: dict[str, Any], success: bool,
        message: str, borrowed_memory: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute only initialized live fixtures; NULL pointers remain values, never NULL structs.

    Private payload flags model borrowed caller pointers and fresh struct fields.
    Helpers remain absent from the adapter/catalog. No printf output is invented.
    """
    operation = operation_name.removeprefix("cp_")
    function = HELPERS[operation]
    return_type = "bool" if operation == "vacia" else "int" if operation in {"contar", "copiar_items"} else "void"
    lines = source_code.replace("\r\n", "\n").split("\n")
    blocks: dict[str, tuple[int, int]] = {}
    for fn in [function, "cp_append_text"]:
        starts = [i for i, line in enumerate(lines) if fn + "(" in line and "{" in line]
        if not starts:
            continue
        start = starts[0]
        depth = 0
        for i in range(start, len(lines)):
            depth += lines[i].count("{") - lines[i].count("}")
            if depth == 0:
                blocks[fn] = (start, i)
                break
    if function not in blocks or (operation == "formatear" and "cp_append_text" not in blocks):
        raise ValueError("Se requiere el C exacto del target y su dependencia de formato.")
    items = before_state.get("items") or []
    if borrowed_memory is None:
        heap = [{"id": f"N{i+1}", "address": f"N{i+1}", "type": "CPNodo", "alive": True,
            "allocated": True, "freed": False, "status": "borrowed", "initialized_mask": 7,
            "fields_valid": True, "field_validity": {"valor": True, "prioridad": True, "sgte": True},
            "fields": {"valor": item["value"], "prioridad": item["priority"],
                "sgte": f"N{i+2}" if i+1 < len(items) else None}}
            for i, item in enumerate(items)]
        fields = {"delante": heap[0]["id"] if heap else None, "atras": heap[-1]["id"] if heap else None,
            "cantidad": payload.get("quantity", before_state.get("cantidad", before_state.get("size", len(items))))}
        mask = 0 if payload.get("fresh_struct") else 7
    else:
        heap, fields = deepcopy(borrowed_memory["nodes"]), deepcopy(borrowed_memory["fields"])
        mask = int(borrowed_memory.get("initialized_mask", 7))
    nodes = {node["id"]: node for node in heap}
    if len(nodes) != len(heap) or set(fields) != {"delante", "atras", "cantidad"}:
        raise ValueError("ColaPrioridad requiere tres campos e identidades únicas.")
    for node in heap:
        if (not node.get("alive") or node.get("initialized_mask") != 7 or node.get("type") != "CPNodo"
                or set(node.get("fields", {})) != {"valor", "prioridad", "sgte"}
                or (node["fields"]["sgte"] is not None and node["fields"]["sgte"] not in nodes)):
            raise ValueError("Se requieren nodos prestados vivos e inicializados.")
        if any(type(node["fields"][k]) is not int or not -2147483648 <= node["fields"][k] <= 2147483647 for k in ["valor", "prioridad"]):
            raise ValueError("Los datos y prioridades deben ser int C representables.")
    if any(fields[k] is not None and fields[k] not in nodes for k in ["delante", "atras"]):
        raise ValueError("Las raíces deben apuntar a nodos vivos o NULL.")
    visited: set[str] = set()
    node = fields["delante"] if mask & 1 else None
    while node is not None:
        if node in visited:
            raise ValueError("La fixture privada debe ser acíclica.")
        visited.add(node)
        node = nodes[node]["fields"]["sgte"]
    null_cola = bool(payload.get("null_cola"))
    if mask != 7 and operation != "inicializar" and not null_cola:
        raise ValueError("No se pueden leer campos indeterminados de ColaPrioridad.")
    capacity = payload.get("capacity", 128 if operation == "formatear" else 4)
    if type(capacity) is not int or (operation == "formatear" and capacity < 0):
        raise ValueError("La capacidad de formato es size_t; no admite un negativo int.")
    values = deepcopy(payload.get("caller_values", [123456] * max(6, capacity)))
    priorities = deepcopy(payload.get("caller_priorities", [654321] * max(6, capacity)))
    byte_buffer = list(payload.get("caller_bytes", [90] * max(130, capacity)))
    if capacity > len(values) and operation == "copiar_items" or capacity > len(priorities) and operation == "copiar_items" or capacity > len(byte_buffer) and operation == "formatear":
        raise ValueError("La capacidad no puede superar el almacenamiento prestado válido.")
    value_written = [False] * len(values)
    priority_written = [False] * len(priorities)
    bytes_written = [False] * len(byte_buffer)
    null_values = bool(payload.get("null_valores"))
    null_priorities = bool(payload.get("null_prioridades"))
    null_destino = bool(payload.get("null_destino"))
    locals_: dict[str, dict[str, Any]] = {}
    helper_locals: dict[str, dict[str, Any]] = {}
    helper_active = False
    active = True
    result: Any = None
    steps: list[dict[str, Any]] = []
    current_function = function
    queue_changed = False

    def var(name: str, typ: str, value: Any, initialized: bool = True, *, scope: str = function) -> dict[str, Any]:
        return {"name": name, "type": typ, "value": deepcopy(value), "initialized": initialized,
            "valid": initialized, "scope": scope, "scope_state": "active", "address": "&" + scope + "." + name}

    def declare(name: str, typ: str, value: Any = None, initialized: bool = False) -> None:
        locals_[name] = var(name, typ, value, initialized)

    def put(name: str, value: Any) -> None:
        locals_[name].update(value=deepcopy(value), initialized=True, valid=True)

    def memory() -> dict[str, Any]:
        root = {"address": "&cp", "type": "ColaPrioridad", "alive": True, "initialized_mask": mask,
            "fields": {k: deepcopy(v) if mask & bit else None for k, v, bit in [
                ("delante", fields["delante"], 1), ("atras", fields["atras"], 2), ("cantidad", fields["cantidad"], 4)]},
            "field_validity": {k: bool(mask & bit) for k, bit in [("delante", 1), ("atras", 2), ("cantidad", 4)]}}
        return {"root": root, "heap": deepcopy(heap), "locals": deepcopy(locals_) if active else {},
            "helper_locals": deepcopy(helper_locals) if helper_active else {},
            "scope": "active" if active else "ended", "helper_scope": "active" if helper_active else "ended",
            "result": deepcopy(result), "return_type": return_type, "allocations": 0, "frees": 0,
            "outputs": {"values": list(values), "priorities": list(priorities), "bytes": list(byte_buffer),
                "values_written": list(value_written), "priorities_written": list(priority_written),
                "bytes_written": list(bytes_written), "ownership": "borrowed caller storage",
                "array_initialized": True, "bytes_initialized": True}}

    def emit(event: str, token: str, condition: bool | None = None, operands: list[dict[str, Any]] | None = None,
            *, fn: str | None = None, closing: bool = False) -> None:
        fn = fn or current_function
        start, end = blocks[fn]
        index = end if closing else next(i for i in range(start, end + 1) if token in lines[i])
        mem = memory()
        params = [var("cola", "ColaPrioridad *" if operation == "inicializar" else "const ColaPrioridad *", None if null_cola else "&cp")]
        if operation == "copiar_items":
            params += [var("valores", "int *", None if null_values else "&caller_valores"),
                var("prioridades", "int *", None if null_priorities else "&caller_prioridades"), var("capacidad", "int", capacity)]
        elif operation == "formatear":
            params += [var("destino", "char *", None if null_destino else "&caller_destino"), var("capacidad", "size_t", capacity)]
        target_vars = params + list(deepcopy(locals_).values()) if active else []
        dependency_vars = list(deepcopy(helper_locals).values()) if helper_active else []
        variables = [var("cp", "ColaPrioridad", mem["root"]["fields"], mask == 7, scope="caller"), *target_vars, *dependency_vars]
        variables[0].update(initialized_mask=mask, field_validity=mem["root"]["field_validity"])
        calls = [{"function": function, "parameters": {v["name"]: v["value"] for v in params},
            "return_type": return_type, "return": None, "continuation": "Caller conserva la cola y sus buffers prestados."}] if active else []
        if helper_active:
            calls.append({"function": "cp_append_text", "parameters": {k: v["value"] for k, v in helper_locals.items() if k in {"destino", "capacidad", "usado", "fmt"}},
                "return_type": "void", "return": None, "continuation": "Regresa al helper target sin valor escalar."})
        state = deepcopy(before_state)
        if queue_changed:
            state.update(items=[], size=0, empty=True)
        previous = deepcopy(steps[-1]["state_after"] if steps else before_state)
        step = {"step_index": len(steps), "line_index": index, "line_text": lines[index], "event_type": event,
            "function_name": fn, "phase": "start" if not steps else "end" if not active else "progress",
            "delay_ms": 100, "condition_result": condition, "state_snapshot": previous, "state_after": state, "console": []}
        frame = build_sequential_frame(structure_id="priority_queue", operation_name=operation, payload=payload, step=step, success=success)
        frame.update(variables=variables, pointers=[{"name": v["name"], "type": v["type"], "target": v["value"],
            "initialized": v["initialized"], "valid": v["valid"], "scope": v["scope"], "scope_state": "active"}
            for v in target_vars + dependency_vars if "*" in v["type"]], heap_objects=deepcopy(heap), call_stack=calls,
            scopes=[{"id": function, "kind": "function", "state": mem["scope"], "scope_state": mem["scope"], "variables": target_vars},
                {"id": "cp_append_text", "kind": "function", "state": mem["helper_scope"], "scope_state": mem["helper_scope"], "variables": dependency_vars}] if operation == "formatear" else
                [{"id": function, "kind": "function", "state": mem["scope"], "scope_state": mem["scope"], "variables": target_vars}],
            helper_memory=mem, memory_state=None, heap_transition={"kind": "stable", "before": deepcopy(heap), "after": deepcopy(heap), "freed": [], "dangling_references": []},
            condition=None if condition is None else {"source": token, "substituted": " ; ".join(x["source"] + " => " + str(x["result"]) for x in operands or []),
                "result": condition, "evaluated_operands": deepcopy(operands or []), "consequence": "Cortocircuito real; no lectura de operandos omitidos."})
        frame["source"]["function"] = fn
        frame["concept"] = "condition" if condition is not None else "return" if event in {"return", "end"} else "call" if event in {"entry", "call"} else "assignment"
        frame["invariant"] = {"text": "Nodos prestados intactos; stores sólo al struct de inicialización o buffers del caller.",
            "holds": True, "symbol": "V", "evidence": "Campos indeterminados enmascarados, cortocircuito, capacidad válida y scopes propios."}
        narration = ("Termina el ámbito y retorna " + ("void sin valor" if fn == "cp_append_text" or return_type == "void" else str(result)) + "." if event in {"return", "end"} else
            "Evalúa únicamente los operandos alcanzados de esta condición C." if condition is not None else
            "Declara almacenamiento local; el campo initialized indica si se puede leer." if event.startswith("declare") else
            "Ejecuta la llamada de formato y conserva separados el buffer, usados y el tamaño que habría escrito." if event in {"call", "format", "resume"} else
            "Ejecuta esta instrucción C sobre el campo o almacenamiento prestado indicado.")
        for level in frame["narration"]:
            frame["narration"][level] = narration
        validate_sequential_frame(frame, source_code=source_code)
        step["pedagogy"] = frame
        steps.append(step)

    def condition(event: str, token: str, terms: list[tuple[str, Any]], *, conjunction: bool = False) -> bool:
        evaluated = []
        result_ = conjunction
        for source, thunk in terms:
            value = bool(thunk())
            evaluated.append({"source": source, "result": value})
            result_ = value
            if (conjunction and not value) or (not conjunction and value):
                break
        emit(event, token, result_, evaluated)
        return result_

    def finish(token: str, value: Any = None, *, implicit: bool = False) -> None:
        nonlocal active, result
        result = value
        active = False
        emit("end" if implicit else "return", token, closing=implicit)

    def write_text(text: str, offset: int, available: int) -> int:
        encoded = list(text.encode("ascii"))
        count = min(len(encoded), available - 1)
        byte_buffer[offset:offset + count] = encoded[:count]
        byte_buffer[offset + count] = 0
        bytes_written[offset:offset + count + 1] = [True] * (count + 1)
        return len(encoded)

    def append(token: str, text: str, arguments: list[int]) -> None:
        nonlocal helper_active, current_function, helper_locals
        emit("call", token)
        helper_active = True
        current_function = "cp_append_text"
        helper_locals = {name: var(name, typ, value, scope=current_function) for name, typ, value in [
            ("destino", "char *", "&caller_destino"), ("capacidad", "size_t", capacity),
            ("usado", "size_t *", "&" + function + ".usado"), ("fmt", "const char *", "%d(p=%d)" if arguments else text)]}
        helper_locals["variadic_arguments"] = var("variadic_arguments", "promoted int arguments", arguments, scope=current_function)
        emit("entry", "static void cp_append_text(")
        for name, typ in [("args", "va_list"), ("escritos", "int")]:
            helper_locals[name] = var(name, typ, None, False, scope=current_function)
            emit("declare-" + name, typ + " " + name + ";")
        guard = condition("guard", "if (destino == NULL", [("destino == NULL", lambda: False),
            ("usado == NULL", lambda: False), ("*usado >= capacidad", lambda: locals_["usado"]["value"] >= capacity)])
        if guard:
            helper_active = False
            emit("return", "return;")
        else:
            helper_locals["args"].update(value="active", initialized=True, valid=True)
            emit("va-start", "va_start(args, fmt);")
            offset = locals_["usado"]["value"]
            written = write_text(text, offset, capacity - offset)
            helper_locals["escritos"].update(value=written, initialized=True, valid=True)
            emit("format", "escritos = vsnprintf(")
            helper_locals["args"].update(value=None, initialized=False, valid=False)
            emit("va-end", "va_end(args);")
            failed = condition("format-error", "if (escritos < 0)", [("escritos < 0", lambda: written < 0)])
            if failed:
                helper_active = False
                emit("return", "return;")
            else:
                truncated = condition("truncation", "if ((size_t)escritos >= capacidad", [("(size_t)escritos >= capacidad - *usado", lambda: written >= capacity - offset)])
                put("usado", capacity if truncated else offset + written)
                emit("saturate" if truncated else "append-count", "*usado = capacidad;" if truncated else "*usado += (size_t)escritos;")
                helper_active = False
                emit("end", "}", closing=True)
        current_function = function
        helper_locals = {}
        emit("resume", token)

    emit("entry", function + "(")
    if operation == "inicializar":
        if condition("guard", "if (cola == NULL)", [("cola == NULL", lambda: null_cola)]):
            finish("return;")
        else:
            for name, bit, value in [("delante", 1, None), ("atras", 2, None), ("cantidad", 4, 0)]:
                fields[name] = value
                mask |= bit
                emit("store-" + name, "cola->" + name + " = ")
            queue_changed = True
            finish("}", implicit=True)
    elif operation == "vacia":
        value = condition("return-condition", "return cola == NULL", [("cola == NULL", lambda: null_cola),
            ("cola->delante == NULL", lambda: fields["delante"] is None), ("cola->cantidad == 0", lambda: fields["cantidad"] == 0)])
        finish("return cola == NULL", value)
    elif operation == "contar":
        if condition("guard", "if (cola == NULL)", [("cola == NULL", lambda: null_cola)]):
            finish("return 0;", 0)
        else:
            finish("return cola->cantidad;", fields["cantidad"])
    elif operation == "copiar_items":
        declare("usados", "int", 0, True)
        emit("declare-usados", "int usados = 0;")
        declare("aux", "CPNodo *")
        emit("declare-aux", "CPNodo *aux;")
        reject = condition("guard", "if (cola == NULL", [("cola == NULL", lambda: null_cola), ("valores == NULL", lambda: null_values),
            ("prioridades == NULL", lambda: null_priorities), ("capacidad <= 0", lambda: capacity <= 0)])
        if reject:
            finish("return 0;", 0)
        else:
            put("aux", fields["delante"])
            emit("assign-aux", "aux = cola->delante;")
            while condition("loop", "while (aux != NULL", [("aux != NULL", lambda: locals_["aux"]["value"] is not None),
                    ("usados < capacidad", lambda: locals_["usados"]["value"] < capacity)], conjunction=True):
                node = nodes[locals_["aux"]["value"]]["fields"]
                i = locals_["usados"]["value"]
                values[i], value_written[i] = node["valor"], True
                emit("store-value", "valores[usados] = aux->valor;")
                priorities[i], priority_written[i] = node["prioridad"], True
                emit("store-priority", "prioridades[usados] = aux->prioridad;")
                put("usados", i + 1)
                emit("increment", "usados++;")
                put("aux", node["sgte"])
                emit("advance", "aux = aux->sgte;")
            finish("return usados;", locals_["usados"]["value"])
    else:
        declare("aux", "CPNodo *")
        emit("declare-aux", "CPNodo *aux;")
        declare("usado", "size_t", 0, True)
        emit("declare-usado", "size_t usado = 0;")
        if condition("guard", "if (destino == NULL", [("destino == NULL", lambda: null_destino), ("capacidad == 0", lambda: capacity == 0)]):
            finish("return;")
        else:
            byte_buffer[0], bytes_written[0] = 0, True
            emit("buffer-init", "destino[0] = ")
            if condition("empty", "if (cola == NULL", [("cola == NULL", lambda: null_cola), ("cola->delante == NULL", lambda: fields["delante"] is None)]):
                write_text("Cola de prioridad vacia", 0, capacity)
                emit("format-empty", "snprintf(destino, capacidad,")
                # The return after snprintf is the second explicit return in this function.
                start, end = blocks[function]
                return_index = next(i for i in range(start, end + 1) if "snprintf(destino, capacidad," in lines[i]) + 1
                finish(lines[return_index].strip())
                steps[-1]["line_index"] = return_index
                steps[-1]["line_text"] = lines[return_index]
                steps[-1]["pedagogy"]["source"]["line_index"] = return_index
                steps[-1]["pedagogy"]["source"]["line_text"] = lines[return_index]
            else:
                append('cp_append_text(destino, capacidad, &usado, "frente -> ");', "frente -> ", [])
                put("aux", fields["delante"])
                emit("assign-aux", "aux = cola->delante;")
                while condition("loop", "while (aux != NULL", [("aux != NULL", lambda: locals_["aux"]["value"] is not None),
                        ("usado < capacidad", lambda: locals_["usado"]["value"] < capacity)], conjunction=True):
                    node = nodes[locals_["aux"]["value"]]["fields"]
                    append('cp_append_text(destino, capacidad, &usado, "%d(p=%d)",', str(node["valor"]) + "(p=" + str(node["prioridad"]) + ")", [node["valor"], node["prioridad"]])
                    put("aux", node["sgte"])
                    emit("advance", "aux = aux->sgte;")
                    if condition("separator", "if (aux != NULL", [("aux != NULL", lambda: locals_["aux"]["value"] is not None),
                            ("usado < capacidad", lambda: locals_["usado"]["value"] < capacity)], conjunction=True):
                        append('cp_append_text(destino, capacidad, &usado, " | ");', " | ", [])
                finish("}", implicit=True)
    return {"structure_id": "priority_queue", "operation_name": operation_name, "payload": deepcopy(payload),
        "source_code": source_code, "code_title": code_title, "steps": steps, "final_state": deepcopy(steps[-1]["state_after"]),
        "success": success, "message": message, "mutates": operation == "inicializar", "execution_started": True,
        "pedagogy_schema_version": SEQUENTIAL_FRAME_SCHEMA_VERSION, "pedagogy_schema": sequential_frame_schema(),
        "learning_profile": deepcopy(SEQUENTIAL_LEARNING_CATALOG["priority_queue"]),
        "instruction_scope": "Private C helper scopes; borrowed nodes/struct/caller buffers; no registered API/UI helper query."}
