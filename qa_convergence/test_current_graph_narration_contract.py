"""Negative controls: the presentation-isolation experiment must not be vacuous."""
from copy import deepcopy
from unittest.mock import patch
import pytest
import _canonical_publication_contract as contract
from app.domain.graph import book_trace


@pytest.mark.parametrize('invoke_but_ignore', [False, True])
def test_narration_experiment_rejects_unused_rewording(invoke_but_ignore):
    # Deliberately incomplete fake execution: these controls must fail before
    # any execution projection could mistakenly certify an unchanged result.
    body = {'execution_trace': {'steps': [{'pedagogy': {
        'narration': {'basic': 'original'}, 'phase': {'goal': 'original'}},
        'debug': {'note': 'original'}}]}}
    def unchanged(*args):
        if invoke_but_ignore:
            book_trace._text({'phase': 'function_exit'}, {})
        return deepcopy(body)
    expected = 'no cambió la presentación' if invoke_but_ignore else 'no invocó'
    with patch.object(contract, 'execute', side_effect=unchanged):
        with pytest.raises(AssertionError, match=expected):
            contract.assert_narration_does_not_change_execution('insert_vertex', {'vertex': 7}, [])
