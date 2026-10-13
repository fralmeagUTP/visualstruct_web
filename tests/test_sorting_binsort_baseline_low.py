"""Permanent Binsort baseline regressions; expected causal failures remain visible."""
from pathlib import Path
import json
import pytest
from app import create_app
from app.domain.sorting.tad_ordenamiento import SortingInterpreter
from app.domain.sorting.counting_sparse_tape import CountingTape
from _audit_binsort_baseline_low import CASES
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-binsort-baseline-low'
def client(values):
 app=create_app();c=app.test_client()
 assert c.post('/api/ordenamiento/create-array',json={'values':values}).status_code==200
 assert c.post('/api/ordenamiento/algorithm',json={'algorithm_id':'binsort'}).status_code==200
 return c
def run(c):
 return c.post('/api/ordenamiento/run',json={'algorithm_id':'binsort','mode':'step_by_step'})
@pytest.mark.parametrize('case',list(CASES))
def test_binsort_native_result_and_delegate_metrics(case):
 oracle=json.loads((E/'native'/(case+'.json')).read_text(encoding='utf-8'));r=run(client(CASES[case]))
 assert r.status_code==200
 d=r.get_json();expected=oracle['outcome']
 assert d['result']['array']==expected['array']
 assert d['result']['metrics']['comparisons']==expected['comparisons']
 assert d['result']['metrics']['moves']==expected['moves']
 assert d['result']['metrics']['swaps']==0
@pytest.mark.parametrize('case',list(CASES))
def test_binsort_native_instruction_count_and_wrapper_return(case):
 oracle=json.loads((E/'native'/(case+'.json')).read_text(encoding='utf-8'))
 c=client(CASES[case]);d=run(c).get_json();trace=d['execution_trace']
 total=trace.get('step_count',len(trace.get('steps',[])))
 assert total==len(oracle['native']),'delegate controls/call/return must not be replaced by aggregated frames'
 frames=trace.get('steps')
 if frames is None:frames=sum((c.get(trace['page_url'],query_string={'start':start,'limit':128}).get_json()['steps'] for start in range(0,total,128)),[])
 tokens=[f['debug']['instruction_event']['token'] for f in frames]
 assert tokens[:3]==['initial','binsort_entry','binsort_delegate'] and tokens[-1]=='binsort_return'
 assert not frames[-1]['pedagogy']['variables'] and not frames[-1]['pedagogy']['call_stack']
def test_binsort_real_helper_stack_and_typed_parameters():
 d=run(client([3,1,2])).get_json();frames=d['execution_trace']['steps']
 assert any(any(x['function']=='obtener_minimo_maximo' for x in f['pedagogy']['call_stack']) for f in frames)
 assert any(any(x['function']=='ordenar_binsort' for x in f['pedagogy']['call_stack']) for f in frames)
def test_binsort_calloc_zero_and_free_lifecycle():
 frames=run(client([3,1,2])).get_json()['execution_trace']['steps']
 assert any(f['debug'].get('instruction_event',{}).get('token')=='count_free' and not f['state_after']['counting_context']['live'] for f in frames)
 assert any(f['debug'].get('instruction_event',{}).get('token')=='count_init' and f['state_after']['auxiliary_array']==[0,0,0] for f in frames)
def test_binsort_C_without_printf_has_no_fictitious_console():
 frames=run(client([3,1,2])).get_json()['execution_trace']['steps']
 assert all(not f['debug'].get('console_events',[]) for f in frames)
def test_binsort_range_ERROR_trace_preserves_accepted_history_main():
 c=client([0,1000000]);before=c.get('/api/ordenamiento/state').get_json();r=run(c)
 assert r.status_code==400;d=r.get_json()
 assert d['history']==before['history'] and d['main_c']==before['main_c'] and d['visual_state']['items']==before['visual_state']['items']
 assert d.get('execution_trace') and not d['execution_trace']['success'],'a rejected delegated call must preserve guards and wrapper ERROR return'
@pytest.mark.parametrize('values',[[],[1]*81,[2147483648],[-2147483649],[1.5],[True]])
def test_binsort_UI_invalid_create_rejected_without_history(values):
 app=create_app();c=app.test_client();r=c.post('/api/ordenamiento/create-array',json={'values':values});assert r.status_code==400
 assert c.get('/api/ordenamiento/state').get_json()['history']==[]
