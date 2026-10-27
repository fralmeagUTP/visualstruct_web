"""Corruption controls for the two calls already present in one historical ID."""
import json
from pathlib import Path
from copy import deepcopy
import pytest
from _circular_insert_memory_oracle import assert_circular_insert_memory
FIXTURE = Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-circular-insert-consumer-low/positive-fixtures.json"
from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize("case", [0,1])
@pytest.mark.parametrize("mutation", [None,"duplicate_heap","duplicate_address","duplicate_pointer","wrong_initial","initialized_early","wrong_value","early_alias","null_parameter","wrong_constructor_parameter","early_publication","early_quantity","wrong_branch_index"])
def test_insertion_controls(case, mutation):
    body = deepcopy(json.loads(audit_input_path(FIXTURE).read_text(encoding="utf-8"))[case])
    steps = body["execution_trace"]["steps"]
    f = steps[4]["pedagogy"]
    if mutation == "duplicate_heap":
        f["heap_objects"].append(deepcopy(f["heap_objects"][-1]));f["heap_transition"]["after"] = deepcopy(f["heap_objects"])
    elif mutation == "duplicate_address":
        if case: f["heap_objects"][-1]["address"] = f["heap_objects"][0]["address"]
        else: f["heap_objects"].append(deepcopy(f["heap_objects"][0]))
        f["heap_transition"]["after"] = deepcopy(f["heap_objects"])
    elif mutation == "duplicate_pointer": f["pointers"].append(deepcopy(f["pointers"][0]))
    elif mutation == "wrong_initial": steps[0]["state_snapshot"]["size"] = 99
    elif mutation == "initialized_early": f["heap_objects"][-1]["fields"]["valor"] = 4 if not case else 9
    elif mutation == "wrong_value": steps[6]["pedagogy"]["heap_objects"][-1]["fields"]["valor"] = 99
    elif mutation == "early_alias": steps[8]["pedagogy"]["memory_state"]["nuevo"] = "N1" if not case else "N2"
    elif mutation == "null_parameter":
        f["memory_state"]["lista"] = "NULL";f["call_stack"][0]["parameters"]["lista"] = "NULL"
        next(p for p in f["pointers"] if p["name"] == "lista")["target"] = "NULL"
    elif mutation == "wrong_constructor_parameter": steps[3]["pedagogy"]["call_stack"][1]["parameters"]["valor"] = 99
    elif mutation == "early_publication": steps[12]["pedagogy"]["memory_state"]["items"].append({"value":4 if not case else 9})
    elif mutation == "early_quantity": steps[13]["pedagogy"]["memory_state"]["cantidad"] = 1 if not case else 2
    elif mutation == "wrong_branch_index":
        source = body["execution_trace"]["source_code"].splitlines()
        matches = [i for i,l in enumerate(source) if l.strip() == "lista->cola = nuevo;"]
        steps[14]["line_index"] = matches[-1] if not case else matches[0]
    if mutation is None: assert_circular_insert_memory(body, [] if not case else [4], 4 if not case else 9)
    else:
        with pytest.raises(AssertionError): assert_circular_insert_memory(body, [] if not case else [4], 4 if not case else 9)

@pytest.mark.parametrize("case",[0,1])
@pytest.mark.parametrize("defect",["items","size","empty","identities","head","heap_link","memory_projection"])
def test_public_projection_corruption_with_next_snapshot_synchronized(case, defect):
    body=deepcopy(json.loads(audit_input_path(FIXTURE).read_text(encoding="utf-8"))[case]); check=lambda:assert_circular_insert_memory(body, [] if not case else [4], 4 if not case else 9)
    steps=body["execution_trace"]["steps"]; s=steps[6]
    public=s["state_after"]
    if defect in {"items","memory_projection"}:
        public["items"]=[{"value":999}]
        if defect=="memory_projection":s["pedagogy"]["memory_state"]["items"]=[{"value":999}]
    elif defect=="size":public["size"]=999
    elif defect=="empty":public["empty"]=not public["empty"]
    elif defect=="head":public["cabeza" if "cabeza" in public else "head"]="Invented"
    elif defect=="heap_link":
        if public["heap_nodes"]:public["heap_nodes"][0]["next"]="Invented"
        else:public["heap_nodes"]=[{"id":"Invented","value":999,"next":"NULL","status":"linked"}]
    else:public["node_ids"]=["Invented"]
    steps[s["step_index"]+1]["state_snapshot"]=deepcopy(public)
    with pytest.raises(AssertionError):check()
