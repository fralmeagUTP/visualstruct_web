"""Finite Quick signoff: native recursive frames, scopes, signed locals and aliases."""
from pathlib import Path
import json,hashlib
import pytest
from _audit_quicksort_baseline import audit,CASES
from app import create_app
from app.domain.sorting.pedagogy import validate_pedagogical_frame
from _audit_sorting_c_source import function_body
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-quicksort-instructions'
@pytest.fixture(scope='module')
def observed(tmp_path_factory):
 out=tmp_path_factory.mktemp('quick-instructions');return out,audit(out)
from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize('case',list(CASES))
def test_native_each_event_recursive_scopes_signed_locals_alias_and_source(case,observed):
 out,r=observed;d=json.loads((audit_input_path(out/(case+'.json'))).read_text(encoding='utf-8'));trace=d['response']['execution_trace'];steps=trace['steps'];native=d['native'];n=len(CASES[case]);previous={}
 assert r['instruction_fidelity'] and len(steps)==len(native)
 for idx,(step,c) in enumerate(zip(steps,native)):
  event=c['event'];token=event['token'];frame=step['pedagogy'];state=step['state_after'];context=state['quick_context'];variables={(v['scope'],v['name']):v for v in frame['variables']}
  validate_pedagogical_frame(frame,source_code=trace['source_code'])
  assert step['debug']['instruction_event']==event and state['items']==c['array'] and step['state_snapshot']['items']==native[max(0,idx-1)]['array'] and step['debug']['console_events']==[]
  calls=[call for call in frame['call_stack'] if call['function']=='quicksort_recursivo'];assert len(calls)==len(event['frames'])
  for depth,(f,call) in enumerate(zip(event['frames'],calls),1):
   scope=f'quicksort_recursivo[{depth}]';assert call['parameters']=={'arreglo':'arreglo del caller','primero':f['primero'],'ultimo':f['ultimo']}
   for name,value in f.items():
    if value is None:assert (scope,name) not in variables
    else:assert variables[scope,name]['value']==value and variables[scope,name]['type']=='int' and variables[scope,name]['initialized']
  assert {scope for scope,name in variables if scope.startswith('quicksort_recursivo')}=={f'quicksort_recursivo[{depth}]' for depth in range(1,len(event['frames'])+1)}
  for key,var in variables.items():assert var['previous']==(previous[key]['value'] if key in previous else None)
  previous=variables
  top=event['frames'][-1] if event['frames'] else {}
  assert all(context[key]==top.get(key) for key in ['primero','ultimo','i','j','pivote']) and context['depth']==len(event['frames'])
  if token in {'initial','sort_return'}:assert variables=={} and frame['call_stack']==[]
  else:assert variables['ordenar_quicksort','n']['value']==n and variables['ordenar_quicksort','n']['type']=='size_t'
  if token=='initial':assert step['line_index'] is None
  else:
   body=function_body(trace['source_code'],event['function']);start=trace['source_code'][:trace['source_code'].index(body)].count('\n');end=start+body.count('\n');assert start<=step['line_index']<=end and step['line_text']==trace['source_code'].splitlines()[step['line_index']]
  if event['a'] is not None:
   assert event['a']==top['i'] and event['b']==top['j'] and 0<=event['a']<n and 0<=event['b']<n
   assert frame['call_stack'][-1]['parameters']=={'a':f"arreglo[{event['a']}]",'b':f"arreglo[{event['b']}]"}
   assert {p['name']:p['index'] for p in frame['pointers']}=={'a':event['a'],'b':event['b']} and all(p['value']==c['array'][p['index']] for p in frame['pointers'])
   assert 'caller suspendido' in frame['loop']['kind']
  else:assert frame['pointers']==[] and all(call['function']!='intercambiar' for call in frame['call_stack'])
  if token in {'swap_declare','swap_guard'}:assert not variables['intercambiar','temporal']['initialized']
  if token in {'swap_temp','swap_assign_a','swap_assign_b'}:assert variables['intercambiar','temporal']['value']==event['temporal'] and variables['intercambiar','temporal']['type']=='int'
  if token=='swap_assign_a':assert c['array'][event['a']]==c['array'][event['b']] and event['temporal']==step['state_snapshot']['items'][event['a']]
  if token=='swap_return':assert ('intercambiar','temporal') not in variables and native[idx+1]['event']['token']=='swap_resume'
  if token in {'i_increment','j_decrement','cross_i_increment','cross_j_decrement'}:
   old=native[idx-1]['event']['frames'][-1];name='i' if token in {'i_increment','cross_i_increment'} else 'j';assert top[name]==old[name]+(1 if name=='i' else -1) and c['array']==native[idx-1]['array']
  if token=='rec_entry':assert top['i'] is None and top['j'] is None and top['pivote'] is None and native[idx+1]['event']['token']=='rec_init'
  if token=='rec_init':assert top['i']==top['primero'] and top['j']==top['ultimo'] and top['pivote']==c['array'][(top['primero']+top['ultimo'])//2]
  if token in {'left_call','right_call'}:
   next_frames=native[idx+1]['event']['frames'];assert next_frames[:-1]==event['frames'] and native[idx+1]['event']['token']=='rec_entry'
  if token=='rec_return':assert len(native[idx-1]['event']['frames'])==len(event['frames'])+1 and native[idx-1]['event']['frames'][:-1]==event['frames']
  if token in {'outer_test','i_test','j_test'}:assert frame['loop']['exit']==(c['condition'] is False)
  assert state['sorted_indices']==(list(range(n)) if token=='sort_return' else [])
 assert d['response']['result']['metrics']['moves']==3*d['response']['result']['metrics']['swaps']
 if case=='single':
  assert d['response']['result']['metrics']['comparisons']==3 and d['response']['result']['metrics']['swaps']==1 and any(c['event']['frames'] and c['event']['frames'][-1]['j']==-1 for c in native)

@pytest.mark.parametrize('case',list(CASES))
def test_actual_browser_recursive_frames_scopes_pivot_aliases_replay_and_callers(case):
 r=json.loads((audit_input_path(E/'browser-first/report.json')).read_text(encoding='utf-8'));row=next(x for x in r['rows'] if x['case']==case)
 assert row['forward_reverse_restorations']==2*row['instructions'] and row['replay_extra_POSTs']==0 and row['page_errors']==[] and row['recursive_scopes_pivot_helper_aliases_match_C']
 assert row['fast_to_step_preserved'] and row['technical_views_visible'] and row['actual_main_elements']==1 and row['reload_main_preserved'] and row['five_stages']
 assert row['caller']['strict_C17'] and row['caller']['doxygen_warnings']==0 and row['caller']['arrays']==[CASES[case],sorted(CASES[case])] and row['caller']['allocations']==row['caller']['frees']==row['caller']['live']==0
 assert r['empty_UI_rejected'] and r['empty_caller']['successful_native_runs']==0

def test_original_25_tests_independent_C_oracle_and_five_closed_modules_preserved():
 assert (audit_input_path(ROOT/'tests/test_sorting_quicksort_baseline_low.py')).read_bytes()==(audit_input_path(E/'before/tests/test_sorting_quicksort_baseline_low.py')).read_bytes()
 b=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-quicksort-baseline-low/native-after'
 for name in ['observed.c','native.jsonl','tad_ordenamiento.c','tad_ordenamiento.h']:assert (audit_input_path(E/'native-first'/name)).read_bytes()==(audit_input_path(b/name)).read_bytes()
 h=json.loads((audit_input_path(ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-shell-instructions/implementation-hashes.json')).read_text(encoding='utf-8'))['files']
 for rel in ['app/domain/sorting/intercambio_instructions.py','app/domain/sorting/seleccion_instructions.py','app/domain/sorting/insercion_instructions.py','app/domain/sorting/burbuja_instructions.py','app/domain/sorting/shell_instructions.py']:assert hashlib.sha256((audit_input_path(ROOT/rel)).read_bytes()).hexdigest()==h[rel]

def test_existing_step_API_keeps_single_original_input_and_history():
 c=create_app().test_client();c.post('/api/ordenamiento/create-array',json={'values':[7]});run=c.post('/api/ordenamiento/run',json={'algorithm_id':'quicksort','mode':'fast'}).get_json();step=c.post('/api/ordenamiento/step',json={'algorithm_id':'quicksort','direction':'next','cursor':0}).get_json()
 assert step['success'] and step['history']==run['history'] and len(step['execution_trace']['steps'])==32 and step['execution_trace']['steps'][0]['state_after']['items']==[7]
 assert step['execution_trace']['steps'][-1]['state_after']['metrics']['moves']==3 and c.get('/api/ordenamiento/state').get_json()['visual_state']['items']==[7]
