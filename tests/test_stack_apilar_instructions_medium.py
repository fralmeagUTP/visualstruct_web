"""Current push behavior beyond saved value snapshots: typed init/order/reload state."""
from pathlib import Path
import json
import pytest
from app import create_app
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-stack-apilar-instructions-medium'
def read(name):return json.loads((E/name).read_text(encoding='utf-8-sig'))
def test_all124_native_events27conditions_and6_direct_guard_traces_match():
 d=read('native-comparison.json');assert (d['calls'],d['events'],d['conditions'],d['original_observations'],d['divergences'])==(14,124,27,32,0) and all(o['match'] for o in d['matches'])
 fs=read('direct-fault-traces.json');assert len(fs)==6 and {f['sample'] for f in fs}=={2,5,8,11,12,13}
 for row in fs:
  t=row['trace'];assert t['steps'][-1]['event_type']=='return' and not t['steps'][-1]['pedagogy']['call_stack']
  assert not any(s['debug']['token']=='root_assigned' for s in t['steps'])
  assert t['steps'][-1]['console'] and t['steps'][-1]['state_after']==t['steps'][0]['state_snapshot']
def test_malloc_opaque_call_has_uninitialized_aux_and_zero_mask_until_individual_stores():
 t=read('report.json')[0]['data']['execution_trace'];by={f['debug']['token']:f for f in t['steps']};enter=by['allocator_enter']['debug'];assert not enter['aux']['initialized'] and enter['call_stack'][-1]['function']=='malloc' and enter['call_stack'][-1]['opaque']
 returned=by['allocator_success_return']['debug'];assert not returned['aux']['initialized'] and len(returned['heap'])==1 and returned['heap'][0]['initialized_mask']==0
 linked=by['link_assigned']['debug'];pub=by['root_assigned']['debug'];assert pub['aux']['valid'] and pub['root']['value']==pub['aux']['value']==linked['aux']['value']
 assert by['return']['debug']['root']['alive'] and {v['name'] for v in by['return']['debug']['variables']}=={'pila'}
def test_prepared_push_GET_no_build_failure_preserve_and_cleanup_namespaces_do_not_conflict(monkeypatch):
 app=create_app();app.config['TESTING']=True;c=app.test_client();url='/sequential/stack'
 d=c.post(url+'/operate',json={'operation':'apilar','payload':{'value':7}}).get_json()
 from app.services.execution_trace_service import ExecutionTraceService
 monkeypatch.setattr(ExecutionTraceService,'build_trace',lambda **kw:pytest.fail('GET rebuilt push trace'))
 assert c.get(url).status_code==200
 with c.session_transaction() as s:assert s['stack_push_prepared_v1']['trace']==d['execution_trace'] and 'stack_cleanup_prepared_v1' not in s
 monkeypatch.undo()
 assert c.post(url+'/operate',json={'operation':'apilar','payload':{'value':'bad'}}).status_code==400
 with c.session_transaction() as s:assert s['stack_push_prepared_v1']['trace']==d['execution_trace']
 c.post(url+'/operate',json={'operation':'limpiar','payload':{}})
 with c.session_transaction() as s:assert 'stack_push_prepared_v1' not in s and s['stack_cleanup_prepared_v1']['trace']['operation_name']=='limpiar'
 c.post(url+'/operate',json={'operation':'apilar','payload':{'value':8}})
 with c.session_transaction() as s:assert 'stack_cleanup_prepared_v1' not in s and s['stack_push_prepared_v1']['trace']['operation_name']=='apilar'
 c.post(url+'/reset')
 with c.session_transaction() as s:assert 'stack_cleanup_prepared_v1' not in s and 'stack_push_prepared_v1' not in s
def test_DOM_equals_canonical_HTTP_and_real_next_button_works_after_reload_without_POST():
 rs=read('browser/report.json');assert len(rs)==4 and all(r['reload_real_next_button_replay'] and r['extra_POSTs']==0 for r in rs)
 for r in rs:
  p=E/'actual-callers'/r['case'];assert (p/'DOM-body.txt').read_text(encoding='utf-8-sig')==(p/'HTTP-main.c').read_text(encoding='utf-8-sig')==(p/'main.c').read_text(encoding='utf-8-sig')
