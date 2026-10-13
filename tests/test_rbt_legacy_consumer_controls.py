"""Pure adversarial controls of the three frozen original RN responses."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from _rbt_legacy_consumer_oracle import assert_rbt_consumer
P=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-rbt-legacy-consumers-low/positive-fixtures.json"
CASES=("rotation","delete_int","delete_text")

def body(case):return deepcopy(json.loads(P.read_text(encoding="utf-8"))[case])

def step(b,text,phase):
    return next(s for s in b["execution_trace"]["steps"] if s["line_text"].strip()==text and s["pedagogy"]["instruction_event"]["phase"]==phase)

@pytest.mark.parametrize("case",CASES)
def test_frozen_original_response(case):assert_rbt_consumer(body(case),case)

@pytest.mark.parametrize("case",CASES)
@pytest.mark.parametrize("defect",("heap_duplicate","card_duplicate","invented_retired","wrong_seed","wrong_payload","wrong_scope","wrong_source","fabricated_allocation"))
def test_rejects_common_memory_source_contract_defect(case,defect):
    b=body(case);ss=b["execution_trace"]["steps"];s=ss[0]
    if defect=="heap_duplicate":s["state_snapshot"]["heap_nodes"].append(deepcopy(s["state_snapshot"]["heap_nodes"][0]))
    elif defect=="card_duplicate":s["pedagogy"]["memory"]["objects_after"].append(deepcopy(s["pedagogy"]["memory"]["objects_after"][0]))
    elif defect=="invented_retired":
        c=deepcopy(s["pedagogy"]["memory"]["objects_after"][0]);c.update(id="N999",address="N999",freed=True,allocated=False);s["pedagogy"]["memory"]["objects_after"].append(c)
    elif defect=="wrong_seed":s["state_snapshot"]["heap_nodes"][0]["value"]=999
    elif defect=="wrong_payload":b["execution_trace"]["payload"]={"value":999}
    elif defect=="wrong_scope":ss[1]["pedagogy"]["memory_state"]["tree_frames"][0]["parameters"]["arbol"]="&other"
    elif defect=="wrong_source":b["execution_trace"]["source_code"]+="\n/* fabricated */"
    else:s["pedagogy"]["memory"]["allocated_objects"]=[{"id":"N999"}]
    with pytest.raises(AssertionError):assert_rbt_consumer(b,case)

@pytest.mark.parametrize("defect",("early_root","missing_completed_child","wrong_parent","wrong_phase","early_free"))
def test_rejects_rotation_defect(defect):
    b=body("rotation")
    if defect=="early_root":s=step(b,"rbt_rotar_dcha(arbol, a);","call");s["pedagogy"]["memory_state"]["head"]="N2"
    elif defect=="missing_completed_child":step(b,"rbt_rotar_dcha(arbol, a);","resume")["state_after"]["root"]["right"]=None
    elif defect=="wrong_parent":step(b,"B->padre = padre;","link")["pedagogy"]["memory_state"]["heap_nodes"][1]["parent"]="N1"
    elif defect=="wrong_phase":step(b,"rbt_rotar_dcha(arbol, a);","resume")["pedagogy"]["instruction_event"]["phase"]="call"
    else:step(b,"*r = B;","link")["pedagogy"]["memory_state"]["heap_nodes"].pop(0)
    with pytest.raises(AssertionError):assert_rbt_consumer(b,"rotation")

@pytest.mark.parametrize("case",("delete_int","delete_text"))
@pytest.mark.parametrize("defect",("wrong_loop_condition","future_reachability","wrong_freed_identity","stale_live_alias","future_sibling","wrong_fix_parameter"))
def test_rejects_delete_defect(case,defect):
    b=body(case)
    if defect=="wrong_loop_condition":step(b,"while (z != NULL && z->nro != key) {","condition")["pedagogy"]["instruction_event"]["condition"]=False
    elif defect=="future_reachability":step(b,"u->padre->izq = v;","link")["state_after"]["size"]=8
    elif defect=="wrong_freed_identity":step(b,"free(z);","free")["pedagogy"]["memory"]["freed_objects"][0]["id"]="N1"
    elif defect=="stale_live_alias":step(b,"arreglarEliminacion(arbol, x, x_parent);","call")["pedagogy"]["memory_state"]["tree_frames"][0]["locals"]["z"]="N2"
    elif defect=="future_sibling":step(b,"static void arreglarEliminacion(RBT *root, RBT x, RBT x_parent) {","enter")["pedagogy"]["memory_state"]["tree_frames"][-1]["locals"]["w"]="N3"
    else:step(b,"static void arreglarEliminacion(RBT *root, RBT x, RBT x_parent) {","enter")["pedagogy"]["memory_state"]["tree_frames"][-1]["parameters"]["x_parent"]="N3"
    with pytest.raises(AssertionError):assert_rbt_consumer(b,case)


@pytest.mark.parametrize("case",CASES)
@pytest.mark.parametrize("defect",["value","topology","color","size","height","memory_projection"])
def test_public_projection_corruption_with_next_snapshot_synchronized(case,defect):
    b=body(case);steps=b["execution_trace"]["steps"];s=steps[1];public=s["state_after"]
    if defect in {"value","memory_projection"}:
        public["root"]["value"]=999
        if defect=="memory_projection":s["pedagogy"]["memory_state"]["root"]["value"]=999
    elif defect=="topology":public["root"]["left"]=None
    elif defect=="color":public["root"]["color"]="RED"
    else:public[defect]=999
    steps[2]["state_snapshot"]=deepcopy(public)
    with pytest.raises(AssertionError):assert_rbt_consumer(b,case)
