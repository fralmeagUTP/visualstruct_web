"""Positive baseline and coordinated corruptions; no extra route cases."""
import json
from pathlib import Path
from copy import deepcopy
import pytest
from _linked_head_insert_memory_oracle import assert_linked_head_insert_memory
FIXTURE = Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-linked-head-insert-consumer-low/positive-fixture.json"
from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize("mutation", [None,"duplicate_heap","duplicate_address","duplicate_pointer","wrong_initial","missing_reserve","unknown_after_call","wrong_value","early_link","early_publication","late_publication","wrong_alias","null_parameter","wrong_parameter","wrong_scope","duplicate_event"])
def test_head_insertion_controls(mutation):
    body = deepcopy(json.loads(audit_input_path(FIXTURE).read_text(encoding="utf-8")))
    steps = body["execution_trace"]["steps"]
    f = steps[2]["pedagogy"]
    if mutation == "duplicate_heap":
        f["heap_objects"].append(deepcopy(f["heap_objects"][-1]));f["heap_transition"]["after"] = deepcopy(f["heap_objects"])
    elif mutation == "duplicate_address":
        f["heap_objects"][-1]["address"] = f["heap_objects"][0]["address"];f["heap_transition"]["after"] = deepcopy(f["heap_objects"])
    elif mutation == "duplicate_pointer": f["pointers"].append(deepcopy(f["pointers"][0]))
    elif mutation == "wrong_initial": steps[0]["state_snapshot"]["items"] = []
    elif mutation == "missing_reserve": f["heap_objects"].pop();f["heap_transition"]["after"] = deepcopy(f["heap_objects"])
    elif mutation == "unknown_after_call": f["heap_objects"][-1]["fields"]["nro"] = "sin inicializar"
    elif mutation == "wrong_value": steps[4]["pedagogy"]["heap_objects"][-1]["fields"]["nro"] = 99
    elif mutation == "early_link": f["heap_objects"][-1]["fields"]["sgte"] = f["heap_objects"][0]["id"]
    elif mutation == "early_publication": steps[4]["pedagogy"]["memory_state"]["head"] = f["heap_objects"][-1]["id"]
    elif mutation == "late_publication": steps[5]["pedagogy"]["memory_state"]["head"] = f["heap_objects"][0]["id"]
    elif mutation == "wrong_alias": f["memory_state"]["q"] = f["heap_objects"][0]["id"]
    elif mutation == "null_parameter":
        f["memory_state"]["lista"] = "NULL";f["call_stack"][0]["parameters"]["lista"] = "NULL";next(p for p in f["pointers"] if p["name"] == "lista")["target"] = "NULL"
    elif mutation == "wrong_parameter": f["call_stack"][0]["parameters"]["valor"] = 99
    elif mutation == "wrong_scope": next(p for p in steps[6]["pedagogy"]["pointers"] if p["name"] == "lista")["target"] = "&cabeza"
    elif mutation == "duplicate_event": steps.insert(3,deepcopy(steps[2]))
    if mutation is None: assert_linked_head_insert_memory(body)
    else:
        with pytest.raises(AssertionError): assert_linked_head_insert_memory(body)

@pytest.mark.parametrize("defect",["items","size","empty","identities","head","heap_link","memory_projection"])
def test_public_projection_corruption_with_next_snapshot_synchronized(defect):
    body=deepcopy(json.loads(audit_input_path(FIXTURE).read_text(encoding="utf-8"))); check=lambda:assert_linked_head_insert_memory(body)
    steps=body["execution_trace"]["steps"]; s=steps[2]
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
