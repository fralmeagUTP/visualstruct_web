"""Shell LOW endpoint evidence plus strong failing causal regressions, no xfail."""
from pathlib import Path
import json,hashlib
import pytest
from _audit_shell_baseline import audit,CASES,UI_CASES
from app import create_app
from test_graph_bfs_documentation import run_doxygen
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-shell-baseline-low'
@pytest.fixture(scope='module')
def observed(tmp_path_factory):
 out=tmp_path_factory.mktemp('shell-baseline');return out,audit(out)
from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize('case',list(CASES))
def test_actual_shell_final_metrics_each_existing_array_and_shortcircuit(case,observed):
 out,r=observed;d=json.loads((audit_input_path(out/(case+'.json'))).read_text(encoding='utf-8'));row=next(x for x in r['rows'] if x['case']==case)
 assert row['final_array_metrics_match'] and d['response']['visual_state']['items']==d['fast_response']['visual_state']['items']==sorted(CASES[case])
 for p in d['projection']:
  step=d['response']['execution_trace']['steps'][p['runtime_index']];c=d['native'][p['native_index']]
  assert step['state_after']['items']==c['array'] and step['state_after']['metrics']['moves']==c['event']['moves']
  if p['token']=='gap_compare':assert step['pedagogy']['condition']['result']==c['condition']
 for idx,c in enumerate(d['native']):
  if c['event']['token']=='while_left' and not c['condition']:
   assert c['event']['j']<c['event']['intervalo'] and d['native'][idx+1]['event']['token']=='while_test'
 assert d['response']['result']['metrics']['swaps']==0

def test_existing_shell_variant_and_raw_guards(observed):
 out,r=observed;inventory=json.loads((audit_input_path(out/'inventory.json')).read_text(encoding='utf-8'));assert inventory['variant']['id']=='shell' and inventory['variant']['c_function']=='ordenar_shell' and inventory['total_methods']==11
 assert r['native_guard_cases']==2 and r['native_guard_observations']==19 and r['empty_API_rejected']

def test_c_h_Doxygen_and_four_closed_modules_preserved(observed):
 out,_=observed;run_doxygen(out,[out/'tad_ordenamiento.c',out/'tad_ordenamiento.h'])
 for ext in ['c','h']:assert (audit_input_path(out/('tad_ordenamiento.'+ext))).read_bytes()==(audit_input_path(ROOT/'docs/tads_C'/('tad_ordenamiento.'+ext))).read_bytes()
 hashes=json.loads((audit_input_path(ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-burbuja-instructions/implementation-hashes.json')).read_text(encoding='utf-8'))['files']
 for rel in ['app/domain/sorting/intercambio_instructions.py','app/domain/sorting/seleccion_instructions.py','app/domain/sorting/insercion_instructions.py','app/domain/sorting/burbuja_instructions.py']:assert hashlib.sha256((audit_input_path(ROOT/rel)).read_bytes()).hexdigest()==hashes[rel]

def test_repeated_shell_history_and_GET_no_redispatch(monkeypatch):
 from app.adapters.sorting_adapter import SortingAdapter
 c=create_app().test_client();c.post('/api/ordenamiento/create-array',json={'values':[4,3,2,1]})
 a=c.post('/api/ordenamiento/run',json={'algorithm_id':'shell','mode':'fast'}).get_json();b=c.post('/api/ordenamiento/run',json={'algorithm_id':'shell','mode':'fast'}).get_json()
 assert a['success'] and b['success'] and sum(e['operation']=='run' for e in b['history'])==2
 monkeypatch.setattr(SortingAdapter,'run',lambda *a,**k:pytest.fail('GET sorted again'))
 d=c.get('/api/ordenamiento/state').get_json();assert d['history']==b['history'] and d['main_c']==b['main_c'] and d['main_c'].count('ordenar_shell(arreglo, n);')==2

@pytest.mark.parametrize('case',list(UI_CASES))
def test_actual_browser_coarse_replay_and_downloaded_C_callers(case):
 r=json.loads((audit_input_path(E/'browser/report.json')).read_text(encoding='utf-8'));row=next(x for x in r['rows'] if x['case']==case)
 assert row['coarse_restorations']==2*row['coarse_steps'] and row['replay_extra_POSTs']==0 and row['page_errors']==[] and row['main_preserved_after_reload'] and row['five_stages'] and row['projected_moves_match_C']
 assert len(row['DOM_shell_variants'])==1 and row['DOM_shell_variants'][0]['id']=='shell'
 assert row['caller']['arrays']==[UI_CASES[case],sorted(UI_CASES[case])] and row['caller']['strict_C17'] and row['caller']['doxygen_warnings']==0 and row['caller']['allocations']==row['caller']['frees']==row['caller']['live']==0
 assert r['empty_UI_rejected'] and r['empty_caller']['successful_native_runs']==0

@pytest.mark.parametrize('case',list(CASES))
def test_every_shell_gap_for_while_local_scope_instruction_is_represented(case,observed):
 out,_=observed;d=json.loads((audit_input_path(out/(case+'.json'))).read_text(encoding='utf-8'));steps=d['response']['execution_trace']['steps'];native=d['native']
 assert len(steps)==len(native),f'{case}: C has {len(native)} observations; runtime has {len(steps)} frames'
 for step,c in zip(steps,native):
  assert step['debug'].get('instruction_event')==c['event'] and step['state_after']['items']==c['array']
  assert (step['pedagogy']['condition']['result'] if step['pedagogy']['condition'] else None)==c['condition']
