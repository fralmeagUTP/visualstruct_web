import json
from pathlib import Path
from time import perf_counter

import pytest

from app.services.c_code_service import CCodeService
from app.services.graph_structure_service import GraphStructureService
from app.services.hash_structure_service import HashStructureService
from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.services.sorting_structure_service import SortingStructureService
from app.services.structure_service import StructureService
from app.services.trace import TraceEngine


SCENARIOS = {
    "linked_list": (StructureService, [("insertar_final", {"value": 4})]),
    "stack": (StructureService, [("apilar", {"value": 4})]),
    "queue": (StructureService, [("encolar", {"value": 4})]),
    "priority_queue": (StructureService, [("encolar", {"value": 4, "priority": 2})]),
    "circular_list": (StructureService, [("insertar_final", {"value": 4})]),
    "sublist": (StructureService, [("insertar_padre", {"parent": 4})]),
    "abb": (HierarchicalStructureService, [("insertar", {"value": 4})]),
    "avl": (HierarchicalStructureService, [("insertar", {"value": 30}), ("insertar", {"value": 10}), ("insertar", {"value": 20})]),
    "red_black": (HierarchicalStructureService, [("insertar", {"value": 10}), ("insertar", {"value": 5}), ("insertar", {"value": 1})]),
    "binary_heap": (HierarchicalStructureService, [("insertar", {"value": 4}), ("insertar", {"value": 1})]),
    "graph": (GraphStructureService, [("create_graph", {"directed": True}), ("insert_edge", {"origin": 1, "target": 2, "weight": 3})]),
    "hash_table": (HashStructureService, [("create_table", {"capacity": 17}), ("insert", {"key": 1, "value": 4})]),
    "sorting": (
        SortingStructureService,
        [
            ("create_array", {"values": [3, 1, 2, 1]}),
            ("select_algorithm", {"algorithm_id": "burbuja"}),
            ("run", {"mode": "step_by_step", "source_code": CCodeService.get_structure_data("sorting_array")["operations"]["burbuja"]}),
        ],
    ),
}


def execute_scenario(structure_id):
    service, operations = SCENARIOS[structure_id]
    history = []
    result = None
    for operation, payload in operations:
        service_id = "sorting_array" if structure_id == "sorting" else structure_id
        if service is SortingStructureService:
            result = service.execute_operation(
                structure_id=service_id, operation_name=operation, payload=payload, history=history
            )
        else:
            result = service.execute_operation(service_id, operation, payload, history)
        assert result["success"] is True, result.get("message")
        history = result["history"]
    return result


@pytest.mark.parametrize("structure_id", sorted(SCENARIOS))
def test_all_13_tads_frames_are_source_mapped_continuous_and_causal(structure_id):
    result = execute_scenario(structure_id)
    trace = result["execution_trace"]
    semantic = TraceEngine.validate_legacy_trace(trace)
    assert semantic
    assert trace["final_state"] == result["visual_state"]
    source_lines = trace["source_code"].splitlines()
    for step in trace["steps"]:
        assert step["line_index"] is not None
        assert " ".join(source_lines[step["line_index"]].split()) == " ".join(step["line_text"].split())


def test_duplicate_values_keep_temporaries_identities_links_and_auxiliary_states(client):
    stack = client.post("/sequential/stack/operate", json={"operation": "apilar", "payload": {"value": 7}}).get_json()
    assert any("temporaries" in step["state_after"] for step in stack["execution_trace"]["steps"])

    client.post("/sequential/sublist/operate", json={"operation": "insertar_padre", "payload": {"parent": 7}})
    duplicate = client.post("/sequential/sublist/operate", json={"operation": "insertar_padre", "payload": {"parent": 7}}).get_json()["visual_state"]
    assert len(duplicate["items"]) == 2
    assert len({item["id"] for item in duplicate["items"]}) == 2

    source = CCodeService.get_structure_data("sorting_array")["operations"]["mergesort"]
    service = SortingStructureService
    history = []
    for operation, payload in (("create_array", {"values": [3, 1, 3, 1]}), ("select_algorithm", {"algorithm_id": "mergesort"}), ("run", {"mode": "step_by_step", "source_code": source})):
        sorting = service.execute_operation(
            structure_id="sorting_array", operation_name=operation, payload=payload, history=history
        )
        history = sorting["history"]
    assert any(step["state_after"].get("auxiliary_array") is not None for step in sorting["execution_trace"]["steps"])
    assert any(step["state_after"].get("active_range") is not None for step in sorting["execution_trace"]["steps"])
    assert sorting["visual_state"]["items"] == [1, 1, 3, 3]

    red_black = execute_scenario("red_black")["execution_trace"]
    colored_frames = [step["state_after"]["root"] for step in red_black["steps"] if step["state_after"].get("root")]
    assert any(root["color"] == "RED" for root in colored_frames)
    assert colored_frames[-1]["color"] == "BLACK"


def test_player_contract_supports_reversible_repeatable_controls():
    source = (Path(__file__).resolve().parents[1] / "static" / "js" / "interpreter_runtime.js").read_text(encoding="utf-8")
    for token in ("playFromStart", "pause", "step", "prev", "reset", "applyStateSnapshot", "applyStateAfter"):
        assert token in source
    assert "applyStateAfter(previousStep);" in source
    assert "applyStateSnapshot(firstStep);" in source
    assert "playToken += 1" in source


@pytest.mark.parametrize("algorithm", [item["id"] for item in __import__("app.domain.sorting.tad_ordenamiento", fromlist=["SORTING_ALGORITHMS"]).SORTING_ALGORITHMS])
def test_sorting_fast_step_backend_final_equivalence(algorithm):
    source = CCodeService.get_structure_data("sorting_array")["operations"][algorithm]
    finals = []
    for mode in ("fast", "step_by_step"):
        history = []
        for operation, payload in (("create_array", {"values": [5, -1, 5, 0, 2]}), ("select_algorithm", {"algorithm_id": algorithm}), ("run", {"mode": mode, "source_code": source})):
            result = SortingStructureService.execute_operation(
                structure_id="sorting_array", operation_name=operation, payload=payload, history=history
            )
            history = result["history"]
        assert result["execution_trace"]["final_state"] == result["visual_state"]
        finals.append(result["visual_state"]["items"])
    assert finals[0] == finals[1] == [-1, 0, 2, 5, 5]


def test_trace_size_latency_and_session_limits(app):
    measurements = []
    for structure_id in sorted(SCENARIOS):
        started = perf_counter()
        result = execute_scenario(structure_id)
        elapsed_ms = (perf_counter() - started) * 1000
        trace_bytes = len(json.dumps(result["execution_trace"], ensure_ascii=False).encode("utf-8"))
        measurements.append((structure_id, elapsed_ms, trace_bytes))
    assert max(item[1] for item in measurements) < 2000
    assert max(item[2] for item in measurements) < 1_000_000
    assert app.config["SESSION_MAX_HISTORY"] <= 300
