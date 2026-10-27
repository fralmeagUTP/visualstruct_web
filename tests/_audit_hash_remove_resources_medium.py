"""Finite overhead measurement of the same23native remove fixtures, not new coverage."""
from pathlib import Path
import sys,json,time,tracemalloc,shutil
R=Path.cwd();sys.path.insert(0,str(R));from app import create_app
from tests.test_hash_remove_instructions import PAIRS
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-remove-instructions-medium';fixtures=json.loads((E/'report.json').read_text(encoding='utf-8'));app=create_app();app.config['TESTING']=True;rows=[]
for case,pairs in PAIRS.items():
 c=app.test_client();c.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':3}})
 for k,v in pairs:c.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':k,'value':v}})
 for fixture in [r for r in fixtures if r['case']==case]:
  tracemalloc.start();start=time.perf_counter();r=c.post('/hash/hash_table/operate',json={'operation':'remove','payload':{'key':fixture['key']}});d=r.get_json();elapsed=time.perf_counter()-start;_,peak=tracemalloc.get_traced_memory();tracemalloc.stop();assert d['result']==bool(fixture['native'][-1]['status']);rows.append({'case':case,'key':fixture['key'],'frames':len(d['execution_trace']['steps']),'peak_tracemalloc_bytes':peak,'JSON_bytes':len(r.data),'seconds_instrumented':elapsed})
summary={'operations':23,'rows':rows,'max_peak_bytes':max(r['peak_tracemalloc_bytes'] for r in rows),'max_JSON_bytes':max(r['JSON_bytes'] for r in rows),'max_seconds_instrumented':max(r['seconds_instrumented'] for r in rows),'limits':['Same23cases; not new semantic coverage','capacity3/chains<=4/int32','tracemalloc/Flask/JSON/session included; notRSS/SLA','No arbitrary sessions/chains/OOM/native performance guarantee']}
if (E/'current-resources.json').exists():shutil.copyfile(E/'current-resources.json',E/'current-resources-first-pass.json')
(E/'current-resources.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k!='rows'}))
