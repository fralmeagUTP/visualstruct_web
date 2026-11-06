"""Finite stdout checks keep whitespace, duplicates, snapshots and causal order."""
import pytest
from e2e_trace_contracts import trace_stdout

@pytest.mark.parametrize('mode,expected', [
    ('events', ['', ' same \n', ' same \n\n same \n\n', ' same \n\n same \n\n\nlast']),
    ('snapshot', ['', ' same \n', ' same \n\n', 'last']),
])
def test_trace_stdout_preserves_every_chunk_and_cursor(mode, expected):
    trace={'console_mode':mode,'steps':[{'console':[' same \n']},
           {'console':[' same \n','']},{'console':['last']}]}
    assert [trace_stdout(trace,i) for i in range(-1,3)]==expected
    assert [trace_stdout(trace,i) for i in range(2,-2,-1)]==expected[::-1]


def test_raw_stdout_takes_precedence_without_normalizing_bytes():
    trace={'steps':[{'console_stdout':' 7\n7\n','console':['host feedback']} ]}
    assert trace_stdout(trace,-1)==''
    assert trace_stdout(trace,0)==' 7\n7\n'

@pytest.mark.parametrize('trace,cursor',[
    ({'steps':[{'console_stdout':None}]},0),
    ({'console_mode':'unknown','steps':[{'console':[]}]},0),
    ({'console_mode':'events','steps':[{'console':[7]}]},0),
    ({'steps':[{}]},1),
    ({'steps':[{}]},-2),
])
def test_stdout_observer_rejects_uncontracted_or_invalid_data(trace,cursor):
    with pytest.raises(AssertionError):trace_stdout(trace,cursor)


@pytest.mark.parametrize('missing', ['allocation_failure','execution_started','success','error'])
def test_implicit_events_are_limited_to_declared_allocation_failure(missing):
    trace={'allocation_failure':True,'execution_started':True,'success':False,
           'error':{'code':'allocation_failed'},'steps':[{'console':[' same \n']},{'console':[' same \n','']}]}
    assert trace_stdout(trace,1)==' same \n\n same \n\n'
    del trace[missing]
    with pytest.raises(AssertionError): trace_stdout(trace,1)


def test_unlabelled_regular_trace_is_not_silently_reinterpreted_as_events():
    with pytest.raises(AssertionError):trace_stdout({'steps':[{'console':['result']}]},0)


from test_sequential_acceptance_criteria_focal import FAULTS
@pytest.mark.parametrize('fault', FAULTS, ids=lambda f:f[0])
def test_actual_allocation_failure_stdout_matches_reached_C_printf(tmp_path,fault):
    from app.services.structure_service import StructureService
    from app.services.execution_trace_service import ExecutionTraceService
    name,family,op,payload,module,class_name,field=fault
    seeds=[('insertar_padre',{'parent':7}),('insertar_hijo',{'parent':7,'child':3})] if family=='sublist' else [('insertar_final',{'value':7}),('insertar_final',{'value':8})]
    if family=='stack':seeds=[('apilar',{'value':7})]
    elif family=='queue':seeds=[('encolar',{'value':7})]
    elif family=='priority_queue':seeds=[('encolar',{'value':7,'priority':2})]
    history=[]
    for seed,values in seeds:
        data=StructureService.execute_operation(family,seed,values,history);assert data['success'];history=data['history']
    from app.domain.sequential.allocation_failure_instruction import build_allocation_failure_trace
    trace=build_allocation_failure_trace(structure_id=family,operation_name=op,payload=payload,
        didactic_data=StructureService._didactic_content(family),before_state=data['visual_state'])
    assert trace['allocation_failure'] and not trace['success']
    reached=[];expected=['']
    for step in trace['steps']:
        value=ExecutionTraceService._printf_literal(step['line_text'],preserve_trailing_newlines=True) if step['line_text'].strip().startswith('printf(') else None
        assert step['console']==([] if value is None else [value])
        if value is not None:reached.append(value)
        expected.append('\n'.join(reached))
    assert [trace_stdout(trace,i) for i in range(-1,len(trace['steps']))]==expected
    assert [trace_stdout(trace,i) for i in range(len(trace['steps'])-1,-2,-1)]==expected[::-1]
    import json,subprocess
    from pathlib import Path
    path=tmp_path/'trace.json';path.write_text(json.dumps(trace))
    run=subprocess.run(['node','qa/emit_e2e_allocation_stdout.js',str(path)],cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True,timeout=30)
    assert run.returncode==0,run.stderr
    for row in json.loads(run.stdout):
        output=expected[row['cursor']+1]
        assert row['raw']==output and row['text']==(output or '(sin salida printf en esta ruta)')


@pytest.mark.parametrize('mode',[None,'unknown','snapshot'])
def test_allocation_observer_rejects_explicit_conflicting_modes(mode):
    trace={'console_mode':mode,'allocation_failure':True,'execution_started':True,'success':False,
           'error':{'code':'allocation_failed'},'steps':[{'console':[' 7\n']}]}
    with pytest.raises(AssertionError):trace_stdout(trace,0)
    trace['steps'][0]['console_stdout']=' 7\n'
    with pytest.raises(AssertionError):trace_stdout(trace,0)
