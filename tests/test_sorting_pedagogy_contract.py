"""Contract and golden-fixture tests for sorting pedagogy frames."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.adapters.sorting_adapter import SortingAdapter
from app.domain.sorting import SORTING_ALGORITHMS
from app.services.c_code_service import CCodeService
from app.domain.sorting.pedagogy import (
    PEDAGOGICAL_FRAME_SCHEMA_VERSION,
    PedagogicalFrameValidationError,
    SORTING_LEARNING_CATALOG,
    SORTING_THEORY_CATALOG,
    build_pedagogical_frame,
    pedagogical_frame_schema,
    validate_pedagogical_frame,
)


def _raw(token: str) -> dict[str, object]:
    return {
        "line_token": token,
        "action": f"Evento {token}",
        "array_snapshot": [3, 1],
        "sorted_indices": [],
        "temporaries": {"temporal": 3} if token == "swap_assign_a" else {},
    }


def test_learning_catalog_covers_all_eleven_algorithms() -> None:
    algorithm_ids = {item["id"] for item in SORTING_ALGORITHMS}
    assert set(SORTING_LEARNING_CATALOG) == algorithm_ids
    for profile in SORTING_LEARNING_CATALOG.values():
        assert profile["objective"]
        assert profile["prior"]
        assert profile["mastery"]
    assert set(SORTING_THEORY_CATALOG) == algorithm_ids
    for theory in SORTING_THEORY_CATALOG.values():
        assert set(theory) == {"best", "average", "worst", "memory", "stable", "in_place"}


def test_published_schema_is_versioned() -> None:
    schema = pedagogical_frame_schema()
    assert schema["version"] == PEDAGOGICAL_FRAME_SCHEMA_VERSION
    assert schema["$id"].endswith("/v1")
    assert schema["levels"] == ["basic", "intermediate", "advanced"]


def test_golden_pedagogical_events_satisfy_contract() -> None:
    fixture_path = Path(__file__).parent / "golden" / "sorting_pedagogical_frames_v1.json"
    fixtures = json.loads(fixture_path.read_text(encoding="utf-8"))["fixtures"]
    for fixture in fixtures.values():
        frame = build_pedagogical_frame(
            algorithm_id="mergesort",
            raw_step=_raw(fixture["line_token"]),
            line_index=0,
            line_text="instruccion();",
        )
        validate_pedagogical_frame(frame, source_code="instruccion();")
        assert frame["concept"] == fixture["concept"]
        narrations = frame["narration"]
        assert len({narrations["basic"], narrations["intermediate"], narrations["advanced"]}) == 3
        assert "Línea C" in narrations["advanced"]


def test_validator_rejects_incomplete_frame_and_wrong_c_line() -> None:
    frame = build_pedagogical_frame(
        algorithm_id="burbuja", raw_step=_raw("compare"), line_index=0, line_text="linea();"
    )
    incomplete = dict(frame)
    incomplete.pop("invariant")
    with pytest.raises(PedagogicalFrameValidationError, match="incompleto"):
        validate_pedagogical_frame(incomplete)
    with pytest.raises(PedagogicalFrameValidationError, match="no coincide"):
        validate_pedagogical_frame(frame, source_code="otra_linea();")


def test_condition_stack_pointer_and_loop_semantics_are_explicit() -> None:
    adapter = SortingAdapter()
    adapter.create_array([2, 1])
    adapter.select_algorithm("burbuja")
    steps = adapter.run("step_by_step", source_code=CCodeService.get_structure_data("sorting_array")["operations"][adapter.to_visual_state()["algorithm"]])["execution_trace"]["steps"]
    comparison = next(step["pedagogy"] for step in steps if step["pedagogy"]["source"]["line_token"] == "compare")
    pointer_assignment = next(step["pedagogy"] for step in steps if step["pedagogy"]["source"]["line_token"] == "swap_assign_a")
    assert comparison["condition"]["expression"] == "2 > 1"
    assert comparison["condition"]["result"] is True
    assert comparison["loop"]["kind"] == "for interno"
    assert comparison["loop"]["iteration"] == 0
    assert comparison["loop"]["bounds"] == [0, 2]
    assert comparison["loop"]["exit"] is False
    assert len(pointer_assignment["call_stack"]) == 2
    assert [pointer["target"] for pointer in pointer_assignment["pointers"]] == ["arreglo[0]", "arreglo[1]"]
    temporal_assignment = next(step["pedagogy"] for step in steps if step["pedagogy"]["source"]["line_token"] == "swap_temp")
    assert any(variable["name"] == "temporal" and variable["changed"] for variable in temporal_assignment["variables"])
    saved = next(variable for variable in pointer_assignment["variables"] if variable["name"] == "temporal")
    assert saved["value"] == saved["previous"] == 2
    assert saved["initialized"] is True
    assert saved["changed"] is False
    partial_write = next(step for step in steps if step["pedagogy"]["source"]["line_token"] == "swap_assign_a")
    assert partial_write["state_after"]["items"] == [1, 1]
    assert "temporal = *a;" in temporal_assignment["source"]["line_text"]
    assert "*a = *b;" in pointer_assignment["source"]["line_text"]


def test_every_frame_is_self_contained_for_exact_reverse_navigation() -> None:
    adapter = SortingAdapter()
    adapter.create_array([3, 1, 2])
    adapter.select_algorithm("quicksort")
    steps = adapter.run("step_by_step", source_code=CCodeService.get_structure_data("sorting_array")["operations"][adapter.to_visual_state()["algorithm"]])["execution_trace"]["steps"]
    for index in range(1, len(steps)):
        assert steps[index]["state_snapshot"] == steps[index - 1]["state_after"]
        validate_pedagogical_frame(steps[index - 1]["pedagogy"])
    recursive = next(frame["pedagogy"] for frame in steps if frame["pedagogy"]["source"]["line_token"] == "rec_init")
    assert recursive["call_stack"][-1]["function"] == "quicksort_recursivo"
    assert recursive["source"]["function"] == "quicksort_recursivo"
    assert "pivote = arreglo[(primero + ultimo) / 2]" in recursive["source"]["line_text"]
    assert recursive["call_stack"][-1]["parameters"] == {"arreglo": "arreglo del caller", "primero": 0, "ultimo": 2}
    pivot = next(variable for variable in recursive["variables"] if variable["name"] == "pivote")
    assert pivot["value"] == 1
    assert pivot["type"] == "int"
    assert pivot["initialized"] is True


@pytest.mark.parametrize("algorithm_id", [item["id"] for item in SORTING_ALGORITHMS])
def test_adapter_exposes_complete_pedagogy_on_every_frame(algorithm_id: str) -> None:
    adapter = SortingAdapter()
    adapter.create_array([3, 1, 2])
    adapter.select_algorithm(algorithm_id)
    trace = adapter.run("step_by_step", source_code=CCodeService.get_structure_data("sorting_array")["operations"][adapter.to_visual_state()["algorithm"]])["execution_trace"]
    assert trace["pedagogy_schema_version"] == PEDAGOGICAL_FRAME_SCHEMA_VERSION
    assert trace["learning_profile"]["objective"]
    for step in trace["steps"]:
        validate_pedagogical_frame(step["pedagogy"])
        if algorithm_id == "heapsort":
            state = step["state_after"]
            items = state["items"]
            confirmed = state["sorted_indices"]
            # Completed extractions form the suffix; partial heapify/swap writes
            # do not guarantee a global heap before that phase completes.
            heap_n = len(items) - len(confirmed)
            assert confirmed == list(range(heap_n, len(items)))
            assert state["heap_context"]["heap_n"] == heap_n
            observed_max_heap = all(items[(child - 1) // 2] >= items[child] for child in range(1, heap_n))
            assert step["pedagogy"]["invariant"]["holds"] is observed_max_heap
            assert state["heap_context"]["max_heap"] is observed_max_heap
            assert items[heap_n:] == sorted(items[heap_n:])
            token = step["pedagogy"]["source"]["line_token"]
            completed_build = token == "build_test" and step["pedagogy"]["condition"]["result"] is False
            if completed_build or token in {"extract_heap_resume", "sort_return"}:
                assert observed_max_heap is True
                assert all(left <= right for left in items[:heap_n] for right in items[heap_n:])
        else:
            assert step["pedagogy"]["invariant"]["holds"] is True
        assert step["pedagogy"]["invariant"]["text"]
        assert "corresponde a la instrucción" not in step["pedagogy"]["invariant"]["text"]
    if algorithm_id == "heapsort":
        assert trace["final_state"]["items"] == [1, 2, 3]
        assert any(step["pedagogy"]["invariant"]["holds"] is False for step in trace["steps"])
    assert trace["theory_profile"] == SORTING_THEORY_CATALOG[algorithm_id]
