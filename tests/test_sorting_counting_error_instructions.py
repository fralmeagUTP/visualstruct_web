"""Failed Counting call traces: native causal oracles and read-only replay."""
from pathlib import Path
from dataclasses import replace
import json
import pytest
import hashlib
from _audit_approved_source_supersessions import assert_historical_protected_hash
from app import create_app
from app.domain.sorting.counting_sparse_instructions import SimulatedCountingAllocationFailure
from app.domain.sorting.tad_ordenamiento import SortingInterpreter
from app.services.counting_trace_service import get_counting_store
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-counting-error-instructions'

def null_allocator(_length):raise SimulatedCountingAllocationFailure('isolated QA only')
def prepare(c,values):
    assert c.post('/api/ordenamiento/create-array',json={'values':values}).status_code==200
    assert c.post('/api/ordenamiento/algorithm',json={'algorithm_id':'counting_sort'}).status_code==200
    return c.get('/api/ordenamiento/state').get_json()
def run(c):return c.post('/api/ordenamiento/run',json={'algorithm_id':'counting_sort','mode':'step_by_step'})
def forbid(*args,**kwargs):raise AssertionError('readonly replay must not execute any sorting method')

from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize('case',['range_two','range_eighty','null_two','null_negative_duplicates'])
def test_error_native_complete_events_retirement_and_unchanged_accepted_state(case):
    d=json.loads((audit_input_path(E/'native-errors'/(case+'.json'))).read_text(encoding='utf-8'))
    for ext in ['c','h']:assert_historical_protected_hash(ROOT,'docs/tads_C/tad_ordenamiento.'+ext,hashlib.sha256((audit_input_path(E/'native-errors'/('tad_ordenamiento.'+ext))).read_bytes()).hexdigest())
    app=create_app();app.testing=True
    if d['case']['simulated_calloc']:app.config['COUNTING_QA_ALLOCATOR']=null_allocator
    c=app.test_client();before=prepare(c,d['case']['input']);r=run(c);assert r.status_code==400
    data=r.get_json();t=data['execution_trace'];frames=t.get('steps')
    if frames is None:frames=sum((c.get(t['page_url'],query_string={'start':start,'limit':128}).get_json()['steps'] for start in range(0,len(d['native']),128)),[])
    assert len(frames)==len(d['native'])
    previous_vars={}
    for index,(native,frame) in enumerate(zip(d['native'],frames)):
        assert frame['debug']['instruction_event']=={k:v for k,v in native.items() if k!='case'}
        assert frame['state_snapshot']['items']==frame['state_after']['items']==d['case']['input']
        assert frame['state_snapshot']['auxiliary_array'] is None and frame['state_after']['auxiliary_array'] is None
        assert frame['line_text']==('' if frame['line_index'] is None else t['source_code'].splitlines()[frame['line_index']])
        assert frame['pedagogy']['invariant']['holds']
        for v in frame['pedagogy']['variables']:
            old=previous_vars.get((v['scope'],v['name']))
            assert v['previous']==(old['value'] if old else None)
            assert v['changed']==(old is None or (old['value'],old['initialized'])!=(v['value'],v['initialized']))
        previous_vars={(v['scope'],v['name']):v for v in frame['pedagogy']['variables']}
    assert data['history']==before['history'] and data['visual_state']==before['visual_state'] and data['main_c']==before['main_c']
    assert not t['success'] and not t['mutates'] and t['native_status']==0 and t['accepted_state']==before['visual_state']
    assert t['error']['simulated']==d['case']['simulated_calloc'] and not t['error']['real_c_execution']
    last=frames[-1];assert last['pedagogy']['concept']=='return' and not last['pedagogy']['variables'] and not last['pedagogy']['pointers'] and not last['pedagogy']['call_stack']
    assert 'return ORDENAMIENTO_ERROR' in last['line_text'] and last['state_after']['last_operation']['status']=='error'
    guard=frames[-2];assert guard['pedagogy']['condition']['result'] is True
    assert not last['state_after']['counting_context']['live'] and not last['state_after']['counting_context']['released']
    if d['case']['simulated_calloc']:
        ptr=next(v for v in guard['pedagogy']['variables'] if v['name']=='conteo');assert ptr['initialized'] and ptr['value']=='NULL'
        assert 'NULL' in frames[-3]['debug']['note']
    else:assert not any(f['debug']['instruction_event']['token']=='size_guard' for f in frames)

