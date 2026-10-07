"""Per-event free identities are separate from cumulative retired history."""
import pytest
from test_priority_queue_trace_conformance import _operate

@pytest.mark.parametrize("count", [0, 1, 3])
def test_cleanup_freed_is_exact_live_heap_delta_and_history_is_preserved(client, count):
    for i in range(count):
        assert _operate(client, "encolar", {"value": str(10+i), "priority": str(i+1)})["success"]
    trace = _operate(client, "limpiar")["execution_trace"]
    seen = set()
    for step in trace["steps"]:
        frame = step["pedagogy"]; transition = frame["heap_transition"]
        before = {n["id"] for n in transition["before"]}
        after = {n["id"] for n in transition["after"]}
        freed = transition["freed"]
        ids = {n["id"] for n in freed}
        assert ids == before - after
        assert len(ids) == len(freed)
        assert len(ids) == (1 if step["event_type"] == "node_free" else 0)
        assert not seen.intersection(ids)
        seen.update(ids)
        retired = [n for n in frame["cleanup_memory"]["heap"] if not n["alive"]]
        assert {n["id"] for n in retired} == seen
        assert frame["cleanup_memory"]["frees"] == len(seen)
        assert all(not n["fields_valid"] and n["initialized_mask"] == 0 and n["historical_fields"] for n in retired)
    assert len(seen) == count
    assert trace["final_state"]["items"] == []
