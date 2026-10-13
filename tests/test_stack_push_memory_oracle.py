"""Pure counterexamples for detached Apilar memory and alias lifetime."""
from __future__ import annotations
from copy import deepcopy
import pytest
from _stack_push_memory_oracle import assert_empty_stack_push_memory


def _fixture() -> dict:
    """Hand-written empty-stack C path, without importing application code."""
    source = """void pila_apilar(ptrPila *p, int valor) {
    if (p == NULL) {
        printf("Error: pila no inicializada.\\n");
        return;
    }
    ptrPila aux = (ptrPila) malloc(sizeof(struct NodoPila));
    if (aux == NULL) {
        printf("Error: No se pudo asignar memoria.\\n");
        return;
    }
    aux->nro = valor;
    aux->sgte = *p;
    *p = aux;
}
"""
    tokens = ["entry", "root_guard", "allocator_enter", "allocator_success_return", "aux_allocated", "allocation_guard", "value_assigned", "link_assigned", "root_assigned", "return"]
    indices = [0, 1, 5, 5, 5, 6, 10, 11, 12, 13]
    rows = source.splitlines()
    steps = []
    old_heap = []
    for i, token in enumerate(tokens):
        root = "RESERVA_1" if i >= 8 else None
        mask = 3 if i >= 7 else 1 if i >= 6 else 0
        heap = [] if i < 3 else [{"id": "RESERVA_1", "address": "RESERVA_1", "type": "struct NodoPila", "alive": True, "allocated": True, "freed": False, "fields_valid": mask == 3, "initialized_mask": mask, "field_validity": {"nro": mask >= 1, "sgte": mask == 3}, "status": "linked" if i >= 8 else "temporary", "fields": {"nro": 9 if mask >= 1 else None, "sgte": None}}]
        aux = None if i < 2 or i == 9 else {"type": "ptrPila", "value": "RESERVA_1" if i >= 4 else None, "initialized": i >= 4, "valid": i >= 4}
        def variable(name: str, kind: str, value, scope: str, initialized=True, valid=True) -> dict:
            return {"name": name, "type": kind, "value": value, "scope": scope, "scope_state": "active", "initialized": initialized, "valid": valid}
        variables = [variable("pila", "ptrPila", root, "caller")]
        if i < 9:
            variables += [variable("p", "ptrPila *", "&pila", "pila_apilar"), variable("valor", "int", 9, "pila_apilar")]
            if i >= 2:
                variables.append(variable("aux", "ptrPila", aux["value"], "pila_apilar", aux["initialized"], aux["valid"]))
        calls = [] if i == 9 else [{"function": "pila_apilar", "parameters": {"p": "&pila", "valor": 9}}]
        if i == 2:
            calls.append({"function": "malloc", "parameters": {"size": "sizeof(struct NodoPila)"}, "opaque": True})
        state = {"items": [{"value": 9}] if i >= 8 else [], "size": int(i >= 8), "empty": i < 8}
        frame = {"push_memory": {"root": {"type": "ptrPila", "identity": "&pila", "value": root, "alive": True, "valid": True, "initialized": True}, "heap": deepcopy(heap), "aux": aux, "variables": deepcopy(variables), "call_stack": deepcopy(calls)}, "heap_objects": deepcopy(heap), "heap_transition": {"before": deepcopy(old_heap), "after": deepcopy(heap), "freed": [], "dangling_references": [], "kind": "allocate" if i == 3 else "link" if i == 8 else "stable"}, "variables": variables, "scopes": [] if i == 9 else [{"id": "pila_apilar", "variables": [v for v in variables if v["scope"] == "pila_apilar"]}], "call_stack": calls, "source": {"line_index": indices[i], "line_text": rows[indices[i]]}, "condition": {"result": False} if i in {1, 5} else None}
        steps.append({"step_index": i, "event_type": token, "debug": {"token": token}, "line_index": indices[i], "line_text": rows[indices[i]], "state_snapshot": deepcopy(steps[-1]["state_after"] if steps else {"items": [], "size": 0, "empty": True}), "state_after": state, "console": [], "condition_result": False if i in {1, 5} else None, "pedagogy": frame})
        old_heap = deepcopy(heap)
    final = deepcopy(steps[-1]["state_after"])
    return {"success": True, "visual_state": final, "execution_trace": {"structure_id": "stack", "operation_name": "apilar", "source_code": source, "steps": steps, "final_state": deepcopy(final)}}


