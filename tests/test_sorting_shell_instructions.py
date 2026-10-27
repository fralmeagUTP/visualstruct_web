"""Finite Shell instruction signoff against the preserved actual-C oracle."""
from pathlib import Path
import json
import pytest
from _audit_shell_baseline import audit,CASES
from app import create_app
from app.domain.sorting.pedagogy import validate_pedagogical_frame
from _audit_sorting_c_source import function_body
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-shell-instructions'
@pytest.fixture(scope='module')
def observed(tmp_path_factory):
 out=tmp_path_factory.mktemp('shell-instructions');return out,audit(out)

from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize('case',list(CASES))
def test_every_native_clause_local_lifetime_shortcircuit_group_and_source(case,observed):
 out,r=observed;d=json.loads((audit_input_path(out/(case+'.json'))).read_text(encoding='utf-8'));trace=d['response']['execution_trace'];steps=trace['steps'];native=d['native'];n=len(CASES[case]);previous={}
 assert r['instruction_fidelity'] and len(steps)==len(native)
 for idx,(step,c) in enumerate(zip(steps,native)):
  event=c['event'];token=event['token'];frame=step['pedagogy'];state=step['state_after'];context=state['shell_context'];variables={v['name']:v for v in frame['variables']}
  validate_pedagogical_frame(frame,source_code=trace['source_code'])
  assert step['debug']['instruction_event']==event and state['items']==c['array'] and step['state_snapshot']['items']==native[max(0,idx-1)]['array']
  assert step['debug']['console_events']==[] and frame['pointers']==[] and state['swapping_indices']==[]
  if token in {'initial','sort_return'}:
   assert frame['variables']==[] and frame['call_stack']==[] and context['intervalo'] is None and not context['gap_declared']
  else:
   assert variables['n']['value']==n and variables['n']['type']=='size_t'
   if token!='sort_entry':assert variables['intervalo']['value']==event['intervalo'] and variables['intervalo']['initialized']==(event['intervalo'] is not None) and variables['intervalo']['scope']=='ordenar_shell'
   assert context['intervalo']==event['intervalo']
  for name,ctype,scope in [('i','size_t','ordenar_shell:cuerpo_intervalo'),('j','size_t','ordenar_shell:cuerpo_i'),('temporal','int','ordenar_shell:cuerpo_i')]:
   if event[name] is None and not(name=='i' and token=='i_declare'):assert name not in variables
   else:assert variables[name]['value']==event[name] and variables[name]['type']==ctype and variables[name]['scope']==scope and variables[name]['initialized']==(event[name] is not None)
   assert context[name]==event[name]
  for name,var in variables.items():
   prior=previous.get((var['scope'],name));assert var['previous']==(prior['value'] if prior else None)
  previous={(v['scope'],v['name']):v for v in variables.values()}
  if token=='initial':assert step['line_index'] is None
  else:
   body=function_body(trace['source_code'],event['function']);start=trace['source_code'][:trace['source_code'].index(body)].count('\n');end=start+body.count('\n')
   assert start<=step['line_index']<=end and step['line_text']==trace['source_code'].splitlines()[step['line_index']]
  gap=event['intervalo'];i=event['i'];group=list(range(i%gap,n,gap)) if gap and i is not None and i<n and token!='sort_return' else []
  assert context['group']==group
  if token=='i_declare':assert not variables['i']['initialized']
  if token=='temp_take':assert 'j' not in variables and variables['temporal']['value']==c['array'][i] and c['array']==step['state_snapshot']['items']
  if token=='while_left' and c['condition'] is False:
   assert event['j']<gap and native[idx+1]['event']['token']=='while_test' and native[idx+1]['condition'] is False and native[idx+1]['event']['comparisons']==event['comparisons']
  if token=='while_compare':assert event['j']>=gap and state['comparing_indices']==[event['j']-gap]
  if token in {'while_left','while_compare'}:assert frame['loop']['kind']=='while interno' and not frame['loop']['exit']
  if token=='while_test':assert frame['loop']['exit']==(c['condition'] is False)
  if token=='shift':
   j=event['j'];assert c['array'][j]==c['array'][j-gap] and variables['temporal']['value']==step['state_snapshot']['temporaries']['temporal']
   assert native[idx+1]['event']['token']=='j_subtract' and native[idx+1]['event']['j']==j-gap and native[idx+1]['array']==c['array']
  if token=='inner_body_exit':assert 'j' not in variables and 'temporal' not in variables and variables['i']['value']==i and native[idx+1]['event']['token']=='i_increment'
  if token=='gap_body_exit':
   assert 'i' not in variables and 'j' not in variables and 'temporal' not in variables and context['gap_completed']==gap
   assert native[idx+1]['event']['token']=='gap_divide' and native[idx+1]['event']['intervalo']==gap//2
   assert all(c['array'][k]<=c['array'][k+gap] for k in range(n-gap))
  if token=='gap_divide':assert 'i' not in variables and frame['loop']['kind']=='for intervalo' and native[idx+1]['event']['token']=='gap_test'
  assert state['sorted_indices']==(list(range(n)) if token=='sort_return' else [])
 assert trace['final_state']['items']==sorted(CASES[case]) and d['response']['result']['metrics']['swaps']==0

