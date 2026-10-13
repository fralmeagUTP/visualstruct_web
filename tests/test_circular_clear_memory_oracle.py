"""Fixed baseline positive and coordinated lifetime/store corruptions."""
import json
from copy import deepcopy
from pathlib import Path
import pytest
from _circular_clear_memory_oracle import assert_circular_clear_memory
FIXTURE=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-circular-clear-consumer-low/positive-fixture.json"
@pytest.mark.parametrize("mutation",[None,"duplicate_heap","duplicate_address","duplicate_pointer","wrong_initial","early_detach","missing_tail_store","early_root","early_count","missing_count","premature_free","wrong_free_id","duplicate_freed","missing_free","live_freed_alias","invalid_next","null_parameter","wrong_source_branch","last_root_early"])
def test_destructor_controls(mutation):
    body=deepcopy(json.loads(FIXTURE.read_text(encoding="utf-8")))
    steps=body["execution_trace"]["steps"];f=steps[8]["pedagogy"];ids=[n["id"] for n in f["heap_objects"]]
    if mutation=="duplicate_heap":f["heap_objects"].append(deepcopy(f["heap_objects"][0]));f["heap_transition"]["after"]=deepcopy(f["heap_objects"])
    elif mutation=="duplicate_address":f["heap_objects"][-1]["address"]=f["heap_objects"][0]["address"]
    elif mutation=="duplicate_pointer":f["pointers"].append(deepcopy(f["pointers"][0]))
    elif mutation=="wrong_initial":steps[0]["state_snapshot"]["size"]=2
    elif mutation=="early_detach":f["memory_state"]["items"].pop()
    elif mutation=="missing_tail_store":steps[9]["pedagogy"]["heap_objects"][-1]["fields"]["sgte"]=ids[0]
    elif mutation=="early_root":steps[7]["pedagogy"]["memory_state"]["cabeza"]=ids[1]
    elif mutation=="early_count":f["memory_state"]["cantidad"]=2
    elif mutation=="missing_count":steps[11]["pedagogy"]["memory_state"]["cantidad"]=3
    elif mutation=="premature_free":f["heap_objects"].pop(0);f["heap_transition"]["after"]=deepcopy(f["heap_objects"])
    elif mutation=="wrong_free_id":steps[12]["pedagogy"]["heap_transition"]["freed"][0]["id"]=ids[1]
    elif mutation=="duplicate_freed":steps[12]["pedagogy"]["heap_transition"]["freed"]*=2
    elif mutation=="missing_free":steps[20]["pedagogy"]["heap_transition"]["freed"]=[]
    elif mutation=="live_freed_alias":steps[12]["pedagogy"]["memory_state"]["actual"]=ids[0]
    elif mutation=="invalid_next":steps[13]["pedagogy"]["memory_state"]["actual"]=ids[0]
    elif mutation=="null_parameter":f["memory_state"]["lista"]="NULL";f["call_stack"][0]["parameters"]["lista"]="NULL";next(p for p in f["pointers"] if p["name"]=="lista")["target"]="NULL"
    elif mutation=="wrong_source_branch":
        source=body["execution_trace"]["source_code"].splitlines();steps[26]["line_index"]=next(i for i,l in enumerate(source) if l.strip()=="free(actual);")
    elif mutation=="last_root_early":steps[22]["pedagogy"]["memory_state"]["cabeza"]="NULL"
    if mutation is None:assert_circular_clear_memory(body)
    else:
        with pytest.raises(AssertionError):assert_circular_clear_memory(body)

@pytest.mark.parametrize("defect",["items","size","empty","identities","head","heap_link","memory_projection"])
def test_public_projection_corruption_with_next_snapshot_synchronized(defect):
    body=deepcopy(json.loads(FIXTURE.read_text(encoding="utf-8"))); check=lambda:assert_circular_clear_memory(body)
    steps=body["execution_trace"]["steps"]; s=steps[7]
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
