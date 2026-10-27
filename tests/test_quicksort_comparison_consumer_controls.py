"""Pure negatives of the single original QuickSort three-value path."""
from copy import deepcopy
from pathlib import Path
import json
import pytest
from _quicksort_comparison_consumer_oracle import assert_quicksort_comparison_consumer
P=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-quicksort-comparison-consumers-low/positive-fixtures.json"
from scripts.published_test_inputs import audit_input_path
def result():return deepcopy(next(iter(json.loads(audit_input_path(P).read_text(encoding="utf-8")).values())))
def test_frozen_original_comparisons():assert_quicksort_comparison_consumer(result())
@pytest.mark.parametrize("defect",("true_flipped","false_flipped","missing_false","wrong_operand","wrong_index","wrong_pivot","future_increment","array_mutation","wrong_counter","wrong_function","wrong_frame","wrong_alias","wrong_pointer","future_temporary","stale_temporary","wrong_stack","extra_recursion","wrong_final"))
def test_rejects_causal_quicksort_defect(defect):
    r=result();ss=r["steps"]
    if defect=="true_flipped":ss[12]["condition_result"]=False
    elif defect=="false_flipped":ss[14]["condition_result"]=True
    elif defect=="missing_false":ss.pop(14)
    elif defect=="wrong_operand":ss[14]["condition_expression"]="1 < 2"
    elif defect=="wrong_index":ss[14]["comparing_indices"]=[0]
    elif defect=="wrong_pivot":ss[10]["quick_context"]["pivote"]=3
    elif defect=="future_increment":ss[12]["quick_context"]["i"]=1
    elif defect=="array_mutation":ss[14]["array_snapshot"]=[1,3,2]
    elif defect=="wrong_counter":ss[14]["metrics"]["comparisons"]-=1
    elif defect=="wrong_function":ss[14]["source_function"]="other"
    elif defect=="wrong_frame":ss[14]["instruction_event"]["frames"][0]["primero"]=1
    elif defect=="wrong_alias":ss[20]["instruction_event"]["b"]=2
    elif defect=="wrong_pointer":ss[20]["instruction_pointers"][1]["target"]="arreglo[2]"
    elif defect=="future_temporary":ss[20]["instruction_variables"].append({"scope":"intercambiar","name":"temporal","value":2,"initialized":True})
    elif defect=="stale_temporary":ss[26]["instruction_event"]["temporal"]=2
    elif defect=="wrong_stack":ss[14]["instruction_stack"].append("quicksort_recursivo")
    elif defect=="extra_recursion":ss[31]["condition_result"]=True
    else:r["final_state"]["items"]=[1,3,2]
    with pytest.raises(AssertionError):assert_quicksort_comparison_consumer(r)
