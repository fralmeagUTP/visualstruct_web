"""Binsort-specific causal, ownership, and full-domain sparse regression gates."""
from scripts.published_test_inputs import audit_input_path
from pathlib import Path
from dataclasses import replace
import json, hashlib
import pytest
from _audit_approved_source_supersessions import assert_historical_protected_hash
from app import create_app
from app.domain.sorting.tad_ordenamiento import SortingInterpreter
from app.domain.sorting.binsort_instructions import BinsortTape
from app.domain.sorting.counting_sparse_tape import expand_small
from app.domain.sorting.counting_sparse_instructions import SimulatedCountingAllocationFailure
from app.services.counting_trace_service import get_counting_store
ROOT=Path(__file__).resolve().parents[1]
C=ROOT/'openspec/changes/audit-local-quality-and-unified-controls'
LOW=C/'evidence/visible-sorting-binsort-baseline-low'
ERR=C/'evidence/visible-sorting-counting-error-instructions/native-errors'

def prepare(values, allocator=None):
 app=create_app();app.testing=True
 if allocator:app.config['COUNTING_QA_ALLOCATOR']=allocator
 c=app.test_client();assert c.post('/api/ordenamiento/create-array',json={'values':values}).status_code==200
 assert c.post('/api/ordenamiento/algorithm',json={'algorithm_id':'binsort'}).status_code==200
 return app,c,c.get('/api/ordenamiento/state').get_json()
def run(c):return c.post('/api/ordenamiento/run',json={'algorithm_id':'binsort','mode':'step_by_step'})
def null(_):raise SimulatedCountingAllocationFailure('isolated QA only')
def forbidden(*a,**kw):raise AssertionError('immutable replay dispatched sorting')

def check_vars(frames):
 prior={}
 for f in frames:
  assert f['pedagogy']['invariant']['holds']
  for v in f['pedagogy']['variables']:
   old=prior.get((v['scope'],v['name']))
   assert v['previous']==(old['value'] if old else None)
   assert v['changed']==(old is None or (old['value'],old['initialized'])!=(v['value'],v['initialized']))
  prior={(v['scope'],v['name']):v for v in f['pedagogy']['variables']}

def all_frames(c,t):
 if 'steps' in t:return t['steps']
 return sum((c.get(t['page_url'],query_string={'start':i,'limit':128}).get_json()['steps'] for i in range(0,t['step_count'],128)),[])

@pytest.mark.parametrize('case',['single','normal','negative_duplicates','outside_five','range_six','eighty_equal','near_min','range_thousand'])
def test_binsort_all_native_events_before_after_and_suspended_wrapper(case):
 d=json.loads((audit_input_path(LOW/'native'/(case+'.json'))).read_text(encoding='utf-8'))
 app,c,_=prepare(d['case']['input']);response=run(c).get_json();t=response['execution_trace'];frames=all_frames(c,t)
 assert len(frames)==len(d['native']);check_vars(frames)
 for i,(native,f) in enumerate(zip(d['native'],frames)):
  event=dict(f['debug']['instruction_event'])
  if isinstance(event['conteo'],dict):event['conteo']=expand_small(event['conteo'])
  assert event=={k:v for k,v in native.items() if k!='case'}
  assert f['state_after']['items']==native['array']
  assert f['state_snapshot']['items']==d['native'][max(0,i-1)]['array']
  assert f['line_text']==('' if f['line_index'] is None else t['source_code'].splitlines()[f['line_index']])
  stack=[x['function'] for x in f['pedagogy']['call_stack']]
  if i not in (0,len(frames)-1):assert stack[0]=='ordenar_binsort'
  assert not f['debug']['console_events']
 assert [x['function'] for x in frames[-2]['pedagogy']['call_stack']]==['ordenar_binsort']
 assert not frames[-1]['pedagogy']['variables'] and not frames[-1]['pedagogy']['pointers'] and not frames[-1]['pedagogy']['call_stack']
 assert t['native_status']==1 and frames[-1]['debug']['native_status']==1
 assert frames[2]['pedagogy']['concept']=='call' and 'return ordenar_counting_sort' in frames[2]['line_text']

