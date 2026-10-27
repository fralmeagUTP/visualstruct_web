"""Small visual regressions of verified Sublista child-removal state."""
import json,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
pytestmark=pytest.mark.e2e

def test_sublist_node_titles_active_function_and_visible_c_line(tmp_path):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[]
 try:
  with sync() as p:
   browser=p.chromium.launch();context=browser.new_context(viewport={'width':1280,'height':1000});page=context.new_page();posts=[];errors=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
   assert context.request.post(base+'/sequential/sublist/operate',data={'operation':'insertar_padre','payload':{'parent':7}}).json()['success']
   for child in [3,3,5]:assert context.request.post(base+'/sequential/sublist/operate',data={'operation':'insertar_hijo','payload':{'parent':7,'child':child}}).json()['success']
   page.goto(base+'/sequential/sublist',wait_until='networkidle');page.select_option('#operation-select','eliminar_hijo');page.fill('#field-parent','7');page.fill('#field-child','3');page.click('#seq-step-mode')
   with page.expect_response(lambda r:r.url.endswith('/sublist/operate') and r.request.method=='POST') as response:page.click('#seq-sim-execute')
   data=response.value.json();assert data['success'];count=len(posts)
   for index,step in enumerate(data['execution_trace']['steps']):
    page.click('#seq-sim-step');page.wait_for_function("n=>document.querySelector('#seq-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
    fn=step['pedagogy']['call_stack'][-1]['function'] if step['pedagogy']['call_stack'] else 'sin función';assert fn in page.locator('#seq-progress-detail').inner_text()
    if step['line_text'].strip() not in {'padre->sub = actual->sgte;','free(actual);'}:continue
    for view in ['current','linked']:
     page.click('#stack-view-'+view)
     for card in page.locator('[data-sublist-node]').all():
      assert card.locator('.stack-linked-node-id').inner_text()==card.get_attribute('data-sublist-node')
      assert card.locator('.stack-linked-node-id').evaluate('el=>el.scrollWidth<=el.clientWidth+1')
     if step['line_text'].strip()=='padre->sub = actual->sgte;':
      assert page.locator('[data-sublist-node="H1.1"]').get_attribute('data-sublist-status')=='detached'
      assert page.locator('[data-sublist-node="H1.1"]').get_attribute('data-sublist-next')=='H1.2'
     else:assert page.locator('[data-sublist-node="H1.1"]').count()==0 and page.locator('[data-sublist-freed="H1.1"]').count()==1
     # Wait for the production smooth scroll; do not infer visibility from an immediate screenshot.
     page.wait_for_function('''index=>{const line=document.querySelector(`#op-pseudocode [data-line="${index}"]`);if(!line)return false;let box=line.parentElement;while(box){const style=getComputedStyle(box);if(box.scrollHeight>box.clientHeight+1&&/(auto|scroll)/.test(style.overflowY)){const l=line.getBoundingClientRect(),b=box.getBoundingClientRect();return l.top>=b.top-2&&l.bottom<=b.bottom+2;}box=box.parentElement;}return true;}''',arg=step['line_index'],timeout=3000)
     page.screenshot(path=str(tmp_path/f'sublist-minor-{view}-{index}.png'),full_page=True);rows.append({'view':view,'step':index,'function':fn,'source_line':step['line_index']})
   assert len(posts)==count and not errors;browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (tmp_path/'sublist-minor-visual-review.json').write_text(json.dumps({'rows':rows,'extra_posts':0},indent=2),encoding='utf-8')
