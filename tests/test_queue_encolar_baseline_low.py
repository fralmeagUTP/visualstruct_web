"""Finite enqueue regressions derived from current C events and actual UI/callers."""
from pathlib import Path
import json
import pytest
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-queue-encolar-instructions-medium'
from scripts.published_test_inputs import audit_input_path
def read(n):return json.loads((audit_input_path(E/n)).read_text(encoding='utf-8-sig'))
def sample():return read('report.json')[0]
def frame(token):
 fs=sample()['data']['execution_trace']['steps']
 return next(f for f in fs if token in f['line_text'] and (('malloc(' not in token) or f['event_type']=='allocator_success_return'))
def pointer(f,name):return next(p for p in f['pedagogy']['pointers'] if p['name']==name)
@pytest.mark.parametrize('case',['empty','single','duplicate','bounds'])
def test_finite_C_API_enqueue_results_preserve_fifo_duplicates_negative_int_bounds(case):
 rs=[r for r in read('report.json') if r['case']==case];assert len(rs)==2 and all(r['C_API_final_match'] and r['data']['success'] for r in rs)
@pytest.mark.parametrize('case',['empty','single','duplicate','bounds'])
def test_forty_value_and_heap_cardinality_observations_do_not_publish_early(case):
 for r in read('report.json'):
  if r['case']==case:assert all(o['root_values_match'] and o['native_heap_count']==o['trace_heap_count'] for o in r['observations'])
def test_safe_native14calls140events35conditions_guard_fault_masks_and_ownership():
 ns=read('native-report.json');assert len(ns)==140 and sum(n['condition']!=-1 for n in ns)==35 and len({n['sample'] for n in ns})==14
 assert [n['event'] for n in ns if n['root_argument_NULL']]==['entry','root_guard','root_error_printf','return']
 assert sum(n['event']=='allocator_NULL_return' for n in ns)==5
 for sid in [r['native_sample'] for r in read('report.json')]:
  events=[n for n in ns if n['sample']==sid];aid=next(n for n in events if n['event']=='aux_allocated')['aux_id'];assert [next(h['mask'] for h in n['live'] if h['id']==aid) for n in events if n['event'] in ['aux_allocated','value_assigned','link_assigned']]==[0,1,3]
 assert 'OWNERSHIP 12 12 0' in (audit_input_path(E/'native/stderr.log')).read_text(encoding='utf-8-sig')
def test_q_borrows_live_typed_initialized_caller_struct_address():
 p=pointer(frame('if (q == NULL)'), 'q');assert p['type']=='struct Cola *' and p['target']=='&cola' and p.get('scope')=='cola_encolar' and p.get('initialized') is True and p.get('valid') is True

def test_valid_empty_queue_guard_uses_address_not_empty_front():
 c=frame('if (q == NULL)')['pedagogy']['condition'];assert c['result'] is False and c['substituted']=='&cola == NULL'
def test_actual_C_scalar_valor_is_initialized_callee_parameter():
 vs=[v for v in frame('aux->nro = valor;')['pedagogy']['variables'] if v['name']=='valor'];assert vs and vs[0]['type']=='int' and vs[0].get('scope')=='cola_encolar' and vs[0].get('initialized') is True

def test_caller_front_rear_variables_use_NodoCola_type_and_scope():
 vs=[v for v in frame('if (q == NULL)')['pedagogy']['variables'] if v['name'] in ['delante','atras']];assert len(vs)==2 and all(v['type']=='struct NodoCola *' and v.get('scope')=='caller' for v in vs)
@pytest.mark.parametrize('line,mask',[('malloc(sizeof(struct NodoCola))',0),('aux->nro = valor;',1),('aux->sgte = NULL;',3)])
def test_reserved_fields_have_exact_validity_mask_after_each_store(line,mask):
 h=next(h for h in frame(line)['pedagogy']['heap_objects'] if h['status']=='temporary');assert h.get('initialized_mask')==mask and h.get('field_validity')=={'nro':bool(mask&1),'sgte':bool(mask&2)}
