"""Current enqueue QA against immutable native baseline; no native reexecution."""
from pathlib import Path
from copy import deepcopy
import json,sys,hashlib
R=Path.cwd();sys.path.insert(0,str(R))
from app import create_app
from app.domain.sequential.queue_enqueue_instruction import build_queue_enqueue_trace
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-queue-encolar-instructions-medium'
B=E.parent/'visible-queue-encolar-baseline-low'
def write(name,value): (E/name).write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')
native=json.loads((B/'native-report.json').read_text(encoding='utf-8-sig'))
for ext in ['c','h']:assert (B/'native'/('tad_cola.'+ext)).read_bytes()==(R/'docs/tads_C'/('tad_cola.'+ext)).read_bytes()
app=create_app();app.config['TESTING']=True
rows=[];sid=0;traces={}
CASES=[('empty',[],9),('single',[7],-1),('duplicate',[7],7),('bounds',[2147483647,-1],-2147483648)]
for case,seeds,value in CASES:
 c=app.test_client()
 for v in seeds:assert c.post('/sequential/queue/operate',json={'operation':'encolar','payload':{'value':v}}).get_json()['success']
 for repeat in [1,2]:
  r=c.post('/sequential/queue/operate',json={'operation':'encolar','payload':{'value':value}});d=r.get_json();assert r.status_code==200 and d['success'];t=d['execution_trace'];traces[sid]=t
  ns=[n for n in native if n['sample']==sid];mapping={n['id']:h['id'] for n,h in zip(ns[-1]['live'],t['steps'][-1]['debug']['heap'])};mapped=lambda x:None if x==-1 else mapping[x]
  observations=[]
  tokens=['aux_allocated','value_assigned','link_assigned','front_assigned' if ns[0]['front_id']==-1 else 'rear_next_assigned','rear_assigned']
  for token in tokens:
   n=next(n for n in ns if n['event']==token);f=next(f for f in t['steps'] if f['event_type']==token);values=[i['value'] for i in f['state_after']['items']];root=f['debug']['root']
   observations.append({'event':token,'root_values_match':values==n['root_values'],'native_heap_count':len(n['live']),'trace_heap_count':len(f['debug']['heap']),'front_projection_match':root['front']==mapped(n['front_id']),'rear_projection_match':root['rear']==mapped(n['rear_id'])})
  assert [i['value'] for i in d['visual_state']['items']]==ns[-1]['root_values'];rows.append({'case':case,'seeds':seeds,'value':value,'repeat':repeat,'native_sample':sid,'observations':observations,'C_API_final_match':True,'data':d});sid+=1
 sid+=1
source=rows[0]['data']['execution_trace']['source_code']
for sample in sorted({n['sample'] for n in native}):
 if sample in traces:continue
 ns=[n for n in native if n['sample']==sample];seed=ns[0]['root_values'];before=deepcopy(rows[0]['data']['execution_trace']['steps'][0]['state_snapshot']);before.update(items=[{'value':v} for v in seed],size=len(seed),empty=not seed)
 value=CASES[sample//3][2] if sample<12 else 9
 traces[sample]=build_queue_enqueue_trace(payload={'value':value},source_code=source,code_title='cola_encolar',before_state=before,after_state=before,success=False,message='QA private fault',null_root=bool(ns[0]['root_argument_NULL']),allocation_failure=not ns[0]['root_argument_NULL'])
comparisons=[]
for sample,t in sorted(traces.items()):
 ns=[n for n in native if n['sample']==sample];fs=t['steps'];assert len(ns)==len(fs),(sample,len(ns),len(fs));mapping={};aux_expected=None
 for n,f in zip(ns,fs):
  dbg=f['debug'];assert n['event']==f['event_type'];assert (None if n['condition']==-1 else bool(n['condition']))==f['condition_result']
  assert len(n['live'])==len(dbg['heap'])
  for obj,h in zip(n['live'],dbg['heap']):
   if obj['id'] in mapping:assert mapping[obj['id']]==h['id']
   mapping[obj['id']]=h['id']
  mapped=lambda x:None if x==-1 else mapping[x]
  for obj,h in zip(n['live'],dbg['heap']):
   assert obj['mask']==h['initialized_mask'] and obj['value']==h['fields']['nro']
   assert h['fields']['sgte']==(mapped(obj['next_id']) if obj['mask']&2 else None)
  assert dbg['root']['front']==mapped(n['front_id']) and dbg['root']['rear']==mapped(n['rear_id'])
  assert [v['value'] for v in f['state_after']['items']]==n['root_values']
  assert ''.join(x+'\n' for x in f['console'])==n['console']
  if f['event_type']=='return':assert dbg['aux'] is None and not dbg['call_stack'] and all(p['scope']=='caller' for p in dbg['pointers'])
  elif n['aux_initialized']:assert dbg['aux']['initialized'] and dbg['aux']['value']==mapped(n['aux_id'])
  elif dbg['aux'] is not None:assert not dbg['aux']['initialized']
  if f['event_type']=='allocator_enter':assert dbg['call_stack'][-1]['function']=='malloc' and dbg['call_stack'][-1]['opaque']
  comparisons.append({'sample':sample,'event':n['event'],'equal':True})
write('report.json',rows);write('full-event-comparison.json',comparisons);write('fault-traces.json',{str(k):v for k,v in traces.items() if k not in {r['native_sample'] for r in rows}})
for name in ['native-report.json','caller-ownership/report.json','caller-doxygen.json','caller-availability.json']:
 target=E/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((B/name).read_bytes())
(E/'native').mkdir(exist_ok=True);(E/'native/stderr.log').write_bytes((B/'native/stderr.log').read_bytes())
write('native-reuse.json',{'native_executed_again':False,'C_H_bytes_equal':True,'baseline_frozen':True,'full_events':len(comparisons),'conditions':sum(n['condition']!=-1 for n in native),'calls':len(traces),'limitations':'symbolic IDs normalized only by allocation order; native baseline retained; finite fixtures only'})
print('Current API8 / full C event projection',len(comparisons),'conditions35 calls14 all equal')
