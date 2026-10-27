"""Reuse only compatible priority front native subset against current API."""
from pathlib import Path
import json,sys,re,hashlib,time,tracemalloc,os
R=Path.cwd();sys.path.insert(0,str(R));sys.stdout.reconfigure(encoding='utf-8');C=R/'openspec/changes/audit-local-quality-and-unified-controls';E=C/'evidence/visible-priority-queue-front-instructions-medium';P=C/'evidence/priority-instruction-review';os.environ['SESSION_CACHE_DIR']=str(E/'private-sessions')
from app import create_app
app=create_app();app.config['TESTING']=True;raw=json.loads((E/'reused-front-native-events.json').read_text(encoding='utf-8'));names=['actual','prev','objetivo','objetivoPrev'];norm=lambda x:re.sub(r'\s+',' ',x.strip());cases=[('front',[1,2,3]),('interior',[3,1,2]),('rear',[3,2,1]),('equal-front',[1,1,2]),('equal-interior',[3,1,1]),('several-updates',[4,3,1]),('single',[1]),('empty',[])];rows=[];observations=[];missing=[];conditions=[];resources=[];downloads={}
for kind,ext in [('source','c'),('header','h')]:
 response=app.test_client().get('/help/source/priority_queue/'+kind);assert response.status_code==200 and response.data==(R/'docs/tads_C'/('tad_cola_prioridad.'+ext)).read_bytes();(E/('current-tad_cola_prioridad.'+ext)).write_bytes(response.data);downloads[kind]={'HTTP':200,'SHA':hashlib.sha256(response.data).hexdigest()}
for ci,(label,priorities) in enumerate(cases):
 client=app.test_client()
 for i,p in enumerate(priorities):assert client.post('/sequential/priority_queue/operate',json={'operation':'encolar','payload':{'value':10*(i+1),'priority':p}}).get_json()['success']
 tracemalloc.start();t=time.perf_counter();response=client.post('/sequential/priority_queue/operate',json={'operation':'frente','payload':{}});elapsed=time.perf_counter()-t;cur,peak=tracemalloc.get_traced_memory();tracemalloc.stop();data=response.get_json();trace=data['execution_trace'];rows.append({'case':label,'priorities':priorities,'HTTP':response.status_code,'data':data});resources.append({'case':label,'python_peak_bytes':peak,'response_bytes':len(response.data),'seconds_instrumented':elapsed});steps=trace['steps'];cursor=0
 events=[x for x in raw if x['case']==ci and (x['phase']=='after' or x['phase']=='before' and x['line'].startswith('return '))]
 for event in events:
  matches=[i for i in range(cursor,len(steps)) if norm(steps[i]['line_text'])==norm(event['line'])]
  if not matches:missing.append({'case':label,'line':event['line'],'native':event});continue
  idx=matches[0];cursor=idx+1;s=steps[idx];state=s['state_snapshot'] if event['line'].startswith('return ') else s['state_after'];expected={'items':[{'value':v,'priority':p} for v,p in event['items']],'delante':'NULL' if event['front']==0 else f'N{event["front"]}','atras':'NULL' if event['rear']==0 else f'N{event["rear"]}','cantidad':event['count']}
  for name,node in zip(names,event['aliases']):
   if node is not None:expected[name]='NULL' if node==0 else f'N{node}'
  if event['output_value'] is not None:expected['valor']=event['output_value']
  if event['output_priority'] is not None:expected['prioridad']=event['output_priority']
  mismatches={k:{'native':v,'trace':state.get(k)} for k,v in expected.items() if state.get(k)!=v};condition=s.get('pedagogy',{}).get('condition')
  if event['condition']!=-1:conditions.append({'case':label,'line':event['line'],'native':bool(event['condition']),'trace':condition.get('result') if condition else None,'equal':bool(condition and condition.get('result')==bool(event['condition']))})
  observations.append({'case':label,'line':event['line'],'index':idx,'native':event,'expected':expected,'trace_observed':state,'mismatches':mismatches,'condition_frame':condition,'console':s['console'],'pedagogy':s['pedagogy']})
 # Final output is observed actual C scalar result, not an instructional-state substitute.
 last=events[-1];success=bool(priorities)
 assert data['success']==success
 assert data.get('result')==(last['output_value'] if success else None)
 assert data['visual_state']['items']==[{'value':v,'priority':p} for v,p in last['items']]
 # Existing API projects scalar result only; verify both C outputs at adapter boundary.
 if success:
  from app.adapters.priority_queue_adapter import PriorityQueueAdapter
  adapter=PriorityQueueAdapter()
  for i,prio in enumerate(priorities):adapter.execute('encolar',{'value':10*(i+1),'priority':prio})
  direct=adapter.execute('frente',{})
  assert direct['result']==last['output_value'] and direct['result_priority']==last['output_priority']
  rows[-1]['adapter_both_C_outputs_match']=True
  rows[-1]['API_result_priority_forwarded']='result_priority' in data
(E/'API-report.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');report={'scope':'Current priority front only; 8 historical seeds. Compatible C/H executable tokens, old raw178events reused, no new native execution of these seeds. Before/after phase alignment; declaration initialization and NULL/outputargs not old coverage.','raw_native_events_reused':178,'candidate_after_return_events':sum(sum(x['case']==ci and (x['phase']=='after' or x['phase']=='before' and x['line'].startswith('return ')) for x in raw) for ci in range(8)),'observations':observations,'missing_sequence_events':missing,'condition_comparisons':{'observations':conditions,'mismatches':[x for x in conditions if not x['equal']]},'final8_native_API_results_reachable_equal':True,'downloads':downloads,'divergent_observations':sum(bool(x['mismatches']) for x in observations),'mismatch_keys':sorted({k for x in observations for k in x['mismatches']})};(E/'native-priority-front-current-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(E/'resources.json').write_text(json.dumps({'calls':resources,'max_python_peak_bytes':max(x['python_peak_bytes'] for x in resources),'max_response_bytes':max(x['response_bytes'] for x in resources),'max_instrumented_seconds':max(x['seconds_instrumented'] for x in resources),'limits':'8 finite API tracemalloc includingFlask/session/serialization; no RSS/browser/Cheap/universaldepthhistory/OOM/leak/SLA/sanitizer'},indent=2)+'\n',encoding='utf-8');print('currentAPI8 finalresults equal; reused178 / aligned',len(observations),'missing',len(missing),'divergences',report['divergent_observations'],'conditions',len(conditions),'divergences',len(report['condition_comparisons']['mismatches']))
