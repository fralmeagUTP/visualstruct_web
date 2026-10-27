"""Independent Mostrar oracles only; product remains unchanged."""
from pathlib import Path
import sys,json,hashlib,subprocess,shutil,io,contextlib,tracemalloc,time
R=Path.cwd();sys.path.insert(0,str(R));sys.stdout.reconfigure(encoding='utf-8');E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-queue-show-instructions-medium'
from app import create_app
from app.config import Config
from app.services.structure_service import StructureService
from app.services.execution_trace_service import ExecutionTraceService
from app.domain.sequential import tad_pila as S,tad_cola as Q
from app.adapters.stack_adapter import StackAdapter
from app.adapters.queue_adapter import QueueAdapter
CASES=[('empty',[]),('single',[17]),('multiple',[17,9,3]),('duplicate',[7,7]),('minus1',[-1]),('minus1-front',[-1,17]),('minus1-rear',[17,-1]),('bounds',[-2147483648,0,2147483647]),('bounds-reverse',[2147483647,0,-2147483648])]
class C(Config):
 TESTING=True
 SESSION_CACHE_DIR=str(E/'private-sessions')
app=create_app(C);downloads=[];reports=[];resources=[]
for sid,stem,typ in [('stack','pila','NodoPila'),('queue','cola','NodoCola')]:
 N=E/('native-'+sid);N.mkdir(exist_ok=True);fixtures=CASES+([('front-only',[19]),('rear-only',[19])] if sid=='queue' else [])
 for kind,ext in [('source','c'),('header','h')]:
  r=app.test_client().get('/help/source/'+sid+'/'+kind);assert r.status_code==200 and r.data==(R/'docs/tads_C'/('tad_'+stem+'.'+ext)).read_bytes();(N/('tad_'+stem+'.'+ext)).write_bytes(r.data);downloads.append({'structure':sid,'kind':kind,'HTTP':200,'SHA256':hashlib.sha256(r.data).hexdigest()})
 L=E.parent/'visible-stack-queue-show-baseline-low'/('native-'+sid)
 for ext in ['c','h']:assert (N/('tad_'+stem+'.'+ext)).read_bytes()==(L/('tad_'+stem+'.'+ext)).read_bytes()
 for name in ['events.jsonl','original-function.txt']:shutil.copyfile(L/name,N/name)
 events=[json.loads(x) for x in (N/'events.jsonl').read_text().splitlines()]
 for fi,(name,values) in enumerate(fixtures):
  ns=[x for x in events if x['fixture']==fi];native_outputs=[x['console'] for x in ns if x['phase'] in ['end','return']];assert len(native_outputs)==2 and native_outputs[0]==native_outputs[1];expected=('Pila vacia.\n' if not values else ''.join('\t'+str(v)+'\n' for v in values)) if sid=='stack' else 'Cola: '+''.join(str(v)+' ' for v in ([] if name=='rear-only' else values))+'\n';assert native_outputs==[expected]*2
  raw=S if sid=='stack' else Q;nodes=[getattr(raw,typ)(v) for v in values]
  for i,n in enumerate(nodes):n.sgte=nodes[i+1] if i+1<len(nodes) else None
  q=(nodes[0] if nodes else None) if sid=='stack' else Q.Cola(nodes[0] if nodes and name!='rear-only' else None,nodes[-1] if nodes and name!='front-only' else None)
  roots=(id(q),None,None) if sid=='stack' else (id(q),id(q.delante),id(q.atras));snap=[(id(n),n.nro,id(n.sgte)) for n in nodes];outs=[]
  for _ in range(2):
   buf=io.StringIO()
   with contextlib.redirect_stdout(buf):result=getattr(raw,stem+'_mostrar')(q)
   assert result is None;outs.append(buf.getvalue());assert [(id(n),n.nro,id(n.sgte)) for n in nodes]==snap;assert roots==((id(q),None,None) if sid=='stack' else (id(q),id(q.delante),id(q.atras)))
  record={'structure':sid,'method':stem+'_mostrar','case':name,'values_order':values,'native':ns,'native_outputs':native_outputs,'raw_outputs':outs,'raw_console_equal':outs==native_outputs,'raw_readonly':True,'raw_return':None,'private_inconsistent_roots':name in ['front-only','rear-only']}
  if not record['private_inconsistent_roots']:
   a=(StackAdapter if sid=='stack' else QueueAdapter)()
   for value in (list(reversed(values)) if sid=='stack' else values):a.execute('apilar' if sid=='stack' else 'encolar',{'value':value})
   state=a.to_visual_state();assert [x['value'] for x in state['items']]==values;record['visual']=state
   try:a.execute('mostrar',{});record['adapter_error']=None
   except Exception as error:record['adapter_error']=type(error).__name__
   tracemalloc.start();start=time.perf_counter();trace=ExecutionTraceService.build_trace(structure_id=sid,operation_name='mostrar',payload={},didactic_data=StructureService._didactic_content(sid),before_state=state,after_state=state,success=True,message='private C mostrar baseline',mutates=False,console_events=[]);peak=tracemalloc.get_traced_memory()[1];elapsed=time.perf_counter()-start;tracemalloc.stop();record['private_trace']=trace;resources.append({'method':record['method'],'case':name,'scope':'private_generic_trace_Cextract_JSON_noHTTPsession','peak_bytes':peak,'seconds':elapsed,'JSON_bytes':len(json.dumps(trace,ensure_ascii=False).encode('utf-8'))})
   client=app.test_client()
   for value in (list(reversed(values)) if sid=='stack' else values):assert client.post('/sequential/'+sid+'/operate',json={'operation':'apilar' if sid=='stack' else 'encolar','payload':{'value':value}}).get_json()['success']
   from unittest.mock import patch
   cls=StackAdapter if sid=='stack' else QueueAdapter;orig=cls.execute;target=[]
   def observe(self,op,payload):
    if op=='mostrar':target.append(op)
    return orig(self,op,payload)
   rejected=[]
   with patch.object(cls,'execute',observe):
    tracemalloc.start();start=time.perf_counter()
    for _ in range(2):
     r=client.post('/sequential/'+sid+'/operate',json={'operation':'mostrar','payload':{}});d=r.get_json();assert r.status_code==400 and not d['success'] and d['visual_state']==state;assert d['execution_trace']['steps']==[] and d['execution_trace']['execution_started'] is False;assert not any(x['operation']=='mostrar' for x in d['history']);rejected.append({'HTTP':400,'data':d})
    peak=tracemalloc.get_traced_memory()[1];elapsed=time.perf_counter()-start;tracemalloc.stop();resources.append({'method':record['method'],'case':name,'scope':'two_rejected_POSTs_session_replay_JSON','peak_bytes':peak,'seconds':elapsed,'JSON_bytes':len(r.data)});assert client.get('/sequential/'+sid).status_code==200 and client.get('/sequential/'+sid).status_code==200 and target==[]
   record.update(rejected=rejected,not_registered=not any(o['name']=='mostrar' for o in a.get_supported_operations()),POST_GET_target=0,journal_query=0)
  reports.append(record)
 summary={'method':stem+'_mostrar','calls':2*len(fixtures),'events':len(events),'conditions':sum(x['phase'] in ['if','while'] for x in events),'printf_events':sum(x['phase']=='printf' for x in events),'raw_equal_cases':sum(x['raw_console_equal'] for x in reports if x['structure']==sid),'raw_cases':len(fixtures)};(E/(sid+'-native-summary.json')).write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(summary)
