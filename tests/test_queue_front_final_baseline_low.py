"""Two independent finite query regressions; red IDs preserved without xfail."""
from pathlib import Path
import json,hashlib
import pytest
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-queue-front-final-baseline-low'
M=E.parent/'visible-queue-front-final-instructions-medium'
METHODS=['frente','final'];CASES=['empty','single','fifo','duplicate','minus1','minus1-front','minus1-rear','bounds','bounds-reverse'];ALL=CASES+['front-only','rear-only']
def read(file):return json.loads(((M if file in ['browser/report.json','caller-report.json','resources.json'] else E)/file).read_text(encoding='utf-8'))
def row(method,name):return next(x for x in read('report.json') if x['method']==method and x['case']==name)
def rawrow(method,name):return next(x for x in read('raw-private-report.json') if x['method']==method and x['case']==name)
def adapter(method,name):
 from app.adapters.queue_adapter import QueueAdapter
 a=QueueAdapter()
 for v in row(method,name)['values_FIFO']:a.execute('encolar',{'value':v})
 return a
def private(method,name):
 from app.services.structure_service import StructureService
 from app.services.execution_trace_service import ExecutionTraceService
 v=row(method,name)['visual']
 return ExecutionTraceService.build_trace(structure_id='queue',operation_name=method,payload={},didactic_data=StructureService._didactic_content('queue'),before_state=v,after_state=v,success=name!='empty',message='private baseline',mutates=False,console_events=[])
@pytest.mark.parametrize('method',METHODS)
@pytest.mark.parametrize('name',ALL)
def test_raw_function_matches_own_C_scalar_guard_and_repeat_readonly(method,name):
 from app.domain.sequential import tad_cola as t
 d=rawrow(method,name);nodes=[t.NodoCola(n['nro']) for n in d['native'][0]['nodes']]
 for i,n in enumerate(nodes):n.sgte=nodes[i+1] if i+1<len(nodes) else None
 q=t.Cola(nodes[0] if nodes and name!='rear-only' else None,nodes[-1] if nodes and name!='front-only' else None)
 before=(id(q),id(q.delante),id(q.atras),[(id(n),n.nro,id(n.sgte)) for n in nodes]);f=getattr(t,'cola_'+method,None);assert callable(f),'Missing Python transcription cola_'+method
 for _ in range(2):assert f(q)==d['native_result'];assert before==(id(q),id(q.delante),id(q.atras),[(id(n),n.nro,id(n.sgte)) for n in nodes])
@pytest.mark.parametrize('method',METHODS)
@pytest.mark.parametrize('name',CASES)
def test_adapter_private_scalar_or_empty_exception_preserves_current_contract(method,name):
 a=adapter(method,name)
 if name=='empty':
  from app.domain.sequential import EstructuraVaciaError
  with pytest.raises(EstructuraVaciaError):a.execute(method,{})
 else:assert a.execute(method,{})['result']==row(method,name)['native_result']
@pytest.mark.parametrize('method',METHODS)
@pytest.mark.parametrize('name',CASES)
def test_repeated_private_queries_preserve_both_roots_nodes_links_values_count(method,name):
 a=adapter(method,name)
 def snapshot():
  q=a._structure._cola;nodes=[];n=q.delante
  while n:nodes.append((id(n),n.nro,id(n.sgte)));n=n.sgte
  return id(q),id(q.delante),id(q.atras),nodes,a._structure._tamano,a.to_visual_state()
 before=snapshot()
 for _ in range(2):
  try:a.execute(method,{})
  except Exception as error:
   from app.domain.sequential import EstructuraVaciaError
   assert name=='empty' and isinstance(error,EstructuraVaciaError)
  assert snapshot()==before
@pytest.mark.parametrize('method',METHODS)
@pytest.mark.parametrize('name',CASES)
def test_private_real_guard_outcome_and_operand_value_match_own_native(method,name):
 conditions=[x['pedagogy']['condition'] for x in private(method,name)['steps'] if x['pedagogy'].get('condition') is not None]
 assert len(conditions)==1,'Actual if/ternary condition required per method'
 c=conditions[0];assert c['result']==bool(row(method,name)['native'][1]['condition'])
 assert '&' not in c['substituted'],'Guard compares a stored node pointer value, never the address of the root field'
 assert ('q.delante' if method=='frente' else 'q.atras') in c['source']