def test_temporary_fields_use_real_C_nro_sgte_names():
 h=next(h for h in frame('aux->sgte = NULL;')['pedagogy']['heap_objects'] if h['status']=='temporary');assert set(h['fields'])=={'nro','sgte'}
def test_malloc_is_exposed_as_opaque_call_not_an_invented_body():
 calls=next(f for f in sample()['data']['execution_trace']['steps'] if f['event_type']=='allocator_enter')['pedagogy']['call_stack'];assert any(c['function']=='malloc' and c.get('opaque') is True for c in calls)
def test_malloc_node_identity_is_preserved_through_front_publication():
 before=next(h for h in frame('aux->sgte = NULL;')['pedagogy']['heap_objects'] if h['status']=='temporary');after=frame('q->delante = aux;')['pedagogy']['heap_objects'];assert any(h['id']==before['id'] and h['status']=='linked' for h in after)
def test_aux_stays_live_alias_of_same_heap_object_until_return():
 f=frame('q->delante = aux;');a=pointer(f,'aux');assert a['target'] in {h['id'] for h in f['pedagogy']['heap_objects']} and a.get('valid') is True and a.get('scope')=='cola_encolar'
def test_actual_front_rear_projection_keeps_C_roots_at_all40_observations():
 os=[o for r in read('report.json') for o in r['observations']];assert len(os)==40 and all(o['front_projection_match'] and o['rear_projection_match'] for o in os)
def test_void_return_retires_only_callee_and_preserves_caller():
 f=sample()['data']['execution_trace']['steps'][-1];assert f['event_type']=='return' and not f['pedagogy']['call_stack'] and all(p.get('scope')=='caller' for p in f['pedagogy']['pointers'])
def test_entry_does_not_invent_undeclared_t_local_pointer():
 f=sample()['data']['execution_trace']['steps'][0];assert not any(p['name']=='t' for p in f['pedagogy']['pointers'])
def test_eight_real_UI_calls_two_views_reverse_exact_history_without_redispatch():
 rs=read('browser/report.json');assert len(rs)==4 and sum(r['actions'] for r in rs)==8 and all(r['forward_same_trace_two_views']==2*sum(o['frames'] for o in r['observations']) and r['back_same_trace_two_views']==2*sum(o['frames']-1 for o in r['observations']) for r in rs)
 assert all(r['five_numbered_sections_match'] and r['history_reload_equal'] and not r['JS_errors'] and r['extra_POSTs']==0 for r in rs);assert [len(r['history_after_reload']) for r in rs]==[2,3,3,4]
def test_reload_restores_exact_prepared_enqueue_trace():
 assert all(r['reload_trace_equal'] for r in read('browser/report.json'))
def test_actual_DOM_mains_C17_balance12_alloc_free_and_control12_NULL_positions():
 rs=read('caller-ownership/report.json');assert len(rs)==4 and sum(r['alloc_free_live'][0] for r in rs)==12
 assert all(r['strict_C17_original'] and r['alloc_free_live'][0]==r['alloc_free_live'][1] and r['alloc_free_live'][2]==0 for r in rs)
 fs=[f for r in rs for f in r['NULL_faults']];assert len(fs)==12 and all(f['exit']==1 and f['kernel_failure_reported'] and not f['failed_operation_announced_applied'] and f['alloc_free_live']==[f['point']-1,f['point']-1,0] for f in fs)
def test_actual_DOM_mains_have_four_documented_Doxygen_symbols_not_just_C_H():
 d=read('caller-doxygen.json');assert d['warning_lines']==0 and d['inputs']==6 and len(d['main_symbols_in_XML'])==4 and d['documented_main_count']==4

def test_HTTP_main_absence_is_recorded_without_inventing_a_download_contract():
 d=read('caller-availability.json');assert d['HTTP_main_status_each']==[404]*4 and not d['HTTP_queue_main_allowlisted'] and d['no_ADDED_endpoint_contract'] and d['HTTP_C_H_verified']
def test_eight_finite_resource_samples_are_measured_without_stress_claims():
 d=read('resources.json');assert len(d['calls'])==8 and all(r['python_peak_bytes']>=r['python_current_bytes']>=0 and r['response_bytes']>0 for r in d['calls'])
