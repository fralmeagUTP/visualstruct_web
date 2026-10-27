import json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from app.config import Config
with tempfile.TemporaryDirectory() as folder:
 class T(Config):TESTING=True;SESSION_CACHE_DIR=folder
 c=create_app(T).test_client();out=[]
 for op,p in [('get',{'key':999}),('insert',{'key':3,'value':7,'simulate_allocation_failure':True})]:
  r=c.post('/hash/hash_table/operate',json={'operation':op,'payload':p});d=r.get_json();assert r.status_code==400,(op,r.status_code);assert d['execution_trace']['steps'];assert not d['success'];out.append({'operation':op,'payload':p,'status':r.status_code,'response':d})
(ROOT/'qa/hash_failure_fixtures.json').write_text(json.dumps(out,ensure_ascii=False));print([(x['operation'],x['status'],len(x['response']['execution_trace']['steps'])) for x in out])
