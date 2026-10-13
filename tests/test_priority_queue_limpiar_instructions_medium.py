"""Live regressions for complete causal comparison and prepared-trace invalidation."""
from pathlib import Path
import json
import pytest
from app import create_app
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-priority-queue-limpiar-instructions-medium'
def test_all_153_native_events_and_41_conditions_match_with_no_retired_field_reads():
 d=json.loads((E/'native-comparison.json').read_text(encoding='utf-8-sig'));assert (d['calls'],d['events'],d['conditions'],d['observations_32_preserved'],d['divergences'])==(9,153,41,32,0)
 assert all(o['match'] for o in d['matches'])
def test_counter_changes_after_free_rear_NULL_before_last_free_and_next_remains_usable():
 rows=json.loads((E/'report.json').read_text(encoding='utf-8-sig'));steps=next(r for r in rows if r['case']=='multi' and r['repeat']==1)['data']['execution_trace']['steps']
 for i,f in enumerate(steps):
  if f['debug']['token']=='node_free':
   g=f['debug'];assert g['root']['cantidad']==steps[i-1]['debug']['root']['cantidad'] and g['next']['valid'] and not g['aux']['valid']
   assert steps[i+2]['debug']['token']=='quantity_decrement' and steps[i+2]['debug']['root']['cantidad']==g['root']['cantidad']-1
   if g['frees']==3:assert g['root']['rear'] is None and steps[i-1]['debug']['token']=='rear_last_NULL_store'
  if f['debug']['token']=='aux_advance':assert f['debug']['aux']['valid'] and f['debug']['aux']['value']==f['debug']['next']['value']
def test_prepared_trace_reload_no_build_and_history_digest_invalidates_only_on_success(monkeypatch):
 app=create_app();app.config['TESTING']=True;c=app.test_client();url='/sequential/priority_queue'
 assert c.post(url+'/operate',json={'operation':'encolar','payload':{'value':7,'priority':1}}).get_json()['success']
 d=c.post(url+'/operate',json={'operation':'limpiar','payload':{}}).get_json()
 from app.services.priority_queue_cleanup_session_service import prepared_cleanup
 from app.services.execution_trace_service import ExecutionTraceService
 monkeypatch.setattr(ExecutionTraceService,'build_trace',lambda **kw:pytest.fail('GET rebuilt trace'))
 with c.session_transaction() as s:assert s['priority_queue_cleanup_prepared_v1']['trace']==d['execution_trace']
 assert c.get(url).status_code==200
 monkeypatch.undo()
 assert c.post(url+'/operate',json={'operation':'encolar','payload':{'value':'bad','priority':1}}).status_code==400
 with c.session_transaction() as s:assert 'priority_queue_cleanup_prepared_v1' in s
 assert c.post(url+'/operate',json={'operation':'encolar','payload':{'value':8,'priority':2}}).get_json()['success']
 with c.session_transaction() as s:assert 'priority_queue_cleanup_prepared_v1' not in s
 c.post(url+'/operate',json={'operation':'limpiar','payload':{}});c.post(url+'/reset')
 with c.session_transaction() as s:assert 'priority_queue_cleanup_prepared_v1' not in s
def test_entry_before_local_declarations_return_keeps_only_caller_fields():
 from app.domain.sequential.priority_queue_cleanup_instruction import build_priority_queue_cleanup_trace
 rows=json.loads((E/'report.json').read_text(encoding='utf-8-sig'));t=rows[0]['data']['execution_trace'];first=t['steps'][0]['debug'];assert first['aux'] is None and first['next'] is None and not any(v['name'] in {'aux','next'} for v in first['variables'])
 last=t['steps'][-1]['debug'];assert last['root']['alive'] and last['root']['initialized_mask']==7 and {v['name'] for v in last['variables']}=={'delante','atras','cantidad'} and not last['call_stack']
 empty=t['final_state'];n=build_priority_queue_cleanup_trace(payload={},source_code=t['source_code'],code_title='C',before_state=empty,after_state=empty,success=True,message='',null_root=True)
 assert [f['debug']['token'] for f in n['steps']]==['entry','aux_declared','next_declared','root_guard','return'] and all(not f['debug']['heap'] for f in n['steps'])
