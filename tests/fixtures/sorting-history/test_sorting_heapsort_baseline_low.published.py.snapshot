"""Heap sort LOW, strong causal fidelity regressions remain failing until scoped MEDIUM."""
from pathlib import Path
import json,hashlib
import pytest
from _audit_heapsort_baseline import audit,CASES,UI_CASES
from app import create_app
from app.domain.sorting.tad_ordenamiento import SortingInterpreter
from test_graph_bfs_documentation import run_doxygen
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'openspec/changes/audit-local-quality-and-unified-controls';E=B/'evidence/visible-sorting-heapsort-baseline-low'
@pytest.fixture(scope='module')
def observed(tmp_path_factory):
 out=tmp_path_factory.mktemp('heapsort-baseline');return out,audit(out)
@pytest.mark.parametrize('case',list(CASES))
def test_heapsort_real_final_metrics_and_helper_assignment_arrays(case,observed):
 out,r=observed;d=json.loads((out/(case+'.json')).read_text(encoding='utf-8'));row=next(x for x in r['rows'] if x['case']==case)
 assert row['final_array_compares_swaps_match'] and d['response']['visual_state']['items']==d['fast_response']['visual_state']['items']==sorted(CASES[case])
 assert d['response']['result']['metrics']['moves']==row['native_moves'] and row['final_metrics_match']
 for p in d['projection']:
  s=d['response']['execution_trace']['steps'][p['runtime_index']];c=d['native'][p['native_index']]
  assert s['state_after']['items']==c['array'] and s['state_after']['metrics']['moves']==c['event']['moves']
  if p['token'] in ['heap_compare_left','heap_compare_right','swap_guard']:assert (s['pedagogy']['condition']['result'] if s['pedagogy']['condition'] else None)==c['condition']
  if p['token'].startswith('swap_'):
   assert {v['name']:v['target'] for v in s['pedagogy']['pointers']}=={alias:f"arreglo[{c['event'][alias]}]" for alias in ['a','b']}
   assert all(v['value']==c['array'][c['event'][v['name']]] for v in s['pedagogy']['pointers'])
   assert s['pedagogy']['call_stack'][-1]['parameters']=={alias:f"arreglo[{c['event'][alias]}]" for alias in ['a','b']}
 for k,c in enumerate(d['native']):
  if c['event']['token'] in ['left_bound','right_bound'] and not c['condition']:assert d['native'][k+1]['event']['token']==('left_test' if c['event']['token']=='left_bound' else 'right_test')
 assert row['native_moves']==3*row['native_swaps']==3*row['native_helper_calls']
def test_heapsort_inventory_and_wrapper_guards_not_TADHeap(observed):
 out,r=observed;inv=json.loads((out/'inventory.json').read_text(encoding='utf-8'));assert inv['variant']['id']=='heapsort' and inv['variant']['c_function']=='ordenar_heapsort' and inv['actual_helper']=='heapify' and inv['distinct_from_TAD']=='binary_heap' and inv['total_methods']==11
 assert r['native_guard_cases']==2 and r['native_guard_observations']==19 and r['empty_API_rejected']
def test_real_helper_NULL_guards_or_shortcircuit_without_array_mutation(observed):
 out,r=observed;rows=[json.loads(s) for s in (out/'native.jsonl').read_text().splitlines() if json.loads(s)['case']>=8];assert r['raw_helper_guard_cases']==2 and r['raw_helper_guard_observations']==13
 assert all(c['array']==[42] and c['event']['moves']==c['event']['swaps']==0 for c in rows);assert not any(c['event']['token']=='swap_b_null' for c in rows if c['case']==8)
def test_real_download_Doxygen_and_seven_closed_modules_untouched(observed):
 out,_=observed;run_doxygen(out,[out/'tad_ordenamiento.c',out/'tad_ordenamiento.h'])
 h=json.loads((B/'evidence/visible-sorting-mergesort-instructions/implementation-hashes.json').read_text(encoding='utf-8'))['files']
 for name in ['intercambio','seleccion','insercion','burbuja','shell','quicksort','mergesort']:
  rel=f'app/domain/sorting/{name}_instructions.py';assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h[rel]
 for ext in ['c','h']:assert (out/('tad_ordenamiento.'+ext)).read_bytes()==(ROOT/'docs/tads_C'/('tad_ordenamiento.'+ext)).read_bytes()
