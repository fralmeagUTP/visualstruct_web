"""Merge LOW results/contracts plus permanent causal failures; no xfail or weakened gates."""
from pathlib import Path
import json,hashlib
import pytest
from _audit_mergesort_baseline import audit,CASES,UI_CASES
from app import create_app
from test_graph_bfs_documentation import run_doxygen
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-mergesort-baseline-low'
@pytest.fixture(scope='module')
def observed(tmp_path_factory):
 out=tmp_path_factory.mktemp('mergesort-baseline');return out,audit(out)
@pytest.mark.parametrize('case',list(CASES))
def test_real_merge_final_metrics_and_shortcircuit(case,observed):
 out,r=observed;d=json.loads((out/(case+'.json')).read_text(encoding='utf-8'));row=next(x for x in r['rows'] if x['case']==case)
 assert row['final_array_metrics_match'] and d['response']['visual_state']['items']==d['fast_response']['visual_state']['items']==sorted(CASES[case])
 for p in d['projection']:
  s=d['response']['execution_trace']['steps'][p['runtime_index']];c=d['native'][p['native_index']]
  assert s['state_after']['items']==c['array'] and s['state_after']['metrics']['moves']==c['event']['moves']
  if p['token']=='merge_compare':assert s['pedagogy']['condition']['result']==c['condition']
 for idx,c in enumerate(d['native']):
  if c['event']['token']=='merge_left' and c['condition'] is False:assert d['native'][idx+1]['event']['token']=='merge_while'
 assert d['response']['result']['metrics']['swaps']==0 and d['native'][-1]['event']['allocations']==d['native'][-1]['event']['frees']==1
 # Initial allocation contains no initialized objects; observer returns null without a read.
 reserve=next(c for c in d['native'] if c['event']['token']=='aux_reserve');assert reserve['event']['aux_live'] and reserve['auxiliary']==[None]*len(CASES[case])
 assert all(v is None for v in d['native'][-1]['auxiliary'])
def test_existing_merge_variant_and_raw_guards(observed):
 out,r=observed;i=json.loads((out/'inventory.json').read_text(encoding='utf-8'));assert i['variant']['id']=='mergesort' and i['variant']['c_function']=='ordenar_mergesort' and i['total_methods']==11
 assert r['native_guard_cases']==2 and r['native_guard_observations']==19 and r['empty_API_rejected']
def test_raw_first_allocation_failure_is_error_without_mutation(observed):
 out,r=observed;rows=[json.loads(x) for x in (out/'native.jsonl').read_text().splitlines() if json.loads(x)['case']==8]
 assert r['forced_allocation_failure_cases']==1 and r['forced_allocation_failure_observations']==12
 assert rows[-1]['event']['token']=='allocation_error' and all(x['array']==[2,1] for x in rows)
 assert all(x['event']['allocations']==x['event']['frees']==0 and not x['event']['aux_live'] for x in rows)
def test_download_C_H_Doxygen_six_closed_modules_preserved(observed):
 out,_=observed;run_doxygen(out,[out/'tad_ordenamiento.c',out/'tad_ordenamiento.h'])
 for ext in ['c','h']:assert (out/('tad_ordenamiento.'+ext)).read_bytes()==(ROOT/'docs/tads_C'/('tad_ordenamiento.'+ext)).read_bytes()
 h=json.loads((ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-quicksort-instructions/implementation-hashes.json').read_text(encoding='utf-8'))['files']
 for name in ['intercambio','seleccion','insercion','burbuja','shell','quicksort']:
  rel=f'app/domain/sorting/{name}_instructions.py';assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h[rel]
def test_repeated_merge_history_GET_does_not_redispatch(monkeypatch):
 from app.adapters.sorting_adapter import SortingAdapter
 c=create_app().test_client();c.post('/api/ordenamiento/create-array',json={'values':[4,3,2,1]});a=c.post('/api/ordenamiento/run',json={'algorithm_id':'mergesort','mode':'fast'}).get_json();b=c.post('/api/ordenamiento/run',json={'algorithm_id':'mergesort','mode':'fast'}).get_json();assert a['success'] and b['success'] and sum(e['operation']=='run' for e in b['history'])==2
 monkeypatch.setattr(SortingAdapter,'run',lambda *a,**k:pytest.fail('GET sorted again'));d=c.get('/api/ordenamiento/state').get_json();assert d['history']==b['history'] and d['main_c']==b['main_c'] and d['main_c'].count('ordenar_mergesort(arreglo, n);')==2
@pytest.mark.parametrize('case',list(UI_CASES))
def test_actual_browser_replay_and_downloaded_callers(case):
 r=json.loads((E/'browser/report.json').read_text(encoding='utf-8'));row=next(x for x in r['rows'] if x['case']==case)
 assert row['coarse_restorations']==2*row['coarse_steps'] and row['replay_extra_POSTs']==0 and row['page_errors']==[] and row['main_preserved_after_reload'] and row['five_stages'] and row['projected_moves_match_C']
 assert len(row['DOM_mergesort_variants'])==1 and row['DOM_mergesort_variants'][0]['id']=='mergesort'
 caller=row['caller'];assert caller['arrays']==[UI_CASES[case],sorted(UI_CASES[case])] and caller['strict_C17'] and caller['doxygen_warnings']==0 and caller['allocations']==caller['frees']==1 and caller['live']==0
 assert caller['first_allocation_failure']=={'returncode':1,'allocations':0,'frees':0,'live':0,'no_success_array_after_failure':True}
 assert r['empty_UI_rejected'] and r['empty_caller']['successful_native_runs']==0
@pytest.mark.parametrize('case',list(CASES))
def test_every_merge_allocation_recursion_write_free_scope_instruction_represented(case,observed):
 out,_=observed;d=json.loads((out/(case+'.json')).read_text(encoding='utf-8'));steps=d['response']['execution_trace']['steps'];native=d['native']
 assert len(steps)==len(native),f'{case}: C {len(native)} observations versus runtime {len(steps)} frames'
 for s,c in zip(steps,native):assert s['debug'].get('instruction_event')==c['event'] and s['state_after']['items']==c['array']
@pytest.mark.parametrize('case',[k for k in CASES if k!='single'])
def test_merge_auxiliary_only_shows_objects_initialized_in_C(case,observed):
 out,_=observed;d=json.loads((out/(case+'.json')).read_text(encoding='utf-8'))
 for p in d['projection']:
  if p['aux_runtime'] is not None:assert p['aux_runtime']==p['aux_native'],f"{case} frame {p['runtime_index']}: C auxiliary {p['aux_native']} versus runtime {p['aux_runtime']}"
