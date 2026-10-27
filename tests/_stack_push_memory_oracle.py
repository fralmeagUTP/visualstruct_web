"""Test-only C contract for the two empty-stack Apilar(9) consumers.

Expected masks, writes, publication and alias lifetime come from tad_pila.c and
the accepted finite closure, not from another run or a final producer flag.
"""
from __future__ import annotations

TOKENS = ("entry", "root_guard", "allocator_enter", "allocator_success_return",
          "aux_allocated", "allocation_guard", "value_assigned", "link_assigned",
          "root_assigned", "return")
MALLOC = "ptrPila aux = (ptrPila) malloc(sizeof(struct NodoPila));"
LINES = ("void pila_apilar(ptrPila *p, int valor) {", "if (p == NULL) {",
         MALLOC, MALLOC, MALLOC, "if (aux == NULL) {", "aux->nro = valor;",
         "aux->sgte = *p;", "*p = aux;", "}")


def assert_empty_stack_push_memory(body: dict, value: int) -> None:
    """Require the actual detached object, individual stores and retained alias."""
    assert type(value) is int
    trace = body["execution_trace"]
    assert body["success"] is True and trace["structure_id"] == "stack"
    assert trace["operation_name"] == "apilar"
    steps = trace["steps"]
    assert len(steps) == len(TOKENS)
    initial = steps[0]["state_snapshot"]
    assert initial["items"] == [] and type(initial["size"]) is int and initial["size"] == 0 and initial["empty"] is True, "fixture starts with an empty stack"
    assert initial == steps[0]["state_after"], "function entry cannot erase initial state"
    source = trace["source_code"].replace("\r\n", "\n").split("\n")
    allocations = steps[3]["pedagogy"]["push_memory"]["heap"]
    assert len(allocations) == 1
    identity = allocations[0]["id"]
    assert isinstance(identity, str) and identity
    previous_heap = []
    for index, step in enumerate(steps):
        frame = step["pedagogy"]
        memory = frame["push_memory"]
        assert step["step_index"] == index and step["event_type"] == TOKENS[index]
        assert step["debug"]["token"] == TOKENS[index]
        line_index = step["line_index"]
        assert type(line_index) is int and 0 <= line_index < len(source)
        assert step["line_text"] == source[line_index] and step["line_text"].strip() == LINES[index]
        assert frame["source"]["line_index"] == line_index and frame["source"]["line_text"] == step["line_text"]
        if index:
            assert steps[index-1]["state_after"] == step["state_snapshot"]
        root = identity if index >= 8 else None
        assert memory["root"] == {"type": "ptrPila", "identity": "&pila", "value": root,
                                  "alive": True, "valid": True, "initialized": True}
        expected_heap = []
        if index >= 3:
            mask = 3 if index >= 7 else 1 if index >= 6 else 0
            expected_heap = [{"id": identity, "address": identity, "type": "struct NodoPila",
                              "alive": True, "allocated": True, "freed": False,
                              "fields_valid": mask == 3, "initialized_mask": mask,
                              "field_validity": {"nro": mask >= 1, "sgte": mask == 3},
                              "status": "linked" if index >= 8 else "temporary",
                              "fields": {"nro": value if mask >= 1 else None, "sgte": None}}]
        assert memory["heap"] == expected_heap and frame["heap_objects"] == expected_heap
        transition = frame["heap_transition"]
        assert transition["before"] == previous_heap and transition["after"] == expected_heap
        assert transition["freed"] == [] and transition["dangling_references"] == []
        assert transition["kind"] == ("allocate" if index == 3 else "link" if index == 8 else "stable")
        previous_heap = expected_heap
        expected_aux = None if index < 2 or index == 9 else {
            "type": "ptrPila", "value": identity if index >= 4 else None,
            "initialized": index >= 4, "valid": index >= 4}
        assert memory["aux"] == expected_aux
        assert memory["variables"] == frame["variables"]
        variables = frame["variables"]
        names = [v["name"] for v in variables]
        expected_names = ["pila"] if index == 9 else ["pila", "p", "valor"] + (["aux"] if index >= 2 else [])
        assert len(names) == len(set(names)) and set(names) == set(expected_names)
        by_name = {v["name"]: v for v in variables}
        assert (by_name["pila"]["type"], by_name["pila"]["value"], by_name["pila"]["scope"], by_name["pila"]["scope_state"]) == ("ptrPila", root, "caller", "active")
        assert by_name["pila"]["initialized"] is True and by_name["pila"]["valid"] is True
        if index < 9:
            assert (by_name["p"]["type"], by_name["p"]["value"], by_name["p"]["scope"]) == ("ptrPila *", "&pila", "pila_apilar")
            assert (by_name["valor"]["type"], by_name["valor"]["value"], by_name["valor"]["scope"]) == ("int", value, "pila_apilar")
            for name in ("p", "valor"):
                assert by_name[name]["initialized"] is True and by_name[name]["valid"] is True, "C parameters initialized and valid throughout scope"
                assert by_name[name]["scope_state"] == "active", "C parameter scope remains active"
            assert len(frame["scopes"]) == 1 and frame["scopes"][0]["id"] == "pila_apilar"
            assert frame["scopes"][0]["variables"] == [v for v in variables if v["scope"] == "pila_apilar"]
            if index >= 2:
                aux = by_name["aux"]
                assert (aux["type"], aux["value"], aux["initialized"], aux["valid"], aux["scope"]) == (
                    "ptrPila", expected_aux["value"], expected_aux["initialized"], expected_aux["valid"], "pila_apilar")
        else:
            assert frame["scopes"] == []
        calls = memory["call_stack"]
        assert calls == frame["call_stack"]
        assert [call["function"] for call in calls] == ([] if index == 9 else ["pila_apilar", "malloc"] if index == 2 else ["pila_apilar"])
        if index < 9:
            assert calls[0]["parameters"] == {"p": "&pila", "valor": value}
        if index == 2:
            assert calls[1]["opaque"] is True and calls[1]["parameters"] == {"size": "sizeof(struct NodoPila)"}
        if index in {1, 5}:
            assert step["condition_result"] is False and frame["condition"]["result"] is False
        assert step["console"] == [], "Apilar successful path has no printf"
        expected_items = [{"value": value}] if index >= 8 else []
        state = step["state_after"]
        assert state["items"] == expected_items and state["size"] == len(expected_items)
        assert state["empty"] is (not expected_items)
    assert trace["final_state"] == body["visual_state"] == steps[-1]["state_after"]
