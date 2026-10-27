from copy import deepcopy
from pathlib import Path
import json
import pytest
from _rn_console_consumer_oracle import assert_empty_rn_console,TEXT
P=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-rn-console-consumer-low"
from scripts.published_test_inputs import audit_input_path
FIXTURE=json.loads((audit_input_path(P/"rn-console-before-traces.json")).read_text(encoding="utf-8"))[-1]
def test_original_console_capture():assert_empty_rn_console(FIXTURE)
@pytest.mark.parametrize("fault",["dropLF","dropTAB","duplicate","late","early","drop","source","sourceindex","phase","coordinatedstdout","coordinatedheap","parameter","color","mask","return","final"])
def test_corrupted_console_capture_rejected(fault):
    r=deepcopy(FIXTURE);s=r["execution_trace"]["steps"]
    if fault=="dropLF":s[22]["console"]=[TEXT.rstrip("\n")]
    elif fault=="dropTAB":s[22]["console"]=[TEXT.lstrip("\t")]
    elif fault=="duplicate":s[23]["console"]=[TEXT]
    elif fault=="late":s[22]["console"]=[];s[24]["console"]=[TEXT]
    elif fault=="early":s[22]["console"]=[];s[19]["console"]=[TEXT]
    elif fault=="drop":s[22]["console"]=[]
    elif fault=="source":r["execution_trace"]["source_code"]+="\n// fabricated"
    elif fault=="sourceindex":s[22]["line_index"]=s[21]["line_index"]
    elif fault=="phase":s[22]["pedagogy"]["instruction_event"]["phase"]="caller"
    elif fault=="coordinatedstdout":
        for i in (22,23,24):s[i]["pedagogy"]["memory_state"]["console_stdout"]="invented"
    elif fault=="coordinatedheap":
        for state in (s[22]["state_snapshot"],s[22]["state_after"]):state["heap_nodes"][0]["value"]=99
    elif fault=="parameter":s[22]["state_snapshot"]["tree_frames"][-1]["parameters"]["dato"]=99
    elif fault=="color":s[22]["state_snapshot"]["heap_nodes"][0]["color"]="RED"
    elif fault=="mask":s[22]["state_snapshot"]["heap_nodes"][0]["initialized"]=0
    elif fault=="return":s[23]["pedagogy"]["instruction_event"]["return"]="N1"
    else:r["visual_state"]["root"]["value"]=99;r["execution_trace"]["final_state"]=deepcopy(r["visual_state"])
    with pytest.raises(AssertionError):assert_empty_rn_console(r)
