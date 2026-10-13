import copy
import json
from pathlib import Path
import pytest
from _phase8_limits_consumer_oracle import assert_complete_trace_json, metric

@pytest.fixture
def rn_body():
    return json.loads(Path("openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-phase8-duplicates-consumer-low/duplicates-final-2-call-12-red_black-insertar-service.json").read_text(encoding="utf-8"))

def test_saved_complete_rn_excess_remains_reported(rn_body):
    encoded = assert_complete_trace_json(rn_body)
    assert len(encoded) == 2_119_908
    item = metric("red_black", 0, 0, len(encoded))
    assert item["historical_size_exceeded"] and item["historical_size_budget_bytes"] == 1_000_000
    assert not item["native_C_timing_measured"] and not item["visual_playback_timing_measured"]

@pytest.mark.parametrize("change", ["body_failure", "trace_failure", "empty_steps", "wrong_final", "source_line", "discontinuity"])
def test_functional_corruptions_are_rejected(rn_body, change):
    trace=rn_body["execution_trace"]
    if change == "body_failure": rn_body["success"]=False
    elif change == "trace_failure": trace["success"]=False
    elif change == "empty_steps": trace["steps"]=[]
    elif change == "wrong_final": trace["final_state"]={}
    elif change == "source_line": trace["steps"][5]["line_text"]="corrupted C source"
    elif change == "discontinuity": trace["steps"][5]["state_snapshot"]={"corrupted":True}
    with pytest.raises((AssertionError, ValueError)):
        assert_complete_trace_json(rn_body)

@pytest.mark.parametrize("size,exceeded", [(999_999,False),(1_000_000,True),(1_000_001,True)])
def test_historical_strict_boundary_not_raised(size,exceeded):
    assert metric("fixture",0,0,size)["historical_size_exceeded"] is exceeded