def test_binsort_repeated_runs_reload_main_and_no_redispatch(monkeypatch):
 c=client([3,1,2]);assert run(c).status_code==200;d=run(c).get_json();assert d['success']
 assert sum(x['operation']=='run' for x in d['history'])==2 and d['main_c'].count('= ordenar_binsort(')==2
 def forbidden(*a,**kw):raise AssertionError('reload must not execute sorting')
 monkeypatch.setattr(SortingInterpreter,'run',forbidden)
 state=c.get('/api/ordenamiento/state').get_json()
 assert state['history']==d['history'] and state['main_c']==d['main_c'] and state['visual_state']['items']==d['visual_state']['items']
def test_binsort_large_admitted_range_avoids_legacy_dense_capture(monkeypatch):
 # Permit one 8MB calloc model, abort before copying million-cell arrays per frame.
 # This sentinel is a safe diagnostic, not simulated native allocation failure/OOM.
 original=SortingInterpreter._record
 class LegacyCapture(Exception):pass
 def guarded(self,*a,**kw):
  if kw.get('auxiliary') is not None and len(kw['auxiliary'])>2048:raise LegacyCapture('legacy dense frame would duplicate million-cell reserve')
  return original(self,*a,**kw)
 monkeypatch.setattr(SortingInterpreter,'_record',guarded)
 try:r=SortingInterpreter([0,999999],'binsort').run()
 except LegacyCapture as error:pytest.fail(str(error))
 assert isinstance(r['steps'],CountingTape),'large admitted Binsort must retain the exact sparse delegate tape'


def test_binsort_raw_C_console_does_not_invent_printf():
 result=SortingInterpreter([3,1,2],'binsort').run()
 assert all(not row['console_output'] for row in result['steps'])


def test_binsort_model_memory_error_is_controlled_and_retry_preserves_previous_run(monkeypatch):
 app=create_app();app.testing=True;c=app.test_client()
 c.post('/api/ordenamiento/create-array',json={'values':[3,1,2]});c.post('/api/ordenamiento/algorithm',json={'algorithm_id':'binsort'})
 assert run(c).status_code==200;before=c.get('/api/ordenamiento/state').get_json()
 original=SortingInterpreter._run_counting_sort
 def fail(self):raise MemoryError('safe isolated Python model injection, no actual OOM/C allocator')
 monkeypatch.setattr(SortingInterpreter,'_run_counting_sort',fail)
 r=run(c);assert r.status_code==400;d=r.get_json()
 assert d['history']==before['history'] and d['main_c']==before['main_c'] and d['visual_state']==before['visual_state']
 assert 'modelo' in d['message'].lower()
 monkeypatch.setattr(SortingInterpreter,'_run_counting_sort',original)
 d=run(c).get_json();assert d['success'] and sum(x['operation']=='run' for x in d['history'])==2

def test_binsort_invalid_run_mode_preserves_accepted_last_operation():
 c=client([3,1,2]);assert run(c).status_code==200;before=c.get('/api/ordenamiento/state').get_json()
 r=c.post('/api/ordenamiento/run',json={'algorithm_id':'binsort','mode':'invalid'})
 assert r.status_code==400;d=r.get_json()
 assert d['history']==before['history'] and d['main_c']==before['main_c'] and d['visual_state']==before['visual_state']


def test_binsort_saved_step_replay_does_not_dispatch_sort_again(monkeypatch):
 app=create_app();app.testing=True;c=app.test_client()
 c.post('/api/ordenamiento/create-array',json={'values':[3,1,2]});c.post('/api/ordenamiento/algorithm',json={'algorithm_id':'binsort'})
 assert run(c).status_code==200
 def forbidden(*a,**kw):raise AssertionError('saved Binsort step redispatches sorting instead of immutable decode')
 monkeypatch.setattr(SortingInterpreter,'run',forbidden)
 r=c.post('/api/ordenamiento/step',json={'algorithm_id':'binsort','cursor':0,'direction':'next'})
 assert r.status_code==200 and r.get_json()['success']
