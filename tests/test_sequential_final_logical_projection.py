"""Return projection follows actual C objects without losing their physical history."""
from copy import deepcopy
import importlib
import pytest

CASES = [(structure, operation, rows) for structure, operation in
         [("priority_queue", "desencolar"), ("priority_queue", "frente")]
         for rows in [[], [(7, 1)], [(30, 2), (10, 1), (20, 3)], [(30, 2), (10, 1), (20, 1)]]]
CASES += [("queue", "desencolar", rows) for rows in [[], [(7, 0)], [(7, 0), (8, 0), (9, 0)]]]


def _run(client, structure, operation, rows):
    initial = None
    for value, priority in rows:
        payload = {"value": str(value)}
        if structure == "priority_queue": payload["priority"] = str(priority)
        response = client.post("/sequential/" + structure + "/operate", json={"operation": "encolar", "payload": payload})
        assert response.status_code == 200
        initial = response.get_json()["visual_state"]
    response = client.post("/sequential/" + structure + "/operate", json={"operation": operation, "payload": {}})
    assert response.status_code == (200 if rows else 400)
    return initial, response.get_json()


def _remaining(structure, operation, rows):
    selected = min(range(len(rows)), key=lambda i: rows[i][1]) if rows and structure == "priority_queue" else 0
    remaining = list(rows)
    if rows and operation == "desencolar": remaining.pop(selected)
    items = [{"value": value, **({"priority": priority} if structure == "priority_queue" else {})} for value, priority in remaining]
    return selected, items


@pytest.mark.parametrize("structure,operation,rows", CASES)
def test_final_logical_projection_keeps_C_root_outputs_scopes_and_history(client, structure, operation, rows):
    initial, body = _run(client, structure, operation, rows)
    trace = body["execution_trace"]; steps = trace["steps"]; final = steps[-1]["state_after"]
    assert final == body["visual_state"] == trace["final_state"]
    selected, items = _remaining(structure, operation, rows)
    assert final["items"] == items and final["size"] == len(items) and final["empty"] is (not items)
    if structure == "priority_queue":
        assert final["out_index"] == (min(range(len(items)), key=lambda i: items[i]["priority"]) if items else -1)
    if rows: assert body["result"] == rows[selected][0]
    if operation == "frente" and rows: assert final == initial
    physical = steps[-1]["pedagogy"]["memory_state"]
    assert {"delante", "atras"} <= physical.keys()
    assert not {"delante", "atras", "actual", "prev", "objetivo", "objetivoPrev", "cantidad", "valor", "prioridad"}.intersection(final)
    memory_key = "front_memory" if operation == "frente" else "dequeue_memory"
    memory = steps[-1]["pedagogy"][memory_key]
    assert memory["scope_state"] == "ended" and memory["call_stack"] == []
    if structure == "priority_queue":
        assert memory["outputs"]["value_written"] is bool(rows)
        assert memory["outputs"]["priority_written"] is bool(rows)
        if rows: assert (memory["outputs"]["value"], memory["outputs"]["priority"]) == rows[selected]
    for i, step in enumerate(steps):
        assert step["line_text"] == trace["source_code"].splitlines()[step["line_index"]]
        if i: assert step["state_snapshot"] == steps[i-1]["state_after"]
    if operation == "frente":
        assert all(step["pedagogy"]["heap_objects"] == steps[0]["pedagogy"]["heap_objects"] for step in steps)
        assert all(not step["pedagogy"]["heap_transition"]["freed"] for step in steps)
    else:
        released = [node for step in steps for node in step["pedagogy"]["heap_transition"]["freed"]]
        assert len(released) == (1 if rows else 0)
        if rows: assert released[0]["historical_fields"]["valor" if structure == "priority_queue" else "nro"] == rows[selected][0]


@pytest.mark.parametrize("structure,operation,module,function", [
    ("priority_queue", "desencolar", "priority_queue_dequeue_instruction", "build_priority_queue_dequeue_trace"),
    ("priority_queue", "frente", "priority_queue_front_instruction", "build_priority_queue_front_trace"),
    ("queue", "desencolar", "queue_dequeue_instruction", "build_queue_dequeue_trace")])
def test_final_return_is_derived_not_copied_from_future_after_state(client, structure, operation, module, function):
    rows = [(30, 2), (10, 1), (20, 3)]
    initial, body = _run(client, structure, operation, rows)
    original = body["execution_trace"]
    poisoned = deepcopy(body["visual_state"])
    poisoned.update(items=[{"value": 999, "priority": -999}], size=999, empty=True, out_index=999)
    builder = getattr(importlib.import_module("app.domain.sequential." + module), function)
    trace = builder(payload={}, source_code=original["source_code"], code_title=original["code_title"],
                    before_state=initial, after_state=poisoned, success=True, message="test-only")
    final = trace["steps"][-1]["state_after"]
    _, items = _remaining(structure, operation, rows)
    assert final["items"] == items and final["size"] == len(items)
    assert final == body["visual_state"] and final != poisoned
    assert "delante" in trace["steps"][-1]["pedagogy"]["memory_state"]
