"""Three frozen consumer cases; coordinated memory and boundary corruptions."""
import json
from copy import deepcopy
from pathlib import Path
import pytest
from _tree_intermediate_consumer_oracle import assert_tree_intermediate_consumer
FIXTURE=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-tree-intermediate-consumers-low/positive-fixtures.json"
NAMES={"abb":"test_abb_successor_copy_precedes_successor_unlink","lr":"test_avl_lr_exposes_first_rotation_with_recomputed_metadata","rl":"test_avl_rl_exposes_first_rotation_with_recomputed_metadata"}
def fixture(case):return deepcopy(json.loads(FIXTURE.read_text(encoding="utf-8"))[NAMES[case]])
@pytest.mark.parametrize("case",["abb","lr","rl"])
@pytest.mark.parametrize("mutation",[None,"duplicate_heap","duplicate_cards","invented_retired","wrong_initial","wrong_parameter","wrong_source","early_call_write"])
def test_common_consumer_controls(case,mutation):
    body=fixture(case);steps=body["execution_trace"]["steps"]
    step=next(s for s in steps if s["pedagogy"]["instruction_event"]["phase"]=="call")
    p=step["pedagogy"];m=p["memory_state"]
    if mutation=="duplicate_heap":m["heap_nodes"].append(deepcopy(m["heap_nodes"][0]))
    elif mutation=="duplicate_cards":p["memory"]["objects_after"].append(deepcopy(p["memory"]["objects_after"][0]))
    elif mutation=="invented_retired":
        node=deepcopy(p["memory"]["objects_after"][0]);node.update(id="Fake",address="Fake",freed=True,allocated=False);p["memory"]["objects_after"].append(node)
    elif mutation=="wrong_initial":steps[0]["state_snapshot"]["root"]["value"]=99
    elif mutation=="wrong_parameter":
        frame=next(f for s in steps for f in s["pedagogy"]["memory_state"]["tree_frames"] if f["function"]==("abb_eliminar" if case=="abb" else "avl_insertar"))
        frame["parameters"]["valor" if case=="abb" else "x"]=99
    elif mutation=="wrong_source":step["line_index"]=0
    elif mutation=="early_call_write":
        m["heap_nodes"][0]["value"]=99
        for card in p["memory"]["objects_after"]:
            if card["id"]==m["heap_nodes"][0]["id"]:card["value"]=99
    if mutation is None:assert_tree_intermediate_consumer(body,case)
    else:
        with pytest.raises(AssertionError):assert_tree_intermediate_consumer(body,case)
@pytest.mark.parametrize("case",["abb","lr","rl"])
@pytest.mark.parametrize("mutation",["anchor_child","anchor_metadata","anchor_phase"])
def test_specific_anchor_controls(case,mutation):
    body=fixture(case);steps=body["execution_trace"]["steps"]
    text="nodo->valor = temp->valor;" if case=="abb" else "avl_RSI(r, B);" if case=="lr" else "avl_RSD(r, B);"
    phase="assignment" if case=="abb" else "after"
    anchor=next(s for s in steps if s["line_text"].strip()==text and s["pedagogy"]["instruction_event"]["phase"]==phase)
    if mutation=="anchor_phase":anchor["pedagogy"]["instruction_event"]["phase"]="call"
    elif case=="abb":
        if mutation=="anchor_child":anchor["pedagogy"]["memory_state"]["heap_nodes"][0]["right"]="NULL"
        else:
            released=next(s for s in steps if s["line_text"].strip()=="free(nodo);" and s["pedagogy"]["instruction_event"]["phase"]=="free")
            released["pedagogy"]["memory"]["freed_objects"][0]["id"]="Other"
    else:
        side="left" if case=="lr" else "right"
        if mutation=="anchor_child":anchor["state_after"]["root"][side][side]=None
        else:anchor["state_after"]["root"]["balance_factor"]=0
    with pytest.raises(AssertionError):assert_tree_intermediate_consumer(body,case)


@pytest.mark.parametrize("case",["abb","lr","rl"])
@pytest.mark.parametrize("defect",["value","topology","size","height","memory_projection"])
def test_public_projection_corruption_with_next_snapshot_synchronized(case,defect):
    b=fixture(case);steps=b["execution_trace"]["steps"];s=steps[1];public=s["state_after"]
    if defect in {"value","memory_projection"}:
        public["root"]["value"]=999
        if defect=="memory_projection":s["pedagogy"]["memory_state"]["root"]["value"]=999
    elif defect=="topology":public["root"]["left" if case!="rl" else "right"]=None
    else:public[defect]=999
    steps[2]["state_snapshot"]=deepcopy(public)
    with pytest.raises(AssertionError):assert_tree_intermediate_consumer(b,case)
