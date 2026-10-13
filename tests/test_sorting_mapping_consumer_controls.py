"""Pure boundary controls of the original mixed six-value Merge/Bin traces."""
from copy import deepcopy
from pathlib import Path
import json
import pytest
from _sorting_source_oracle import assert_sorting_source_trace
P=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-mapping-consumers-low/positive-fixtures.json"
VALUES=[5,-1,4,2,2,0]

def trace(algorithm):
    caps=json.loads(P.read_text(encoding="utf-8"));key="tests/test_phase7_trace_contract_remediation.py::test_merge_and_bin_frames_all_map_to_real_c_lines["+algorithm+"]"
    return deepcopy(caps[key][0])

@pytest.mark.parametrize("algorithm",("mergesort","binsort"))
def test_original_frozen_trace_boundary(algorithm):assert_sorting_source_trace(trace(algorithm),VALUES)

@pytest.mark.parametrize("algorithm",("mergesort","binsort"))
@pytest.mark.parametrize("defect",("unmapped_instruction","wrong_text","out_of_range","extra_initial","active_initial","variables_initial","pointers_initial","condition_initial","mutated_initial","counter_initial","function_initial","token_initial","concept_initial","index_initial","function_missing"))
def test_rejects_forged_boundary_or_unmapped_native_event(algorithm,defect):
    t=trace(algorithm);first=t["steps"][0];s=t["steps"][1];p=first["pedagogy"]
    if defect=="unmapped_instruction":s["line_index"]=s["pedagogy"]["source"]["line_index"]=None;s["line_text"]=s["pedagogy"]["source"]["line_text"]=""
    elif defect=="wrong_text":s["line_text"]=s["pedagogy"]["source"]["line_text"]="fabricated();"
    elif defect=="out_of_range":s["line_index"]=s["pedagogy"]["source"]["line_index"]=len(t["source_code"].splitlines())+1
    elif defect=="extra_initial":x=deepcopy(first);x["step_index"]=len(t["steps"]);t["steps"].append(x)
    elif defect=="active_initial":p["call_stack"]=[{"function":"ordenar_"+algorithm}]
    elif defect=="variables_initial":p["variables"]=[{"name":"future"}]
    elif defect=="pointers_initial":p["pointers"]=[{"name":"future"}]
    elif defect=="condition_initial":p["condition"]={"result":True}
    elif defect=="mutated_initial":first["state_after"]["items"]=sorted(VALUES)
    elif defect=="counter_initial":first["state_after"]["metrics"]["moves"]=1
    elif defect=="function_initial":p["source"]["function"]="ordenar_"+algorithm
    elif defect=="token_initial":p["source"]["line_token"]="enter"
    elif defect=="concept_initial":p["concept"]="assignment"
    elif defect=="index_initial":first["line_index"]=p["source"]["line_index"]=s["line_index"]
    else:s["pedagogy"]["source"]["function"]=None
    with pytest.raises(AssertionError):assert_sorting_source_trace(t,VALUES)
