"""Exhaustive acceptance matrix for the sorting visualizer OpenSpec."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

from app.adapters.sorting_adapter import SortingAdapter
from app.domain.sorting import SORTING_ALGORITHMS, SortingExecutionError
from app.services.c_code_service import CCodeService
from app.services.trace import TraceEngine


ALGORITHMS = [item["id"] for item in SORTING_ALGORITHMS]
COMMON_CASES = [
    [5, 1, 4, 2, 3],
    [1, 2, 3, 4, 5],
    [5, 4, 3, 2, 1],
    [3, 1, 3, 2, 1, 3],
    [-7, 0, 4, -2, 4, -7],
    [9],
]


def _run(algorithm: str, values: list[int], mode: str = "step_by_step") -> dict:
    adapter = SortingAdapter()
    adapter.create_array(values)
    adapter.select_algorithm(algorithm)
    source = CCodeService.get_structure_data("sorting_array")["operations"][algorithm]
    return adapter.run(mode, source_code=source)


@pytest.mark.parametrize("algorithm", ALGORITHMS)
@pytest.mark.parametrize("values", COMMON_CASES)
def test_every_algorithm_orders_representative_partitions(algorithm: str, values: list[int]) -> None:
    result = _run(algorithm, values)
    output = result["visual_state"]["items"]
    assert output == sorted(values)
    assert Counter(output) == Counter(values)
    trace = result["execution_trace"]
    assert trace["steps"][-1]["state_after"] == trace["final_state"]
    TraceEngine.validate_legacy_trace(trace)


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_fast_and_step_modes_are_equivalent(algorithm: str) -> None:
    values = [8, -3, 8, 0, 2, -9, 4]
    fast = _run(algorithm, values, "fast")
    stepped = _run(algorithm, values, "step_by_step")
    assert fast["visual_state"]["items"] == stepped["visual_state"]["items"] == sorted(values)
    assert fast["result"]["metrics"] == stepped["result"]["metrics"]


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_every_didactic_step_maps_to_the_visible_c_source(algorithm: str) -> None:
    result = _run(algorithm, [5, 1, 4, 2, 3])
    trace = result["execution_trace"]
    source_lines = trace["source_code"].replace("\r\n", "\n").split("\n")
    for step in trace["steps"]:
        assert isinstance(step["line_index"], int), (algorithm, step["debug"]["note"])
        assert step["line_text"] == source_lines[step["line_index"]]


@pytest.mark.parametrize(
    "algorithm",
    ["intercambio", "seleccion", "insercion", "burbuja", "shell", "quicksort", "mergesort", "heapsort", "radixsort"],
)
def test_comparison_algorithms_accept_c_int_extremes(algorithm: str) -> None:
    values = [2147483647, -2147483648, 0, -1, 2147483647]
    assert _run(algorithm, values)["visual_state"]["items"] == sorted(values)


@pytest.mark.parametrize("algorithm", ["counting_sort", "binsort"])
def test_counting_algorithms_reject_excessive_range_without_mutating_input(algorithm: str) -> None:
    adapter = SortingAdapter()
    values = [-2147483648, 2147483647]
    adapter.create_array(values)
    adapter.select_algorithm(algorithm)
    with pytest.raises(SortingExecutionError, match="rango de conteo"):
        adapter.run("fast")
    assert adapter.to_visual_state()["items"] == values


@pytest.mark.parametrize("value", [-2147483649, 2147483648])
def test_values_outside_c_int_are_rejected_without_state_mutation(value: int) -> None:
    adapter = SortingAdapter()
    adapter.create_array([3, 2, 1])
    with pytest.raises(ValueError, match="rango de int C"):
        adapter.create_array([value])
    assert adapter.to_visual_state()["items"] == [3, 2, 1]


def test_random_generation_is_reproducible_and_validates_c_int_bounds() -> None:
    first = SortingAdapter().generate_random_array(80, -10, 10, seed=20260823)["result"]["array"]
    second = SortingAdapter().generate_random_array(80, -10, 10, seed=20260823)["result"]["array"]
    assert first == second
    assert len(first) == 80 and all(-10 <= value <= 10 for value in first)
    with pytest.raises(ValueError, match="rango de int C"):
        SortingAdapter().generate_random_array(1, -2147483649, 0, seed=1)


def test_random_array_without_explicit_seed_is_stable_when_history_is_replayed(client) -> None:
    generated = client.post(
        "/api/ordenamiento/random-array",
        json={"size": 12, "min_value": -20, "max_value": 20},
    ).get_json()
    original = generated["visual_state"]["items"]
    saved_random = next(item for item in generated["history"] if item["operation"] == "generate_random_array")
    assert isinstance(saved_random["payload"]["seed"], int)

    client.post("/api/ordenamiento/algorithm", json={"algorithm_id": "burbuja"})
    before_run = client.get("/api/ordenamiento/state").get_json()["visual_state"]["items"]
    executed = client.post(
        "/api/ordenamiento/run",
        json={"mode": "fast", "algorithm_id": "burbuja"},
    ).get_json()
    assert before_run == original
    assert executed["visual_state"]["items"] == sorted(original)


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_visible_c_includes_validation_helper_for_every_algorithm(algorithm: str) -> None:
    source = CCodeService.get_structure_data("sorting_array")["operations"][algorithm]
    assert "static int arreglo_valido" in source


@pytest.mark.parametrize("algorithm", ["intercambio", "seleccion", "burbuja", "quicksort", "heapsort"])
def test_visible_c_includes_swap_helper_when_it_is_executed(algorithm: str) -> None:
    source = CCodeService.get_structure_data("sorting_array")["operations"][algorithm]
    assert "static void intercambiar" in source


def test_trace_enters_validation_and_swap_helpers_with_real_transient_state() -> None:
    trace = _run("burbuja", [2, 1])["execution_trace"]
    notes = [step["debug"]["note"] for step in trace["steps"]]
    lines = [step["line_text"].strip() for step in trace["steps"]]
    assert any("arreglo_valido comprueba" in note for note in notes)
    assert "return arreglo != NULL && n > 0;" in lines
    assert "if (a == NULL || b == NULL) return;" in lines
    assert "temporal = *a;" in lines
    assert "*a = *b;" in lines
    assert "*b = temporal;" in lines
    assign_first = next(step for step in trace["steps"] if step["line_text"].strip() == "*a = *b;")
    assert assign_first["state_after"]["items"] == [1, 1]
    assert assign_first["state_after"]["temporaries"] == {"temporal": 2}


def test_prev_alias_returns_the_previous_frame() -> None:
    adapter = SortingAdapter()
    adapter.create_array([3, 1, 2])
    adapter.select_algorithm("burbuja")
    result = adapter.step("prev", 3, source_code=CCodeService.get_structure_data("sorting_array")["operations"]["burbuja"])
    assert result["cursor"] == 2
    assert result["visual_state"] == result["execution_trace"]["steps"][2]["state_after"]


def test_run_algorithm_override_uses_matching_c_source(client) -> None:
    client.post("/api/ordenamiento/create-array", json={"values": "5,1,4,2,3"})
    client.post("/api/ordenamiento/algorithm", json={"algorithm_id": "burbuja"})
    response = client.post("/api/ordenamiento/run", json={"mode": "step_by_step", "algorithm_id": "quicksort"})
    assert response.status_code == 200
    trace = response.get_json()["execution_trace"]
    assert trace["operation_name"] == "quicksort"
    assert "quicksort_recursivo" in trace["source_code"]
    assert "ordenar_burbuja" not in trace["source_code"]


def test_api_rejects_out_of_range_value_and_preserves_previous_array(client) -> None:
    client.post("/api/ordenamiento/create-array", json={"values": "3,2,1"})
    rejected = client.post("/api/ordenamiento/create-array", json={"values": "2147483648"})
    assert rejected.status_code == 400
    assert rejected.get_json()["visual_state"]["items"] == [3, 2, 1]


@pytest.mark.parametrize("malformed", ["1,,2", ",1,2", "1,2,", "1,dos,3"])
def test_api_rejects_malformed_manual_arrays_without_mutation(client, malformed: str) -> None:
    client.post("/api/ordenamiento/create-array", json={"values": "3,2,1"})
    rejected = client.post("/api/ordenamiento/create-array", json={"values": malformed})
    assert rejected.status_code == 400
    assert rejected.get_json()["visual_state"]["items"] == [3, 2, 1]


def test_complete_api_option_flow_random_step_state_and_reset(client) -> None:
    generated = client.post(
        "/api/ordenamiento/random-array",
        json={"size": 8, "min_value": -5, "max_value": 5, "seed": 77},
    )
    assert generated.status_code == 200
    original = generated.get_json()["visual_state"]["items"]
    selected = client.post("/api/ordenamiento/algorithm", json={"algorithm_id": "insercion"})
    assert selected.status_code == 200
    first = client.post(
        "/api/ordenamiento/step",
        json={"direction": "next", "cursor": -1, "algorithm_id": "insercion"},
    )
    assert first.status_code == 200 and first.get_json()["cursor"] == 0
    previous = client.post(
        "/api/ordenamiento/step",
        json={"direction": "prev", "cursor": 1, "algorithm_id": "insercion"},
    )
    assert previous.status_code == 200 and previous.get_json()["cursor"] == 0
    state = client.get("/api/ordenamiento/state")
    assert state.status_code == 200 and state.get_json()["visual_state"]["items"] == original
    reset = client.post("/api/ordenamiento/reset", json={})
    assert reset.status_code == 200 and reset.get_json()["visual_state"]["items"] == []


def test_sorting_console_does_not_fabricate_printf_from_debug_notes() -> None:
    source = (Path(__file__).resolve().parents[1] / "static" / "js" / "sorting.js").read_text(encoding="utf-8")
    assert "step.debug.console_events" in source
    assert "[printf] ${String(debug).trim()}" not in source
    assert "renderSortingConsole(consoleBox, [`[printf] ${data.message}`])" not in source
