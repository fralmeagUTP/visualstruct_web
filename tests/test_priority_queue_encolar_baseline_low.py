"""Finite normative priority enqueue regressions; baseline failures stay visible."""
from pathlib import Path
import json
import pytest
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-priority-queue-encolar-instructions-medium'
def read(name):return json.loads((E/name).read_text(encoding='utf-8-sig'))
def sample():return read('report.json')[0]
def frames():return sample()['data']['execution_trace']['steps']
def frame(line):return next(f for f in frames() if f['line_text'].strip()==line and ('malloc(' not in line or f['event_type']=='allocator_success_return'))
def pointer(f,name):return next(p for p in f['pedagogy']['pointers'] if p['name']==name)

@pytest.mark.parametrize('case',['empty','single','duplicate','bounds'])
def test_C_API_final_enqueue_FIFO_and_stable_priority_agree(case):
 rs=[r for r in read('report.json') if r['case']==case];assert len(rs)==2 and all(r['final_fifo_and_stable_priority_match'] and r['data']['success'] for r in rs)

@pytest.mark.parametrize('case',['empty','single','duplicate','bounds'])
def test_all72_reachable_value_priority_observations_match_actual_C(case):
 assert all(o['root_items_match'] for r in read('report.json') if r['case']==case for o in r['observations'])

@pytest.mark.parametrize('case,index',[('duplicate',0),('single',1),('bounds',2)])
def test_arrival_order_is_not_sorted_and_equal_priorities_keep_first_candidate(case,index):
 for r in read('report.json'):
  if r['case']==case:
   items=r['data']['visual_state']['items'];assert items==[{'value':v,'priority':p} for v,p in r['seeds']]+[{'value':r['value'],'priority':r['priority']}]*r['repeat'];assert r['data']['visual_state']['out_index']==index

def test_safe_native14calls242events48conditions_with_initialized_fields_only():
 ns=read('native-report.json');assert len(ns)==242 and len({n['sample'] for n in ns})==14 and sum(n['condition']!=-1 for n in ns)==48
 for r in read('report.json'):
  ns=r['native_events'];aid=next(n for n in ns if n['event']=='helper_new_allocated')['helper_new_id'];assert [next(h['mask'] for h in n['live'] if h['id']==aid) for n in ns if n['event'] in ['helper_new_allocated','value_assigned','priority_assigned','link_assigned']]==[0,1,3,7]
 assert (E/'native/stderr.log').read_text(encoding='utf-8-sig').strip()=='OWNERSHIP 12 12 0'

def test_native_NULL_root_returns_false_before_helper_or_allocation():
 ns=[n for n in read('native-report.json') if n['root_NULL']];assert [n['event'] for n in ns]==['entry','new_declared','root_guard','return_false'] and all(not n['live'] for n in ns)

def test_native_five_controlled_malloc_NULL_calls_preserve_roots_quantity_and_live_nodes():
 alln=read('native-report.json');ss={n['sample'] for n in alln if n['event']=='allocator_NULL_return'};assert len(ss)==5
 for sid in ss:
  ns=[n for n in alln if n['sample']==sid];assert ns[-1]['event']=='return_false'
  for field in ['front_id','rear_id','quantity','root_items','live']:assert ns[0][field]==ns[-1][field]
  assert not any(n['event'] in ['value_assigned','priority_assigned','link_assigned','count_incremented'] for n in ns)

def test_trace_executes_initialized_root_guard_using_caller_address():
 fs=[f for f in frames() if f['line_text'].strip()=='if (cola == NULL) {'];assert len(fs)==1
 p=pointer(fs[0],'cola');assert p['type']=='ColaPrioridad *' and p['target']=='&cp' and p.get('scope')=='cp_encolar' and p.get('initialized') is True and p.get('valid') is True
 assert fs[0]['pedagogy']['condition']['result'] is False and fs[0]['pedagogy']['condition']['substituted']=='&cp == NULL'

def test_parent_nuevo_declaration_is_visible_uninitialized_before_root_guard():
 fs=[f for f in frames() if f['line_text'].strip()=='CPNodo *nuevo;'];assert len(fs)==1
 p=pointer(fs[0],'nuevo');assert p['type']=='CPNodo *' and p.get('scope')=='cp_encolar' and p.get('initialized') is False and p.get('valid') is False

def test_actual_scalar_valor_prioridad_are_typed_initialized_parent_parameters():
 vs=frames()[0]['pedagogy']['variables'];selected=[v for v in vs if v['name'] in ['valor','prioridad']];assert len(selected)==2 and all(v['type']=='int' and v.get('scope')=='cp_encolar' and v.get('initialized') is True for v in selected)

def test_caller_front_rear_quantity_are_initialized_typed_caller_fields():
 vs=frames()[0]['pedagogy']['variables'];selected=[v for v in vs if v['name'] in ['delante','atras','cantidad']];assert len(selected)==3 and all(v.get('scope')=='caller' and v.get('initialized') is True for v in selected);assert all(v['type']=='CPNodo *' for v in selected if v['name']!='cantidad');assert next(v for v in selected if v['name']=='cantidad')['type']=='int'

def test_helper_call_keeps_parent_continuation_and_real_C_parameters():
 calls=frame('static CPNodo *cp_crear_nodo(int valor, int prioridad) {')['pedagogy']['call_stack'];assert [c['function'] for c in calls]==['cp_encolar','cp_crear_nodo'];assert calls[-1]['parameters']=={'valor':9,'prioridad':3}

def test_shadowed_nuevo_locals_have_distinct_function_scopes():
 f=frame('nuevo->valor = valor;');vs=[v for v in f['pedagogy']['variables'] if v['name']=='nuevo'];assert {v.get('scope') for v in vs}=={'cp_encolar','cp_crear_nodo'}

