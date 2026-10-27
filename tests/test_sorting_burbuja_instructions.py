"""Finite improved-bubble signoff against the independent actual-C oracle."""
from pathlib import Path
import json
import pytest
from _audit_approved_source_supersessions import assert_historical_protected_hash
from _audit_burbuja_baseline import CASES,audit
from app import create_app
from app.domain.sorting.pedagogy import validate_pedagogical_frame
from _audit_sorting_c_source import function_body
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-burbuja-instructions'

@pytest.fixture(scope='module')
def observed(tmp_path_factory):
 out=tmp_path_factory.mktemp('burbuja-instructions');return out,audit(out)

from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize('case',list(CASES))
def test_every_C_instruction_flag_scopes_neighbors_and_early_break(case,observed):
 out,report=observed;data=json.loads((audit_input_path(out/(case+'.json'))).read_text(encoding='utf-8'));trace=data['response']['execution_trace'];steps=trace['steps'];native=data['native'];n=len(CASES[case]);confirmed=set()
 assert report['instruction_fidelity'] and len(steps)==len(native)
 for index,(step,c) in enumerate(zip(steps,native)):
  frame=step['pedagogy'];event=c['event'];token=event['token'];state=step['state_after'];variables={v['name']:v for v in frame['variables']};bubble=state['bubble_context']
  validate_pedagogical_frame(frame,source_code=trace['source_code'])
  assert step['debug']['instruction_event']==event and state['items']==c['array'] and step['state_snapshot']['items']==native[max(0,index-1)]['array']
  assert step['debug']['console_events']==[]
  if token in {'initial','sort_return'}:
   assert frame['variables']==[] and frame['call_stack']==[] and bubble['pasada'] is None and bubble['j'] is None and bubble['hubo_intercambio'] is None
  else:
   assert variables['n']['value']==n and variables['n']['type']=='size_t'
   for name,ctype in [('pasada','size_t'),('j','size_t'),('hubo_intercambio','int')]:
    if name in variables:
     assert variables[name]['value']==event[name] and variables[name]['type']==ctype and variables[name]['scope']=='ordenar_burbuja'
     assert variables[name]['initialized']==(event[name] is not None)
   assert bubble['pasada']==event['pasada'] and bubble['j']==event['j'] and bubble['hubo_intercambio']==event['hubo_intercambio']
  if token=='sort_declare_indices':assert 'hubo_intercambio' not in variables and not variables['j']['initialized'] and not variables['pasada']['initialized']
  if token=='sort_declare_flag':assert not variables['hubo_intercambio']['initialized']
  if token=='initial':assert step['line_index'] is None
  else:
   body=function_body(trace['source_code'],event['function']);start=trace['source_code'][:trace['source_code'].index(body)].count('\n');end=start+body.count('\n')
   assert start<=step['line_index']<=end and step['line_text']==trace['source_code'].splitlines()[step['line_index']]
  if event['a'] is not None:
   assert event['a']==event['j'] and event['b']==event['j']+1 and 0<=event['a']<event['b']<n
   assert frame['call_stack'][-1]['parameters']=={'a':f"arreglo[{event['a']}]",'b':f"arreglo[{event['b']}]"}
   assert {p['name']:p['index'] for p in frame['pointers']}=={'a':event['a'],'b':event['b']}
   assert all(p['value']==c['array'][p['index']] for p in frame['pointers'])
   assert frame['loop']['kind']=='for interno (caller suspendido)'
  else:assert frame['pointers']==[] and all(call['function']!='intercambiar' for call in frame['call_stack'])
  if token in {'swap_declare','swap_guard'}:assert not variables['temporal']['initialized']
  if token in {'swap_temp','swap_assign_a','swap_assign_b'}:assert variables['temporal']['value']==event['temporal'] and variables['temporal']['scope']=='intercambiar'
  if token=='swap_assign_a':assert c['array'][event['a']]==c['array'][event['b']] and event['temporal']==step['state_snapshot']['items'][event['a']]
  if token=='swap_return':assert 'temporal' not in variables
  if token=='flag_set':assert native[index-1]['event']['token']=='swap_resume' and native[index-2]['event']['token']=='swap_return' and event['hubo_intercambio']==1
  if token=='flag_reset':assert event['hubo_intercambio']==0 and native[index+1]['event']['token']=='inner_init' and native[index+1]['event']['j']==0
  if token=='inner_test' and c['condition'] is False:
   assert event['j']+1==n-event['pasada'] and bubble['neighbors']==[] and frame['loop']['exit']
   confirmed.add(n-event['pasada']-1)
  if token=='stop_test':
   assert c['condition']==(not event['hubo_intercambio']) and not frame['loop']['exit']
   assert native[index+1]['event']['token']==('early_break' if c['condition'] else 'outer_complete')
  if token=='early_break':
   assert native[index+1]['event']['token']=='sort_return' and frame['loop']['exit'] and state['active_range'] is None
   confirmed=set(range(n))
  if token=='sort_return':confirmed=set(range(n))
  assert state['sorted_indices']==sorted(confirmed)
 assert trace['final_state']['items']==sorted(CASES[case])
 assert data['response']['result']['metrics']['moves']==3*data['response']['result']['metrics']['swaps']

