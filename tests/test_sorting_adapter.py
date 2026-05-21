"""Unit tests for sorting adapter."""

from __future__ import annotations

from app.adapters.sorting_adapter import SortingAdapter


def test_sorting_adapter_supports_algorithms_from_c_contract() -> None:
    """Adapter should expose algorithms mapped to C methods."""
    adapter = SortingAdapter()
    algorithm_ids = {item["id"] for item in adapter.get_supported_algorithms()}
    assert "burbuja" in algorithm_ids
    assert "quicksort" in algorithm_ids
    assert "radixsort" in algorithm_ids


def test_create_array_and_select_algorithm() -> None:
    """Adapter should accept manual arrays and algorithm selection."""
    adapter = SortingAdapter()
    adapter.execute("create_array", {"values": "5,3,8,1"})
    state = adapter.to_visual_state()
    assert state["items"] == [5, 3, 8, 1]
    adapter.execute("select_algorithm", {"algorithm_id": "insercion"})
    assert adapter.to_visual_state()["algorithm"] == "insercion"


def test_run_fast_and_step_by_step_reach_same_final_array() -> None:
    """Fast mode must match last interpreted step result."""
    adapter_fast = SortingAdapter()
    adapter_fast.execute("create_array", {"values": "9,4,7,1,5"})
    adapter_fast.execute("select_algorithm", {"algorithm_id": "burbuja"})
    fast = adapter_fast.execute("run", {"mode": "fast", "source_code": "void ordenar_burbuja(int a[], size_t n) {}"})

    adapter_step = SortingAdapter()
    adapter_step.execute("create_array", {"values": "9,4,7,1,5"})
    adapter_step.execute("select_algorithm", {"algorithm_id": "burbuja"})
    step = adapter_step.execute("run", {"mode": "step_by_step", "source_code": "void ordenar_burbuja(int a[], size_t n) {}"})

    assert fast["visual_state"]["items"] == step["visual_state"]["items"]
    assert fast["visual_state"]["items"] == sorted([9, 4, 7, 1, 5])
    assert len(step["execution_trace"]["steps"]) > 0


def test_invalid_empty_array_is_rejected() -> None:
    """Empty arrays should be rejected."""
    adapter = SortingAdapter()
    try:
        adapter.execute("create_array", {"values": ""})
        assert False, "Expected ValueError for empty array."
    except ValueError as exc:
        assert "obligatorio" in str(exc).lower()
