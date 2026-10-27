"""Pure original recreation caller boundary mutation controls."""
from pathlib import Path
from copy import deepcopy
import json,pytest
from _hash_visible_caller_consumer_oracle import assert_hash_visible_contract
ROOT=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-hash-methods-consumer-low"
from scripts.published_test_inputs import audit_input_path
@pytest.fixture(scope="module")
def saved():return json.loads((audit_input_path(ROOT/"hashvisible-before-call-4-create_table.json")).read_text(encoding="utf-8"))
def test_original_recreation_positive(saved):assert_hash_visible_contract(saved)
@pytest.mark.parametrize("fault",["boundary_index","boundary_line","boundary_function","boundary_event","boundary_position","native_index","native_line","free","live_heap","root","allocation","scope","source","next_entry"])
def test_boundary_corruptions_rejected(saved,fault):
    p=deepcopy(saved);steps=p["execution_trace"]["steps"];s=steps[0]
    if fault=="boundary_index":s["line_index"]=-2
    elif fault=="boundary_line":s["line_text"]="th_destruir(&tabla);"
    elif fault=="boundary_function":s["instruction_event"]["function"]="th_inicializar"
    elif fault=="boundary_event":s["event_type"]="native_free"
    elif fault=="boundary_position":steps[0],steps[1]=steps[1],steps[0]
    elif fault=="native_index":steps[1]["line_index"]=-1
    elif fault=="native_line":steps[1]["line_text"]="unrelated();"
    elif fault=="free":s["debug"]["freed"].pop()
    elif fault=="live_heap":s["debug"]["heap"]=[{"id":"0xHASH-1"}]
    elif fault=="root":s["debug"]["root"]["capacity"]=17
    elif fault=="allocation":s["debug"]["allocations"]=1
    elif fault=="scope":s["debug"]["call_stack"]=["th_inicializar"]
    elif fault=="source":p["execution_trace"]["source_code"]+="\n"
    else:steps[1]["event_type"]="bucket_allocate"
    with pytest.raises(AssertionError):assert_hash_visible_contract(p)

OTHER_VISIBLE=[(5,"insert"),(6,"get"),(7,"contains"),(8,"remove"),(9,"keys"),(10,"values"),(11,"items"),(12,"stats"),(13,"clear"),(14,"destroy_table")]
@pytest.mark.parametrize("call,operation",OTHER_VISIBLE)
def test_other_original_visible_captures_positive(call,operation):
    body=json.loads((audit_input_path(ROOT/("hashvisible-final-1-call-"+str(call)+"-"+operation+".json"))).read_text(encoding="utf-8"))
    assert_hash_visible_contract(body)
@pytest.mark.parametrize("call,operation",OTHER_VISIBLE)
def test_non_creation_cannot_claim_caller_boundary(call,operation):
    body=json.loads((audit_input_path(ROOT/("hashvisible-final-1-call-"+str(call)+"-"+operation+".json"))).read_text(encoding="utf-8"))
    s=body["execution_trace"]["steps"][0]
    s["line_index"]=-1;s["line_text"]="";s["event_type"]="caller_recreate"
    with pytest.raises(AssertionError):assert_hash_visible_contract(body)
