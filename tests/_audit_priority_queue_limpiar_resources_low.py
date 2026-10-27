"""Finite isolated in-process API resource measurements; no native baseline replay."""
from pathlib import Path
import sys,json,tracemalloc,time,tempfile
R=Path.cwd();sys.path.insert(0,str(R))
from app import create_app
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-priority-queue-limpiar-baseline-completion-low'
app=create_app();app.config['TESTING']=True
rows=[]
for name,values in [('empty',[]),('single',[(-1,2)]),('multi',[(7,3),(-2,1),(7,1)]),('reinsert',[(7,3),(-2,1),(7,1)])]:
 c=app.test_client()
 for v,p in values:assert c.post('/sequential/priority_queue/operate',json={'operation':'encolar','payload':{'value':v,'priority':p}}).get_json()['success']
 for repeat in [1,2]:
  if name=='reinsert' and repeat==2:assert c.post('/sequential/priority_queue/operate',json={'operation':'encolar','payload':{'value':8,'priority':-1}}).get_json()['success']
  tracemalloc.start();t=time.perf_counter();r=c.post('/sequential/priority_queue/operate',json={'operation':'limpiar','payload':{}});elapsed=time.perf_counter()-t;current,peak=tracemalloc.get_traced_memory();tracemalloc.stop();d=r.get_json();assert r.status_code==200 and d['success'] and d['visual_state']['items']==[]
  rows.append({'case':name,'repeat':repeat,'python_peak_bytes':peak,'python_current_bytes':current,'elapsed_instrumented_seconds':elapsed,'response_bytes':len(r.data),'frames':len(d['execution_trace']['steps'])})
x={'calls':rows,'max_python_peak_bytes':max(r['python_peak_bytes'] for r in rows),'max_response_bytes':max(r['response_bytes'] for r in rows),'max_instrumented_seconds':max(r['elapsed_instrumented_seconds'] for r in rows),'limitations':'tracemalloc Python allocation peak only; includes in-process Flask dispatch/session/serialization, excludes browser/RSS/C allocations; finite fixtures, not SLA/depth/history/OOM certification'}
(E/'resources.json').write_text(json.dumps(x,indent=2),encoding='utf-8');print(json.dumps(x))
