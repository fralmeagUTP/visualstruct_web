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
    assert result["metrics"]["comparisons"] == 0


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
    assert any(
        step["line_token"] == "radix_digit" for step in result["steps"]
    )
