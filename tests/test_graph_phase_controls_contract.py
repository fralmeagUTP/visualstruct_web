"""Do not satisfy a phase census by selecting hidden or incomplete controls."""
import pytest
from _graph_phase_controls_contract import PUBLIC_OPERATIONS, assert_public_graph_phase_controls


@pytest.mark.parametrize('phase', PUBLIC_OPERATIONS)
@pytest.mark.parametrize('mutation', ['none', 'hidden_active', 'visible_inactive', 'missing_option', 'extra_option', 'duplicate_option', 'wrong_selector'])
def test_public_phase_control_census(phase, mutation):
    selector = '#graph-operation-select' if phase == 'construccion' else '#graph-algorithm-select'
    options = sorted(PUBLIC_OPERATIONS[phase])
    active, inactive = True, False
    if mutation == 'hidden_active': active = False
    elif mutation == 'visible_inactive': inactive = True
    elif mutation == 'missing_option': options.pop()
    elif mutation == 'extra_option': options.append('fake_operation')
    elif mutation == 'duplicate_option': options.append(options[0])
    elif mutation == 'wrong_selector': selector = '#hidden-operation'
    if mutation == 'none':
        assert_public_graph_phase_controls(phase, selector, options, active, inactive)
    else:
        with pytest.raises(AssertionError):
            assert_public_graph_phase_controls(phase, selector, options, active, inactive)