@pytest.mark.parametrize('values,simulated', [([0,1000000],False),([0]+[1000000]*79,False),([5,0],True)])
def test_error_owned_page_export_step_reload_do_not_dispatch_or_mutate(monkeypatch,values,simulated):
    app=create_app();app.testing=True
    if simulated:app.config['COUNTING_QA_ALLOCATOR']=null_allocator
    c=app.test_client();before=prepare(c,values);data=run(c).get_json();t=data['execution_trace'];key=t['trace_id']
    monkeypatch.setattr(SortingInterpreter,'run',forbid)
    with app.app_context():store=get_counting_store();entry=store.entries[key];records=json.dumps(entry.source.tape.records,sort_keys=True);expires=entry.expires
    assert app.test_client().get(t['page_url']).status_code==404
    page=c.get(t['page_url'],query_string={'concept':'return','occurrence':10000}).get_json();assert page['steps'][-1]['debug']['instruction_event']['token']=='error_return'
    export=c.get(t['export_url']).get_json()['compact_trace'];assert not export['success'] and not export['mutates'] and export['native_status']==0 and export['accepted_state']==before['visual_state']
    step=c.post('/api/ordenamiento/step',json={'algorithm_id':'counting_sort','cursor':999999,'direction':'next'});assert step.status_code==200 and step.get_json()['step']['debug']['instruction_event']['token']=='error_return' and not step.get_json()['execution_trace']['success']
    state=c.get('/api/ordenamiento/state').get_json();assert state['history']==before['history'] and state['main_c']==before['main_c'] and state['visual_state']==before['visual_state']
    html=c.get('/sorting/visualizador');assert html.status_code==200 and key.encode() in html.data
    with app.app_context():assert store.entries[key].expires==expires and json.dumps(store.entries[key].source.tape.records,sort_keys=True)==records
    with app.app_context():store.entries[key]=replace(entry,expires=0)
    assert c.get(t['page_url']).status_code==410 and c.get(t['export_url']).status_code==410 and c.post('/api/ordenamiento/step',json={'algorithm_id':'counting_sort'}).status_code==410
    assert c.get('/api/ordenamiento/state').get_json()['history']==before['history']

@pytest.mark.parametrize('testing',[False,True])
def test_QA_hook_testing_only_public_input_ignored_and_retry(testing):
    app=create_app();app.testing=testing;app.config['COUNTING_QA_ALLOCATOR']=null_allocator;c=app.test_client();prepare(c,[5,0])
    response=c.post('/api/ordenamiento/run',json={'algorithm_id':'counting_sort','mode':'fast','simulate_calloc_failure':True,'COUNTING_QA_ALLOCATOR':'null'})
    assert response.status_code==(400 if testing else 200)
    if testing:
        trace=response.get_json()['execution_trace'];assert trace['error']['origin']=='qa-injection' and trace['error']['simulated'] and 'simulado' in trace['error']['label']
        app.config.pop('COUNTING_QA_ALLOCATOR');good=run(c).get_json();assert good['success'] and sum(x['operation']=='run' for x in good['history'])==1
        html=c.get('/sorting/visualizador').data;assert trace['trace_id'].encode() not in html
    else:assert response.get_json()['success']

def test_plain_python_memory_failure_is_not_real_C_or_labeled_native_simulation():
    app=create_app();app.testing=True
    def fail(_):raise MemoryError('controlled model failure, not real exhaustion')
    app.config['COUNTING_QA_ALLOCATOR']=fail;c=app.test_client();prepare(c,[5,0]);t=run(c).get_json()['execution_trace'];assert t['error']['origin']=='python-model-allocation' and not t['error']['simulated'] and not t['error']['real_c_execution']

def test_transport_storage_failure_has_no_fabricated_native_ERROR():
    app=create_app();c=app.test_client();before=prepare(c,[5,0])
    with app.app_context():get_counting_store().max_bytes=1
    r=run(c);assert r.status_code==400;d=r.get_json();assert 'execution_trace' not in d and 'native_status' not in d and d['history']==before['history'] and d['visual_state']==before['visual_state']

def test_reset_revokes_error_source_and_new_input_clears_failed_attempt():
    app=create_app();c=app.test_client();prepare(c,[0,1000000]);old=run(c).get_json()['execution_trace'];prepare(c,[3,1]);assert old['trace_id'].encode() not in c.get('/sorting/visualizador').data
    c.post('/api/ordenamiento/reset',json={});assert c.get(old['page_url']).status_code==404 and c.get('/api/ordenamiento/state').get_json()['history']==[]


def test_failed_attempt_after_accepted_run_preserves_existing_main_and_latest_trace(monkeypatch):
    app=create_app();app.testing=True;c=app.test_client();prepare(c,[5,0]);accepted=run(c).get_json();old=accepted['execution_trace'];before=c.get('/api/ordenamiento/state').get_json()
    app.config['COUNTING_QA_ALLOCATOR']=null_allocator;failed=run(c).get_json();t=failed['execution_trace']
    assert not failed['success'] and failed['history']==before['history'] and failed['main_c']==before['main_c'] and failed['visual_state']==before['visual_state']
    assert sum(x['operation']=='run' for x in failed['history'])==1 and t['trace_id']!=old['trace_id'] and t['accepted_state']==before['visual_state']
    monkeypatch.setattr(SortingInterpreter,'run',forbid)
    html=c.get('/sorting/visualizador').data;assert t['trace_id'].encode() in html and old['trace_id'].encode() not in html
    assert c.get(old['page_url']).status_code==200 and c.get('/api/ordenamiento/state').get_json()==before
