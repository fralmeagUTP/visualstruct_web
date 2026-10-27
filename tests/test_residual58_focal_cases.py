"""New finite58 cases: private sessions, literal operation results and phase context."""
from __future__ import annotations
from copy import deepcopy
import json,threading
from pathlib import Path
import pytest
from werkzeug.serving import make_server
from app import create_app
from app.config import Config
CASES=json.loads((Path(__file__).parent/'fixtures/residual58-focal-v1.json').read_text(encoding='utf-8'))['cases']

def family(row):
 if row['id'].startswith('algorithm:'):return 'graph-algorithms'
 if row['id'].startswith('control:'):return 'browser-export'
 if row['id'].startswith('route:'):return 'comparison-route'
 return row['id'].split(':',1)[1].split('/')[0]

@pytest.fixture
def residual58_app(tmp_path):
 class PrivateConfig(Config):
  TESTING=True
  APP_ENV='testing'
  SECRET_KEY='residual58-private-only'
  SESSION_TYPE='cachelib'
  SESSION_CACHE_DIR=str(tmp_path/'sessions')
  SESSION_COOKIE_NAME='residual58_private'
 return create_app(PrivateConfig)

@pytest.fixture
def residual58_client(residual58_app):return residual58_app.test_client()

def post_operation(client,module,sid,operation,payload=None):
 response=client.post(f'/{module}/{sid}/operate',json={'operation':operation,'payload':payload or {}})
 assert response.status_code==200,response.get_json()
 return response.get_json()

def nested(body,path):
 value=body
 for piece in path.split('.'):value=value[piece]
 return value

def run_case(client,row):
 ident=row['id'];parts=ident.split(':',1)[1].split('/')
 module='graph' if ident.startswith('algorithm:') or ident.startswith('route:') else parts[0]
 sid='graph' if module=='graph' else parts[1]
 for step in row['setup']:
  if step.get('method')=='GET':
   response=client.get(step['path']);assert response.status_code==step['expected_status'];assert step['expected_content'].encode() in response.data
  elif step.get('method')=='POST':
   response=client.post(step['path'],json=step['json']);assert response.status_code==200,response.get_json()
  else:post_operation(client,module,sid,step['operation'],step['payload'])
 req=row['request_or_gesture']
 with client.session_transaction() as session:before=deepcopy(dict(session))
 response=client.post(req['path'],json=req['json']);assert response.status_code==row['expected_status'],response.get_json()
 body=response.get_json();assert body['success'] is True
 for key,value in row['expected'].items():
  if key.startswith('followup.'):
   _,operation,result_key=key.split('.');follow=post_operation(client,module,sid,operation);assert follow[result_key]==value
  elif key=='normalized_result.mst_edges':
   actual=sorted([min(a,b),max(a,b),weight] for a,b,weight in body['result']['mst_edges']);assert actual==value
  elif key=='result_numeric_equality':assert body['result']==value
  elif key=='directed_preserved':assert body['visual_state']['directed'] is value
  elif key=='input_equals_supplied_snapshot':assert body['input']==req['json']['graph']
  elif key=='session_state_and_history_before_equals_after':
   with client.session_transaction() as session:assert dict(session)==before
  else:assert nested(body,key)==value
 return body

API_CASES=[row for row in CASES if not row['id'].startswith('control:')]
@pytest.mark.parametrize('row',API_CASES,ids=lambda row:family(row)+'::'+row['id'])
def test_residual58_concrete_api_case(residual58_client,row):
 run_case(residual58_client,row)

@pytest.mark.e2e
def test_residual58_export_scale_real_downloads(residual58_app,tmp_path):
 from PIL import Image
 from playwright.sync_api import sync_playwright
 row=next(row for row in CASES if row['id'].startswith('control:'))
 server=make_server('127.0.0.1',0,residual58_app,threaded=True);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch();context=browser.new_context(viewport=row['request_or_gesture']['viewport'],accept_downloads=True);page=context.new_page();errors=[];posts=[]
   page.on('pageerror',lambda error:errors.append(str(error)))
   page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None)
   page.goto(base+'/sorting/visualizador',wait_until='networkidle')
   response=context.request.post(base+'/api/ordenamiento/create-array',data={'values':[7,2,9]});assert response.status==200
   page.reload(wait_until='networkidle')
   assert page.locator('#sorting-visual-state').is_visible()
   count=len(posts);sizes=[];geometry=[]
   for scale in ['1','2']:
    page.select_option('#export-jpg-scale',scale);assert page.locator('#export-jpg-scale').input_value()==scale
    geometry.append(page.locator('#sorting-visual-state').evaluate('(e)=>[e.getBoundingClientRect().width,e.getBoundingClientRect().height,e.scrollWidth,e.scrollHeight]'))
    with page.expect_download() as download:page.click('#export-visual-jpg-btn')
    dest=tmp_path/f'scale-{scale}.jpg';download.value.save_as(dest)
    with Image.open(dest) as image:
     assert image.format=='JPEG';assert any(low!=high for low,high in image.convert('RGB').getextrema());sizes.append(image.size)
   assert geometry[0]==geometry[1]
   assert sizes[1]==(2*sizes[0][0],2*sizes[0][1])
   assert len(posts)==count and not errors
   context.close();browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (tmp_path/'export-scale-result.json').write_text(json.dumps({'sizes':sizes,'geometry':geometry,'extra_posts':len(posts)-count,'errors':errors}),encoding='utf-8')
