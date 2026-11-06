"""Finite all-algorithm boundary matrix for the general review."""
import pytest
from app.domain.sorting.tad_ordenamiento import SORTING_ALGORITHMS, SortingInterpreter, SortingExecutionError

@pytest.mark.parametrize('algorithm', [item['id'] for item in SORTING_ALGORITHMS])
@pytest.mark.parametrize('values', [[], [-3,-1,0,2], [4,4,4], [-999,-997,-998], [999,997,998]])
def test_all_algorithms_boundaries(algorithm, values):
    if not values:
        with pytest.raises(SortingExecutionError, match='vacío'):
            SortingInterpreter(values, algorithm).run()
    else:
        result = SortingInterpreter(values, algorithm).run()
        assert result['final_state']['items'] == sorted(values)
        assert result['steps']
