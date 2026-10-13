"""No final query result before completion, also after backward replay/reset."""
import json,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
pytestmark=pytest.mark.e2e

@pytest.mark.parametrize('seed,operation,target',[([], 'altura',None),([10,5,15],'altura',None),([], 'buscar',7),([10,5,15],'buscar',5),([10,5,15],'buscar',99),([], 'inorden',None),([10,5,15],'inorden',None)])
def test_avl_query_message_has_no_future_result_and_rewinds(tmp_path,seed,operation,target):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';errors=[];posts=[];rows=[]
 try:
  with sync() as p:
   browser=p.chromium.launch();context=browser.new_context();page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
   for value in seed:assert context.request.post(base+'/hierarchical/avl/operate',data={'operation':'insertar','payload':{'value':value}}).json()['success']
   page.goto(base+'/hierarchical/avl',wait_until='networkidle');page.select_option('#operation-select',operation)
   if target is not None:page.locator('[name="value"]').fill(str(target))
   page.click('#hier-step-mode')
   with page.expect_response(lambda r:r.url.endswith('/avl/operate') and r.request.method=='POST') as response:page.click('#hier-sim-play')
   data=response.value.json();assert data['success'];count=len(posts);assert count==1;steps=data['execution_trace']['steps'];final=data['message'];pending='Consulta preparada: resultado pendiente hasta completar la traza.'
   box=page.locator('#message-box');assert box.inner_text()==pending and box.inner_text()!=final;rows.append({'boundary':'initial','message':box.inner_text()})
   page.locator('#hier-sim-step').evaluate('b=>b.click()');page.wait_for_function("()=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: 1/')");assert box.inner_text()==pending
   for index in range(1,len(steps)):
    page.locator('#hier-sim-step').evaluate('b=>b.click()')
    page.wait_for_function("n=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
    assert box.inner_text()==(final if index==len(steps)-1 else pending)
   assert box.inner_text()==final;rows.append({'boundary':'final','message':box.inner_text()})
   page.locator('#hier-sim-prev').evaluate('b=>b.click()');page.wait_for_function("n=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=len(steps)-1);assert box.inner_text()==pending
   # Closing step mode seeks the finished trace; opening it restores the initial state.
   page.click('#hier-step-mode');assert box.inner_text()==final;assert not page.locator('#hier-sim-step').is_visible()
   page.click('#hier-step-mode');assert box.inner_text()==pending;assert len(posts)==count and not errors
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (tmp_path/'query-result-boundary-review.json').write_text(json.dumps({'seed':seed,'operation':operation,'target':target,'rows':rows,'extra_replay_posts':0,'errors':errors},indent=2),encoding='utf-8')