(E/'report.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(E/'downloads.json').write_text(json.dumps(downloads,indent=2)+'\n',encoding='utf-8');(E/'resources.json').write_text(json.dumps({'samples':resources,'limits':'Finite per-method/privategenerictraces vs rejected API; no acceptedquery/RSS/browsermemory/unboundedhistory/SLA/OOM/sanitizer proof.'},indent=2)+'\n',encoding='utf-8')

from app.domain.sequential.show_instruction import build_show_trace
comparison=[]
for d in reports:
 sid=d['structure'];source=StructureService._didactic_content(sid)['operations']['mostrar'];ns=d['native'];n=ns[0]
 def symbol(i):return None if i==-1 else 'N'+str(i+1)
 heap=[{'id':symbol(x['id']),'address':symbol(x['id']),'type':'struct NodoCola','alive':True,'allocated':True,'freed':False,'status':'borrowed','initialized_mask':3,'fields_valid':True,'field_validity':{'nro':True,'sgte':True},'fields':{'nro':x['nro'],'sgte':symbol(x['next_id'])}} for x in n['nodes']]
 fields={'delante':symbol(n['front_id']),'atras':symbol(n['rear_id'])}
 state=d.get('visual',{'items':[{'value':x['nro']} for x in n['nodes']] if fields['delante'] else [],'size':len(n['nodes']) if fields['delante'] else 0,'empty':not bool(fields['delante'])})
 traces=[];samples=sorted({x['sample'] for x in ns})
 for sample in samples:
  tr=build_show_trace(structure_id=sid,payload={},source_code=source,code_title='C actual',before_state=state,after_state=state,success=True,message='private Mostrar',borrowed_memory={'nodes':heap,'fields':fields} if d['private_inconsistent_roots'] else None);oracle=[x for x in ns if x['sample']==sample];assert len(tr['steps'])==len(oracle)
  for step,native in zip(tr['steps'],oracle):
   m=step['pedagogy'];sm=m['show_memory'];assert step['event_type']==native['phase'];assert ''.join(step['console'])==native['console'];assert step['line_text']==source.replace('\r\n','\n').split('\n')[step['line_index']];assert step['state_after']==state and step['state_snapshot']==state;assert sm['allocations']==sm['frees']==0 and m['heap_transition']['before']==m['heap_transition']['after'];assert sm['aux_initialized']==bool(native['aux_initialized']) and (sm['aux'] if sm['aux_initialized'] else None)==(symbol(native['aux_id']) if native['aux_initialized'] else None)
   if native['phase'] in ['if','while']:assert m['condition']['result']==bool(native['condition'])
   if native['phase'] in ['return','end']:assert sm['scope']=='ended' and sm['parameter'] is None and m['call_stack']==[] and not any(v['scope']==d['method'] for v in m['variables'])
   assert not any(v['name']=='return' and v['type']=='int' for v in m['variables'])
   for h,hn in zip(sm['heap'],native['nodes']):assert h['fields']=={'nro':hn['nro'],'sgte':symbol(hn['next_id'])} and h['alive'] and h['initialized_mask']==3
  traces.append(tr)
 comparison.append({'method':d['method'],'case':d['case'],'traces':traces,'events_compared':len(ns),'conditions_compared':sum(x['phase'] in ['if','while'] for x in ns),'native_outputs':d['native_outputs'],'raw_outputs':d['raw_outputs'],'private_inconsistent_roots':d['private_inconsistent_roots']})
assert sum(x['events_compared'] for x in comparison)==432 and sum(x['conditions_compared'] for x in comparison)==126
(E/'private-native-comparison.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Current Mostrar432events126conditions40calls matchC,raw20/20 exact,API36reject400zeroCsteps;native reused.')
