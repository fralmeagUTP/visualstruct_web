"""Fresh Cola cleanup C snapshots, reload dispatch and safe object lifetimes."""
from pathlib import Path
import json
from app.services.execution_trace_service import ExecutionTraceService
from tests._audit_queue_limpiar_compare_medium import collect
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-queue-limpiar-instructions-medium'
def op(c,name,**payload):
 r=c.post('/sequential/queue/operate',json={'operation':name,'payload':payload});assert r.status_code==200;return r.get_json()
def saved(c):
 with c.session_transaction() as s:return s.get('queue_cleanup_prepared_v1')
def test_fresh_nine_calls_match_original_92_C_events_and_25_conditions():
 rows,checks=collect();assert len(rows)==len(checks)==9 and sum(c['frames'] for c in checks)==92 and sum(c['conditions'] for c in checks)==25
 assert all(c['all_snapshots_match'] for c in checks)
def test_GET_restores_without_trace_dispatch_rejection_preserves_mutation_reset_invalidate(client,monkeypatch):
 op(client,'encolar',value=7);d=op(client,'limpiar');record=saved(client);assert record['trace']==d['execution_trace'];original=ExecutionTraceService.build_trace
 def forbidden(**kwargs):raise AssertionError('GET must restore trace without build_trace dispatch')
 monkeypatch.setattr(ExecutionTraceService,'build_trace',forbidden);assert client.get('/sequential/queue').status_code==200 and saved(client)==record
 monkeypatch.setattr(ExecutionTraceService,'build_trace',original);assert client.post('/sequential/queue/operate',json={'operation':'unsupported','payload':{}}).status_code==400 and saved(client)==record
 op(client,'encolar',value=8);assert saved(client) is None;op(client,'limpiar');assert saved(client)
 assert client.post('/sequential/queue/reset').status_code==200 and saved(client) is None
def test_rear_invalid_only_after_last_free_until_store_and_fields_history_never_used(client):
 for v in [7,-2,7]:op(client,'encolar',value=v)
 fs=op(client,'limpiar')['execution_trace']['steps'];ids=[n['id'] for n in fs[0]['debug']['heap']]
 invalid=[]
 for f in fs:
  d=f['debug'];assert [n['id'] for n in d['heap']]==ids and d['root']['alive'] and d['root']['valid']
  assert d['root']['initialized_mask']==(3 if d['root']['rear_valid'] else 1)
  if not d['root']['rear_valid']:invalid.append(d['token']);assert d['root']['rear'] is None and d['root']['rear_historical_identity']==ids[-1]
  for n in d['heap']:
   if not n['alive']:assert not n['fields_valid'] and n['initialized_mask']==0 and n['fields']=={'nro':None,'sgte':None} and n['historical_fields']
  if d['token']=='root_assigned':assert d['aux']['valid'] and any(n['alive'] and n['status']=='detached' and n['id']==d['aux']['value'] for n in d['heap'])
 assert invalid==['node_free','while_guard','front_NULL_store'];assert fs[-1]['debug']['scopes']==[] and fs[-1]['pedagogy']['call_stack']==[]
from scripts.published_test_inputs import audit_input_path
def test_actual_DOM_caller_reports_NULL_failure_before_applied_and_documentation_present():
 rows=json.loads((audit_input_path(E/'caller-ownership/report.json')).read_text());assert len(rows)==4 and sum(len(r['NULL_faults']) for r in rows)==8
 for r in rows:
  assert r['DOM_body_unchanged'] and r['strict_C17_original'] and r['alloc_free_live'][0]==r['alloc_free_live'][1] and r['alloc_free_live'][2]==0
  assert all(f['exit']==1 and f['alloc_free_live'][0]==f['alloc_free_live'][1] and f['alloc_free_live'][2]==0 and not f['failed_operation_announced_applied'] for f in r['NULL_faults'])
 d=json.loads((audit_input_path(E/'caller-doxygen.json')).read_text());assert d['warning_lines']==0 and d['documented_main_count']==4
