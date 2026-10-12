"""Retained Sorting semantics under migration; not universal C-event certification."""
from collections import Counter
from copy import deepcopy
import pytest
from app.domain.sorting.tad_ordenamiento import SortingInterpreter, SortingExecutionError, ORDENAMIENTO_RANGO_MAX
from test_sorting17_retained_units import invariants, context

ALGORITHMS = ['intercambio', 'seleccion', 'insercion', 'burbuja', 'shell', 'counting_sort', 'radixsort']
CASES = [pytest.param([1, 2, 3, 4], id='ordered'), pytest.param([4, 3, 2, 1], id='reverse'), pytest.param([2, 2, 1, 1], id='duplicates'), pytest.param([-3, 0, -1, 0], id='mixed')]

@pytest.mark.parametrize('algorithm', ALGORITHMS)
@pytest.mark.parametrize('values', CASES)
def test_retained_seven_semantic_partitions(algorithm, values, request):
    original = list(values)
    context('public-engine:' + request.node.nodeid)
    current = SortingInterpreter(values, algorithm).run()
    assert values == original
    assert current['final_state']['items'] == sorted(original)
    context('retained-body:' + request.node.nodeid)
    obj = SortingInterpreter(values, algorithm)
    getattr(obj, '_run_' + algorithm)()
    assert obj.values == sorted(original) == current['final_state']['items']
    assert Counter(obj.values) == Counter(original) and values == original
    n = len(original)
    if algorithm in {'intercambio', 'seleccion'}:
        assert obj.metrics.comparisons == n * (n - 1) // 2
    if algorithm == 'insercion':
        inversions = sum(original[i] > original[j] for i in range(n) for j in range(i + 1, n))
        assert obj.metrics.moves == 2 * (n - 1) + inversions and obj.metrics.swaps == 0
    if algorithm == 'burbuja':
        assert obj.metrics.moves == 3 * obj.metrics.swaps
        if original == sorted(original):
            assert obj.metrics.swaps == 0
            assert any(step['line_token'] == 'break' for step in obj._steps)
    if algorithm == 'counting_sort':
        assert obj.metrics.comparisons == 2 * (n - 1)
        assert obj.metrics.moves == 3 * n and obj.metrics.swaps == 0
    invariants(obj, original)

@pytest.mark.parametrize('exp', [1, 10, 100])
def test_retained_decimal_digit_is_stable_and_owned(exp, request):
    context('retained-helper:' + request.node.nodeid)
    original = [21, 11, 12, 22, 0, 30]
    values = list(original)
    obj = SortingInterpreter(values, 'radixsort')
    work = list(original)
    obj._counting_digit(work, exp)
    # Stable decimal-key sorting is an independent oracle; equal digits retain order.
    expected = sorted(original, key=lambda number: (number // exp) % 10)
    assert work == expected and Counter(work) == Counter(original)
    assert values == original and obj.values == original
    assert obj.metrics.moves == len(original) and obj.metrics.comparisons == 0
    assert len(obj._steps) == obj.metrics.steps == 1
    step = obj._steps[0]
    assert step['auxiliary_snapshot'] == expected and step['array_snapshot'] == original
    saved = deepcopy(step)
    work[0] += 100
    assert step == saved
    step['auxiliary_snapshot'][0] += 200
    assert values == original and obj.values == original

def test_retained_counting_range_guard_preserves_values(request):
    context('range-guard:' + request.node.nodeid)
    original = [0, ORDENAMIENTO_RANGO_MAX]
    for method in ('retained', 'public'):
        values = list(original)
        obj = SortingInterpreter(values, 'counting_sort')
        with pytest.raises(SortingExecutionError, match='rango'):
            obj._run_counting_sort() if method == 'retained' else obj.run()
        assert values == original and obj.values == original
        assert obj._steps == [] and obj.metrics.moves == obj.metrics.comparisons == 0