def test_repeated_heapsort_history_GET_no_sort_again(monkeypatch):
 from app.adapters.sorting_adapter import SortingAdapter
 c=create_app().test_client();c.post('/api/ordenamiento/create-array',json={'values':[4,3,2,1]});a=c.post('/api/ordenamiento/run',json={'algorithm_id':'heapsort','mode':'fast'}).get_json();b=c.post('/api/ordenamiento/run',json={'algorithm_id':'heapsort','mode':'fast'}).get_json();assert a['success'] and b['success'] and sum(e['operation']=='run' for e in b['history'])==2
 monkeypatch.setattr(SortingAdapter,'run',lambda *a,**k:pytest.fail('GET sorted again'));d=c.get('/api/ordenamiento/state').get_json();assert d['main_c']==b['main_c'] and d['history']==b['history'] and d['main_c'].count('ordenar_heapsort(arreglo, n);')==2
def test_shared_swap_default_preserved_and_heap_optin_no_fake_TAD_console():
 p=SortingInterpreter([2,1],'heapsort');p._swap(0,1);old=json.loads((E/'default-helper-before.json').read_text(encoding='utf-8'));assert old=={'values':p.values,'steps':p._steps,'metrics':vars(p.metrics)}
 p=SortingInterpreter([4,3,2,1],'heapsort');d=p.run();assert not any(s['console_output'] for s in d['steps'])
@pytest.mark.parametrize('case',list(UI_CASES))
def test_actual_browser_coarse_replay_and_C17_downloaded_callers(case):
 r=json.loads((E/'browser-final/report.json').read_text(encoding='utf-8'));row=next(x for x in r['rows'] if x['case']==case)
 assert row['coarse_restorations']==2*row['coarse_steps'] and row['replay_extra_POSTs']==0 and row['page_errors']==[] and row['main_preserved_after_reload'] and row['five_stages'] and row['projected_moves_match_C'] and row['printf_frames']==[]
 assert len(row['DOM_heapsort_variants'])==1 and row['DOM_heapsort_variants'][0]['id']=='heapsort'
 c=row['caller'];assert c['arrays']==[UI_CASES[case],sorted(UI_CASES[case])] and c['strict_C17'] and c['doxygen_warnings']==0 and c['allocations']==c['frees']==c['live']==0 and c['successful_native_runs']==1
 assert r['empty_UI_rejected'] and r['empty_caller']['successful_native_runs']==0
@pytest.mark.parametrize('case',list(CASES))
def test_every_C_heapsort_for_heapify_recursion_helper_instruction_represented(case,observed):
 out,_=observed;d=json.loads((out/(case+'.json')).read_text(encoding='utf-8'));steps=d['response']['execution_trace']['steps'];native=d['native'];assert len(steps)==len(native),f'{case}: C {len(native)} observations, runtime {len(steps)} frames'
 for step,c in zip(steps,native):assert step['debug'].get('instruction_event')==c['event'] and step['state_after']['items']==c['array']
@pytest.mark.parametrize('case',list(CASES))
def test_real_wrapper_size_t_i_heapify_locals_scope_call_parameters(case,observed):
 out,_=observed;d=json.loads((out/(case+'.json')).read_text(encoding='utf-8'));steps=d['response']['execution_trace']['steps']
 # Even n1 executes both real for initializers/tests; demand these controls and the C i local.
 for token in ['build_init','build_test','extract_init','extract_test']:
  c=next(c for c in d['native'] if c['event']['token']==token);matches=[s for s in steps if s['debug'].get('instruction_event')==c['event']];assert matches,f'{case}: missing actual C control {token}'
  assert any(v['name']=='i' and v['type']=='size_t' and v.get('scope')=='ordenar_heapsort' and v['value']==c['event']['i'] for v in matches[0]['pedagogy']['variables'])
 for p in d['projection']:
  c=d['native'][p['native_index']];s=steps[p['runtime_index']]
  if c['event']['frames']:
   top=c['event']['frames'][-1];assert any(call['function']=='heapify' and call['parameters'].get('n')==top['n'] and call['parameters'].get('raiz')==top['raiz'] for call in s['pedagogy']['call_stack'])
