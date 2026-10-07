"""Regression of logical cp_encolar state versus retained C caller memory."""
from copy import deepcopy
import pytest
from app.domain.sequential.priority_queue_enqueue_instruction import build_priority_queue_enqueue_trace
from app.services.trace.engine import TraceEngine, TraceContractError

MEMORY_FIELDS = {"node_ids", "delante", "atras", "cantidad"}
CASES = [([], 9, 3), ([(7, 2)], -1, -1), ([(7, 1)], 7, 1), ([(4, 2), (5, 2)], 6, 2)]

def logical(items):
    return {"kind": "priority", "title": "Cola de prioridad (orden de llegada)",
            "items": [{"value": v, "priority": p} for v, p in items],
            "size": len(items), "empty": not items,
            "out_index": min(range(len(items)), key=lambda i: items[i][1]) if items else -1}

def execute(client, seeds, value, priority):
    client.post("/sequential/priority_queue/reset")
    for v, p in seeds:
        assert client.post("/sequential/priority_queue/operate", json={"operation": "encolar", "payload": {"value": v, "priority": p}}).status_code == 200
    response = client.post("/sequential/priority_queue/operate", json={"operation": "encolar", "payload": {"value": value, "priority": priority}})
    assert response.status_code == 200
    return response.get_json()

def assert_contract(trace, expected):
    saved = deepcopy(trace)
    semantic = TraceEngine.validate_legacy_trace(trace)
    assert len(semantic) == len(trace["steps"])
    assert trace == saved
    assert trace["steps"][-1]["state_after"] == trace["final_state"] == expected
    source = trace["source_code"].splitlines()
    for index, step in enumerate(trace["steps"]):
        assert step["step_index"] == index
        assert step["line_text"].strip() == source[step["line_index"]].strip()
        if index == len(trace["steps"]) - 1:
            assert not MEMORY_FIELDS.intersection(step["state_after"])
        else:
            assert MEMORY_FIELDS <= step["state_after"].keys()
        memory = step["pedagogy"]["memory_state"]
        assert MEMORY_FIELDS <= memory.keys()
        assert memory["items"] == step["state_after"]["items"]
        root = step["pedagogy"]["enqueue_memory"]["root"]
        assert (memory["delante"], memory["atras"], memory["cantidad"]) == (root["front"] or "NULL", root["rear"] or "NULL", root["quantity"])
        if index:
            assert trace["steps"][index-1]["state_after"] == step["state_snapshot"]
    return trace["steps"]

