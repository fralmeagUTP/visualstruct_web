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


def _root_C_array(memory, name):
    if not memory["frames"]:
        return None
    values = [scope["variables"][name]["value"]
              for scope in memory["frames"][0]["scopes"]
              if name in scope["variables"]]
    if not values:
        return None
    assert len(values) == 1
    nodes = [node for node in memory["heap_nodes"] if node["id"] == values[0]]
    if not nodes:
        return None
    assert len(nodes) == 1 and "items" in nodes[0]
    return nodes[0]


@pytest.mark.parametrize("operation", ["run_dijkstra", "run_bellman_ford"])
def test_shortest_path_frames_transport_algorithm_tables(operation):
    result = _graph_shortest_trace(operation)
    trace = result["execution_trace"]
    steps = trace["steps"]
    progress = [step["debug"]["graph_progress"] for step in steps]
    assert all(set(("distances", "previous", "visited", "candidates")) <= set(item)
               for item in progress)
    # Function entry precedes localarray allocation; caller receipt followsfree.
    assert progress[0]["distances"] == progress[0]["previous"] == {}
    assert progress[-1]["distances"] == progress[-1]["previous"] == {}
    assert steps[0]["pedagogy"]["instruction_event"]["phase"] == "enter"
    assert steps[-1]["pedagogy"]["instruction_event"]["phase"] == "caller_receipt"
    source_lines = trace["source_code"].splitlines()
    anchors = {}
    for index, step in enumerate(steps):
        frame = step["pedagogy"]
        event = frame["instruction_event"]
        if event["C_executed"]:
            assert type(step["line_index"]) is int
            assert 0 <= step["line_index"] < len(source_lines)
            assert step["line_text"] == source_lines[step["line_index"]]
            assert event["statement"] == step["line_text"]
        for name in ("dist", "prev"):
            if _root_C_array(frame["instruction_state_after"], name) is None:
                field = "distances" if name == "dist" else "previous"
                assert step["debug"]["graph_progress"][field] == {}
        if event["C_executed"] and event["phase"] == "write":
            if step["line_text"].strip() in ("dist[idx_inicio] = 0;", "alcanzable[idx_inicio] = 1;"):
                anchors[step["line_text"].strip()] = index
        if event["C_executed"] and event["phase"] == "free" and step["line_text"].strip() == "free(dist);":
            anchors["free(dist);"] = index
    initialized = anchors["dist[idx_inicio] = 0;"]
    step = steps[initialized]
    memory = step["pedagogy"]["instruction_state_after"]
    vertices = _root_C_array(memory, "vertices")["items"]
    assert set(vertices) == {1, 2, 3}
    assert _root_C_array(memory, "dist")["items"][vertices.index(1)] == 0
    if operation == "run_bellman_ford":
        # Writing0 does not make a vertex reachable before the separateflagwrite.
        assert progress[initialized]["distances"]["1"] == "\u221e"
        mask_index = anchors["alcanzable[idx_inicio] = 1;"]
        assert mask_index == initialized + 1
        mask = steps[mask_index]["pedagogy"]
        assert _root_C_array(mask["instruction_state_before"], "alcanzable")["items"][vertices.index(1)] == 0
        assert _root_C_array(mask["instruction_state_after"], "alcanzable")["items"][vertices.index(1)] == 1
        initialized = mask_index
    assert progress[initialized]["distances"] == {"1": 0, "2": "\u221e", "3": "\u221e"}
    assert progress[initialized]["previous"] == {"1": None, "2": None, "3": None}
    free_index = anchors["free(dist);"]
    assert initialized < free_index
    free_step = steps[free_index]
    frame = free_step["pedagogy"]
    old_memory, new_memory = frame["instruction_state_before"], frame["instruction_state_after"]
    old_dist = _root_C_array(old_memory, "dist")
    assert old_dist is not None and _root_C_array(new_memory, "dist") is None
    assert frame["instruction_event"]["value"] == old_dist["id"]
    assert any(node["id"] == old_dist["id"] for node in new_memory["retired_objects"])
    vertices = _root_C_array(old_memory, "vertices")["items"]
    assert dict(zip(vertices, old_dist["items"])) == {1: 0, 2: 4, 3: 5}
    previous = _root_C_array(old_memory, "prev")["items"]
    assert {vertex: None if previous[i] == -1 else vertices[previous[i]]
            for i, vertex in enumerate(vertices)} == {1: None, 2: 1, 3: 2}
    assert progress[free_index - 1]["distances"] == {"1": 0, "2": 4, "3": 5}
    assert progress[free_index - 1]["previous"] == {"1": None, "2": 1, "3": 2}
    assert progress[free_index]["distances"] == {}
    assert result["success"] is True
    assert result["result"]["distance_to_destination"] == 5
    assert result["result"]["path"] == [1, 2, 3]
    assert trace["final_state"] == result["visual_state"] == steps[-1]["state_after"]


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
    assert result["execution_trace"]["steps"][-1]["console"] == ["\tEl numero ha sido insertado"]
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