@pytest.mark.parametrize('case',['range_two','range_eighty','null_two','null_negative_duplicates'])
def test_binsort_complete_native_delegated_ERROR_and_parent_retirement(case):
 d=json.loads((audit_input_path(ERR/(case+'.json'))).read_text(encoding='utf-8'));app,c,before=prepare(d['case']['input'],null if d['case']['simulated_calloc'] else None)
 r=run(c);assert r.status_code==400;data=r.get_json();t=data['execution_trace'];frames=all_frames(c,t);native=d['native']
 assert len(frames)==len(native)+3;check_vars(frames)
 observed=json.loads((audit_input_path(C/'evidence/visible-sorting-binsort-instructions/native-errors'/(case+'.json'))).read_text(encoding='utf-8'))['native']
 assert len(frames)==len(observed)
 for f,n in zip(frames,observed):assert f['debug']['instruction_event']=={k:v for k,v in n.items() if k!='case'}
 for f,n in zip([frames[0],*frames[3:-1]],native):assert f['debug']['instruction_event']=={k:v for k,v in n.items() if k!='case'}
 assert frames[-2]['debug']['instruction_event']['token']=='error_return'
 assert [x['function'] for x in frames[-2]['pedagogy']['call_stack']]==['ordenar_binsort']
 assert frames[-1]['debug']['instruction_event']['token']=='binsort_return' and frames[-1]['debug']['native_status']==0
 assert not frames[-1]['pedagogy']['call_stack'] and not frames[-1]['pedagogy']['variables']
 assert not t['success'] and not t['mutates'] and t['native_status']==0
 assert t['error']['simulated']==d['case']['simulated_calloc'] and not t['error']['real_c_execution']
 assert data['visual_state']==before['visual_state'] and data['history']==before['history'] and data['main_c']==before['main_c']

@pytest.mark.parametrize('values,allocator',[([3,1,2],None),([0,999999],None),([0,1000000],None),([5,0],null)])
def test_binsort_owned_immutable_replay_export_reload_expiry_reset(monkeypatch,values,allocator):
 app,c,before=prepare(values,allocator);data=run(c).get_json();t=data['execution_trace'];key=t['trace_id'];accepted=c.get('/api/ordenamiento/state').get_json()
 monkeypatch.setattr(SortingInterpreter,'run',forbidden)
 with app.app_context():store=get_counting_store();entry=store.entries[key];original=json.dumps(entry.source.tape.records,sort_keys=True)
 assert app.test_client().get(t['page_url']).status_code==404
 last=c.get(t['page_url'],query_string={'concept':'return','occurrence':99999999}).get_json()['steps'][0]
 assert last['debug']['instruction_event']['token']=='binsort_return'
 assert c.get(t['export_url']).get_json()['compact_trace']['native_status']==int(data['success'])
 s=c.post('/api/ordenamiento/step',json={'algorithm_id':'binsort','cursor':99999999,'direction':'next'})
 assert s.status_code==200 and s.get_json()['step']['debug']['instruction_event']['token']=='binsort_return'
 assert c.get('/api/ordenamiento/state').get_json()==accepted and key.encode() in c.get('/sorting/visualizador').data
 with app.app_context():
  assert store.entries[key].expires==entry.expires and json.dumps(entry.source.tape.records,sort_keys=True)==original
  store.entries[key]=replace(entry,expires=0)
 assert c.get(t['page_url']).status_code==410 and c.get(t['export_url']).status_code==410
 assert c.post('/api/ordenamiento/step',json={'algorithm_id':'binsort'}).status_code==410
 c.post('/api/ordenamiento/reset',json={});assert c.get(t['page_url']).status_code==404

