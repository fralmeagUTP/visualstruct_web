"""Capture real accepted and rejected HTTP operations for frontend preservation QA."""
from pathlib import Path
import json,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from app.config import Config
with tempfile.TemporaryDirectory() as folder:
 class C(Config): TESTING=True;SESSION_CACHE_DIR=folder;SESSION_MAX_HISTORY=1
 client=create_app(C).test_client()
 rows=[]
 for value,status in [(10,200),(20,409)]:
  response=client.post('/hierarchical/avl/operate',json={'operation':'insertar','payload':{'value':value}})
  assert response.status_code==status
  rows.append({'status':status,'data':response.get_json()})
 assert rows[1]['data']['preserve_session'] is True
 (ROOT/'qa_general/frontend-fixtures/avl-conflict.json').write_text(json.dumps(rows))
 print('PASS real AVL HTTP200 then409 captured at session history budget1.')
