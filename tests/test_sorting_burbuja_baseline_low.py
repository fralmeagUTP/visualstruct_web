"""Finite improved-bubble baseline and scoped move-counter regressions."""
from pathlib import Path
import json,sys,types
import pytest
from _audit_burbuja_baseline import audit,CASES,UI_CASES
from app.domain.sorting.tad_ordenamiento import SortingInterpreter
from app import create_app
from test_graph_bfs_documentation import run_doxygen
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-burbuja-baseline-low'
@pytest.fixture(scope='module')
def observed(tmp_path_factory):
 out=tmp_path_factory.mktemp('burbuja-baseline');return out,audit(out)

from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize('case',list(CASES))
def test_final_counts_early_stop_and_each_existing_array_move_match_C(case,observed):
 out,report=observed;data=json.loads((audit_input_path(out/(case+'.json'))).read_text(encoding='utf-8'));row=next(r for r in report['rows'] if r['case']==case)
 assert row['final_comparison_swap_parity'] and row['moves_match'] and row['native_moves']==3*row['swaps'] and row['array_differences']==0
 assert data['response']['visual_state']['items']==data['fast_response']['visual_state']['items']==sorted(CASES[case])
 for projection in data['projection']:
  c=data['native'][projection['native_index']];step=data['response']['execution_trace']['steps'][projection['runtime_index']]
  assert step['state_after']['items']==c['array'] and projection['moves_native']==projection['moves_runtime']
  if projection['token']=='compare':assert step['pedagogy']['condition']['result']==c['condition']
 assert row['completed_passes']=={'single':0,'ordered':1,'reverse':3,'duplicates':1,'negative':2,'extremes':2,'early_after_swap':2}[case]
 assert row['early_stop']==(case not in ['single','reverse'])


def test_exact_existing_variant_and_native_guards(observed):
 out,r=observed;inventory=json.loads((audit_input_path(out/'inventory.json')).read_text(encoding='utf-8'))
 assert inventory['C_definitions']==inventory['H_declarations']==['ordenar_burbuja'] and len(inventory['registered_variants'])==len(inventory['API_variants'])==1 and inventory['total_sorting_ids']==11
 assert r['native_guard_cases']==2 and r['native_guard_observations']==21 and r['empty_API_rejected']


def test_c_h_doxygen_and_closed_modules_preserved(observed):
 out,_=observed;run_doxygen(out,[out/'tad_ordenamiento.c',out/'tad_ordenamiento.h'])
 for ext in ['c','h']:assert (audit_input_path(out/('tad_ordenamiento.'+ext))).read_bytes()==(audit_input_path(ROOT/'docs/tads_C'/('tad_ordenamiento.'+ext))).read_bytes()
 closed=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-insercion-instructions/implementation-hashes.json'
 import hashlib
 hashes=json.loads(audit_input_path(closed).read_text(encoding='utf-8'))['files']
 for rel in ['app/domain/sorting/intercambio_instructions.py','app/domain/sorting/seleccion_instructions.py','app/domain/sorting/insercion_instructions.py']:assert hashlib.sha256((audit_input_path(ROOT/rel)).read_bytes()).hexdigest()==hashes[rel]


def test_default_shared_helper_keeps_original_behavior_without_running_closed_methods():
 source=E/'before/app/domain/sorting/tad_ordenamiento.py';module=types.ModuleType('_burbuja_original_helper');sys.modules[module.__name__]=module
 try:
  exec(compile(audit_input_path(source).read_text(encoding='utf-8'),str(source),'exec'),module.__dict__)
  old=module.SortingInterpreter([2,1],'shell');current=SortingInterpreter([2,1],'shell')
  old._swap(0,1);current._swap(0,1)
  assert old._steps==current._steps and old.values==current.values and old.metrics.moves==current.metrics.moves==0
 finally:sys.modules.pop(module.__name__,None)


def test_repeated_bubble_history_and_get_no_redispatch(monkeypatch):
 from app.adapters.sorting_adapter import SortingAdapter
 c=create_app().test_client();c.post('/api/ordenamiento/create-array',json={'values':[2,1,3,4]})
 a=c.post('/api/ordenamiento/run',json={'algorithm_id':'burbuja','mode':'fast'}).get_json();b=c.post('/api/ordenamiento/run',json={'algorithm_id':'burbuja','mode':'fast'}).get_json();assert a['success'] and b['success'] and sum(e['operation']=='run' for e in b['history'])==2
 assert a['result']['metrics']['moves']==3 and b['result']['metrics']['moves']==0
 monkeypatch.setattr(SortingAdapter,'run',lambda *a,**k:pytest.fail('GET redispatched sorting'))
 state=c.get('/api/ordenamiento/state').get_json();assert state['history']==b['history'] and state['main_c']==b['main_c'] and state['main_c'].count('ordenar_burbuja(arreglo, n);')==2

@pytest.mark.parametrize('case',list(UI_CASES))
def test_actual_recorded_browser_replay_inventory_moves_and_caller(case):
 r=json.loads((audit_input_path(E/'browser/report.json')).read_text(encoding='utf-8'));row=next(row for row in r['rows'] if row['case']==case)
 assert row['coarse_restorations']==2*row['coarse_steps'] and row['replay_extra_POSTs']==0 and row['page_errors']==[] and row['main_preserved_after_reload'] and row['five_stages'] and row['projected_moves_match_C']
 assert len(row['DOM_bubble_variants'])==1 and row['DOM_bubble_variants'][0]['id']=='burbuja'
 assert row['caller']['arrays']==[UI_CASES[case],sorted(UI_CASES[case])] and row['caller']['strict_C17'] and row['caller']['doxygen_warnings']==0 and row['caller']['allocations']==row['caller']['frees']==row['caller']['live']==0
 assert r['empty_UI_rejected'] and r['empty_caller']['successful_native_runs']==0

@pytest.mark.parametrize('case',list(CASES))
def test_every_bubble_control_flag_helper_scope_instruction_is_represented(case,observed):
 out,_=observed;d=json.loads((audit_input_path(out/(case+'.json'))).read_text(encoding='utf-8'));steps=d['response']['execution_trace']['steps'];native=d['native']
 assert len(steps)==len(native),f'{case}: C has {len(native)} observations; runtime has {len(steps)} frames'
 for step,c in zip(steps,native):
  assert step['debug'].get('instruction_event')==c['event']
  assert step['state_after']['items']==c['array']
  assert (step['pedagogy']['condition']['result'] if step['pedagogy']['condition'] else None)==c['condition']
