"""Corrupt the two existing values against the unchanged accepted memory contract."""
import json
from copy import deepcopy
from pathlib import Path
import pytest
from _stack_push_memory_oracle import assert_empty_stack_push_memory
FIXTURE=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-stack-canonical-golden-consumers-low/positive-fixtures.json"
from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize("value",[7,42])
@pytest.mark.parametrize("mutation",[None,"seven_frames","swapped_malloc_phases","duplicate_heap","missing_reservation","wrong_initial","uninitialized_parameter","invalid_parameter","wrong_parameter","wrong_scope","early_value","early_link","early_root","wrong_value"])
def test_consumer_contract_controls(value,mutation):
    body=deepcopy(json.loads(audit_input_path(FIXTURE).read_text(encoding="utf-8"))[str(value)])
    steps=body["execution_trace"]["steps"]
    if mutation=="seven_frames":body["execution_trace"]["steps"]=[steps[i] for i in [0,1,4,5,6,7,8]]
    elif mutation=="swapped_malloc_phases":steps[2]["event_type"],steps[3]["event_type"]=steps[3]["event_type"],steps[2]["event_type"]
    elif mutation in {"duplicate_heap","missing_reservation"}:
        heap=steps[3]["pedagogy"]["push_memory"]["heap"]
        if mutation=="duplicate_heap":heap.append(deepcopy(heap[0]))
        else:heap.clear()
        steps[3]["pedagogy"]["heap_objects"]=deepcopy(heap);steps[3]["pedagogy"]["heap_transition"]["after"]=deepcopy(heap)
    elif mutation=="wrong_initial":steps[0]["state_snapshot"]["items"]=[{"value":value}]
    elif mutation in {"uninitialized_parameter","invalid_parameter","wrong_parameter","wrong_scope"}:
        f=steps[0]["pedagogy"]
        variable=next(v for v in f["variables"] if v["name"]=="valor")
        key={"uninitialized_parameter":"initialized","invalid_parameter":"valid","wrong_parameter":"value","wrong_scope":"scope_state"}[mutation]
        variable[key]="ended" if mutation=="wrong_scope" else 99 if mutation=="wrong_parameter" else False
        f["push_memory"]["variables"]=deepcopy(f["variables"])
        f["scopes"][0]["variables"]=[deepcopy(v) for v in f["variables"] if v["scope"]=="pila_apilar"]
    elif mutation=="early_value":steps[3]["pedagogy"]["push_memory"]["heap"][0]["fields"]["nro"]=value
    elif mutation=="early_link":steps[6]["pedagogy"]["push_memory"]["heap"][0]["initialized_mask"]=3
    elif mutation=="early_root":steps[7]["pedagogy"]["push_memory"]["root"]["value"]=steps[7]["pedagogy"]["push_memory"]["heap"][0]["id"]
    elif mutation=="wrong_value":steps[6]["pedagogy"]["push_memory"]["heap"][0]["fields"]["nro"]=99
    if mutation is None:assert_empty_stack_push_memory(body,value)
    else:
        with pytest.raises(AssertionError):assert_empty_stack_push_memory(body,value)
