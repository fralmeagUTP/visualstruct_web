"""Historical native comparisons retain returns without reviving dead frames."""
import pytest
from _instruction_context_contract import context_stack

def test_completed_context_keeps_return_value_and_live_stack_separate():
    live={'frame_id':'caller','scope_status':'activo','return':None}
    done={'frame_id':'F1','scope_status':'terminado (contexto del retorno)','return':'N1'}
    frame={'call_stack':[live],'completed_call_stack':[done]}
    assert context_stack(frame)==[live,done]
    assert frame['call_stack']==[live] and frame['completed_call_stack']==[done]

def test_reintroduced_or_unfinished_completed_frame_is_rejected():
    frame={'frame_id':'F1','scope_status':'terminado','return':'N1'}
    with pytest.raises(AssertionError):context_stack({'call_stack':[frame],'completed_call_stack':[frame]})
    with pytest.raises(AssertionError):context_stack({'call_stack':[],'completed_call_stack':[{**frame,'scope_status':'activo'}]})
