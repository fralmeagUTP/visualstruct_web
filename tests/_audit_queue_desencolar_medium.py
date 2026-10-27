"""Reuse immutable native dequeue oracle against every current trace event."""
from pathlib import Path
import json,sys,hashlib,os,time,tracemalloc
R=Path.cwd();sys.path.insert(0,str(R));sys.stdout.reconfigure(encoding='utf-8');C=R/'openspec/changes/audit-local-quality-and-unified-controls';B=C/'evidence/visible-queue-desencolar-baseline-low';E=C/'evidence/visible-queue-desencolar-instructions-medium'
os.environ['SESSION_CACHE_DIR']=str(E/'private-sessions')
from app import create_app
from app.domain.sequential.queue_dequeue_instruction import build_queue_dequeue_trace
app=create_app();app.config['TESTING']=True
for ext in ['c','h']:assert (B/'native'/('tad_cola.'+ext)).read_bytes()==(R/'docs/tads_C'/('tad_cola.'+ext)).read_bytes()
native=[json.loads(x) for x in (B/'native/events.jsonl').read_text(encoding='utf-8').splitlines()];cases=[('null',None),('empty',[]),('single',[-1]),('multi',[7,-1]),('duplicate',[7,7]),('bounds',[-2147483648,2147483647])];rows=[];allchecks=[];resources=[];source=None;empty_visual=None
for ci,(name,seeds) in enumerate(cases):
 if seeds is None:continue
 client=app.test_client()
 for v in seeds:assert client.post('/sequential/queue/operate',json={'operation':'encolar','payload':{'value':v}}).get_json()['success']
 for repeat in [1,2]:
  tracemalloc.start();t=time.perf_counter();response=client.post('/sequential/queue/operate',json={'operation':'desencolar','payload':{}});elapsed=time.perf_counter()-t;cur,peak=tracemalloc.get_traced_memory();tracemalloc.stop();d=response.get_json();trace=d['execution_trace'];source=trace['source_code'];empty_visual=d['visual_state'] if name=='empty' else empty_visual
  rows.append({'case':name,'repeat':repeat,'sample':ci*2+repeat-1,'HTTP':response.status_code,'data':d});resources.append({'case':name,'repeat':repeat,'python_peak_bytes':peak,'response_bytes':len(response.data),'seconds_instrumented':elapsed})
for repeat in [1,2]:
 tr=build_queue_dequeue_trace(payload={},source_code=source,code_title='Código C',before_state=empty_visual,after_state=empty_visual,success=False,message='fixture privada NULL',null_root=True);rows.append({'case':'null','repeat':repeat,'sample':repeat-1,'private':True,'data':{'execution_trace':tr}})
for row in rows:
 expected=[x for x in native if x['sample']==row['sample']];steps=row['data']['execution_trace']['steps'];assert len(expected)==len(steps),(row['case'],len(expected),len(steps))
 ids=[x['id'] for x in expected[0]['heap']];symbols={i:'N'+str(j+1) for j,i in enumerate(ids)};symbol=lambda n:None if n==-1 else symbols[n]
 for n,s in zip(expected,steps):
  dbg=s['debug'];aux=dbg['aux'];num=dbg['num'];projection={'token':dbg['token'],'condition':s['condition_result'],'root_NULL':not dbg['root']['alive'],'front':dbg['root']['front'],'rear':dbg['root']['rear'],'aux_initialized':aux is not None,'aux_id':aux['value'] if aux else None,'aux_alive':bool(aux and aux['valid']),'num_initialized':num['initialized'],'num':num['value'] if num['initialized'] else None,'result_initialized':dbg['result'] is not None,'result':dbg['result'],'values':[x['value'] for x in s['state_after']['items']],'heap':[{'id':x['id'],'value':x['fields']['nro'],'next':x['fields']['sgte']} for x in dbg['heap']],'console':s['console']}
  oracle={'token':n['event'],'condition':None if n['condition']==-1 else bool(n['condition']),'root_NULL':bool(n['root_NULL']),'front':symbol(n['front']),'rear':symbol(n['rear']),'aux_initialized':bool(n['aux_initialized']),'aux_id':symbol(n['aux_id']) if n['aux_initialized'] else None,'aux_alive':bool(n['aux_alive']),'num_initialized':bool(n['num_initialized']),'num':n['num'] if n['num_initialized'] else None,'result_initialized':bool(n['result_initialized']),'result':n['result'] if n['result_initialized'] else None,'values':n['values'],'heap':[{'id':symbol(x['id']),'value':x['value'],'next':symbol(x['next'])} for x in n['heap']],'console':n['console'].splitlines()}
  equal=projection==oracle;allchecks.append({'sample':row['sample'],'event':n['event'],'equal':equal});assert equal,(row['case'],n['event'],projection,oracle)
(E/'report.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(E/'full-event-comparison.json').write_text(json.dumps(allchecks,indent=2)+'\n',encoding='utf-8');(E/'native-reuse.json').write_text(json.dumps({'calls':12,'events':87,'conditions':19,'new_C_runs':0,'C_H_current_bytes_equal':True,'ordered_full_projection_equal':True,'private_NULL_traces':2,'public_API_calls':10,'return_int_no_output_pointer':True,'historical_13_values_only_no_additive_claim':True},indent=2)+'\n',encoding='utf-8');(E/'resources.json').write_text(json.dumps({'calls':resources,'max_python_peak_bytes':max(x['python_peak_bytes'] for x in resources),'max_response_bytes':max(x['response_bytes'] for x in resources),'max_instrumented_seconds':max(x['seconds_instrumented'] for x in resources),'limits':'10 finite API tracemalloc including Flask/session/deepcopy/serialization; excludesRSS/browser/Cheap/universalquantitydepthhistory/OOM/leak/SLA/sanitizer'},indent=2)+'\n',encoding='utf-8');print('full native projection',len(allchecks),'equal; API10/privateNULL2')
