"""Corruption controls for graph structure and uncertified partial frames."""
from copy import deepcopy
import pytest
from _final_graph_oracle import assert_final_graph, assert_observed_graph_frame


def _state():
    return {"structure": "graph", "directed": False, "weighted": True,
            "nodes": [{"id": str(v), "label": str(v), "value": str(v), "marked": 0} for v in (1, 2)],
            "edges": [{"source": "1", "target": "2", "weight": 3}],
            "metadata": {"vertices_count": 2, "edges_count": 1, "is_empty": False}}


def test_valid_graph_shape():
    assert_final_graph(_state())


@pytest.mark.parametrize("corruption", ["duplicate_vertex", "missing_endpoint", "duplicate_edge", "node_count", "edge_count", "empty", "weighted", "mark", "weight"])
def test_final_graph_oracle_rejects_corruption(corruption):
    state = _state()
    if corruption == "duplicate_vertex": state["nodes"].append(deepcopy(state["nodes"][0]))
    elif corruption == "missing_endpoint": state["edges"][0]["target"] = "9"
    elif corruption == "duplicate_edge": state["edges"].append({"source": "2", "target": "1", "weight": 3})
    elif corruption == "node_count": state["metadata"]["vertices_count"] = 3
    elif corruption == "edge_count": state["metadata"]["edges_count"] = 0
    elif corruption == "empty": state["metadata"]["is_empty"] = True
    elif corruption == "weighted": state["weighted"] = False
    elif corruption == "mark": state["nodes"][0]["marked"] = True
    else: state["edges"][0]["weight"] = float("nan")
    with pytest.raises(AssertionError): assert_final_graph(state)


def _observation():
    import json
    from pathlib import Path
    return json.loads((Path(__file__).parent / "fixtures/graph_observed_dist_write.json").read_text())["trace"]


def test_real_observed_partial_write():
    trace = _observation(); assert_observed_graph_frame(trace["steps"][0], trace, 0)


@pytest.mark.parametrize("corruption", ["fabricated_phase", "QA_empty_memory", "missing_graph_roots", "missing_returned", "no_function_frame", "event_step_mismatch", "event_ledger_mismatch", "observer_memory_mismatch", "write_storage_mismatch", "condition_mutation", "allocate_without_allocation", "false_invariant"])
def test_partial_frame_oracle_rejects_causal_corruption(corruption):
    trace = _observation(); step = trace["steps"][0]; frame = step["pedagogy"]; event = frame["instruction_event"]
    if corruption == "fabricated_phase": event["phase"] = "fabricated-with-no-C-event"
    elif corruption == "QA_empty_memory":
        event["phase"] = "fabricated-with-no-C-event"
        for key in ("instruction_state_before", "instruction_state_after", "memory_state"):
            frame[key] = {"graph": {}, "frames": [], "heap_nodes": [], "retired_objects": []}
    elif corruption == "missing_graph_roots": frame["instruction_state_after"]["graph"] = {}
    elif corruption == "missing_returned": del frame["instruction_state_after"]["returned"]
    elif corruption == "no_function_frame": frame["instruction_state_after"]["frames"] = []
    elif corruption == "event_step_mismatch": step["debug"]["stage"] = "return"
    elif corruption == "event_ledger_mismatch": event["value"] = 999
    elif corruption == "observer_memory_mismatch": step["debug"]["graph_memory"]["graph"]["v"] = "invented"
    elif corruption == "write_storage_mismatch":
        for memory in (frame["instruction_state_after"], frame["memory_state"], step["debug"]["graph_memory"]):
            for node in memory["heap_nodes"]:
                if "items" in node: node["items"] = [999 if value == 0 else value for value in node["items"]]
    elif corruption in {"condition_mutation", "allocate_without_allocation"}:
        phase = "condition" if corruption == "condition_mutation" else "allocate"
        event["phase"] = step["debug"]["stage"] = trace["C_instruction_events"][0]["phase"] = phase
    else: frame["invariant"]["holds"] = False
    with pytest.raises((AssertionError, KeyError)): assert_observed_graph_frame(step, trace, 0)


def _legacy_statement(model):
    import json
    from pathlib import Path
    trace = json.loads((Path(__file__).parent / "fixtures/graph_observed_bfs_statement.json").read_text())["trace"]
    if model == "dfs":
        # Same legacy schema rule; a real BFS statement supplies memory/source.
        trace.pop("bfs_instruction_model"); trace["dfs_instruction_model"] = True
        debug = trace["steps"][0]["debug"]
        debug["dfs_memory"] = debug.pop("bfs_memory")
    return trace

@pytest.mark.parametrize("model", ["bfs", "dfs"])
@pytest.mark.parametrize("flag", [False, None, 0, 1, "true"])
def test_legacy_C_statement_rejects_explicit_false_or_invalid_flag(model, flag):
    trace = _legacy_statement(model)
    step = trace["steps"][0]
    step["pedagogy"]["instruction_event"]["C_executed"] = flag
    with pytest.raises(AssertionError):
        assert_observed_graph_frame(step, trace, 0)

@pytest.mark.parametrize("model", ["bfs", "dfs"])
@pytest.mark.parametrize("explicit_true", [False, True])
def test_legacy_C_statement_accepts_absent_flag_or_boolean_true(model, explicit_true):
    trace = _legacy_statement(model); step = trace["steps"][0]
    if explicit_true: step["pedagogy"]["instruction_event"]["C_executed"] = True
    else: step["pedagogy"]["instruction_event"].pop("C_executed", None)
    assert_observed_graph_frame(step, trace, 0)