@pytest.mark.parametrize('values,expected',[([999999,0],3000054),([int(i*999999/79) for i in range(80)],3000912),([0]+[999999]*79,3000834),([2147483642,2147483647],72)])
def test_binsort_full_admitted_range_exact_sparse_representation(values,expected):
 result=SortingInterpreter(values,'binsort').run();tape=result['steps']
 assert isinstance(tape,BinsortTape) and len(tape)==expected
 assert result['final_state']['items']==sorted(values)
 assert len(tape.records)<1300
 assert tape[0]['line_token']=='initial' and tape[2]['line_token']=='binsort_delegate' and tape[-1]['line_token']=='binsort_return'
 assert all(tape[i]['binsort_context']['active'] for i in [1,2,3,len(tape)//2,len(tape)-2])
 assert tape[-1]['binsort_context']['return_status']==1
 for p,record in enumerate(tape.records):
  if record['kind']=='zero_span':
   begin=tape.ends[p-1];end=tape.ends[p]
   for index in [begin,begin+1,begin+2,end-3,end-2,end-1]:
    row=tape[index];bucket=record['start']+(index-begin)//3
    assert row['instruction_event']['token']==['rebuild_test','bucket_test','rebuild_increment'][(index-begin)%3]
    assert row['instruction_event']['i']==bucket+((index-begin)%3==2)
    assert not dict(row['instruction_event']['conteo']['nonzero']).get(bucket,0)

def test_binsort_transport_rejection_preserves_state_without_native_ERROR():
 app,c,before=prepare([3,1,2])
 with app.app_context():get_counting_store().max_bytes=1
 d=run(c).get_json();assert not d['success'] and 'execution_trace' not in d and 'native_status' not in d
 assert d['visual_state']==before['visual_state'] and d['history']==before['history']

@pytest.mark.parametrize('testing',[True,False])
def test_binsort_QA_hook_is_private_and_testing_only(testing):
 app,c,_=prepare([5,0],null);app.testing=testing
 r=c.post('/api/ordenamiento/run',json={'algorithm_id':'binsort','mode':'fast','simulate_calloc_failure':True})
 assert r.status_code==(400 if testing else 200)
 if testing:
  assert r.get_json()['execution_trace']['error']['simulated']
  app.config.pop('COUNTING_QA_ALLOCATOR');accepted=run(c).get_json()
  assert accepted['success'] and sum(x['operation']=='run' for x in accepted['history'])==1

def test_binsort_no_saved_step_does_not_dispatch(monkeypatch):
 app,c,_=prepare([5,0]);monkeypatch.setattr(SortingInterpreter,'run',forbidden)
 assert c.post('/api/ordenamiento/step',json={'algorithm_id':'binsort','cursor':0}).status_code==404
 assert c.post('/api/ordenamiento/step',json={'cursor':0}).status_code==404

def test_binsort_protected_sources_and_original_regressions_unchanged():
 e=C/'evidence/visible-sorting-binsort-instructions'
 for f,h in json.loads((audit_input_path(e/'protected-before.json')).read_text(encoding='utf-8')).items():assert_historical_protected_hash(ROOT,f,h)
 original=json.loads((audit_input_path(e/'original-test-sha.json')).read_text(encoding='utf-8'))
 for f,h in original.items():assert hashlib.sha256((audit_input_path(ROOT/f)).read_bytes()).hexdigest()==h


def test_binsort_plain_model_allocation_failure_is_separate_from_native_and_QA():
 def fail(_):raise MemoryError('controlled model failure, no exhaustion')
 app,c,before=prepare([5,0],fail);d=run(c).get_json();t=d['execution_trace']
 assert t['error']['origin']=='python-model-allocation' and not t['error']['simulated'] and not t['error']['real_c_execution']
 assert t['native_status']==0 and d['history']==before['history'] and d['visual_state']==before['visual_state']


@pytest.mark.parametrize('case',['cap_two','wide_eighty'])
def test_binsort_maximum_decorator_preserves_verified_delegate_records(monkeypatch,case):
 import app.domain.sorting.binsort_instructions as module
 report=json.loads((audit_input_path(C/'evidence/visible-sorting-counting-native-fault-low'/('stream-'+case+'-binary/report.json'))).read_text(encoding='utf-8'))
 capture={};original=module.run_counting_sparse_trace
 def observe(values,**kwargs):
  result=original(values,**kwargs);capture['delegate']=result['steps'];return result
 monkeypatch.setattr(module,'run_counting_sparse_trace',observe)
 result=SortingInterpreter(report['input'],'binsort').run();bin_tape=result['steps'];delegate=capture['delegate']
 assert len(delegate)==report['logical_events'] and len(bin_tape)==len(delegate)+3
 assert bin_tape[0]['instruction_event']==delegate[0]['instruction_event']
 begin=0
 for record,end in zip(delegate.records,delegate.ends):
  indices={max(1,begin),end-1}
  if record['kind']=='zero_span':indices.update([begin+1,begin+2,(begin+end)//2,end-3,end-2])
  for index in sorted(i for i in indices if 1<=i<len(delegate)):
   wrapped=bin_tape[index+2];raw=delegate[index]
   for key in ['instruction_event','array_snapshot','auxiliary_snapshot','counting_context','condition_result','condition_expression','line_token','source_function']:
    assert wrapped.get(key)==raw.get(key)
   assert wrapped['instruction_stack']==['ordenar_binsort']+raw['instruction_stack']
  begin=end
 assert [(r['start'],r['end']) for r in bin_tape.records if r['kind']=='zero_span']==[(r['start'],r['end']) for r in delegate.records if r['kind']=='zero_span']

