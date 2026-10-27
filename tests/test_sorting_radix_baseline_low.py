"""Permanent Radix LOW regressions: current causal defects stay visible without xfail."""

from pathlib import Path

import json

import pytest

from app import create_app

from app.domain.sorting.tad_ordenamiento import SortingInterpreter

from _audit_radix_baseline_low import CASES

ROOT=Path(__file__).resolve().parents[1];E=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-radix-baseline-low'

def prepare(values,testing=False):

 app=create_app();app.testing=testing;c=app.test_client()

 assert c.post('/api/ordenamiento/create-array',json={'values':values}).status_code==200

 assert c.post('/api/ordenamiento/algorithm',json={'algorithm_id':'radixsort'}).status_code==200

 return app,c



def run(c):return c.post('/api/ordenamiento/run',json={'algorithm_id':'radixsort','mode':'step_by_step'})



from scripts.published_test_inputs import audit_input_path
def oracle(case):return json.loads((audit_input_path(E/'native'/(case+'.json'))).read_text(encoding='utf-8'))

@pytest.mark.parametrize('case',list(CASES))

def test_radix_native_result(case):

 _,c=prepare(CASES[case]);d=run(c).get_json();expected=oracle(case)['outcome']

 assert d['success'] and d['result']['array']==expected['array'] and expected['status']==1

@pytest.mark.parametrize('case',list(CASES))

def test_radix_native_controls_and_helper_events_not_aggregated(case):

 _,c=prepare(CASES[case]);t=run(c).get_json()['execution_trace'];d=oracle(case)

 # Approved conditional-scope repair removes only historical unentered block markers.
 values=CASES[case];inactive=set()
 if not any(x<0 for x in values):inactive.add('negative_block_exit')
 if not any(x>=0 for x in values):inactive.add('positive_block_exit')
 native=[e for e in d['native'] if e['token'] not in inactive]
 assert t.get('step_count',len(t.get('steps',[])))==len(native)
 assert all('instruction_event' in f['debug'] for f in t['steps'])
 actual=[f['debug']['instruction_event'] for f in t['steps']]
 expected=[{k:v for k,v in e.items() if k!='case'} for e in native]
 assert json.dumps(actual,sort_keys=True)==json.dumps(expected,sort_keys=True)
 assert not any(e['token'] in inactive for e in actual)

@pytest.mark.parametrize('case',list(CASES))

def test_radix_executed_value_max_comparisons_not_discarded(case):

 _,c=prepare(CASES[case]);metrics=run(c).get_json()['result']['metrics'];d=oracle(case)

 # Regardless of counting sign/loop tests, executed C value comparisons cannot be omitted.

 assert metrics['comparisons']>=d['native'][-1]['max_value_comparisons']



def test_radix_real_digit_helper_scope_and_uint32_parameters():

 _,c=prepare([170,45,75,90]);frames=run(c).get_json()['execution_trace']['steps']

 assert any(any(x['function']=='counting_por_digito' for x in f['pedagogy']['call_stack']) for f in frames)

 assert any(v['type']=='uint32_t' for f in frames for v in f['pedagogy']['variables'])



def test_radix_malloc_output_indeterminate_until_writes_and_free_retired():

 _,c=prepare([7]);frames=run(c).get_json()['execution_trace']['steps'];tokens=[f['debug'].get('instruction_event',{}).get('token') for f in frames]

 assert 'digit_allocate' in tokens and 'digit_free' in tokens and tokens[-1]=='radix_return'

 allocate=frames[tokens.index('digit_allocate')];assert allocate['state_after']['radix_context']['digit_output_initialized']==[False]

 assert not frames[-1]['pedagogy']['variables'] and not frames[-1]['pedagogy']['call_stack']



def test_radix_raw_C_without_printf_does_not_emit_narration_as_console():

 d=SortingInterpreter([3,1,2],'radixsort').run();assert all(not row['console_output'] for row in d['steps'])



def test_radix_controlled_model_memory_failure_preserves_previous_run(monkeypatch):

 app,c=prepare([3,1,2]);assert run(c).status_code==200;before=c.get('/api/ordenamiento/state').get_json()

 def fail(*a,**kw):raise MemoryError('isolated model injection, no real memory exhaustion')

 monkeypatch.setattr(SortingInterpreter,'_counting_digit',fail)

 r=run(c);assert r.status_code==400;d=r.get_json()

 assert d['visual_state']==before['visual_state'] and d['history']==before['history'] and d['main_c']==before['main_c']



