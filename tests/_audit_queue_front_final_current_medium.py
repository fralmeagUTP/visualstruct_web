"""Independent readonly query-only native/adapter/private trace/rejected API baselines."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib,tracemalloc,time
R=Path.cwd();sys.path.insert(0,str(R));sys.stdout.reconfigure(encoding='utf-8')
from app import create_app
from app.config import Config
from app.adapters.queue_adapter import QueueAdapter
from app.services.structure_service import StructureService
from app.services.execution_trace_service import ExecutionTraceService
from app.domain.sequential import tad_cola as raw
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-queue-front-final-instructions-medium';N=E/'native';N.mkdir(exist_ok=True)
CASES=[('empty',[]),('single',[17]),('fifo',[17,9,3]),('duplicate',[7,7]),('minus1',[-1]),('minus1-front',[-1,17]),('minus1-rear',[17,-1]),('bounds',[-2147483648,0,2147483647]),('bounds-reverse',[2147483647,0,-2147483648])];PRIVATE=[('front-only',[19]),('rear-only',[19])];METHODS=['frente','final']
class Q(Config):
 TESTING=True
 SESSION_CACHE_DIR=str(E/'private-API-sessions')
app=create_app(Q);downloads=[]
for kind,ext in [('source','c'),('header','h')]:
 r=app.test_client().get('/help/source/queue/'+kind);assert r.status_code==200 and r.data==(R/('docs/tads_C/tad_cola.'+ext)).read_bytes();(N/('tad_cola.'+ext)).write_bytes(r.data);downloads.append({'kind':kind,'HTTP':200,'SHA':hashlib.sha256(r.data).hexdigest()})
L=E.parent/'visible-queue-front-final-baseline-low'
assert all((N/('tad_cola.'+ext)).read_bytes()==(L/'native'/('tad_cola.'+ext)).read_bytes() for ext in ['c','h'])
shutil.copyfile(L/'native/events.jsonl',N/'events.jsonl')
native=[json.loads(x) for x in (N/'events.jsonl').read_text().splitlines()];assert len(native)==132
rows=[];private_rows=[];resources=[]
for fi,(name,values) in enumerate(CASES+PRIVATE):
 head=None;tail=None
 for v in reversed(values):head=raw.NodoCola(v,head);tail=head if tail is None else tail
 q=raw.Cola(None if name=='rear-only' else head,None if name=='front-only' else tail)
 for method in METHODS:
  ns=[x for x in native if x['fixture']==fi and x['method']==method];f=getattr(raw,'cola_'+method,None);raw_out=[]
  for _ in range(2):raw_out.append(f(q) if callable(f) else 'missing raw function')
  private_rows.append({'method':method,'case':name,'fixture':fi,'private_inconsistent_roots':name in ['front-only','rear-only'],'native':ns,'native_result':ns[2]['result'],'raw_outputs':raw_out})
  if name in ['front-only','rear-only']:continue
  a=QueueAdapter()
  for v in values:a.execute('encolar',{'value':v})
  state=a.to_visual_state();node=a._structure._cola.delante;before=[];root=(id(a._structure._cola),id(a._structure._cola.delante),id(a._structure._cola.atras),a._structure._tamano)
  while node:before.append((id(node),node.nro,id(node.sgte)));node=node.sgte
  outputs=[];traces=[]
  for repeat in range(2):
   try:outputs.append({'result':a.execute(method,{})['result']})
   except Exception as error:outputs.append({'exception':type(error).__name__})
   assert a.to_visual_state()==state
   tracemalloc.start();start=time.perf_counter();t=ExecutionTraceService.build_trace(structure_id='queue',operation_name=method,payload={},didactic_data=StructureService._didactic_content('queue'),before_state=state,after_state=state,success=bool(values),message='private adapter query',mutates=False,console_events=[]);JSONsize=len(json.dumps(t,ensure_ascii=False).encode('utf-8'));elapsed=time.perf_counter()-start;peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop();traces.append(t);resources.append({'method':method,'case':name,'repeat':repeat+1,'scope':'private_trace_build_Cextract_JSON_noHTTPsession','peak_bytes':peak,'JSON_bytes':JSONsize,'seconds':elapsed})
  after=[];node=a._structure._cola.delante
  while node:after.append((id(node),node.nro,id(node.sgte)));node=node.sgte
  assert after==before and root==(id(a._structure._cola),id(a._structure._cola.delante),id(a._structure._cola.atras),a._structure._tamano)
  client=app.test_client()
  for v in values:assert client.post('/sequential/queue/operate',json={'operation':'encolar','payload':{'value':v}}).get_json()['success']
  from unittest.mock import patch
  original=QueueAdapter.execute;queries=[]
  def observe(self,op,payload):
   if op in METHODS:queries.append(op)
   return original(self,op,payload)
  rejected=[]
  with patch.object(QueueAdapter,'execute',observe):
   tracemalloc.start();start=time.perf_counter()
   for repeat in range(2):
    r=client.post('/sequential/queue/operate',json={'operation':method,'payload':{}});data=r.get_json();assert r.status_code==400 and not data['success'] and data['visual_state']==state;assert data['execution_trace']['steps']==[] and data['execution_trace']['execution_started'] is False;assert not any(x['operation'] in METHODS for x in data['history']);rejected.append({'HTTP':400,'data':data})
   elapsed=time.perf_counter()-start;peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop();resources.append({'method':method,'case':name,'scope':'two_rejected_HTTP_POSTs_session_replay_serialization','peak_bytes':peak,'JSON_bytes':len(r.data),'seconds':elapsed})
   assert client.get('/sequential/queue').status_code==200 and client.get('/sequential/queue').status_code==200;assert queries==[]
  conditions=[s['pedagogy']['condition'] for s in traces[0]['steps'] if s['pedagogy'].get('condition') is not None]
  rows.append({'method':method,'case':name,'values_FIFO':values,'native':ns,'native_result':ns[2]['result'],'adapter_outputs':outputs,'root_nodes_links_count_readonly':True,'visual':state,'private_traces':traces,'condition_outcome_native_equal':len(conditions)==1 and conditions[0]['result']==bool(ns[1]['condition']),'condition_substitution':conditions[0].get('substituted') if conditions else None,'rejected':rejected,'public_query_dispatch_POST_GET':0,'query_journal':0,'not_registered':not any(x['name']==method for x in a.get_supported_operations())})
summary={}
for method in METHODS:
 summary[method]={}
 for scope in ['private_trace_build_Cextract_JSON_noHTTPsession','two_rejected_HTTP_POSTs_session_replay_serialization']:
  rr=[x for x in resources if x['method']==method and x['scope']==scope];summary[method][scope]={'samples':len(rr),'max_python_peak_bytes':max(x['peak_bytes'] for x in rr),'max_JSON_bytes':max(x['JSON_bytes'] for x in rr),'max_seconds':max(x['seconds'] for x in rr)}
for filename,data in [('report.json',rows),('raw-private-report.json',private_rows),('downloads.json',downloads),('resources.json',{'samples':resources,'by_method_scope':summary,'limits':'Two methods independently, private trace vs rejected API distinct; fixturesfinite including C17privateinconsistentroots outsidepublicAPI. No successqueryAPI/RSS/browser/unboundedhistory/SLA/OOM/sanitizer guarantee.'})]:
 (E/filename).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

from app.domain.sequential.queue_query_instruction import build_queue_query_trace
comparisons=[]
source=(N/'tad_cola.c').read_text(encoding='utf-8-sig')
for d in private_rows:
 ns=d['native'];first=ns[0]
 def symbol(i):return None if i==-1 else 'N'+str(i+1)
 heap=[{'id':symbol(n['id']),'address':symbol(n['id']),'type':'struct NodoCola','alive':True,'allocated':True,'freed':False,'status':'borrowed','initialized_mask':3,'fields_valid':True,'field_validity':{'nro':True,'sgte':True},'fields':{'nro':n['nro'],'sgte':symbol(n['next_id'])}} for n in first['nodes']]
 fields={'delante':symbol(first['front_id']),'atras':symbol(first['rear_id'])}
 normal=next((x for x in rows if x['method']==d['method'] and x['case']==d['case']),None)
 state=normal['visual'] if normal else {'items':[{'value':19}] if fields['delante'] else [],'size':1 if fields['delante'] else 0,'empty':not bool(fields['delante']),'kind':'linear','title':'Cola'}
 traces=[]
 for repeat in range(2):
  tr=build_queue_query_trace(operation_name=d['method'],payload={},source_code=source,code_title='C privado',before_state=state,after_state=state,success=True,message='Oráculo privado',borrowed_memory={'nodes':heap,'fields':fields})
  assert d['raw_outputs'][repeat]==d['native_result']
  for s,n in zip(tr['steps'],ns[repeat*3:repeat*3+3]):
   m=s['pedagogy'];qm=m['query_memory'];assert s['event_type']==n['phase'];assert qm['fields']==fields and qm['heap']==heap and m['heap_transition']['before']==m['heap_transition']['after'];assert s['state_after']==state and s['console']==[];assert not qm['caller_storage']['written'] and not qm['caller_storage']['initialized'];assert qm['allocations']==qm['frees']==0
   if n['phase']=='condition':assert m['condition']['result']==bool(n['condition']) and '&' not in m['condition']['substituted']
   if n['phase']=='return':assert qm['return_value']==n['result'] and qm['function_scope']=='ended' and m['call_stack']==[] and qm['parameter_struct'] is None
   else:assert qm['parameter_struct']['value']==fields and qm['parameter_struct']['type']=='struct Cola' and qm['parameter_struct']['address']!=qm['caller_struct']['address']
  traces.append(tr)
 comparisons.append({'method':d['method'],'case':d['case'],'native_result':d['native_result'],'fields':fields,'traces':traces,'events_compared':6,'conditions_compared':2,'private_inconsistent_roots':d['private_inconsistent_roots']})
assert sum(x['events_compared'] for x in comparisons)==132
(E/'current-native-comparison.json').write_text(json.dumps(comparisons,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Current: 44 private query comparisons,132 events,44 conditions; live API36 reject400 zero C steps; native reused exact C/H.')
