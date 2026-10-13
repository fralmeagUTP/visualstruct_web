"""Finite insertion instruction signoff, reusing the original independent C oracle."""
from pathlib import Path
from _audit_approved_source_supersessions import assert_historical_protected_hash
import json,hashlib
import pytest
from _audit_insercion_baseline import CASES,audit
from app import create_app
from app.domain.sorting.pedagogy import validate_pedagogical_frame
from _audit_sorting_c_source import function_body
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-insercion-instructions'

@pytest.fixture(scope='module')
def observed(tmp_path_factory):
 out=tmp_path_factory.mktemp('insercion-instructions');return out,audit(out)

@pytest.mark.parametrize('case',list(CASES))
def test_each_instruction_locals_scope_control_partial_shift_and_source(case,observed):
 out,report=observed;data=json.loads((out/(case+'.json')).read_text(encoding='utf-8'));trace=data['response']['execution_trace'];steps=trace['steps'];native=data['native']
 assert report['instruction_fidelity'] and len(steps)==len(native)
 for index,(step,c) in enumerate(zip(steps,native)):
  frame=step['pedagogy'];event=c['event'];token=event['token'];state=step['state_after'];variables={v['name']:v for v in frame['variables']}
  validate_pedagogical_frame(frame,source_code=trace['source_code'])
  assert step['debug']['instruction_event']==event and state['items']==c['array'] and step['state_snapshot']['items']==native[max(0,index-1)]['array']
  assert step['debug']['console_events']==[] and frame['pointers']==[] and state['swapping_indices']==[]
  if token in {'initial','sort_return'}:assert frame['variables']==[] and frame['call_stack']==[]
  else:
   assert variables['n']['value']==len(CASES[case]) and variables['n']['type']=='size_t'
   if token!='sort_entry':assert variables['i']['value']==event['i'] and variables['i']['initialized']==(event['i'] is not None) and variables['i']['type']=='size_t'
  for name,ctype in [('j','size_t'),('clave','int')]:
   if event[name] is None:assert name not in variables
   else:assert variables[name]['value']==event[name] and variables[name]['type']==ctype and variables[name]['scope']=='ordenar_insercion:cuerpo_for'
  assert state['insertion_context']['clave']==event['clave'] and state['insertion_context']['j']==event['j']
  if token=='initial':assert step['line_index'] is None
  else:
   body=function_body(trace['source_code'],event['function']);start=trace['source_code'][:trace['source_code'].index(body)].count('\n');end=start+body.count('\n')
   assert start<=step['line_index']<=end and step['line_text']==trace['source_code'].splitlines()[step['line_index']]
  if token=='key_take':assert 'clave' in variables and 'j' not in variables and c['array']==step['state_snapshot']['items']
  if token=='shift':
   j=event['j'];assert c['array'][j]==c['array'][j-1] and variables['clave']['value']==step['state_snapshot']['temporaries']['clave']
   assert native[index+1]['event']['token']=='j_decrement' and native[index+1]['event']['j']==j-1 and native[index+1]['array']==c['array']
  if token=='while_left' and c['condition'] is False:
   assert event['j']==0 and native[index+1]['event']['token']=='while_test' and native[index+1]['condition'] is False
   assert native[index+1]['event']['comparisons']==event['comparisons']
  if token=='while_compare':assert event['j']>0 and state['comparing_indices']==[event['j']-1]
  if token in {'while_left','while_compare'}:assert frame['loop']['kind']=='while interno' and not frame['loop']['exit']
  if token=='while_test':assert frame['loop']['exit']==(c['condition'] is False)
  if token=='body_exit':assert 'j' not in variables and 'clave' not in variables and variables['i']['value']==event['i']
  assert state['sorted_indices']==(list(range(len(CASES[case]))) if token=='sort_return' else [])
 assert trace['final_state']['items']==sorted(CASES[case]) and data['response']['result']['metrics']['swaps']==0


def test_existing_step_api_preserves_original_input_and_does_not_add_run():
 client=create_app().test_client();client.post('/api/ordenamiento/create-array',json={'values':[2,1]})
 run=client.post('/api/ordenamiento/run',json={'algorithm_id':'insercion','mode':'fast'}).get_json()
 step=client.post('/api/ordenamiento/step',json={'direction':'next','cursor':0,'algorithm_id':'insercion'}).get_json()
 assert step['success'] and step['history']==run['history']
 assert step['execution_trace']['steps'][0]['state_after']['items']==[2,1]
 assert len(step['execution_trace']['steps'])==len(run['execution_trace']['steps'])==25
 assert client.get('/api/ordenamiento/state').get_json()['visual_state']['items']==[1,2]


def test_closed_intercambio_seleccion_modules_and_c_h_unchanged():
 for relative in ['app/domain/sorting/intercambio_instructions.py','app/domain/sorting/seleccion_instructions.py']:
  assert (ROOT/relative).read_bytes()==(EVIDENCE/'before'/relative).read_bytes()
 baseline=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-insercion-baseline-low/native-current'
 for extension in ['c','h']:assert_historical_protected_hash(ROOT,'docs/tads_C/tad_ordenamiento.'+extension,hashlib.sha256((baseline/('tad_ordenamiento.'+extension)).read_bytes()).hexdigest())

@pytest.mark.parametrize('case',list(CASES))
def test_actual_browser_complete_replay_clave_j_real_array_and_callers(case):
 report=json.loads((EVIDENCE/'browser-first/report.json').read_text(encoding='utf-8'));row=next(r for r in report['rows'] if r['case']==case)
 assert row['forward_reverse_restorations']==2*row['instructions'] and row['replay_extra_POSTs']==0 and row['page_errors']==[] and row['fast_to_step_preserved'] and row['technical_views_visible']
 assert row['real_array_no_fictitious_hole'] and row['clave_j_all_frames_match_C'] and row['reload_main_preserved'] and row['five_stages']
 assert row['actual_main_elements']==1 and row['caller']['strict_C17'] and row['caller']['doxygen_warnings']==0 and row['caller']['allocations']==row['caller']['frees']==row['caller']['live']==0
 assert row['caller']['arrays']==[CASES[case],sorted(CASES[case])] and report['empty_UI_rejected'] and report['empty_caller']['successful_native_runs']==0
