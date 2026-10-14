"""Finite Intercambio instruction signoff; other methods remain outside this block."""
import json,subprocess,sys,hashlib
from pathlib import Path
from _audit_approved_source_supersessions import assert_historical_protected_hash
import pytest
from _audit_intercambio_instructions import audit,CASES
from app.domain.sorting.tad_ordenamiento import SortingInterpreter
from app.services.sorting_structure_service import SortingStructureService as S
from app.domain.sorting.pedagogy import validate_pedagogical_frame
from test_graph_bfs_documentation import run_doxygen
ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture(scope='module')
def observed(tmp_path_factory):
 out=tmp_path_factory.mktemp('intercambio-instructions');report=audit(out);return out,report
from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize('case',list(CASES))
def test_every_observed_c_transition_and_scopes(case,observed):
 out,report=observed;d=json.loads((audit_input_path(out/(case+'.json'))).read_text(encoding='utf-8'));trace=d['response']['execution_trace'];steps=trace['steps']
 assert next(r for r in report['rows'] if r['case']==case)['differences']==0
 for step,c in zip(steps,d['native']):
  frame=step['pedagogy'];token=c['event']['token'];vars={v['name']:v for v in frame['variables']};validate_pedagogical_frame(frame,source_code=trace['source_code'])
  if token=='initial' or token=='sort_return':assert frame['variables']==[] and frame['call_stack']==[] and frame['pointers']==[]
  else:
   assert vars['n']['type']=='size_t' and vars['n']['value']==len(CASES[case])
   if token!='sort_entry':
    for name in ['i','j']:assert vars[name]['value']==c['event'][name] and vars[name]['type']=='size_t' and vars[name]['initialized']==(c['event'][name] is not None)
  in_swap=c['event']['a'] is not None
  assert ('intercambiar' in [r['function'] for r in frame['call_stack']])==in_swap
  assert len(frame['pointers'])==(2 if in_swap else 0)
  if in_swap:
   for pointer in frame['pointers']:assert pointer['value']==c['array'][c['event'][pointer['name']]]
  if token in ['swap_declare','swap_guard']:assert vars['temporal']['initialized'] is False
  if token=='swap_assign_a':
   assert c['array'][c['event']['a']]==c['array'][c['event']['b']]
   assert vars['temporal']['value']==step['state_snapshot']['temporaries']['temporal']
  if token=='compare':assert frame['loop']['kind']=='for interno' and frame['loop']['exit'] is False
  if in_swap:assert 'caller suspendido' in frame['loop']['kind'] and frame['loop']['exit'] is False
  if token=='swap_return':assert 'temporal' not in vars and not frame['pointers']
  if token in ['outer_test','inner_test'] and c['condition'] is False:assert frame['loop']['exit'] is True
  if token=='inner_test' and c['condition'] is False:assert vars['j']['value']==len(CASES[case])
 assert trace['final_state']['items']==sorted(CASES[case]);assert d['response']['result']['metrics']['comparisons']==len(CASES[case])*(len(CASES[case])-1)//2
 assert d['response']['result']['metrics']['moves']==3*d['response']['result']['metrics']['swaps']

def test_native_guards_are_separate_from_api_empty_rejection(observed):
 _,r=observed;assert r['native_guard_cases']==2 and r['api_empty_rejected'] and r['native_empty_null_rows']==19

def test_actual_http_source_still_has_doxygen_contract(observed):
 out,_=observed;run_doxygen(out,[out/'tad_ordenamiento.c',out/'tad_ordenamiento.h'])
 baseline=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-baseline-low/documentation-ownership'
 for ext in ['c','h']:
  name='tad_ordenamiento.'+ext
  assert (audit_input_path(out/name)).read_bytes()==(audit_input_path(ROOT/'docs/tads_C'/name)).read_bytes()
  assert_historical_protected_hash(ROOT,'docs/tads_C/'+name,hashlib.sha256((audit_input_path(baseline/name)).read_bytes()).hexdigest())

def test_interpreter_keeps_existing_final_state_contract():
 interpreter=SortingInterpreter([2,1],'intercambio');d=interpreter.run();assert interpreter.values==[1,2];assert d['final_state']['items']==[1,2] and d['final_state']['last_operation']['name']=='intercambio';assert d['metrics']['moves']==3

def test_original_run_step_history_and_get_remain_chronological(monkeypatch):
 def execute(op,p,h):return S.execute_operation(structure_id='sorting_array',operation_name=op,payload=p,history=h)
 h=execute('create_array',{'values':[2,1]},[])['history'];run=execute('run',{'mode':'fast','algorithm_id':'intercambio'},h);h=run['history'];step=execute('step',{'direction':'next','cursor':16,'algorithm_id':'intercambio'},h)
 assert step['success'] and step['history']==h and step['execution_trace']['steps'][0]['state_after']['items']==[2,1]
 assert S.get_view_model('sorting_array',h)['visual_state']['items']==[1,2]
 second=execute('run',{'mode':'fast','algorithm_id':'intercambio'},h);assert second['execution_trace']['steps'][0]['state_after']['items']==[1,2];assert sum(e['operation']=='run' for e in second['history'])==2

@pytest.fixture(scope='module')
def browser_observed(observed,tmp_path_factory):
 native,_=observed;out=tmp_path_factory.mktemp('intercambio-browser');r=subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('_audit_intercambio_browser.py')),str(out),str(native)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=120);(out/'runner.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stdout+r.stderr;return json.loads((audit_input_path(out/'report.json')).read_text(encoding='utf-8'))
@pytest.mark.parametrize('case',list(CASES))
def test_actual_browser_reversible_states_and_mode(case,browser_observed):
 row=next(r for r in browser_observed['rows'] if r['case']==case);assert row['forward_reverse_restorations']==2*row['instructions'];assert row['replay_extra_POSTs']==0 and row['page_errors']==[] and row['fast_to_step_preserved'] and row['technical_views_visible'];assert row['actual_main_elements']==1;assert browser_observed['empty_UI_rejected']


@pytest.fixture(scope='module')
def main_prototype(tmp_path_factory):
 out=tmp_path_factory.mktemp('intercambio-main-prototype');r=subprocess.run([sys.executable,'-B',str(ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/sorting-main-minimal-prototype.py'),str(out)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=60);(out/'runner.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stdout+r.stderr;return json.loads((audit_input_path(out/'report.json')).read_text(encoding='utf-8'))
@pytest.mark.parametrize('case',['manual_repeated','recreate_negative','random_materialized'])
def test_offline_main_proposal_compiles_and_replays_history(case,main_prototype):
 row=next(r for r in main_prototype['rows'] if r['case']==case);assert row['strict_C17'] and row['doxygen_warnings']==0 and row['matches_saved_chronology'];assert row['actually_displayed_UI_main'] is False
