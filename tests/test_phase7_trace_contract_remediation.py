from pathlib import Path

import pytest

from app.adapters.sorting_adapter import SortingAdapter
from app.domain.sorting.tad_ordenamiento import SortingInterpreter
from app.services.c_code_service import CCodeService
from app.services.graph_structure_service import GraphStructureService
from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.services.trace import TraceContractError, TraceEngine


ROOT = Path(__file__).resolve().parents[1]


def _graph_shortest_trace(operation="run_dijkstra"):
    history = []
    for name, payload in (
        ("create_graph", {"directed": True}),
        ("insert_edge", {"origin": 1, "target": 2, "weight": 4}),
        ("insert_edge", {"origin": 2, "target": 3, "weight": 1}),
    ):
        result = GraphStructureService.execute_operation("graph", name, payload, history)
        history = result["history"]
    return GraphStructureService.execute_operation("graph", operation, {"start": 1, "end": 3}, history)


@pytest.mark.parametrize("operation", ["run_dijkstra", "run_bellman_ford"])
def test_shortest_path_frames_transport_algorithm_tables(operation):
    result = _graph_shortest_trace(operation)
    progress = [step["debug"]["graph_progress"] for step in result["execution_trace"]["steps"]]
    assert all(set(("distances", "previous", "visited", "candidates")) <= set(item) for item in progress)
    assert progress[0]["distances"]["1"] == 0.0
    assert progress[-1]["distances"]["3"] == 5.0
    assert progress[-1]["previous"]["3"] == "2"


def test_quicksort_emits_true_and_false_condition_evaluations():
    steps = SortingInterpreter([1, 2, 3], "quicksort").run()["steps"]
    evaluations = [step for step in steps if step.get("line_token") in {"move_i", "move_j"}]
    assert evaluations
    assert any(": False." in step["action"] for step in evaluations)
    assert any(step["comparing_indices"] == [1, 1] for step in evaluations)


@pytest.mark.parametrize("algorithm", ["mergesort", "binsort"])
def test_merge_and_bin_frames_all_map_to_real_c_lines(algorithm):
    source = CCodeService.get_structure_data("sorting_array")["operations"][algorithm]
    adapter = SortingAdapter()
    adapter.execute("create_array", {"values": [5, -1, 4, 2, 2, 0]})
    adapter.execute("select_algorithm", {"algorithm_id": algorithm})
    trace = adapter.execute("run", {"mode": "step_by_step", "source_code": source})["execution_trace"]
    lines = source.splitlines()
    assert all(step["line_index"] is not None for step in trace["steps"])
    assert all(" ".join(lines[step["line_index"]].split()) == " ".join(step["line_text"].split()) for step in trace["steps"])


def test_console_is_transported_as_events_and_not_reconstructed_by_frontend():
    history = []
    result = HierarchicalStructureService.execute_operation("red_black", "insertar", {"value": 10}, history)
    assert result["execution_trace"]["steps"][-1]["console"] == ["El numero ha sido insertado"]
    for script in ("sequential.js", "hierarchical.js", "graph.js", "hash.js"):
        source = (ROOT / "static/js" / script).read_text(encoding="utf-8")
        assert "Array.isArray(step.console)" in source
        assert "[printf] ${finalMessage}" not in source


def _step(index, before, after, *, event="line", text=None):
    return {
        "line_index": index,
        "line_text": text if text is not None else f"line {index}",
        "event_type": event,
        "phase": "progress",
        "state_snapshot": before,
        "state_after": after,
        "console": [],
    }


def test_trace_requires_deep_continuity_or_explicit_rebase():
    discontinuous = {"structure_id": "stack", "steps": [_step(0, {"x": 0}, {"x": 1}), _step(1, {"x": 9}, {"x": 2})], "final_state": {"x": 2}}
    with pytest.raises(TraceContractError, match="Discontinuidad"):
        TraceEngine.validate_legacy_trace(discontinuous)
    discontinuous["steps"][1]["event_type"] = "rebase"
    TraceEngine.validate_legacy_trace(discontinuous)


def test_trace_rejects_out_of_range_and_normalized_text_mismatch():
    trace = {"structure_id": "queue", "source_code": "line 0\nline 1", "steps": [_step(2, {}, {})], "final_state": {}}
    with pytest.raises(TraceContractError, match="fuera de rango"):
        TraceEngine.validate_legacy_trace(trace)
    trace["steps"] = [_step(1, {}, {}, text="inventada")]
    with pytest.raises(TraceContractError, match="no coincide"):
        TraceEngine.validate_legacy_trace(trace)
