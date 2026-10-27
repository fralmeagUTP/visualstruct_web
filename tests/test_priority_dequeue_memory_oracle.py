"""Mutation controls for detached-object lifetime, no extra app cases."""
import json
from copy import deepcopy
from pathlib import Path
import pytest
from _priority_dequeue_memory_oracle import assert_priority_dequeue_lifetime
FIXTURE = Path(__file__).resolve().parents[1] / "openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-priority-dequeue-memory-consumer-low/positive-fixture.json"
from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize("mutation", [None, "missing", "early_free", "wrong_value", "wrong_alias", "invalid_alias", "bad_link", "wrong_output", "resurrect", "wrong_retired", "live_fields", "duplicate_retired"])
def test_lifetime_controls(mutation):
    body = deepcopy(json.loads(audit_input_path(FIXTURE).read_text(encoding="utf-8")))
    steps = body["execution_trace"]["steps"]
    unlink = next(s for s in steps if s["line_text"].strip() == "objetivoPrev->sgte = objetivo->sgte;")
    release = next(s for s in steps if s["line_text"].strip() == "free(objetivo);")
    m = unlink["pedagogy"]["dequeue_memory"]
    node = next(n for n in m["heap"] if n["fields"]["valor"] == 20)
    pointer = next(p for p in m["pointers"] if p["name"] == "objetivo")
    retired = release["pedagogy"]["dequeue_memory"]["retired"]
    if mutation == "missing": m["heap"].remove(node)
    elif mutation == "early_free": node["alive"] = False
    elif mutation == "wrong_value": node["fields"]["valor"] = 30
    elif mutation == "wrong_alias": pointer["target"] = "other"
    elif mutation == "invalid_alias": pointer["valid"] = False
    elif mutation == "bad_link": next(n for n in m["heap"] if n["fields"]["valor"] == 10)["fields"]["sgte"] = node["id"]
    elif mutation == "wrong_output": m["outputs"]["value_written"] = True
    elif mutation == "resurrect": release["pedagogy"]["dequeue_memory"]["heap"].append(node)
    elif mutation == "wrong_retired": retired[0]["id"] = "other"
    elif mutation == "live_fields": retired[0]["fields"] = retired[0]["historical_fields"]
    elif mutation == "duplicate_retired": retired.append(deepcopy(retired[0]))
    if mutation is None: assert_priority_dequeue_lifetime(body)
    else:
        with pytest.raises(AssertionError): assert_priority_dequeue_lifetime(body)

@pytest.mark.parametrize("line", ["objetivoPrev->sgte = objetivo->sgte;", "*valor = objetivo->valor;", "*prioridad = objetivo->prioridad;"])
def test_coordinated_duplicate_live_card_is_rejected(line):
    body = deepcopy(json.loads(audit_input_path(FIXTURE).read_text(encoding="utf-8")))
    step = next(s for s in body["execution_trace"]["steps"] if s["line_text"].strip() == line)
    heap = step["pedagogy"]["dequeue_memory"]["heap"]
    heap.append(deepcopy(next(n for n in heap if n["fields"]["valor"] == 20)))
    step["pedagogy"]["heap_objects"] = deepcopy(heap)
    step["pedagogy"]["heap_transition"]["after"] = deepcopy(heap)
    with pytest.raises(AssertionError):
        assert_priority_dequeue_lifetime(body)