@pytest.mark.parametrize('case',list(CASES))
def test_actual_UI_complete_replay_numeric_gap_locals_and_real_C_callers(case):
 r=json.loads((audit_input_path(E/'browser-first/report.json')).read_text(encoding='utf-8'));row=next(x for x in r['rows'] if x['case']==case)
 assert row['forward_reverse_restorations']==2*row['instructions'] and row['replay_extra_POSTs']==0 and row['page_errors']==[]
 assert row['gap_indices_temporal_scope_match_C'] and row['fast_to_step_preserved'] and row['technical_views_visible'] and row['five_stages'] and row['actual_main_elements']==1 and row['reload_main_preserved']
 assert row['caller']['strict_C17'] and row['caller']['doxygen_warnings']==0 and row['caller']['arrays']==[CASES[case],sorted(CASES[case])]
 assert row['caller']['allocations']==row['caller']['frees']==row['caller']['live']==0 and r['empty_UI_rejected'] and r['empty_caller']['successful_native_runs']==0
 d=json.loads((audit_input_path(E/'browser-first'/(case+'.json'))).read_text(encoding='utf-8'))
 for capture in d['captures']:
  variables=d['response']['execution_trace']['steps'][capture['cursor']]['pedagogy']['variables']
  assert all(var['scope'] in cells[3] for var,cells in zip(variables,capture['shown']['variables']))

def test_original_regressions_oracle_bytes_and_four_closed_modules_unchanged():
 import hashlib
 from _sorting_published_test_contract import assert_published_test_successor, _FixturePathAdapter
 import ast
 receipt=json.loads((ROOT/'tests/fixtures/sorting-history/shell-test-migration.json').read_text())
 assert_published_test_successor(ROOT,dict(path=receipt['source']['path'],sha256=receipt['original_declared_sha256']),'shell')
 normalize=lambda raw:ast.dump(_FixturePathAdapter().visit(ast.parse(raw)),include_attributes=False)
 assert normalize((audit_input_path(ROOT/'tests/test_sorting_shell_baseline_low.py')).read_text(encoding='utf-8-sig'))==normalize((audit_input_path(E/'before/tests/test_sorting_shell_baseline_low.py')).read_text(encoding='utf-8-sig'))
 baseline=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-shell-baseline-low/native-current'
 for name in ['observed.c','native.jsonl','tad_ordenamiento.c','tad_ordenamiento.h']:assert (audit_input_path(E/'native-first'/name)).read_bytes()==(audit_input_path(baseline/name)).read_bytes()
 h=json.loads((audit_input_path(ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-burbuja-instructions/implementation-hashes.json')).read_text(encoding='utf-8'))['files']
 for rel in ['app/domain/sorting/intercambio_instructions.py','app/domain/sorting/seleccion_instructions.py','app/domain/sorting/insercion_instructions.py','app/domain/sorting/burbuja_instructions.py']:assert hashlib.sha256((audit_input_path(ROOT/rel)).read_bytes()).hexdigest()==h[rel]

def test_existing_step_API_preserves_input_and_readonly_history():
 c=create_app().test_client();c.post('/api/ordenamiento/create-array',json={'values':[4,3,2,1]});run=c.post('/api/ordenamiento/run',json={'algorithm_id':'shell','mode':'fast'}).get_json()
 step=c.post('/api/ordenamiento/step',json={'direction':'next','cursor':0,'algorithm_id':'shell'}).get_json();assert step['success'] and step['history']==run['history'] and len(step['execution_trace']['steps'])==86
 assert step['execution_trace']['steps'][0]['state_after']['items']==[4,3,2,1] and c.get('/api/ordenamiento/state').get_json()['visual_state']['items']==[1,2,3,4]
