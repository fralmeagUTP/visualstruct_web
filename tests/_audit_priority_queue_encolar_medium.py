"""Compare current priority enqueue full traces with immutable safe native events."""
from pathlib import Path
from copy import deepcopy
import sys,json,time,tracemalloc
R=Path.cwd();sys.path.insert(0,str(R))
from app import create_app
from app.domain.sequential.priority_queue_enqueue_instruction import build_priority_queue_enqueue_trace
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-priority-queue-encolar-instructions-medium';B=E.parent/'visible-priority-queue-encolar-baseline-low'
def write(n,d): (E/n).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
read=lambda n:json.loads((B/n).read_text(encoding='utf-8-sig'))
native=read('native-report.json')
for ext in ['c','h']:assert (B/'native'/('tad_cola_prioridad.'+ext)).read_bytes()==(R/'docs/tads_C'/('tad_cola_prioridad.'+ext)).read_bytes()
app=create_app();app.config['TESTING']=True;rows=[];traces={};resources=[];sid=0
CASES=[('empty',[],(9,3)),('single',[(7,2)],(-1,-1)),('duplicate',[(7,1)],(7,1)),('bounds',[(2147483647,2147483647),(-1,-1)],(-2147483648,-2147483648))]
for case,seeds,(value,priority) in CASES:
 c=app.test_client()
 for v,p in seeds:assert c.post('/sequential/priority_queue/operate',json={'operation':'encolar','payload':{'value':v,'priority':p}}).get_json()['success']
 for repeat in [1,2]:
  tracemalloc.start();start=time.perf_counter();r=c.post('/sequential/priority_queue/operate',json={'operation':'encolar','payload':{'value':value,'priority':priority}});elapsed=time.perf_counter()-start;current,peak=tracemalloc.get_traced_memory();tracemalloc.stop();d=r.get_json();assert r.status_code==200 and d['success'];t=d['execution_trace'];traces[sid]=t;ns=[n for n in native if n['sample']==sid];mapping={n['id']:h['id'] for n,h in zip(ns[-1]['live'],t['steps'][-1]['debug']['heap'])};mapped=lambda x:None if x==-1 else mapping[x]
  tokens=['helper_new_allocated','value_assigned','priority_assigned','link_assigned','helper_return','front_assigned' if ns[0]['front_id']==-1 else 'rear_next_assigned','rear_assigned','count_incremented','return_true'];observations=[]
  for token in tokens:
   n=next(n for n in ns if n['event']==token);f=next(f for f in t['steps'] if f['event_type']==token);root=f['debug']['root'];observations.append({'event':token,'root_items_match':f['state_after']['items']==n['root_items'],'quantity_match':f['state_after']['cantidad']==n['quantity'],'front_match':root['front']==mapped(n['front_id']),'rear_match':root['rear']==mapped(n['rear_id']),'heap_count_match':len(f['debug']['heap'])==len(n['live'])})
  assert d['visual_state']['items']==ns[-1]['root_items'] and d['visual_state']['out_index']==ns[-1]['out_index'];rows.append({'case':case,'seeds':seeds,'value':value,'priority':priority,'repeat':repeat,'native_sample':sid,'native_events':ns,'observations':observations,'final_fifo_and_stable_priority_match':True,'data':d});resources.append({'case':case,'repeat':repeat,'python_peak_bytes':peak,'python_current_bytes':current,'response_bytes':len(r.data),'elapsed_instrumented_seconds':elapsed,'frames':len(t['steps'])});sid+=1
 sid+=1
source=rows[0]['data']['execution_trace']['source_code']
for sid in sorted({n['sample'] for n in native}):
 if sid in traces:continue
 ns=[n for n in native if n['sample']==sid];before=deepcopy(rows[0]['data']['execution_trace']['steps'][0]['state_snapshot']);before.update(items=ns[0]['root_items'],cantidad=ns[0]['quantity'],size=len(ns[0]['root_items']),empty=not ns[0]['root_items'])
 traces[sid]=build_priority_queue_enqueue_trace(payload={'value':ns[0]['value_parameter'],'priority':ns[0]['priority_parameter']},source_code=source,code_title='cp_encolar',before_state=before,after_state=before,success=False,message='Private QA only',null_root=bool(ns[0]['root_NULL']),allocation_failure=not bool(ns[0]['root_NULL']))
