"""Private helper fidelity against native statement events, plus absent public exposure."""
from pathlib import Path
import importlib.util,json
import pytest
from unittest.mock import patch
from app import create_app
from app.config import Config
from app.adapters.priority_queue_adapter import PriorityQueueAdapter
from app.services.c_code_service import CCodeService
from app.services.execution_trace_service import ExecutionTraceService
from app.domain.sequential.priority_queue_helpers_instruction import build_priority_helper_trace
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-priority-queue-five-helpers-instructions-medium';L=E.parent/'visible-priority-queue-five-helpers-baseline-low'
from scripts.published_test_inputs import audit_input_path
spec=importlib.util.spec_from_file_location('priority_helpers_oracle_compare',audit_input_path(E/'compare_private.py'));observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
observer.E=audit_input_path(E)
ROWS=json.loads((audit_input_path(L/'report.json')).read_text());NATIVE={r['ID']:r for r in json.loads((audit_input_path(E/'native-event-inventory.json')).read_text())};METHODS=['inicializar','vacia','contar','copiar_items','formatear']
for entry in NATIVE.values():
 entry['events_path']=str(audit_input_path(ROOT/entry['events_path']))
@pytest.mark.parametrize('row',ROWS,ids=['PQ5I-'+r['ID'].removeprefix('PQ5-') for r in ROWS])
def test_typed_statement_memory_scope_buffer_matches_native(row):
 trace=observer.make_trace(row);observer.compare(row,trace,NATIVE[row['ID']])
 assert trace['steps'][-1]['pedagogy']['helper_memory']['scope']=='ended'
 assert trace['steps'][-1]['pedagogy']['call_stack']==[]
 assert not any(v['scope'] in [row['method'],'cp_append_text'] for v in trace['steps'][-1]['pedagogy']['variables'])
 assert trace['steps'][-1]['pedagogy']['helper_memory']['return_type']==('bool' if row['method']=='cp_vacia' else 'int' if row['method'] in ['cp_contar','cp_copiar_items'] else 'void')
 if row['method']=='cp_formatear':assert all(s['console']==[] for s in trace['steps'])
@pytest.mark.parametrize('operation',METHODS,ids=['PQ5D-'+m for m in METHODS])
def test_private_dispatch_extracts_exact_target_without_registering(operation):
 state={'kind':'priority','items':[],'size':0,'empty':True,'out_index':-1}
 for name in [operation,'cp_'+operation]:
  tr=ExecutionTraceService.build_trace(structure_id='priority_queue',operation_name=name,payload={},didactic_data=CCodeService._build_priority_queue_data(),before_state=state,after_state=state,success=True,message='private',mutates=operation=='inicializar')
  assert tr['steps'][0]['function_name']=='cp_'+operation and tr['execution_started']
 assert not any(o['name'] in [operation,'cp_'+operation] for o in PriorityQueueAdapter().get_supported_operations())
@pytest.mark.parametrize('operation',METHODS+['cp_'+m for m in METHODS],ids=['PQ5A-'+m for m in METHODS+['cp_'+m for m in METHODS]])
@pytest.mark.parametrize('populated',[False,True],ids=['empty','populated'])
def test_absent_API_helpers_reject_before_target_dispatch_preserve_history_reload(operation,populated,tmp_path):
 class PrivateConfig(Config):
  TESTING=True
  SESSION_CACHE_DIR=str(tmp_path/'sessions')
 app=create_app(PrivateConfig);client=app.test_client()
 if populated:
  for v,p in [(17,9),(9,1),(3,1)]:assert client.post('/sequential/priority_queue/operate',json={'operation':'encolar','payload':{'value':v,'priority':p}}).get_json()['success']
 original=PriorityQueueAdapter.execute;target=[]
 def observe(self,op,payload):
  if op in METHODS+['cp_'+m for m in METHODS]:target.append(op)
  return original(self,op,payload)
 baseline=None
 with patch.object(PriorityQueueAdapter,'execute',observe),patch('app.domain.sequential.priority_queue_helpers_instruction.build_priority_helper_trace',side_effect=AssertionError('Rejected helper must not invoke C engine')):
  for _ in range(2):
   response=client.post('/sequential/priority_queue/operate',json={'operation':operation,'payload':{}});data=response.get_json();assert response.status_code==400 and not data['success'];trace=data['execution_trace'];assert trace['steps']==[] and trace['execution_started'] is False and trace['validation']['stage']=='supported_operations'
   snapshot=(data['visual_state'],data['history'])
   if baseline is None:baseline=snapshot
   else:assert snapshot==baseline
   assert len(data['history'])==(3 if populated else 0) and not any(h['operation']==operation for h in data['history'])
  assert client.get('/sequential/priority_queue').status_code==200 and not target
@pytest.mark.parametrize('problem',['cycle','dead','uninitialized-root','small-buffer','negative-size_t'],ids=['PQ5G-'+x for x in ['cycle','dead','uninitialized-root','small-buffer','negative-size_t']])
def test_private_fixture_guard_rejects_unsafe_memory_before_read(problem):
 payload={'capacity':2};memory={'nodes':[{'id':'N1','type':'CPNodo','alive':True,'initialized_mask':7,'fields':{'valor':17,'prioridad':1,'sgte':None}}],'fields':{'delante':'N1','atras':'N1','cantidad':1},'initialized_mask':7};operation='copiar_items'
 if problem=='cycle':memory['nodes'][0]['fields']['sgte']='N1'
 elif problem=='dead':memory['nodes'][0]['alive']=False
 elif problem=='uninitialized-root':memory['initialized_mask']=0
 elif problem=='small-buffer':payload['caller_values']=[1]
 else:operation='formatear';payload['capacity']=-1
 with pytest.raises(ValueError):build_priority_helper_trace(operation_name=operation,payload=payload,source_code=CCodeService._build_priority_queue_data()['operations'][operation],code_title='Codigo C',before_state={'kind':'priority','items':[],'size':0},after_state={},success=True,message='private',borrowed_memory=memory)