@pytest.mark.parametrize('case',list(CASES))
def test_actual_browser_all_frames_controls_neighbors_flag_and_C_callers(case):
 report=json.loads((audit_input_path(EVIDENCE/'browser-first/report.json')).read_text(encoding='utf-8'));row=next(r for r in report['rows'] if r['case']==case)
 assert row['forward_reverse_restorations']==2*row['instructions'] and row['replay_extra_POSTs']==0 and row['page_errors']==[]
 assert row['flag_indices_helper_parameters_match_C'] and row['fast_to_step_preserved'] and row['technical_views_visible'] and row['five_stages']
 assert row['actual_main_elements']==1 and row['reload_main_preserved'] and row['caller']['strict_C17'] and row['caller']['doxygen_warnings']==0
 assert row['caller']['arrays']==[CASES[case],sorted(CASES[case])] and row['caller']['allocations']==row['caller']['frees']==row['caller']['live']==0
 assert report['empty_UI_rejected'] and report['empty_caller']['successful_native_runs']==0

def test_original_seven_causal_regressions_closed_modules_and_C_H_unchanged():
 assert (audit_input_path(ROOT/'tests/test_sorting_burbuja_baseline_low.py')).read_bytes()==(audit_input_path(EVIDENCE/'before/tests/test_sorting_burbuja_baseline_low.py')).read_bytes()
 previous=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-insercion-instructions/before'
 for relative in ['app/domain/sorting/intercambio_instructions.py','app/domain/sorting/seleccion_instructions.py']:
  assert (audit_input_path(ROOT/relative)).read_bytes()==(audit_input_path(previous/relative)).read_bytes()
 baseline=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-burbuja-baseline-low/native-after'
 for name in ['tad_ordenamiento.c','tad_ordenamiento.h']:
  assert_historical_protected_hash(ROOT,'docs/tads_C/'+name,__import__('hashlib').sha256((audit_input_path(baseline/name)).read_bytes()).hexdigest())
 for name in ['observed.c','native.jsonl']:assert (audit_input_path(EVIDENCE/'native-current'/name)).read_bytes()==(audit_input_path(baseline/name)).read_bytes()

def test_step_API_preserves_original_input_without_new_history(observed):
 client=create_app().test_client();client.post('/api/ordenamiento/create-array',json={'values':[2,1,3,4]})
 run=client.post('/api/ordenamiento/run',json={'algorithm_id':'burbuja','mode':'fast'}).get_json()
 step=client.post('/api/ordenamiento/step',json={'direction':'next','cursor':0,'algorithm_id':'burbuja'}).get_json()
 assert step['success'] and step['history']==run['history'] and len(step['execution_trace']['steps'])==50
 assert step['execution_trace']['steps'][0]['state_after']['items']==[2,1,3,4]
 assert client.get('/api/ordenamiento/state').get_json()['visual_state']['items']==[1,2,3,4]