comparisons=[]
for sid,t in sorted(traces.items()):
 ns=[n for n in native if n['sample']==sid];assert len(ns)==len(t['steps']),(sid,len(ns),len(t['steps']));mapping={}
 for n,f in zip(ns,t['steps']):
  dbg=f['debug'];assert n['event']==f['event_type'];assert f['condition_result']==(None if n['condition']==-1 else bool(n['condition']));assert len(n['live'])==len(dbg['heap']);assert f['state_after']['items']==n['root_items'] and f['state_after']['out_index']==n['out_index'] and f['state_after']['cantidad']==n['quantity']
  for a,h in zip(n['live'],dbg['heap']):assert a['id'] not in mapping or mapping[a['id']]==h['id'];mapping[a['id']]=h['id']
  mapped=lambda x:None if x==-1 else mapping[x]
  for a,h in zip(n['live'],dbg['heap']):
   assert a['mask']==h['initialized_mask'];assert h['fields']['valor']==a['value'] and h['fields']['prioridad']==a['priority'];assert h['fields']['sgte']==(mapped(a['next_id']) if a['mask']&4 else None);assert h['field_validity']=={'valor':bool(a['mask']&1),'prioridad':bool(a['mask']&2),'sgte':bool(a['mask']&4)}
  assert dbg['root']['front']==mapped(n['front_id']) and dbg['root']['rear']==mapped(n['rear_id']) and dbg['root']['quantity']==n['quantity'];assert f['console']==[] and f['pedagogy']['heap_transition']['freed']==[]
  if n['helper_active']:
   assert any(c['function']=='cp_crear_nodo' for c in dbg['call_stack'])
   if n['helper_new_initialized']:assert dbg['helper_new']['initialized'] and dbg['helper_new']['value']==mapped(n['helper_new_id'])
   elif dbg['helper_new'] is not None:assert not dbg['helper_new']['initialized']
  else:assert dbg['helper_new'] is None
  if n['event'] in ['return_true','return_false']:
   assert not dbg['call_stack'] and dbg['parent_new'] is None and all(p['scope']=='caller' for p in dbg['pointers']);assert dbg['return_value']==(n['event']=='return_true')
  elif n['parent_new_initialized']:assert dbg['parent_new']['initialized'] and dbg['parent_new']['value']==mapped(n['parent_new_id'])
  elif dbg['parent_new'] is not None:assert not dbg['parent_new']['initialized']
  if n['event']=='allocator_enter':assert [c['function'] for c in dbg['call_stack']]==['cp_encolar','cp_crear_nodo','malloc'] and dbg['call_stack'][-1]['opaque']
  comparisons.append({'sample':sid,'event':n['event'],'equal':True})
assert len(comparisons)==242 and sum(n['condition']!=-1 for n in native)==48
write('report.json',rows);write('full-event-comparison.json',comparisons);write('fault-traces.json',{str(k):v for k,v in traces.items() if k not in {r['native_sample'] for r in rows}});write('native-reuse.json',{'calls':14,'events':242,'conditions':48,'new_C_runs':0,'C_H_current_bytes_equal':True,'full_projection_equal':True,'private_python_faults':6,'no_public_fault_API_or_real_OOM':True,'baseline_remains_immutable':True})
write('resources.json',{'calls':resources,'max_python_peak_bytes':max(x['python_peak_bytes'] for x in resources),'max_response_bytes':max(x['response_bytes'] for x in resources),'max_instrumented_seconds':max(x['elapsed_instrumented_seconds'] for x in resources),'limitations':'8 finite tracemalloc Python/API samples; includes Flask/session/serialization, not RSS/browser/Cheap/arbitrarydepthhistory/OOM/leak/SLA'})
for name in ['native-report.json','downloads.json','caller-ownership/report.json','caller-doxygen.json']:
 q=E/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((B/name).read_bytes())
(E/'native').mkdir(exist_ok=True);(E/'native/stderr.log').write_bytes((B/'native/stderr.log').read_bytes())
print('Full current projection242events48conditions14calls matches reused C;72observations no divergences;8new API finite resource samples')