def test_handwritten_memory_contract_positive() -> None:
    assert_empty_stack_push_memory(_fixture(), 9)


@pytest.mark.parametrize("corruption", ["missing_allocation", "duplicate_object", "invented_free", "premature_value", "wrong_value", "early_link_validity", "wrong_link", "early_root", "early_aux", "lost_alias_after_publish", "early_scope_exit", "callee_survives_return", "invented_console", "omitted_store_event", "false_source", "discontinuity"])
def test_stack_memory_oracle_rejects_corruption(corruption: str) -> None:
    body = _fixture()
    steps = body["execution_trace"]["steps"]
    if corruption == "missing_allocation":
        steps[3]["pedagogy"]["push_memory"]["heap"] = []
    elif corruption == "duplicate_object":
        steps[3]["pedagogy"]["push_memory"]["heap"].append(deepcopy(steps[3]["pedagogy"]["push_memory"]["heap"][0]))
    elif corruption == "invented_free":
        steps[8]["pedagogy"]["heap_transition"]["freed"] = [{"id": "RESERVA_1"}]
    elif corruption == "premature_value":
        steps[3]["pedagogy"]["push_memory"]["heap"][0]["fields"]["nro"] = 9
    elif corruption == "wrong_value":
        steps[6]["pedagogy"]["push_memory"]["heap"][0]["fields"]["nro"] = 99
    elif corruption == "early_link_validity":
        steps[6]["pedagogy"]["push_memory"]["heap"][0]["field_validity"]["sgte"] = True
    elif corruption == "wrong_link":
        steps[7]["pedagogy"]["push_memory"]["heap"][0]["fields"]["sgte"] = "NO_RESERVADO"
    elif corruption == "early_root":
        steps[6]["pedagogy"]["push_memory"]["root"]["value"] = "RESERVA_1"
    elif corruption == "early_aux":
        steps[2]["pedagogy"]["push_memory"]["aux"]["initialized"] = True
    elif corruption == "lost_alias_after_publish":
        steps[8]["pedagogy"]["push_memory"]["aux"] = None
    elif corruption == "early_scope_exit":
        steps[7]["pedagogy"]["scopes"] = []
    elif corruption == "callee_survives_return":
        steps[9]["pedagogy"]["call_stack"] = deepcopy(steps[8]["pedagogy"]["call_stack"])
    elif corruption == "invented_console":
        steps[8]["console"] = ["Aplicado"]
    elif corruption == "omitted_store_event":
        steps[6]["event_type"] = "root_assigned"
    elif corruption == "false_source":
        steps[6]["line_text"] = "aux->nro = 99;"
    else:
        steps[7]["state_snapshot"]["size"] = 999
    with pytest.raises(AssertionError):
        assert_empty_stack_push_memory(body, 9)



def test_coordinated_nonempty_initial_stack_cannot_disappear_on_entry() -> None:
    body = _fixture()
    entry = body["execution_trace"]["steps"][0]
    entry["state_snapshot"] = {"items": [{"value": 123}], "size": 1, "empty": False}
    entry["pedagogy"]["state_before"] = deepcopy(entry["state_snapshot"])
    with pytest.raises(AssertionError, match="fixture starts with an empty stack"):
        assert_empty_stack_push_memory(body, 9)


@pytest.mark.parametrize(("parameter", "corruption"), [("p", "uninitialized"), ("p", "invalid"), ("p", "scope"), ("valor", "uninitialized"), ("valor", "invalid"), ("valor", "scope"), ("valor", "both_flags")])
def test_coordinated_entry_parameter_corruption_is_rejected(parameter: str, corruption: str) -> None:
    body = _fixture()
    frame = body["execution_trace"]["steps"][0]["pedagogy"]
    item = next(v for v in frame["variables"] if v["name"] == parameter)
    if corruption in {"uninitialized", "both_flags"}:
        item["initialized"] = False
    if corruption in {"invalid", "both_flags"}:
        item["valid"] = False
    if corruption == "scope":
        item["scope"] = "caller"
    # Coordinate all three representations: rejection cannot rely on mismatch.
    frame["push_memory"]["variables"] = deepcopy(frame["variables"])
    frame["scopes"][0]["variables"] = [deepcopy(v) for v in frame["variables"] if v["scope"] == "pila_apilar"]
    with pytest.raises(AssertionError):
        assert_empty_stack_push_memory(body, 9)