@pytest.mark.parametrize('method',METHODS)
@pytest.mark.parametrize('name',CASES)
def test_private_q_is_struct_by_value_with_borrowed_field_aliases_not_pointer_param(method,name):
 m=private(method,name)['steps'][0]['pedagogy'];q=next((x for x in m['variables'] if x['name']=='q'),None)
 assert q is not None and q['type']=='struct Cola','q is struct copy by value, not struct Cola* or const'
 assert q['initialized'] and q['scope']=='cola_'+method and q['scope_state']=='active'
 heap=m['heap_objects'];head=heap[0]['id'] if heap else None;tail=heap[-1]['id'] if heap else None;assert q['value']=={'delante':head,'atras':tail}
 assert not any(p['name']=='q' for p in m['pointers'])
 for field,target in [('delante',head),('atras',tail)]:
  p=next(p for p in m['pointers'] if p['name']=='q.'+field);assert p['type']=='struct NodoCola *' and p['target']==target and p['initialized']
@pytest.mark.parametrize('method',METHODS)
@pytest.mark.parametrize('name',CASES)
def test_private_heap_exact_nro_sgte_fields_roots_mask_and_readonly_each_frame(method,name):
 values=row(method,name)['values_FIFO'];steps=private(method,name)['steps']
 for step in steps:
  m=step['pedagogy'];heap=m['heap_objects'];assert len(heap)==len(values);assert step['state_after']==row(method,name)['visual'] and step['console']==[];assert m['heap_transition']['before']==m['heap_transition']['after']
  if not heap:
   assert any(x['name']=='cola' and x['type']=='struct Cola' and x['initialized'] and x['scope']=='caller' for x in m['variables']);continue
  for i,n in enumerate(heap):assert n['type']=='struct NodoCola' and n['alive'] and n['initialized_mask']==3 and n['fields']=={'nro':values[i],'sgte':heap[i+1]['id'] if i+1<len(heap) else None}
@pytest.mark.parametrize('method',METHODS)
@pytest.mark.parametrize('name',CASES)
def test_private_int_return_ends_q_scope_leaves_nodes_and_caller_pending(method,name):
 m=private(method,name)['steps'][-1]['pedagogy'];r=next((x for x in m['variables'] if x['name']=='return'),None);assert r is not None and r['type']=='int' and r['value']==row(method,name)['native_result'] and r['initialized']
 assert m['call_stack']==[] and any(x.get('state')=='ended' for x in m['scopes']);assert not any(x['scope']=='cola_'+method for x in m['variables'])
 c=next(x for x in m['variables'] if x['name']=='caller_result');assert c['type']=='int' and c['initialized'] is False and c['written'] is False
@pytest.mark.parametrize('method',METHODS)
@pytest.mark.parametrize('name',CASES)
def test_live_rejected_unregistered_method_POST_GET_zero_query_no_fake_C_steps(method,name):
 from app import create_app
 from app.config import Config
 from app.adapters.queue_adapter import QueueAdapter
 from unittest.mock import patch
 class Q(Config):
  TESTING=True
  SESSION_CACHE_DIR=str(M/'private-regression-sessions')
 c=create_app(Q).test_client();d=row(method,name)
 for v in d['values_FIFO']:assert c.post('/sequential/queue/operate',json={'operation':'encolar','payload':{'value':v}}).get_json()['success']
 queries=[];original=QueueAdapter.execute
 def observe(self,op,payload):
  if op in METHODS:queries.append(op)
  return original(self,op,payload)
 results=[]
 with patch.object(QueueAdapter,'execute',observe):
  for _ in range(2):
   r=c.post('/sequential/queue/operate',json={'operation':method,'payload':{}});data=r.get_json();assert r.status_code==400 and not data['success'] and data['visual_state']==d['visual'];assert not any(x['operation'] in METHODS for x in data['history']);results.append(data)
  assert c.get('/sequential/queue').status_code==200 and c.get('/sequential/queue').status_code==200 and queries==[]
 for data in results:
  assert data['execution_trace']['execution_started'] is False and data['execution_trace']['steps']==[]
  assert not any(x['pedagogy'].get('concept') in ('call','return') for x in data['execution_trace']['steps']),'Rejected method did not execute C: validation cannot fabricate call/return'
