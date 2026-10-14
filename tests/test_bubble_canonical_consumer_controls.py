"""Pure adversarial controls for three original Bubble canonical fixtures."""
from copy import deepcopy
from pathlib import Path
import json
import pytest
from _bubble_canonical_consumer_oracle import assert_bubble_canonical_consumer
P=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-bubble-canonical-consumers-low/positive-fixtures.json"
CASES={"golden":("tests/test_execution_trace_golden.py::test_sorting_trace_golden",[3,1,2]),"phase8":("tests/test_phase8_visual_integration.py::test_all_13_tads_frames_are_source_mapped_continuous_and_causal[sorting]",[3,1,2,1]),"helpers":("tests/test_sorting_module_detailed_qa.py::test_trace_enters_validation_and_swap_helpers_with_real_transient_state",[2,1])}
from scripts.published_test_inputs import audit_input_path
def body(case):return deepcopy(json.loads(audit_input_path(P).read_text(encoding="utf-8"))[CASES[case][0]])
def step(b,token):return next(s for s in b["execution_trace"]["steps"] if s["pedagogy"]["source"]["line_token"]==token)
@pytest.mark.parametrize("case",tuple(CASES))
def test_frozen_original_causal_trace(case):assert_bubble_canonical_consumer(body(case),CASES[case][1])
@pytest.mark.parametrize("case",tuple(CASES))
@pytest.mark.parametrize("defect",("initial_mutation","unmapped_real","wrong_source","flipped_condition","lost_comparison","wrong_flag","early_array","bad_partial","wrong_temp","duplicate_variable","future_temp","wrong_pointer","wrong_parameter","stale_local","wrong_final"))
def test_rejects_bubble_causal_defect(case,defect):
    b=body(case);t=b["execution_trace"];first=t["steps"][0]
    if defect=="initial_mutation":first["state_after"]["items"]=sorted(CASES[case][1])
    elif defect=="unmapped_real":s=step(b,"swap_temp");s["line_index"]=s["pedagogy"]["source"]["line_index"]=None;s["line_text"]=s["pedagogy"]["source"]["line_text"]=""
    elif defect=="wrong_source":t["source_code"]+="\n/* fabricated */"
    elif defect=="flipped_condition":step(b,"compare")["pedagogy"]["condition"]["result"]=False
    elif defect=="lost_comparison":step(b,"compare")["state_after"]["metrics"]["comparisons"]=0
    elif defect=="wrong_flag":step(b,"swap_call")["debug"]["instruction_event"]["hubo_intercambio"]=1
    elif defect=="early_array":step(b,"swap_call")["state_after"]["items"]=sorted(CASES[case][1])
    elif defect=="bad_partial":step(b,"swap_assign_a")["state_after"]["items"]=step(b,"swap_assign_b")["state_after"]["items"][:]
    elif defect=="wrong_temp":step(b,"swap_temp")["state_after"]["temporaries"]["temporal"]=999
    elif defect=="duplicate_variable":s=step(b,"swap_temp");s["pedagogy"]["variables"].append(deepcopy(s["pedagogy"]["variables"][-1]))
    elif defect=="future_temp":step(b,"swap_entry")["pedagogy"]["variables"].append({"scope":"intercambiar","name":"temporal","value":999,"initialized":True})
    elif defect=="wrong_pointer":step(b,"swap_entry")["pedagogy"]["pointers"][0]["target"]="arreglo[99]"
    elif defect=="wrong_parameter":step(b,"swap_entry")["pedagogy"]["call_stack"][-1]["parameters"]["a"]="arreglo[99]"
    elif defect=="stale_local":step(b,"swap_return")["pedagogy"]["variables"].append({"scope":"intercambiar","name":"temporal","value":999,"initialized":True})
    else:b["visual_state"]["items"]=[999]*len(CASES[case][1])
    with pytest.raises(AssertionError):assert_bubble_canonical_consumer(b,CASES[case][1])
