"""Focal projection and coordinated corruptions; no extra native algorithm runs."""
import json
from pathlib import Path
from copy import deepcopy
import pytest
from _priority_front_candidate_oracle import assert_priority_front_candidate
FIXTURE = Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-priority-front-candidate-delta-low/positive-fixture.json"
@pytest.mark.parametrize("mutation", [None,"early","late","wrong_alias","duplicate_heap","duplicate_pointer","wrong_initial","uninitialized_parameter","invalid_parameter","wrong_parameter","early_output"])
def test_candidate_controls(mutation):
    body = deepcopy(json.loads(FIXTURE.read_text(encoding="utf-8")))
    steps = body["execution_trace"]["steps"]
    m = steps[8]["pedagogy"]["front_memory"]
    if mutation == "early": steps[8]["state_after"]["out_index"] = 2
    elif mutation == "late": steps[8]["state_after"]["out_index"] = 0
    elif mutation == "wrong_alias": next(p for p in m["pointers"] if p["name"] == "objetivo")["target"] = "N3"
    elif mutation == "duplicate_heap":
        m["heap"].append(deepcopy(m["heap"][1])); steps[8]["pedagogy"]["heap_objects"] = deepcopy(m["heap"])
    elif mutation == "duplicate_pointer": m["pointers"].append(deepcopy(m["pointers"][0]))
    elif mutation == "wrong_initial": steps[0]["state_snapshot"]["items"] = []
    elif mutation in {"uninitialized_parameter","invalid_parameter","wrong_parameter"}:
        p = next(p for p in steps[0]["pedagogy"]["front_memory"]["pointers"] if p["name"] == "valor")
        p[{"uninitialized_parameter":"initialized","invalid_parameter":"valid","wrong_parameter":"target"}[mutation]] = "NULL" if mutation == "wrong_parameter" else False
    elif mutation == "early_output": m["outputs"]["value_written"] = True
    if mutation is None: assert_priority_front_candidate(body)
    else:
        with pytest.raises(AssertionError): assert_priority_front_candidate(body)
