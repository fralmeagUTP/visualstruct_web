"""Small independent wire witnesses for complete Graph HTTP trace decoding."""
from copy import deepcopy
import pytest
from _graph_trace_contract import decode_graph_http_trace


def _wire():
    state = {"items": [1, 2], "label": "alive"}
    event = {"phase": "write", "line_index": 0, "value": 2}
    return {
        "graph_snapshot_codec": "graph-snapshot-pool/v1",
        "graph_snapshot_pool": [[1, [1, 2]], [0, [["items", {"$graph_ref": 0}], ["label", "alive"]]]],
        "graph_snapshot_stats": {"sampling": False},
        "source_code": "x = 2;",
        "steps": [{"line_index": 0, "line_text": "x = 2;", "state_snapshot": {"$graph_ref": 1},
                   "state_after": {"$graph_ref": 1}, "console": ["actual stdout"]}],
        "final_state": state,
        "C_instruction_events": [event],
    }


def test_decoding_keeps_complete_states_source_console_and_events():
    wire = _wire()
    before = deepcopy(wire)
    logical = decode_graph_http_trace(wire)
    state = {"items": [1, 2], "label": "alive"}
    assert logical == {
        "source_code": "x = 2;",
        "steps": [{"line_index": 0, "line_text": "x = 2;", "state_snapshot": state,
                   "state_after": state, "console": ["actual stdout"]}],
        "final_state": state,
        "C_instruction_events": [{"phase": "write", "line_index": 0, "value": 2}],
    }
    assert wire == before


def test_legacy_logical_trace_passes_through_without_changes():
    logical = {"steps": [{"state_after": {"x": 1}}], "final_state": {"x": 1}}
    assert decode_graph_http_trace(logical) is logical


def test_unknown_codec_is_rejected():
    wire = _wire()
    wire["graph_snapshot_codec"] = "graph-snapshot-pool/future"
    with pytest.raises(ValueError, match="Unknown Graph snapshot codec"):
        decode_graph_http_trace(wire)


@pytest.mark.parametrize("reference", [True, "1", -1, 2])
def test_invalid_step_reference_is_rejected(reference):
    wire = _wire()
    wire["steps"][0]["state_after"] = {"$graph_ref": reference}
    with pytest.raises(ValueError, match="Invalid or forward Graph snapshot reference"):
        decode_graph_http_trace(wire)


def test_forward_pool_reference_is_rejected():
    wire = _wire()
    wire["graph_snapshot_pool"][0] = [1, [{"$graph_ref": 1}]]
    with pytest.raises(ValueError, match="Invalid or forward Graph snapshot reference"):
        decode_graph_http_trace(wire)


def test_reference_without_declared_codec_is_rejected():
    with pytest.raises(AssertionError, match="Undeclared Graph reference transport"):
        decode_graph_http_trace({"steps": [{"state_after": {"$graph_ref": 0}}]})
