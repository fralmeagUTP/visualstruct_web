"""Adversarial checks for the current caller plus unchanged historical consumer."""
from copy import deepcopy
import pytest
from app.services.hash_structure_service import HashStructureService as Service
from _hash_visible_caller_consumer_oracle import assert_hash_current_visible_contract


def execute(operation, payload, history):
    return Service.execute_operation('hash_table', operation, payload, history)


@pytest.fixture(scope='module')
def ordinary():
    history=[]
    results=[]
    for operation,payload in [('create_table',{'capacity':17}), ('insert',{'key':1,'value':10}),
                              ('get',{'key':1}), ('get',{'key':99}), ('contains',{'key':1}),
                              ('stats',{}), ('keys',{}), ('values',{}), ('items',{}),
                              ('remove',{'key':1}), ('clear',{}), ('destroy_table',{})]:
        result=execute(operation,payload,history)
        results.append(result);history=result['history']
    return results


def test_ordinary_callers_and_void_cleanup_preserve_all_original_obligations(ordinary):
    for result in ordinary:
        assert_hash_current_visible_contract(result)


@pytest.mark.parametrize('fault',['source','line','role','executed','source_index','index','state',
    'debug_storage','memory','pedagogy_source','cumulative','total','missing','boundary','tad_line',
    'tad_console','diagnostic_with_caller'])
def test_complete_current_hash_consumer_rejects_corruption(ordinary,fault):
    result=deepcopy(ordinary[1]);trace=result['execution_trace'];steps=trace['steps']
    first=next(i for i,s in enumerate(steps) if s['event_type']=='caller_printf');step=steps[first]
    if fault=='source':trace['caller_source_code']+='\n'
    elif fault=='line':step['instruction_event']['caller_line_text']='printf("forged");'
    elif fault=='role':step['instruction_event']['source_role']='tad'
    elif fault=='executed':step['instruction_event']['C_executed']=False
    elif fault=='source_index':step['line_index']=0
    elif fault=='index':step['step_index']+=1
    elif fault=='state':step['state_after']={}
    elif fault=='debug_storage':step['debug']['forged_storage']=1
    elif fault=='memory':step['pedagogy']['memory']={}
    elif fault=='pedagogy_source':step['pedagogy']['source']['function']='fake'
    elif fault=='cumulative':step['console_stdout']='forged'
    elif fault=='total':result['console_stdout']='forged'
    elif fault=='missing':
        trace['steps']=steps[:first];trace['console_stdout']=result['console_stdout']=''
    elif fault=='boundary':steps[first-1]['debug']['token']='not_a_return'
    elif fault=='tad_line':steps[first-1]['line_text']='not actual C'
    elif fault=='tad_console':steps[first-1]['console']=['forged']
    else:trace['payload']['simulate_allocation_failure']='1'
    with pytest.raises(AssertionError):assert_hash_current_visible_contract(result)


def test_diagnostic_without_stdout_is_explicit_and_cannot_mask_ordinary_missing_caller(ordinary):
    history=ordinary[0]['history']
    result=execute('insert',{'key':1,'value':10,'simulate_allocation_failure':'1'},history)
    assert not any(s['event_type']=='caller_printf' for s in result['execution_trace']['steps'])
    assert_hash_current_visible_contract(result)
    # With a real return and no diagnostic exemption, silence is not accepted.
    current=deepcopy(ordinary[1]);trace=current['execution_trace']
    trace['steps']=[s for s in trace['steps'] if s['event_type']!='caller_printf']
    trace['console_stdout']=current['console_stdout']=''
    with pytest.raises(AssertionError):assert_hash_current_visible_contract(current)


@pytest.mark.parametrize('branch',['ordinary','diagnostic','void'])
def test_full_consumer_rejects_premature_stdout_in_every_silent_branch(ordinary,branch):
    if branch=='ordinary':result=deepcopy(ordinary[1])
    elif branch=='void':result=deepcopy(ordinary[-1])
    else:result=execute('insert',{'key':1,'value':10,'simulate_allocation_failure':'1'},ordinary[0]['history'])
    assert_hash_current_visible_contract(result)
    result['execution_trace']['steps'][0]['console_stdout']='FORGED\n'
    with pytest.raises(AssertionError):assert_hash_current_visible_contract(result)


def test_independent_native_gate_rejects_coordinated_caller_byte_forgery(client,tmp_path,monkeypatch):
    # The structural consumer is not an independent C formatting oracle. This
    # negative invokes the actual native gate and proves it detects synchronized
    # wrong fragment/cumulative/trace/body/journal bytes, not only inconsistency.
    from app.services import hash_caller_stdout
    import test_hash_caller_stdout as native_gate
    original=hash_caller_stdout.attach_caller_stdout
    def forge(trace,operation,payload,state):
        output=original(trace,operation,payload,state)
        if operation!='create_table':return output
        total=''
        for step in trace['steps']:
            if step['event_type']=='caller_printf':
                step['console']=['FORGED\n'];total+='FORGED\n'
                step['console_stdout']=total
                step['pedagogy']['caller_stdout']=total
        trace['console_stdout']=total
        return total
    monkeypatch.setattr(hash_caller_stdout,'attach_caller_stdout',forge)
    calls=[];native=native_gate.native
    def run_native(*args):
        result=native(*args);calls.append(result);return result
    monkeypatch.setattr(native_gate,'native',run_native)
    with pytest.raises(AssertionError):
        native_gate.test_hash_journal_stdout_matches_native_c17(client,tmp_path,[('create_table',{'capacity':3}),('insert',{'key':1,'value':10}),('get',{'key':1})])
    assert len(calls)==1 and 'FORGED' not in calls[0]
