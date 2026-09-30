from collections import Counter

import pytest

from app.adapters.red_black_adapter import RedBlackAdapter
from app.adapters.sorting_adapter import SortingAdapter
from app.domain.sorting.tad_ordenamiento import ORDENAMIENTO_RANGO_MAX, SortingExecutionError, SortingInterpreter
from app.services.hierarchical_structure_service import HierarchicalStructureService


@pytest.mark.parametrize("algorithm", ["counting_sort", "binsort"])
def test_counting_family_rejects_excessive_range_before_auxiliary_allocation(algorithm):
    with pytest.raises(SortingExecutionError, match="supera el máximo"):
        SortingInterpreter([-(2**31), 2**31 - 1], algorithm).run()


@pytest.mark.parametrize("algorithm", ["counting_sort", "binsort"])
def test_counting_family_accepts_documented_boundary_and_preserves_multiset(algorithm):
    values = [ORDENAMIENTO_RANGO_MAX - 1, 0, 7, 7]
    result = SortingInterpreter(values, algorithm).run()["final_state"]["items"]
    assert result == sorted(values)
    assert Counter(result) == Counter(values)


@pytest.mark.parametrize("algorithm", ["counting_sort", "binsort"])
def test_counting_rejection_is_identical_in_fast_and_step_modes(algorithm):
    for mode in ("fast", "step_by_step"):
        adapter = SortingAdapter()
        adapter.execute("create_array", {"values": [-(2**31), 2**31 - 1]})
        adapter.execute("select_algorithm", {"algorithm_id": algorithm})
        with pytest.raises(SortingExecutionError, match="supera el máximo"):
            adapter.execute("run", {"mode": mode, "source_code": ""})


@pytest.mark.parametrize(
    "sequence,deletions",
    [
        ([7, 3, 18, 10, 22, 8, 11, 26], [3, 10, 22]),
        ([11, 2, 14, 1, 7, 15, 5, 8, 4], [14, 1, 2, 7]),
        ([20, 10, 30, 5, 15, 25, 35, 1, 6], [1, 5, 10, 20]),
    ],
)
def test_rbt_leaf_one_child_two_children_and_fixup_preserve_invariants(sequence, deletions):
    adapter = RedBlackAdapter()
    remaining = set(sequence)
    for value in sequence:
        adapter.execute("insertar", {"value": value})
    for value in deletions:
        adapter.execute("eliminar", {"value": value})
        remaining.discard(value)
        state = adapter.to_visual_state()
        assert state["validation"] is True
        assert state["traversals"]["inorden"] == sorted(remaining)
        if state["root"] is not None:
            assert state["root"]["color"] == "BLACK"


def test_rbt_delete_trace_tracks_logical_nodes_and_real_leaf_branch():
    history = []
    for value in (7, 3, 18, 10, 22, 8, 11, 26):
        result = HierarchicalStructureService.execute_operation("red_black", "insertar", {"value": value}, history)
        history = result["history"]
    result = HierarchicalStructureService.execute_operation("red_black", "eliminar", {"value": 3}, history)
    steps = result["execution_trace"]["steps"]
    lines = [str(step.get("line_text", "")).strip() for step in steps]
    assert "x = z->der;" in lines and "x = z->izq;" not in lines
    assert lines.count("while (z != NULL && z->nro != key) {") == 2
    assert steps[-1]["state_after"]["size"] == 7
    assert next(step for step in steps if str(step.get("line_text", "")).strip() == "free(z);")["state_after"]["size"] == 8
    logical = [step["debug"]["logical_nodes"] for step in steps if step.get("debug", {}).get("logical_nodes")]
    assert any(set(nodes) == {"z", "y", "x", "x_parent", "w"} for nodes in logical)
