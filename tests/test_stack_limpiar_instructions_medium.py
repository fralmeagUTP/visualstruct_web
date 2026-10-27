"""Current C callback conformance, prepared cleanup persistence and real callers."""
from pathlib import Path
import hashlib,json,re
from app.services.execution_trace_service import ExecutionTraceService
from tests._audit_stack_limpiar_compare_medium import collect
from tests import _audit_stack_limpiar_compare_medium as original_comparator
from scripts.published_test_inputs import audit_input_path
original_comparator.L=audit_input_path(original_comparator.L)
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-stack-limpiar-instructions-medium'

def execute(client,operation,**payload):
 r=client.post('/sequential/stack/operate',json={'operation':operation,'payload':payload});assert r.status_code==200;return r.get_json()
def prepared(client):
 with client.session_transaction() as record:return record.get('stack_cleanup_prepared_v1')

def test_all_nine_finite_calls_match_original_C_events_roots_and_heap_lifetimes(tmp_path,monkeypatch):
 # Fresh caller output belongs to this execution, not to the preserved oracle.
 monkeypatch.setattr(original_comparator,'E',tmp_path)
 rows,comparisons=collect();assert len(rows)==len(comparisons)==9 and sum(r['frames'] for r in comparisons)==76 and sum(r['conditions'] for r in comparisons)==25

def test_saved_cleanup_reloads_without_trace_dispatch_and_invalidates_only_on_mutation_or_reset(client,monkeypatch):
 execute(client,'apilar',value=7);d=execute(client,'limpiar');saved=prepared(client);assert saved['trace']==d['execution_trace']
 original=ExecutionTraceService.build_trace
 def forbidden(**kwargs):raise AssertionError('GET must not build/redispatch the prepared cleanup')
 monkeypatch.setattr(ExecutionTraceService,'build_trace',forbidden);r=client.get('/sequential/stack');assert r.status_code==200 and 'prepared_cleanup_trace' in r.text;assert prepared(client)==saved
 monkeypatch.setattr(ExecutionTraceService,'build_trace',original)
 rejected=client.post('/sequential/stack/operate',json={'operation':'unsupported','payload':{}});assert rejected.status_code==400 and prepared(client)==saved
 execute(client,'apilar',value=8);assert prepared(client) is None
 execute(client,'limpiar');assert prepared(client)
 assert client.post('/sequential/stack/reset').status_code==200 and prepared(client) is None

from scripts.published_test_inputs import audit_input_path
def test_actual_HTTP_main_matches_compiled_C_artifact_and_ownership_faults(client):
 for value in [7,-2,7]:execute(client,'apilar',value=value)
 execute(client,'limpiar');execute(client,'limpiar');r=client.get('/help/source/stack/main');assert r.status_code==200 and r.data==(audit_input_path(E/'callers/multi.c')).read_bytes() and r.headers['Cache-Control']=='private, no-store'
 page=client.get('/sequential/stack');assert 'stack-main-download' in page.text and '/help/source/stack/main' in page.text
 rows=json.loads((audit_input_path(E/'caller-ownership/report.json')).read_text(encoding='utf-8'));assert len(rows)==4 and sum(len(row['NULL_faults']) for row in rows)==8
 for row in rows:
  source=E/'callers'/(row['case']+'.c');assert hashlib.sha256(audit_input_path(source).read_bytes()).hexdigest()==row['sha256'];assert row['actual_product_main'] and row['strict_C17_original'] and row['alloc_free_live'][0]==row['alloc_free_live'][1] and row['alloc_free_live'][2]==0
  assert all(f['exit']==1 and f['alloc_free_live'][0]==f['alloc_free_live'][1] and f['alloc_free_live'][2]==0 for f in row['NULL_faults'])
 assert json.loads((audit_input_path(E/'caller-doxygen.json')).read_text(encoding='utf-8'))['warnings']==0

def test_duplicate_nodes_keep_identity_and_root_stays_live_at_final_void_return(client):
 for value in [7,-2,7]:execute(client,'apilar',value=value)
 frames=execute(client,'limpiar')['execution_trace']['steps'];original=frames[0]['debug']['heap'];assert len({n['id'] for n in original})==3
 for f in frames:
  d=f['debug'];assert d['root']['alive'] and d['root']['initialized'] and d['root']['valid'];assert [n['id'] for n in d['heap']]==[n['id'] for n in original]
  if d['token']=='root_assigned':assert d['aux']['valid'] and next(n for n in d['heap'] if n['id']==d['aux']['value'])['alive']
  if d['token']=='node_free':assert d['aux']['value'] is None and not d['aux']['valid'] and not d['aux']['initialized'] and d['aux']['historical_identity']
 final=frames[-1];assert final['debug']['root']['value'] is None and final['debug']['scopes']==[] and final['pedagogy']['pointers']==[] and final['pedagogy']['call_stack']==[]
