"""Baseline positive and coordinated duplicate-valued identity corruption controls."""
import json
from copy import deepcopy
from pathlib import Path
import pytest
from _circular_delete_memory_oracle import assert_circular_delete_memory
FIXTURE=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-circular-delete-consumer-low/positive-fixture.json"
from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize("mutation", [None,"duplicate_heap","duplicate_address","duplicate_pointer","wrong_initial","early_root","late_root","wrong_bypass","early_free","wrong_freed_identity","duplicate_retired","missing_free","usable_freed_alias","early_count","late_count","null_parameter","wrong_value_parameter","wrong_source_branch"])
def test_first_match_controls(mutation):
    body=deepcopy(json.loads(audit_input_path(FIXTURE).read_text(encoding="utf-8")))
    steps=body["execution_trace"]["steps"];f=steps[9]["pedagogy"];first,middle,last=[n["id"] for n in f["heap_objects"]]
    if mutation=="duplicate_heap":
        f["heap_objects"].append(deepcopy(f["heap_objects"][0]));f["heap_transition"]["after"]=deepcopy(f["heap_objects"])
    elif mutation=="duplicate_address":f["heap_objects"][-1]["address"]=f["heap_objects"][0]["address"]
    elif mutation=="duplicate_pointer":f["pointers"].append(deepcopy(f["pointers"][0]))
    elif mutation=="wrong_initial":steps[0]["state_snapshot"]["items"]=[{"value":7},{"value":4}]
    elif mutation=="early_root":f["memory_state"]["cabeza"]=middle
    elif mutation=="late_root":steps[11]["pedagogy"]["memory_state"]["cabeza"]=first
    elif mutation=="wrong_bypass":f["heap_objects"][-1]["fields"]["sgte"]=first
    elif mutation=="early_free":f["heap_objects"].pop(0);f["heap_transition"]["after"]=deepcopy(f["heap_objects"])
    elif mutation=="wrong_freed_identity":steps[15]["pedagogy"]["heap_transition"]["freed"][0]["id"]=last
    elif mutation=="duplicate_retired":steps[15]["pedagogy"]["heap_transition"]["freed"]*=2
    elif mutation=="missing_free":steps[15]["pedagogy"]["heap_transition"]["freed"]=[]
    elif mutation=="usable_freed_alias":steps[15]["pedagogy"]["memory_state"]["actual"]=first
    elif mutation=="early_count":f["memory_state"]["cantidad"]=2
    elif mutation=="late_count":steps[14]["pedagogy"]["memory_state"]["cantidad"]=3
    elif mutation=="null_parameter":
        f["memory_state"]["lista"]="NULL";f["call_stack"][0]["parameters"]["lista"]="NULL";next(p for p in f["pointers"] if p["name"]=="lista")["target"]="NULL"
    elif mutation=="wrong_value_parameter":f["call_stack"][0]["parameters"]["valor"]=4
    elif mutation=="wrong_source_branch":
        source=body["execution_trace"]["source_code"].splitlines();steps[15]["line_index"]=next(i for i,l in enumerate(source) if l.strip()=="free(actual);")
    if mutation is None:assert_circular_delete_memory(body)
    else:
        with pytest.raises(AssertionError):assert_circular_delete_memory(body)

@pytest.mark.parametrize("defect",["items","size","empty","identities","head","heap_link","memory_projection"])
def test_public_projection_corruption_with_next_snapshot_synchronized(defect):
    body=deepcopy(json.loads(audit_input_path(FIXTURE).read_text(encoding="utf-8"))); check=lambda:assert_circular_delete_memory(body)
    steps=body["execution_trace"]["steps"]; s=steps[5]
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
