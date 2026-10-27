"""Counting sort LOW preserves causal failures; full instruction trace remains pending."""
from pathlib import Path
import json,hashlib
import pytest
from _audit_counting_baseline import audit,CASES,UI_CASES
from _audit_counting_limits import audit as limits
from app import create_app
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-counting-baseline-low';H=E.parent/'visible-sorting-heapsort-instructions'
@pytest.fixture(scope='module')
def observed(tmp_path_factory):
    out=tmp_path_factory.mktemp('counting');return out,audit(out)
from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize('case',list(CASES))
def test_final_array_and_explicit_data_write_metrics(case,observed):
    out,r=observed;d=json.loads((audit_input_path(out/(case+'.json'))).read_text(encoding='utf-8'));row=next(x for x in r['rows'] if x['case']==case)
    assert d['response']['visual_state']['items']==d['fast_response']['visual_state']['items']==sorted(CASES[case])
    assert row['runtime_metrics']['comparisons']==row['native_comparisons']==2*(len(CASES[case])-1)
    assert row['runtime_metrics']['moves']==row['native_moves']==3*len(CASES[case]) and row['runtime_metrics']['swaps']==0
    for p in d['projection']:
        s=d['response']['execution_trace']['steps'][p['runtime_index']];c=d['native'][p['native_index']]
        assert s['state_after']['items']==c['array']
        assert s['state_after']['auxiliary_array']==c['conteo']
        assert s['state_after']['metrics']['comparisons']==c['comparisons'] and s['state_after']['metrics']['moves']==c['moves']
@pytest.mark.parametrize('case',list(CASES))
def test_every_C_minmax_for_bucket_array_write_decrement_free_instruction(case,observed):
    out,_=observed;d=json.loads((audit_input_path(out/(case+'.json'))).read_text(encoding='utf-8'));steps=d['response']['execution_trace']['steps'];assert len(steps)==len(d['native'])
    for s,c in zip(steps,d['native']):assert s['state_after']['items']==c['array'] and s['debug'].get('instruction_event') is not None
@pytest.mark.parametrize('case',list(CASES))
def test_real_minmax_scope_count_pointer_zeroed_calloc_and_free(case,observed):
    out,_=observed;d=json.loads((audit_input_path(out/(case+'.json'))).read_text(encoding='utf-8'));steps=d['response']['execution_trace']['steps']
    assert any(s['pedagogy']['call_stack'][-1]['function']=='obtener_minimo_maximo' for s in steps if s['pedagogy']['call_stack'])
    allocation=next(s for s in steps if s['state_after']['trace_token']=='count_init');assert any(p['name']=='conteo' for p in allocation['pedagogy']['pointers'])
    assert any(v['name']=='rango' and v['type']=='size_t' for v in allocation['pedagogy']['variables'])
    assert any(s['state_after']['trace_token']=='count_free' for s in steps)

def test_raw_defined_int32_range_boundaries_guards_calloc_failure(tmp_path):
    r=limits(tmp_path);assert r['public_cases']==8 and r['helper_guard_cases']==4 and r['calloc_failure_cases']==1 and r['allocations']==r['frees']==3 and r['live']==0

def test_actual_download_Doxygen_and_eight_modules_preserved(observed):
    from test_graph_bfs_documentation import run_doxygen
    out,_=observed;run_doxygen(out,[out/'tad_ordenamiento.c',out/'tad_ordenamiento.h']);h=json.loads((audit_input_path(H/'implementation-hashes.json')).read_text())['files']
    prior=json.loads((audit_input_path(E.parent/'visible-sorting-mergesort-instructions/implementation-hashes.json')).read_text())['files']
    for method in ['intercambio','seleccion','insercion','burbuja','shell','quicksort','mergesort','heapsort']:
        rel=f'app/domain/sorting/{method}_instructions.py';assert hashlib.sha256((audit_input_path(ROOT/rel)).read_bytes()).hexdigest()==(h if rel in h else prior)[rel]
    for ext in ['c','h']:assert (audit_input_path(out/('tad_ordenamiento.'+ext))).read_bytes()==(audit_input_path(ROOT/'docs/tads_C'/('tad_ordenamiento.'+ext))).read_bytes()

def test_API_input_bounds_and_rejected_range_no_run():
    for values in [[],[1.5],[True],[2147483648],[-2147483649],list(range(81))]:
        c=create_app().test_client();d=c.post('/api/ordenamiento/create-array',json={'values':values}).get_json();assert not d['success']
    c=create_app().test_client();assert c.post('/api/ordenamiento/create-array',json={'values':[-2147483648,2147483647]}).get_json()['success'];d=c.post('/api/ordenamiento/run',json={'algorithm_id':'counting_sort'}).get_json();assert not d['success'] and all(e['operation']!='run' for e in d['history'])
    assert c.get('/api/ordenamiento/state').get_json()['visual_state']['items']==[-2147483648,2147483647]

def test_repeated_history_reload_does_not_sort(monkeypatch):
    from app.adapters.sorting_adapter import SortingAdapter
    c=create_app().test_client();c.post('/api/ordenamiento/create-array',json={'values':[2,1]})
    for _ in range(2):d=c.post('/api/ordenamiento/run',json={'algorithm_id':'counting_sort'}).get_json();assert d['success']
    monkeypatch.setattr(SortingAdapter,'run',lambda *a,**kw:pytest.fail('GET sorted again'));g=c.get('/api/ordenamiento/state').get_json();assert g['history']==d['history'] and g['main_c']==d['main_c'] and g['main_c'].count('ordenar_counting_sort(arreglo, n);')==2

def test_no_raw_TAD_printf_attribution():
    from app.domain.sorting.tad_ordenamiento import SortingInterpreter
    assert not any(s['console_output'] for s in SortingInterpreter([2,1],'counting_sort').run()['steps'])
@pytest.mark.parametrize('case',list(UI_CASES))
def test_actual_coarse_browser_and_downloaded_C17_caller(case):
    r=json.loads((audit_input_path(E/'browser-verified/report.json')).read_text());row=next(x for x in r['rows'] if x['case']==case)
    assert row['forward_reverse_restorations']==2*row['instructions'] and row['replay_extra_POSTs']==0 and row['page_errors']==[] and row['reload_main_preserved'] and row['JSON_exact_cursor_state_main_preserved'] and row['five_stages']
    c=row['caller'];assert c['strict_C17'] and c['doxygen_warnings']==0 and c['allocations']==c['frees']==1 and c['live']==0 and c['successful_native_runs']==1
    assert c['first_allocation_failure']=={'returncode':1,'allocations':0,'frees':0,'live':0,'no_success_array_after_failure':True}
    assert r['empty_UI_rejected']