def test_radix_saved_step_does_not_redispatch(monkeypatch):

 app,c=prepare([3,1,2],True);assert run(c).status_code==200

 def forbid(*a,**kw):raise AssertionError('saved Radix navigation redispatches sort')

 monkeypatch.setattr(SortingInterpreter,'run',forbid)

 assert c.post('/api/ordenamiento/step',json={'algorithm_id':'radixsort','cursor':0,'direction':'next'}).status_code==200



@pytest.mark.parametrize('values',[[],[1]*81,[2147483648],[-2147483649],[1.5],[True]])

def test_radix_invalid_public_create_preserves_empty_history(values):

 app=create_app();c=app.test_client();assert c.post('/api/ordenamiento/create-array',json={'values':values}).status_code==400

 assert c.get('/api/ordenamiento/state').get_json()['history']==[]



def test_radix_repeated_runs_main_reload_without_sort(monkeypatch):

 _,c=prepare([3,1,2]);assert run(c).status_code==200;d=run(c).get_json()

 assert sum(x['operation']=='run' for x in d['history'])==2 and d['main_c'].count('= ordenar_radixsort(')==2

 def forbid(*a,**kw):raise AssertionError('reload executes sorting')

 monkeypatch.setattr(SortingInterpreter,'run',forbid)

 s=c.get('/api/ordenamiento/state').get_json();assert s['history']==d['history'] and s['main_c']==d['main_c'] and s['visual_state']['items']==d['visual_state']['items']



def test_radix_actual_source_contains_wrapper_and_private_helpers():

 _,c=prepare([3,1,2]);s=run(c).get_json()['execution_trace']['source_code']

 assert all(x+'(' in s for x in ['ordenar_radixsort','counting_por_digito','arreglo_valido'])



def test_radix_maximum_admitted_digit_domain_completes_without_fixture_cutoff():

 values=[-2147483648,2147483647]*40;d=SortingInterpreter(values,'radixsort').run();assert d['final_state']['items']==sorted(values)

 # Approved LOW correction: logical C events are not transport frame/payload limits.
 native_rows=[json.loads(line) for line in (audit_input_path(E.parent/'visible-sorting-radix-instructions/native-expanded/native.jsonl')).read_text(encoding='utf-8').splitlines()]
 native=[row for row in native_rows if row.get('case')==40 and 'token' in row]
 outcome=next(row for row in native_rows if row.get('outcome')=='maximum')
 assert native and len(d['steps'])==len(native)==d['metrics']['steps']
 for index,expected in enumerate(native):
  raw=d['steps'][index]
  assert raw['instruction_event']=={k:v for k,v in expected.items() if k not in {'case','typed_observation'}}
  assert raw['array_snapshot']==expected['array'] and not raw['console_output']
  ctx=raw['radix_context'];buffers=ctx['buffers'];status={'undeclared':0,'uninitialized':1,'NULL':2,'live':3,'freed':4}
  observation=dict(wrapper_declared=ctx['wrapper_declared'],helper_declared=ctx['helper_declared'],negative_status=status[buffers['negative']['status']],positive_status=status[buffers['positive']['status']],output_status=status[buffers['output']['status']],helper_n=ctx['helper_n'] if ctx['helper_active'] else None,helper_alias=ctx['group'] if ctx['helper_active'] else None,magnitud=ctx['magnitud'],block=1 if ctx['block']=='negative' else 2 if ctx['block']=='positive' else 0,index_initialized=ctx['indice'] is not None)
  for name in ['negative','positive','output']:observation[name+'_initialized']=[value is not None for value in buffers[name]['cells']] if buffers[name]['live'] else None
  assert observation==expected['typed_observation']
 assert outcome['status']==1 and d['final_state']['items']==outcome['array']
 last=d['steps'][-1];event=last['instruction_event'];ctx=last['radix_context']
 assert event['return_status']==1 and event['allocations']==event['frees']==outcome['allocations']==outcome['frees'] and event['live']==outcome['live']==0
 assert not ctx['wrapper_active'] and not ctx['helper_active'] and not ctx['valid_active']
 assert all(not buffer['live'] and buffer['cells'] is None for buffer in ctx['buffers'].values())
 assert d['metrics']['comparisons']==event['max_value_comparisons'] and d['metrics']['swaps']==0
 assert d['metrics']['moves']==sum(event[key] for key in ['work_writes','count_writes','digit_output_writes','caller_writes'])





def test_radix_never_highlights_unexecuted_negative_join_for_positive_zero_input():

 _,c=prepare([0,0,0]);frames=run(c).get_json()['execution_trace']['steps']

 assert not any('uint32_t magnitud = negativos[i - 1]' in f['line_text'] for f in frames), 'negative join body does not execute with zero negative values'

