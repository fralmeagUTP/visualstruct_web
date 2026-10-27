"""Step zero must not present the first instruction's future local scopes."""
import threading
import pytest
from app import create_app
from werkzeug.serving import make_server
pytestmark=pytest.mark.e2e

@pytest.mark.parametrize('operation',['eliminar_padre','eliminar_hijo'])
def test_parent_initial_state_has_no_future_scopes_on_load_and_rewind(operation):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync() as p:
   browser=p.chromium.launch();context=browser.new_context();page=context.new_page();posts=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
   assert context.request.post(base+'/sequential/sublist/operate',data={'operation':'insertar_padre','payload':{'parent':7}}).json()['success']
   assert context.request.post(base+'/sequential/sublist/operate',data={'operation':'insertar_hijo','payload':{'parent':7,'child':3}}).json()['success']
   page.goto(base+'/sequential/sublist');page.select_option('#operation-select',operation);page.locator('[name="parent"]').fill('7')
   if operation=='eliminar_hijo':page.locator('[name="child"]').fill('3')
   page.click('#seq-step-mode')
   with page.expect_response(lambda r:r.url.endswith('/sublist/operate') and r.request.method=='POST') as response:page.click('#seq-sim-execute')
   assert response.value.json()['success'];page.wait_for_function("()=>document.querySelector('#seq-sim-counter').textContent.startsWith('Paso: 0/')")
   for view in ['current','linked']:
    page.click('#stack-view-'+view)
    for phase in ['load','rewind']:
     if phase=='rewind':
      page.click('#seq-sim-step');page.click('#seq-sim-step');page.click('#seq-sim-prev');page.click('#seq-sim-prev')
     assert page.locator('[data-sublist-frame]').count()==0
     assert page.locator('#seq-variable-view [data-seq-variable]').count()==0,phase
     assert 'ninguna instrucción ejecutada' in page.locator('#seq-pedagogy-summary').inner_text()
   assert len(posts)==1;browser.close()
 finally:server.shutdown();thread.join(timeout=5)