def test_malloc_is_opaque_callee_nested_under_helper_and_parent():
 calls=next(f for f in frames() if f['event_type']=='allocator_enter')['pedagogy']['call_stack'];assert [c['function'] for c in calls]==['cp_encolar','cp_crear_nodo','malloc'] and calls[-1].get('opaque') is True

@pytest.mark.parametrize('line,mask',[('CPNodo *nuevo = (CPNodo *)malloc(sizeof(CPNodo));',0),('nuevo->valor = valor;',1),('nuevo->prioridad = prioridad;',3),('nuevo->sgte = NULL;',7)])
def test_reserved_fields_have_exact_masks_after_real_C_stores(line,mask):
 h=next(h for h in frame(line)['pedagogy']['heap_objects'] if h['status']=='temporary');assert h.get('initialized_mask')==mask and h.get('field_validity')=={'valor':bool(mask&1),'prioridad':bool(mask&2),'sgte':bool(mask&4)}

def test_linked_node_fields_use_real_C_names_including_next_pointer():
 f=frame('cola->delante = nuevo;');hs=[h for h in f['pedagogy']['heap_objects'] if h['status']=='linked'];assert hs and all(set(h['fields'])=={'valor','prioridad','sgte'} for h in hs)

def test_returned_helper_object_preserves_identity_through_publication():
 old=next(h for h in frame('return nuevo;')['pedagogy']['heap_objects'] if h['status']=='temporary');published=frame('cola->delante = nuevo;')['pedagogy']['heap_objects'];assert any(h['id']==old['id'] and h['status']=='linked' for h in published)

def test_parent_nuevo_is_live_alias_of_actual_heap_object_until_exit():
 f=frame('cola->atras = nuevo;');p=pointer(f,'nuevo');assert isinstance(p['target'],str) and p['target'] in {h['id'] for h in f['pedagogy']['heap_objects']} and p.get('scope')=='cp_encolar' and p.get('valid') is True

def test_count_increment_does_not_free_or_retire_any_node():
 for r in read('report.json'):
  f=next(f for f in r['data']['execution_trace']['steps'] if f['line_text'].strip()=='cola->cantidad++;');assert f['pedagogy']['heap_transition']['freed']==[]

def test_all72_front_rear_projections_keep_actual_C_extremes():
 os=[o for r in read('report.json') for o in r['observations']];assert len(os)==72 and all(o['front_match'] and o['rear_match'] for o in os)

def test_all72_quantity_observations_keep_actual_C_counter():
 os=[o for r in read('report.json') for o in r['observations']];assert len(os)==72 and all(o['quantity_match'] for o in os)

def test_all72_heap_cardinalities_have_one_object_per_actual_allocation():
 os=[o for r in read('report.json') for o in r['observations']];assert len(os)==72 and all(o['heap_count_match'] for o in os)

def test_return_true_retires_only_callee_and_reports_real_bool_value():
 f=frames()[-1];assert f['pedagogy']['call_stack']==[] and all(p.get('scope')=='caller' for p in f['pedagogy']['pointers']);assert f['debug']['return_value'] is True

def test_entry_has_no_undeclared_p_t_ant_locals():
 assert not any(p['name'] in ['p','t','ant'] for p in frames()[0]['pedagogy']['pointers'])

def test_eight_actual_UI_calls_two_views_reverse_without_redispatch():
 rs=read('browser/report.json');assert len(rs)==4 and sum(r['actions'] for r in rs)==8 and all(r['forward_same_trace_two_views']==2*sum(o['frames'] for o in r['observations']) and r['back_same_trace_two_views']==2*sum(o['frames']-1 for o in r['observations']) for r in rs)
 assert all(r['history_reload_equal'] and r['five_numbered_sections_match'] and not r['JS_errors'] and r['extra_POSTs']==0 for r in rs)

def test_four_reloads_keep_exact_prepared_enqueue_trace():
 assert all(r['reload_trace_equal'] for r in read('browser/report.json'))

def test_actual_next_after_reload_is_enabled_for_prepared_enqueue():
 assert all(r['reload_next_enabled'] for r in read('browser/report.json'))

def test_actual_DOM_C17_mains_balance12_alloc_free_and_report12_NULL_failures():
 rs=read('caller-ownership/report.json');assert len(rs)==4 and sum(r['alloc_free_live'][0] for r in rs)==12 and all(r['strict_C17_original'] and r['alloc_free_live'][0]==r['alloc_free_live'][1] and r['alloc_free_live'][2]==0 for r in rs)
 fs=[f for r in rs for f in r['NULL_faults']];assert len(fs)==12 and all(f['exit']==1 and f['caller_failure_reported'] and not f['failed_operation_announced_applied'] and f['alloc_free_live']==[f['point']-1,f['point']-1,0] for f in fs)

def test_actual_DOM_main_Doxygen_has_four_documented_symbols_and_no_warnings():
 d=read('caller-doxygen.json');assert d['inputs']==6 and d['documented_main_count']==4 and d['warning_lines']==0

def test_HTTP_C_H_are_actual_D_bytes_and_main_absence_is_recorded():
 d=read('downloads.json');assert d['source']['HTTP']==d['header']['HTTP']==200 and d['main_HTTP_status']==404

def test_eight_finite_resource_samples_are_measured_without_stress_claims():
 d=read('resources.json');assert len(d['calls'])==8 and all(x['python_peak_bytes']>=x['python_current_bytes']>=0 and x['response_bytes']>0 for x in d['calls'])
