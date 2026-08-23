from collections import Counter

import pytest

from app.adapters.sorting_adapter import SortingAdapter
from app.domain.sorting.tad_ordenamiento import SortingExecutionError, SortingInterpreter
from scripts.check_c_conformance import run_checks


INT_MIN = -(2**31)
INT_MAX = 2**31 - 1


@pytest.mark.parametrize(
    "values",
    [
        [INT_MIN],
        [INT_MIN, INT_MAX, -1, 0, 1],
        [INT_MIN, INT_MIN, -1, 0, 7, 7, INT_MAX],
        [-9, -1, -10, -9],
        [0],
    ],
)
def test_radix_python_boundary_cases_preserve_multiset_and_order(values):
    result = SortingInterpreter(values, "radixsort").run()["final_state"]["items"]
    assert result == sorted(values)
    assert Counter(result) == Counter(values)


def test_radix_fast_and_step_modes_match_at_integer_limits():
    values = [INT_MAX, INT_MIN, 0, -1, INT_MIN, 7]
    outputs = []
    for mode in ("fast", "step_by_step"):
        adapter = SortingAdapter()
        adapter.execute("create_array", {"values": values})
        adapter.execute("select_algorithm", {"algorithm_id": "radixsort"})
        result = adapter.execute("run", {"mode": mode, "source_code": ""})
        outputs.append(result["visual_state"]["items"])
    assert outputs[0] == outputs[1] == sorted(values)


def test_radix_empty_input_remains_a_typed_invalid_case():
    with pytest.raises(SortingExecutionError, match="vacio"):
        SortingInterpreter([], "radixsort").run()


def test_radix_c17_harness_covers_int_min_boundary():
    run_checks(compiler="gcc", sanitizers=False, only={"sorting"}, qa_events=True)