@pytest.mark.parametrize("seeds,value,priority", CASES)
def test_enqueue_complete_logical_contract_retains_ownership(client, seeds, value, priority):
    result = execute(client, seeds, value, priority)
    expected = logical(seeds + [(value, priority)])
    assert result["visual_state"] == expected
    steps = assert_contract(result["execution_trace"], expected)
    events = [s["event_type"] for s in steps]
    assert events == ["entry", "new_declared", "root_guard", "helper_call", "helper_entry", "allocator_enter", "allocator_success_return", "helper_new_allocated", "helper_allocation_guard", "value_assigned", "priority_assigned", "link_assigned", "helper_return", "helper_exit", "parent_new_assigned", "parent_allocation_guard", "empty_guard", "rear_next_assigned" if seeds else "front_assigned", "rear_assigned", "count_incremented", "return_true"]
    by_event = {s["event_type"]: s for s in steps}
    new_id = f"N{len(seeds)+1}"
    for event, mask in [("allocator_success_return", 0), ("value_assigned", 1), ("priority_assigned", 3), ("link_assigned", 7)]:
        heap = by_event[event]["pedagogy"]["heap_objects"]
        assert len(heap) == len(seeds) + 1
        node = next(n for n in heap if n["id"] == new_id)
        assert node["initialized_mask"] == mask and node["alive"] and not node["freed"]
    final = steps[-1]["pedagogy"]["enqueue_memory"]
    assert final["root"] == {"identity": "&cp", "type": "ColaPrioridad", "alive": True, "valid": True, "initialized": True, "front": "N1", "rear": new_id, "quantity": len(seeds)+1}
    assert final["parent_new"] is None and final["helper_new"] is None and not final["call_stack"]
    assert {v["scope"] for v in final["variables"]} == {"caller"}
    assert all(n["alive"] and not n["freed"] for n in final["heap"])
    assert len({n["id"] for n in final["heap"]}) == len(seeds)+1
    # The C counter changes only at its store, never at publication of the link.
    assert all(s["pedagogy"]["enqueue_memory"]["root"]["quantity"] == len(seeds) for s in steps[:events.index("count_incremented")])
    assert by_event["count_incremented"]["pedagogy"]["enqueue_memory"]["root"]["quantity"] == len(seeds)+1
    assert all(not s["pedagogy"]["heap_transition"]["freed"] for s in steps)
    assert by_event["parent_new_assigned"]["pedagogy"]["enqueue_memory"]["parent_new"]["value"] == new_id
    assert by_event["helper_return"]["pedagogy"]["enqueue_memory"]["helper_new"]["value"] == new_id
    assert by_event["entry"]["state_after"]["items"] == logical(seeds)["items"]
    assert by_event["helper_return"]["state_after"]["items"] == logical(seeds)["items"]

@pytest.mark.parametrize("seeds,null_root,allocation_failure", [([], True, False), ([], False, True), ([(7, 2)], False, True)])
def test_private_NULL_branches_preserve_full_trace_and_caller(client, seeds, null_root, allocation_failure):
    reference = execute(client, [], 9, 3)["execution_trace"]
    before = logical(seeds)
    trace = build_priority_queue_enqueue_trace(payload={"value": 9, "priority": 3}, source_code=reference["source_code"], code_title=reference["code_title"], before_state=before, after_state=before, success=False, message="", null_root=null_root, allocation_failure=allocation_failure)
    steps = assert_contract(trace, before)
    assert steps[-1]["event_type"] == "return_false" and steps[-1]["debug"]["return_value"] is False
    assert all(s["state_after"]["items"] == before["items"] for s in steps)
    assert all(len(s["pedagogy"]["heap_objects"]) == len(seeds) for s in steps)
    assert all(not s["pedagogy"]["heap_transition"]["freed"] for s in steps)
    assert steps[-1]["pedagogy"]["enqueue_memory"]["root"]["alive"] is not null_root
    assert ("allocator_NULL_return" in [s["event_type"] for s in steps]) is allocation_failure
    assert "allocator_success_return" not in [s["event_type"] for s in steps]

def test_final_state_is_not_manufactured_from_supplied_future_and_bad_trace_is_rejected(client):
    reference = execute(client, [], 9, 3)["execution_trace"]
    poison = logical([(999, 999)])
    trace = build_priority_queue_enqueue_trace(payload={"value": 9, "priority": 3}, source_code=reference["source_code"], code_title=reference["code_title"], before_state=logical([]), after_state=poison, success=True, message="")
    assert trace["steps"][-1]["state_after"]["items"] == logical([(9, 3)])["items"]
    with pytest.raises(TraceContractError):
        TraceEngine.validate_legacy_trace(trace)

def test_saved_frame_memory_and_logical_state_have_independent_ownership(client):
    trace = execute(client, [], 9, 3)["execution_trace"]
    assert_contract(trace, logical([(9, 3)]))
    saved = deepcopy(trace["steps"][0])
    final = trace["steps"][-1]
    final["pedagogy"]["memory_state"]["items"][0]["value"] = 123
    final["pedagogy"]["enqueue_memory"]["heap"][0]["fields"]["valor"] = 456
    assert final["state_after"]["items"][0]["value"] == 9
    assert trace["steps"][0] == saved
