"""Permanent finite push regressions; incomplete fidelity stays red without xfail."""
from pathlib import Path
import json
import pytest
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-stack-apilar-baseline-low'
M=E.parent/'visible-stack-apilar-instructions-medium'
if (M/'caller-ownership/report.json').exists():E=M
def read(name):return json.loads((E/name).read_text(encoding='utf-8-sig'))
def rows():return read('report.json')
def sample():return next(r for r in rows() if r['case']=='empty' and r['repeat']==1)
def frame(line):
 fs=[f for f in sample()['data']['execution_trace']['steps'] if f['line_text'].strip()==line];return next((f for f in fs if f.get('debug',{}).get('token')=='aux_allocated'),fs[0])
def pointer(f,name):return next(p for p in f['pedagogy']['pointers'] if p['name']==name)
@pytest.mark.parametrize('case',['empty','single','duplicate','bounds'])
def test_finite_C_API_push_results_preserve_duplicate_negative_and_int_bound(case):
 rs=[r for r in rows() if r['case']==case];assert len(rs)==2 and all(r['C_API_final_match'] and r['data']['success'] for r in rs)
@pytest.mark.parametrize('case',['empty','single','duplicate','bounds'])
def test_root_values_and_live_cardinality_already_match_C_without_early_publish(case):
 for r in rows():
  if r['case']==case:assert all(o['root_values_match'] and o['native_heap_count']==o['trace_heap_count'] for o in r['observations'])
def test_safe_native_guards_faults_partial_masks_and_lifetimes():
 ns=read('native-report.json');assert len(ns)==124 and sum(n['condition']!=-1 for n in ns)==27 and len({n['sample'] for n in ns})==14
 null=[n for n in ns if n['root_argument_NULL']];assert [n['event'] for n in null]==['entry','root_guard','root_error_printf','return'] and 'pila no inicializada' in null[-1]['console']
 faults=[n for n in ns if n['event']=='allocator_NULL_return'];assert len(faults)==5
 for sid in [r['native_sample'] for r in rows()]:
  events=[n for n in ns if n['sample']==sid];aid=next(n for n in events if n['event']=='aux_allocated')['aux_id'];assert [next(h['mask'] for h in n['live'] if h['id']==aid) for n in events if n['event'] in ['aux_allocated','value_assigned','link_assigned']]==[0,1,3]
 assert 'OWNERSHIP 12 12 0' in (E/'native/stderr.log').read_text(encoding='utf-8')
def test_p_is_pointer_to_caller_storage_not_top_node_or_NULL():
 p=pointer(frame('if (p == NULL) {'),'p');assert p['type']=='ptrPila *' and p['target'] and p.get('valid') is True and p.get('scope')=='pila_apilar'
def test_valid_empty_root_guard_never_substitutes_NULL_equal_NULL():
 c=frame('if (p == NULL) {')['pedagogy']['condition'];assert c['result'] is False and c['substituted']!='NULL == NULL'
def test_actual_C_scalar_param_valor_is_scoped_initialized():
 vs=frame('aux->nro = valor;')['pedagogy']['variables'];v=next(v for v in vs if v['name']=='valor');assert v['type']=='int' and v.get('scope')=='pila_apilar' and v.get('initialized') is True
@pytest.mark.parametrize('line,mask',[('ptrPila aux = (ptrPila) malloc(sizeof(struct NodoPila));',0),('aux->nro = valor;',1),('aux->sgte = *p;',3)])
def test_temporary_heap_fields_have_exact_initialization_mask(line,mask):
 h=next(h for h in frame(line)['pedagogy']['heap_objects'] if h['status']=='temporary');assert h.get('initialized_mask')==mask and h.get('field_validity')=={'nro':bool(mask&1),'sgte':bool(mask&2)}
def test_fields_use_actual_C_nro_and_sgte_names():
 h=next(h for h in frame('aux->sgte = *p;')['pedagogy']['heap_objects'] if h['status']=='temporary');assert set(h['fields'])=={'nro','sgte'}
def test_malloc_object_identity_survives_publication():
 before=next(h for h in frame('aux->sgte = *p;')['pedagogy']['heap_objects'] if h['status']=='temporary');after=frame('*p = aux;')['pedagogy']['heap_objects'];assert any(h['id']==before['id'] and h['status']=='linked' for h in after)
def test_aux_remains_live_alias_after_publication_until_return():
 f=frame('*p = aux;');p=pointer(f,'aux');assert p['target'] in {h['id'] for h in f['pedagogy']['heap_objects']} and p.get('valid') is True
 assert p.get('scope')=='pila_apilar'
def test_void_return_retires_only_callee_and_preserves_caller():
 f=sample()['data']['execution_trace']['steps'][-1];assert f['event_type']=='return' and not f['pedagogy']['call_stack'] and not any(p.get('scope')=='pila_apilar' for p in f['pedagogy']['pointers'])
def test_eight_UI_calls_two_views_reverse_exact_history_and_no_redispatch():
 rs=read('browser/report.json');assert len(rs)==4 and sum(r['actions'] for r in rs)==8 and sum(r['forward_same_trace_two_views'] for r in rs)==(160 if E==M else 112) and sum(r['back_same_trace_two_views'] for r in rs)==(144 if E==M else 96)
 assert all(r['five_numbered_sections_match'] and r['history_reload_equal'] and not r['JS_errors'] and r['extra_POSTs']==0 for r in rs)
 assert [len(r['history_after_reload']) for r in rs]==[2,3,3,4]
def test_reload_keeps_the_exact_last_prepared_push_trace():
 assert all(r['reload_trace_equal'] for r in read('browser/report.json'))
def test_actual_DOM_main_releases_all_ownership_at_exit():
 rs=[r for r in read('caller-ownership/report.json') if r['surface']=='DOM'];assert len(rs)==4
 assert all(r['normal_alloc_free_live'][0]==r['normal_alloc_free_live'][1] and r['normal_alloc_free_live'][2]==0 for r in rs)
def test_actual_HTTP_main_C17_balanced_faults_do_not_announce_failed_push():
 rs=[r for r in read('caller-ownership/report.json') if r['surface']=='HTTP'];assert len(rs)==4 and sum(r['normal_alloc_free_live'][0] for r in rs)==12
 assert all(r['strict_C17'] and r['normal_alloc_free_live'][0]==r['normal_alloc_free_live'][1] and r['normal_alloc_free_live'][2]==0 for r in rs)
 assert sum(len(r['NULL_faults']) for r in rs)==12 and all(f['exit']==1 and f['kernel_diagnostic'] and f['alloc_free_live'][0]==f['alloc_free_live'][1] and f['alloc_free_live'][2]==0 and not f['failed_push_falsely_applied'] for r in rs for f in r['NULL_faults'])
def test_actual_DOM_main_reports_NULL_failure_without_false_success():
 rs=[r for r in read('caller-ownership/report.json') if r['surface']=='DOM'];assert all(f['exit']!=0 and not f['failed_push_falsely_applied'] for r in rs for f in r['NULL_faults'])
def test_both_actual_caller_surfaces_have_four_documented_main_symbols():
 ds=read('caller-doxygen.json');assert {d['surface'] for d in ds}=={'DOM','HTTP'} and all(d['warnings']==0 and len(d['main_symbols'])==4 for d in ds)
 assert all(d['documented']==4 for d in ds)
def test_eight_finite_resource_samples_are_instrumented_not_stress_claims():
 d=read('resources.json');assert len(d['calls'])==8 and all(r['python_peak_bytes']>=r['python_current_bytes']>=0 and r['response_bytes']>0 for r in d['calls'])
