"""Focal checks of conservative pending-source classification."""
from scripts.build_pending_quality_links import concrete

def case(expression,value):
    return {'expected':{'assertions':[{'expression':expression,'literal_expected':[value]}]}}

def test_generic_success_or_nonempty_trace_is_not_concrete():
    assert not concrete(case("data['success'] is True",True))
    assert not concrete(case("len(data['execution_trace']['steps']) > 0",0))

def test_explicit_state_and_literal_page_content_are_concrete():
    assert concrete(case("data['visual_state']['items'] == [3,2,1]",[3,2,1]))
    assert concrete(case("b'/help/manual' in response.data",{'bytes_hex':'00'}))

def test_provider_error_and_status_alone_are_not_concrete():
    assert not concrete(case('response.status_code == 400',400))
    assert not concrete(case("data['message'] == 'provider unavailable'",'provider unavailable'))