@pytest.mark.parametrize('method',METHODS)
@pytest.mark.parametrize('name',['empty','fifo','bounds','minus1-front'])
def test_existing_browser_rejection_readonly_reload_no_new_selector_or_records(method,name):
 d=next(x for x in read('browser/report.json') if x['case']==name);assert d['not_registered'] and d['no_new_selectors'] and d['history_readonly'] and d['visual_state_readonly'] and d['both_views_unchanged'] and d['five_sections'] and d['extra_UI_POSTs']==0 and not d['JS_errors'];assert len(d['rejected_by_method'][method])==2 and all(x['HTTP']==400 for x in d['rejected_by_method'][method]);assert d['standalone_query_records']==0 and d['standalone_calls_by_method'][method]==0
@pytest.mark.parametrize('name',['fifo','bounds','minus1-front'])
def test_shared_actual_DOM_setup_only_C17_caller_ownership_NULL_Doxygen_once(name):
 d=read('caller-report.json');c=next(x for x in d['cases'] if x['case']==name);assert hashlib.sha256((M/'actual-callers'/name/'main.c').read_bytes()).hexdigest()==c['SHA'];assert c['runs']['C17']['exit']==c['runs']['ownership']['exit']==0 and c['alloc']==c['free'] and c['live']==0;assert len(c['controlled_NULL'])==c['alloc'] and all(x['exit']==1 for x in c['controlled_NULL']);assert d['Doxygen_warnings']==0 and d['documented_mains']==3 and d['Doxygen_inputs']==5 and d['empty_caller_absent'] and d['main_HTTP']==404;assert all(n==0 for n in c['standalone_query_calls'].values())
def test_shared_native_defined_by_value_fixtures_and_resources_have_separate_method_scopes():
 native=[json.loads(x) for x in (E/'native/events.jsonl').read_text().splitlines()];assert len(native)==132
 for method in METHODS:
  rows=[x for x in native if x['method']==method];assert len(rows)==66 and sum(x['phase']=='condition' for x in rows)==22
  for fixture in range(11):
   ns=[x for x in rows if x['fixture']==fixture];assert len(ns)==6 and ns[2]['result']==ns[5]['result'];assert all((x['front_id'],x['rear_id'],x['nodes'])==(ns[0]['front_id'],ns[0]['rear_id'],ns[0]['nodes']) for x in ns)
 r=read('resources.json');assert len(r['samples'])==54 and all(set(x)=={'private_trace_build_Cextract_JSON_noHTTPsession','two_rejected_HTTP_POSTs_session_replay_serialization'} for x in r['by_method_scope'].values());assert all(v['max_python_peak_bytes']>0 for x in r['by_method_scope'].values() for v in x.values())

@pytest.mark.parametrize('method',METHODS)
@pytest.mark.parametrize('name',['front-only','rear-only'])
def test_private_partial_roots_typed_copy_alias_guard_return_scope_readonly(method,name):
 from app.domain.sequential.queue_query_instruction import build_queue_query_trace
 d=rawrow(method,name);n=d['native'][0];heap=[{'id':'N1','address':'N1','type':'struct NodoCola','alive':True,'allocated':True,'freed':False,'initialized_mask':3,'fields':{'nro':19,'sgte':None}}]
 fields={'delante':None if n['front_id']==-1 else 'N1','atras':None if n['rear_id']==-1 else 'N1'}
 state={'items':[{'value':19}] if fields['delante'] else [],'size':int(bool(fields['delante'])),'empty':not bool(fields['delante'])}
 source=(E/'native/tad_cola.c').read_text(encoding='utf-8-sig')
 for repeat in range(2):
  tr=build_queue_query_trace(operation_name=method,payload={},source_code=source,code_title='C',before_state=state,after_state=state,success=True,message='Private roots',borrowed_memory={'nodes':heap,'fields':fields})
  assert len(tr['steps'])==3
  for step in tr['steps']:
   m=step['pedagogy'];q=m['query_memory'];assert q['heap']==heap and q['fields']==fields and step['state_after']==state and step['console']==[];assert not q['caller_storage']['written'] and not q['caller_storage']['initialized'];assert q['allocations']==q['frees']==0
   if step['event_type']!='return':
    assert q['parameter_struct']['type']=='struct Cola' and q['parameter_struct']['value']==fields and q['parameter_struct']['address']!=q['caller_struct']['address']
    for field in fields:assert next(p for p in m['pointers'] if p['name']=='q.'+field)['target']==fields[field]
   else:assert q['parameter_struct'] is None and m['call_stack']==[] and q['function_scope']=='ended' and q['return_value']==d['native'][repeat*3+2]['result']
  cond=tr['steps'][1]['pedagogy']['condition'];assert cond['result']==bool(d['native'][repeat*3+1]['condition']) and '&' not in cond['substituted']
