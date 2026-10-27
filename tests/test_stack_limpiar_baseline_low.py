"""LOW unsuppressed limpiar regressions against safe independent original-C oracle."""
from pathlib import Path
import json,pytest
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-stack-limpiar-baseline-low'
UI_E=E.parent/'visible-stack-limpiar-instructions-medium'
from scripts.published_test_inputs import audit_input_path
def ui_report():
 path=(UI_E if (audit_input_path(UI_E/'browser/report.json')).exists() else E)/'browser/report.json'
 return json.loads(audit_input_path(path).read_text(encoding='utf-8'))
CASES={'empty':[],'single':[-1],'multi':[7,-2,7],'reinsert':[7,-2,7]}
def execute(client,op,**payload):
 r=client.post('/sequential/stack/operate',json={'operation':op,'payload':payload});assert r.status_code==200;d=r.get_json();assert d['success'];return d

def prepare(client,case='multi'):
 for value in CASES[case]:execute(client,'apilar',value=value)
def trace(client):prepare(client);return execute(client,'limpiar')['execution_trace']
def values(f):return [x['value'] for x in f['state_after']['items']]
@pytest.mark.parametrize('case',list(CASES))
def test_final_empty_repeat_and_reinsert_match_original_C(client,case):
 prepare(client,case)
 for repeat in [1,2]:
  if case=='reinsert' and repeat==2:execute(client,'apilar',value=8)
  d=execute(client,'limpiar');n=next(r for r in json.loads((audit_input_path(E/'report.json')).read_text(encoding='utf-8')) if r['case']==case and r['repeat']==repeat)['native_events'][-1];assert d['visual_state']['items']==n['root_values']==[] and d['visual_state']['size']==0

def test_independent_C_free_order_live_detached_node_and_NULL_guard():
 ns=json.loads((audit_input_path(E/'native-report.json')).read_text(encoding='utf-8'));assert len(ns)==76
 for sid in range(8):
  frames=[n for n in ns if n['sample']==sid];assert frames[-1]['root_values']==[]
  assigned=[n for n in frames if n['event']=='root_assigned'];freed=[n for n in frames if n['event']=='node_free'];assert len(assigned)==len(freed)
  for a,f in zip(assigned,freed):
   assert a['root_ids']==f['root_ids'] and a['aux_valid'] and not f['aux_valid'];assert a['aux_id'] not in a['root_ids'] and a['aux_id'] in [h['id'] for h in a['live']];assert len(a['live'])==len(f['live'])+1
 guard=[n for n in ns if n['sample']==8];assert [n['event'] for n in guard]==['entry','aux_declared','root_guard','return'] and guard[-2]['condition']==1 and guard[-1]['frees']==0
 assert (audit_input_path(E/'native/stderr.log')).read_text(encoding='utf-8').strip()=='OWNERSHIP 8 8 0'

def test_root_changes_at_assignment_before_free_not_after(client):
 frames=trace(client)['steps'];native=[n for n in json.loads((audit_input_path(E/'native-report.json')).read_text(encoding='utf-8')) if n['sample']==4 and n['event']=='root_assigned'];fs=[f for f in frames if f['line_text'].strip()=='*p = aux->sgte;'];assert len(fs)==len(native)==3
 for n,f in zip(native,fs):assert values(f)==n['root_values']

def test_unlinked_aux_still_alive_before_free(client):
 f=next(f for f in trace(client)['steps'] if f['line_text'].strip()=='*p = aux->sgte;');assert len(values(f))==2;assert len(f['pedagogy']['heap_transition']['after'])==3

def test_root_parameter_pointer_to_pointer_type_and_alias(client):
 frames=trace(client)['steps'];ps=[p for f in frames for p in f['pedagogy']['pointers'] if p['name']=='p'];assert ps and all(p['type'] in {'ptrPila *','struct NodoPila **'} for p in ps);assert any(p.get('alias') for p in ps)

def test_aux_declared_indeterminate_until_assignment(client):
 f=next(f for f in trace(client)['steps'] if f['line_text'].strip()=='ptrPila aux;');aux=next(v for v in f['pedagogy']['variables'] if v['name']=='aux');assert aux['type']=='ptrPila' and aux['initialized'] is False and aux['value'] is None

def test_aux_assignment_targets_original_live_node_identity(client):
 f=next(f for f in trace(client)['steps'] if f['line_text'].strip()=='aux = *p;');aux=next(p for p in f['pedagogy']['pointers'] if p['name']=='aux');assert aux['target'] is not None;assert aux['target'] in {h['id'] for h in f['pedagogy']['heap_transition']['after']}

def test_free_retires_original_heap_object_and_invalidates_aux_storage(client):
 fs=[f for f in trace(client)['steps'] if f['line_text'].strip()=='free(aux);']
 for f in fs:
  aux=next(p for p in f['pedagogy']['pointers'] if p['name']=='aux');assert aux.get('valid') is False
  retired=f['pedagogy']['heap_transition']['freed'];assert retired and all(h.get('fields_valid') is False and h.get('initialized_mask')==0 for h in retired)

def test_function_scope_ends_at_final_void_return(client):
 f=trace(client)['steps'][-1];assert f['phase']=='end';assert f['pedagogy']['call_stack']==[];assert all(p['name'] not in {'p','aux'} for p in f['pedagogy']['pointers'])

def test_repeated_mutation_history_survives_page_get(client):
 prepare(client,'single');first=execute(client,'limpiar');second=execute(client,'limpiar');assert [h['operation'] for h in second['history']].count('limpiar')==2;assert client.get('/sequential/stack').status_code==200;third=execute(client,'limpiar');assert [h['operation'] for h in third['history']].count('limpiar')==3

def test_empty_clean_has_no_free_or_printf_and_void_API_result(client):
 d=execute(client,'limpiar');assert d['result'] is None
 assert not any('free(aux);'==f['line_text'].strip() for f in d['execution_trace']['steps']);assert all(f['console']==[] for f in d['execution_trace']['steps'])

def test_UI_reload_keeps_prepared_limpiar_trace_without_redispatch():
 rows=ui_report();assert len(rows)==4 and all(r['reload_trace_equal'] and r['extra_POSTs']==0 and not r['JS_errors'] for r in rows)

def test_UI_five_numbered_sections_and_both_view_replay():
 rows=ui_report();assert len(rows)==4
 for r in rows:
  assert len(r['five_numbered_sections'])==5 and r['forward_same_trace_two_views']==2*sum(len(o['trace']['steps']) for o in r['observations']);assert r['back_same_trace_two_views']==r['forward_same_trace_two_views']-4
