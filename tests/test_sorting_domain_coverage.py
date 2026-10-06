"""Boundary and validation coverage for the sorting domain interpreter."""

from __future__ import annotations

import pytest

from app.domain.sorting.tad_ordenamiento import (
    SortingExecutionError,
    SortingInterpreter,
)


def test_sorting_interpreter_rejects_unknown_algorithm() -> None:
    with pytest.raises(SortingExecutionError, match="no existe"):
        SortingInterpreter([3, 1], "bogosort")


def test_sorting_interpreter_rejects_empty_array() -> None:
    with pytest.raises(SortingExecutionError, match="vacio"):
        SortingInterpreter([], "quicksort").run()


def test_single_element_quicksort_uses_recursive_base_case() -> None:
    result = SortingInterpreter([7], "quicksort").run()
    assert result["final_state"]["items"] == [7]
    # Current C executes inclusive scan and self-swap even for n=1.
    assert {k: result["metrics"][k] for k in ("comparisons", "swaps", "moves")} == {"comparisons": 3, "swaps": 1, "moves": 3}
    assert len(result["steps"]) == 32
    tokens = [step["line_token"] for step in result["steps"]]
    assert tokens.count("i_test") == tokens.count("j_test") == tokens.count("cross_test") == 1
    assert tokens.count("swap_temp") == tokens.count("swap_assign_a") == tokens.count("swap_assign_b") == 1
    assert all(step["array_snapshot"] == [7] for step in result["steps"])
    event = result["steps"][-1]["instruction_event"]
    assert event["frames"] == [] and event["token"] == "sort_return"


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([-12, 3, -1, 0, 25, -12], [-12, -12, -1, 0, 3, 25]),
        ([-9, -100, -2], [-100, -9, -2]),
    ],
)
def test_radixsort_orders_negative_and_mixed_values(
    values: list[int], expected: list[int]
) -> None:
    result = SortingInterpreter(values, "radixsort").run()
    assert result["final_state"]["items"] == expected
    # Real helper instruction and scoped uint32 digit selection, not aggregate marker.
    steps = result["steps"]
    selected = [i for i, step in enumerate(steps) if step["line_token"] == "digit_select"]
    assert selected
    for i in selected:
        step = steps[i]
        ctx = step["radix_context"]
        assert step["source_function"] == "counting_por_digito"
        assert ctx["wrapper_active"] and ctx["helper_active"] and ctx["helper_declared"]
        assert ctx["buffers"]["output"]["live"] and ctx["group"] in {"negative", "positive"}
        assert ctx["digito"] == (ctx["valor"] // ctx["helper_exp"]) % 10
        assert steps[i - 1]["line_token"] == "digit_value_read"
        assert steps[i + 1]["line_token"] == "digit_output_write"
        assert steps[i + 2]["line_token"] == "digit_frequency_decrement"
        event = step["instruction_event"]
        assert event["token"] == "digit_select" and event["digito"] == ctx["digito"]
        assert event["array"] == step["array_snapshot"]
    last = steps[-1]
    event = last["instruction_event"]
    ctx = last["radix_context"]
    assert event["token"] == "radix_return" and event["return_status"] == 1
    assert event["allocations"] == event["frees"] and event["live"] == 0
    assert not ctx["wrapper_active"] and not ctx["helper_active"] and not ctx["valid_active"]
    assert all(not buf["live"] and buf["cells"] is None for buf in ctx["buffers"].values())
    assert result["metrics"]["comparisons"] == event["max_value_comparisons"]
    assert result["metrics"]["moves"] == sum(event[k] for k in ["work_writes", "count_writes", "digit_output_writes", "caller_writes"])
