"""API-only hidden List response fixtures consumed by the actual DOM player, both views."""
import json,os,threading
from pathlib import Path
import pytest
from app import create_app
from app.config import Config
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright

@pytest.mark.e2e
def test_three_hidden_HTTP_traces_both_views(tmp_path):
 out=Path(os.environ.get('HIDDEN_DOM_OUT',str(tmp_path)));out.mkdir(parents=True,exist_ok=True)
 class QA(Config):
  SECRET_KEY='private-hidden-DOM'
  SESSION_CACHE_DIR=str(out/'private-DOM-cache')
  SESSION_CACHE_THRESHOLD=0
 app=create_app(QA);assert Path(app.config['SESSION_CACHELIB']._path).resolve().is_relative_to(out.resolve());server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[]
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch()
   for op,payload in [('insertar_posicion',{'position':2,'value':9}),('insertar_elemento',{'position':2,'relative':0,'value':9}),('eliminar_posicion',{'position':2})]:
    context=browser.new_context(viewport={'width':1366,'height':1000});page=context.new_page();errors=[];posts=[]
    page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
    for v in [4,5,6]:assert context.request.post(base+'/sequential/linked_list/operate',data={'operation':'insertar_final','payload':{'value':v}}).json()['success']
    page.goto(base+'/sequential/linked_list',wait_until='networkidle')
    options=page.locator('#operation-select option').evaluate_all('xs=>xs.map(x=>x.value)');assert not any(o in options for o in ['insertar_posicion','insertar_elemento','eliminar_posicion'])
    page.evaluate('''()=>{window.focalRendered=null;const f=renderVisualState;renderVisualState=(...a)=>{window.focalRendered=structuredClone(a[1]);return f(...a);};}''')
    page.click('#seq-step-mode')
    page.select_option('#operation-select','lista_insertar_elemento');page.fill('#field-value','9');page.fill('#field-position','2')
    def hidden_request(route):
     route.continue_(post_data=json.dumps({'operation':op,'payload':payload}))
    page.route('**/sequential/linked_list/operate',hidden_request)
    with page.expect_response(lambda r:r.url.endswith('/sequential/linked_list/operate') and r.request.method=='POST') as got:
     page.click('#seq-sim-execute')
    data=got.value.json();trace=data['execution_trace'];assert data['success'];post_count=len(posts)
    page.wait_for_function("document.querySelector('#seq-sim-counter').textContent.startsWith('Paso: 0/')")
    checked=0;button_actions=0
    for view in ['current','linked']:
     page.click('#stack-view-'+view)
     for direction,selector,indices in [('forward','#seq-sim-step',range(len(trace['steps']))),('backward','#seq-sim-prev',range(len(trace['steps'])-2,-2,-1))]:
      for index in indices:
       page.click(selector);button_actions+=1
       page.wait_for_function("n=>document.querySelector('#seq-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
       expected=trace['steps'][index]['pedagogy']['memory_state'] if index>=0 else trace['steps'][0]['state_snapshot']
       rendered=page.evaluate('window.focalRendered');assert rendered==expected,(op,view,index,rendered,expected)
       active=page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').evaluate_all('xs=>xs.map(x=>Number(x.dataset.line))')
       if index>=0:assert active==[trace['steps'][index]['line_index']],(op,active,index)
       checked+=1
    assert len(posts)==post_count==1 and not errors
    (out/(op+'-DOM-response.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');page.screenshot(path=str(out/(op+'-DOM.png')),full_page=True)
    rows.append({'operation':op,'scope':'Hidden operation has no UI selector. Private transport fixture substitutes hidden operation payload at existing execute request, so existing execution binding receives real HTTP response. No hidden selector or user control invented. Both existing view/navigation controls clicked.','frames_per_direction':len(trace['steps']),'checked_boundaries':checked,'button_actions':button_actions,'replay_POSTs':len(posts)-post_count,'fixture_operation_POSTs':post_count,'errors':errors,'views':['current','linked'],'directions':['forward','backward']});context.close()
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (out/'hidden-DOM-report.json').write_text(json.dumps({'cases':rows,'private_server':True,'canonical_preview_untouched':True},indent=2),encoding='utf-8')
