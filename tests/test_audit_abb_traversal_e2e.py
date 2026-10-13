"""ABB traversal tree/reservations/scopes, exact stdout and bidirectional replay."""
import json,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
from test_audit_abb_traversal_native import abb_traversal_native_review,traversal_matches
from test_audit_abb_insert_native import identities
pytestmark=pytest.mark.e2e

def test_traversals_browser_exact_stdout_scopes_highlight_replay(tmp_path,abb_traversal_native_review):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[];errors=[]
 try:
  with sync() as p:
   browser=p.chromium.launch()
   for case in range(9):
    meta=abb_traversal_native_review['cases'][case];context=browser.new_context(viewport={'width':1366,'height':1000});page=context.new_page();posts=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
    for value in meta['seed']:assert context.request.post(base+'/hierarchical/abb/operate',data={'operation':'insertar','payload':{'value':value}}).json()['success']
    page.goto(base+'/hierarchical/abb',wait_until='networkidle');assert page.locator('#operation-select option').count()==12
    page.evaluate('''()=>{const old=renderHierState;renderHierState=function(...args){window.auditState=structuredClone(args[1]);return old(...args);};}''')
    page.locator('#hier-understand-toggle').click();page.select_option('#operation-select',meta['operation']);page.click('#hier-step-mode')
    with page.expect_response(lambda r:r.url.endswith('/abb/operate') and r.request.method=='POST') as response:page.click('#hier-sim-play')
    data=response.value.json();assert data['success'];count=len(posts);trace=data['execution_trace'];steps=trace['steps']
    events=[{**r['native'],'source_line':r['source_line']} for r in abb_traversal_native_review['rows'] if r['native']['case']==case];events.append(meta['native_endpoint']);oracle={s['step_index']:e for e,s in traversal_matches(trace,events)};mapping=identities(events)
    for direction,selector,indices in [('forward','#hier-sim-step',range(len(steps))),('backward','#hier-sim-prev',range(len(steps)-2,-2,-1))]:
     for index in indices:
      assert page.locator(selector).is_enabled();page.locator(selector).evaluate('b=>b.click()');page.wait_for_function("n=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
      state=page.evaluate('window.auditState');expected=steps[index]['pedagogy']['memory_state'] if index>=0 else steps[0]['state_snapshot'];assert state==expected
      assert state['root']==data['visual_state']['root'];assert page.locator('#hier-printf-console').text_content()==state['console_stdout']
      heap=page.locator('[data-abb-node]').evaluate_all("xs=>xs.map(x=>({id:x.dataset.abbNode,value:Number(x.dataset.abbValue),left:x.dataset.abbLeft,right:x.dataset.abbRight,status:x.dataset.abbStatus}))");assert heap==state['heap_nodes'];assert page.locator('[data-abb-head]').get_attribute('data-abb-head')==state['head'];assert not page.locator('[data-abb-caller]').count()
      assert page.locator('[data-abb-frame]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.abbFrame,depth:Number(x.dataset.abbDepth)}))')==[{'id':f['id'],'depth':f['depth']} for f in state['tree_frames']]
      aliases=page.locator('[data-abb-alias]').evaluate_all('xs=>xs.map(x=>({frame:x.dataset.abbAliasFrame,name:x.dataset.abbAlias,type:x.dataset.abbAliasType,target:x.dataset.abbAliasTarget}))');assert aliases==[{'frame':f['id'],'name':'nodo','type':'ABBNodo *','target':f['parameters']['nodo']} for f in state['tree_frames']]
      def values(root):return [] if root is None else [str(root['value']),*values(root['left']),*values(root['right'])]
      assert sorted(page.locator('.viz-tree-text').all_text_contents())==sorted(values(state['root']))
      ped=steps[index]['pedagogy'] if index>=0 else steps[0]['pedagogy']['initial_frame']
      variables=page.locator('#hier-variables-view tbody tr').evaluate_all('xs=>xs.map(x=>({scope:x.querySelector("small").textContent,previous:x.children[1].textContent,value:x.children[2].textContent}))');assert variables==[{'scope':v['scope'],'previous':str(v['previous']),'value':str(v['value'])} for v in ped['variables']]
      assert page.locator('#hier-stack-view .hier-stack-frame').count()==len(ped['call_stack'])
      if index>=0:
       active=page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').evaluate_all('xs=>xs.map(x=>Number(x.dataset.line))');assert steps[index]['line_index'] in active
       event=oracle[index]
       assert state['console_stdout']==bytes.fromhex(event['console_hex']).decode('ascii')
       if event['phase']=='return':assert len(state['tree_frames'])==len(event['frames'])-1
       elif event['phase']!='caller':assert len(state['tree_frames'])==len(event['frames'])
       assert state['head']==mapping[event['root']]
      else:assert not variables and not state['tree_frames'] and state['console_stdout']==''
      if case in [2,5,8] and direction=='forward' and index>=0 and steps[index]['pedagogy']['instruction_event']['phase']=='printf' and len(state['tree_frames'])>=3:page.screenshot(path=str(tmp_path/f'abb-{meta["operation"]}-{case}-{index}.png'),full_page=True)
      rows.append({'case':case,'operation':meta['operation'],'direction':direction,'index':index,'console_stdout':state['console_stdout'],'frame_ids':[f['id'] for f in state['tree_frames']],'root_unchanged':True})
    assert page.locator('#hier-sim-prev').is_disabled();assert len(posts)==count;assert not page.locator('#hier-step-toggle').is_visible() if page.locator('#hier-step-toggle').count() else True
    context.close();print('ABB traversal browser verified',case,meta['operation'],len(steps),flush=True)
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 assert not errors
 (tmp_path/'abb-traversal-browser-review.json').write_text(json.dumps({'rows':rows,'cases':9,'errors':errors,'extra_replay_posts':0,'representation':'existing tree SVG plus individual heap identity and recursive-scope panels; no new view selector'},indent=2),encoding='utf-8')

def test_traversal_svg_all_nodes_fit_desktop_tablet_and_narrow(tmp_path):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[]
 try:
  with sync() as p:
   browser=p.chromium.launch()
   for operation in ['inorden','preorden','postorden']:
    for width in [1366,768,390]:
     context=browser.new_context(viewport={'width':width,'height':1000});page=context.new_page()
     for value in [10,5,15,3,7,12,18]:assert context.request.post(base+'/hierarchical/abb/operate',data={'operation':'insertar','payload':{'value':value}}).json()['success']
     page.goto(base+'/hierarchical/abb',wait_until='networkidle');page.select_option('#operation-select',operation);page.click('#hier-step-mode')
     with page.expect_response(lambda r:r.url.endswith('/abb/operate') and r.request.method=='POST') as response:page.click('#hier-sim-play')
     assert response.value.json()['success'];page.locator('#hier-sim-step').evaluate('b=>b.click()');page.wait_for_function("()=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: 1/')")
     svg=page.locator('.abb-traversal-canvas .viz-tree-svg');assert svg.is_visible();assert svg.locator('circle').count()==7
     result=svg.evaluate('e=>{const r=e.getBoundingClientRect(),p=e.closest(".abb-traversal-canvas").getBoundingClientRect();return {svg_inside_panel:r.left>=p.left-1&&r.right<=p.right+1,nodes_inside_svg:[...e.querySelectorAll("circle")].every(n=>{const b=n.getBoundingClientRect();return b.left>=r.left-1&&b.right<=r.right+1&&b.top>=r.top-1&&b.bottom<=r.bottom+1}),width:r.width,panel_width:p.width};}')
     assert result['svg_inside_panel'] and result['nodes_inside_svg'],result;assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');rows.append({'operation':operation,'viewport':width,**result})
     if operation=='inorden':page.screenshot(path=str(tmp_path/f'abb-traversal-fit-{width}.png'),full_page=True)
     context.close()
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (tmp_path/'abb-traversal-fit-review.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
