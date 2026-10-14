from pathlib import Path
from copy import deepcopy
import json,pytest
from _stack_push_memory_oracle import assert_empty_stack_push_memory
from _phase8_duplicate_memory_consumer_oracle import assert_duplicate_sublist,assert_duplicate_mergesort,assert_duplicate_RN
from _rbt_legacy_consumer_oracle import assert_rbt_consumer
ROOT=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-phase8-duplicates-consumer-low"
FILES={"stack":"duplicates-final-1-call-1-stack-apilar-service.json","sublist":"duplicates-final-1-call-5-sublist-insertar_padre-service.json","mergesort":"duplicates-final-1-call-9-sorting_array-run-service.json","RN":"duplicates-final-1-call-12-red_black-insertar-service.json"}
from scripts.published_test_inputs import audit_input_path
def load(case):return json.loads((audit_input_path(ROOT/FILES[case])).read_text(encoding="utf-8"))
def check(case,body):
    if case=="stack":assert_empty_stack_push_memory(body,7)
    elif case=="sublist":assert_duplicate_sublist(body)
    elif case=="mergesort":assert_duplicate_mergesort(body)
    else:assert_duplicate_RN(body)
@pytest.mark.parametrize("case",FILES)
def test_original_case_positive(case):check(case,load(case))
@pytest.mark.parametrize("fault",["alias","mask","early_publication","source"])
def test_stack_coordinated_rejections(fault):
    b=load("stack");s=b["execution_trace"]["steps"]
    if fault=="alias":s[8]["pedagogy"]["push_memory"]["aux"]["value"]=None
    elif fault=="mask":
        for node in s[6]["pedagogy"]["push_memory"]["heap"]:node["initialized_mask"]=3
        s[6]["pedagogy"]["heap_objects"]=deepcopy(s[6]["pedagogy"]["push_memory"]["heap"])
    elif fault=="early_publication":s[7]["pedagogy"]["push_memory"]["root"]["value"]=s[8]["pedagogy"]["push_memory"]["root"]["value"]
    else:s[6]["line_index"]=s[7]["line_index"]
    with pytest.raises(AssertionError):check("stack",b)
@pytest.mark.parametrize("fault",["merge_ids","early_value","early_link","alias","returned","duplicate_UI_id"])
def test_sublist_coordinated_rejections(fault):
    b=load("sublist");steps=b["execution_trace"]["steps"];s=steps[8 if fault=="early_value" else 16]
    if fault=="merge_ids":s["pedagogy"]["memory_state"]["heap_nodes"][1]["id"]="P1"
    elif fault=="early_value":s["pedagogy"]["memory_state"]["heap_nodes"][1]["sub"]="NULL"
    elif fault=="early_link":s["pedagogy"]["memory_state"]["heap_nodes"][0]["next"]="P2"
    elif fault=="alias":s["pedagogy"]["memory_state"]["sublist_frames"][0]["locals"]["nuevo"]="P1"
    elif fault=="returned":steps[18]["pedagogy"]["memory_state"]["returned"]="P1"
    else:b["visual_state"]["items"][1]["id"]=b["visual_state"]["items"][0]["id"]
    for step in steps:step["state_after"]=deepcopy(step["pedagogy"]["memory_state"])
    with pytest.raises(AssertionError):check("sublist",b)
@pytest.mark.parametrize("fault",["aux_value","item_copy","allocation","free","alias","source"])
def test_mergesort_coordinated_rejections(fault):
    b=load("mergesort");steps=b["execution_trace"]["steps"]
    if fault=="aux_value":s=next(s for s in steps if s["pedagogy"]["source"]["line_token"]=="aux_right_write");s["state_after"]["auxiliary_array"][0]=3
    elif fault=="item_copy":s=next(s for s in steps if s["pedagogy"]["source"]["line_token"]=="copy_write");s["state_after"]["items"][0]=3
    elif fault=="allocation":steps[9]["state_after"]["merge_context"]["allocations"]=2
    elif fault=="free":steps[145]["state_after"]["merge_context"]["frees"]=0
    elif fault=="alias":next(p for p in steps[33]["pedagogy"]["pointers"] if p["scope"]!="ordenar_mergesort" and p["name"]=="auxiliar")["target"]="another reservation"
    else:steps[9]["line_index"]=None
    with pytest.raises(AssertionError):check("mergesort",b)
@pytest.mark.parametrize("fault",["color","link","alias"])
def test_RN_coordinated_rejections(fault):
    b=load("RN");steps=b["execution_trace"]["steps"]
    s=next(s for s in steps if s["line_text"].strip()=="B->der = A;" and s["pedagogy"]["instruction_event"]["phase"]=="link")
    state=s["pedagogy"]["memory_state"]
    if fault=="alias":state["tree_frames"][-1]["parameters"]["r"]="&another_root"
    else:
        field="color" if fault=="color" else "right";value="RED" if fault=="color" else "NULL"
        node=next(n for n in state["heap_nodes"] if n["id"]=="N2");node[field]=value
        card=next(n for n in s["pedagogy"]["memory"]["objects_after"] if n["id"]=="N2");card[field]=value
    with pytest.raises(AssertionError):check("RN",b)

def test_legitimate_consistent_symbolic_identity_rename():
    b=load("sublist")
    substitutions={"P1":"X1","P2":"X2","0xP1":"0xX1","0xP2":"0xX2","parent-1":"father-A","parent-2":"father-B"}
    def rename(x):
        if isinstance(x,dict):return {substitutions.get(k,k):rename(v) for k,v in x.items()}
        if isinstance(x,list):return [rename(v) for v in x]
        if isinstance(x,str):return substitutions.get(x,x)
        return x
    check("sublist",rename(b))


@pytest.mark.parametrize("defect",["value","topology","color","size","height","memory_projection"])
def test_RN_wrapper_public_projection_corruption_with_next_snapshot_synchronized(defect):
    b=load("RN");steps=b["execution_trace"]["steps"];s=steps[1];public=s["state_after"]
    if defect in {"value","memory_projection"}:
        public["root"]["value"]=999
        if defect=="memory_projection":s["pedagogy"]["memory_state"]["root"]["value"]=999
    elif defect=="topology":public["root"]["left"]=None
    elif defect=="color":public["root"]["color"]="RED"
    else:public[defect]=999
    steps[2]["state_snapshot"]=deepcopy(public)
    with pytest.raises(AssertionError):check("RN",b)
