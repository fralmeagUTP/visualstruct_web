"""Both-view replay regression for visible child-removal source/value fidelity.

Allocation identity, full heap and exact alias display remain open audit criteria.
"""
import json,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
from test_audit_sublist_child_source_native import sublist_native_review,sublist_identity_map
pytestmark=pytest.mark.e2e

def values(event):
 nodes={n['id']:n for n in event['nodes']};out=[];p=event['root']
 while p>0:
  n=nodes[p];children=[];h=n['sub']
  while h>0:children.append(nodes[h]['value']);h=nodes[h]['next']
  out.append({'parent':n['value'],'children':children});p=n['next']
 return out

def test_child_removal_native_values_both_views_highlight_and_no_replay_post(tmp_path,sublist_native_review):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[];errors=[]
 try:
  with sync() as p:
   browser=p.chromium.launch()
   for case in [8,9,10,11,12,20]:
    meta=sublist_native_review['cases'][case];context=browser.new_context();page=context.new_page();posts=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
    for parent,children in meta['seed']:
     assert context.request.post(base+'/sequential/sublist/operate',data={'operation':'insertar_padre','payload':{'parent':parent}}).json()['success']
     for child in children:assert context.request.post(base+'/sequential/sublist/operate',data={'operation':'insertar_hijo','payload':{'parent':parent,'child':child}}).json()['success']
    page.goto(base+'/sequential/sublist',wait_until='networkidle');page.evaluate('''()=>{const old=renderVisualState;renderVisualState=function(...args){window.auditState=structuredClone(args[1]);return old(...args);};}''');page.select_option('#operation-select','eliminar_hijo')
    for name,value in meta['payload'].items():page.locator(f'[name="{name}"]').fill(str(value))
    page.click('#seq-step-mode')
    with page.expect_response(lambda r:r.url.endswith('/sublist/operate') and r.request.method=='POST') as response:page.click('#seq-sim-execute')
    data=response.value.json();count=len(posts)
    if not data['success']:
     assert case in [12,20]
     page.wait_for_function("()=>!document.querySelector('#seq-sim-execute').disabled")
     assert page.locator('#seq-sim-step').is_disabled() and page.locator('#seq-sim-prev').is_disabled()
     assert len(posts)==count
     rows.append({'case':case,'view':'failure','direction':'none','index':None,'native_compared':False,'replay_posts':0})
     context.close();continue
    steps=data['execution_trace']['steps']
    oracle={}
    native_rows=[r for r in sublist_native_review['rows'] if r['native']['case']==case]
    mapping=sublist_identity_map(native_rows)
    # Match native observations by each source-line occurrence, not only line text.
    available=list(enumerate(steps));used=set()
    for row in [r for r in sublist_native_review['rows'] if r['native']['case']==case]:
     for index,step in available:
      if index not in used and step['line_index']==row['step']['line_index']:
       used.add(index);oracle[index]=values(row['native']);break
    assert len(oracle)>10
    for view in ['current','linked']:
     page.click('#stack-view-'+view)
     for direction,selector,indices in [('forward','#seq-sim-step',range(len(steps))),('backward','#seq-sim-prev',range(len(steps)-2,-2,-1))]:
      for index in indices:
       page.click(selector);page.wait_for_function("n=>document.querySelector('#seq-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
       state=page.evaluate('window.auditState');actual=[{'parent':x['parent'],'children':x['children']} for x in state['items']]
       if index in oracle:assert actual==oracle[index]
       canonical=steps[index]['pedagogy']['memory_state'] if index>=0 else steps[0]['state_snapshot']
       assert state==canonical
       rendered_heap=page.locator('[data-sublist-node]').evaluate_all("xs=>xs.map(x=>({id:x.dataset.sublistNode,kind:x.dataset.sublistKind,status:x.dataset.sublistStatus,value:Number(x.dataset.sublistValue),next:x.dataset.sublistNext,...(x.dataset.sublistKind==='parent'?{sub:x.dataset.sublistSub}:{})}))")
       assert sorted(rendered_heap,key=lambda n:n['id'])==sorted(state['heap_nodes'],key=lambda n:n['id'])
       active_frame=state['sublist_frames'][-1] if state['sublist_frames'] else None
       expected_alias={k:v for k,v in {**active_frame['parameters'],**active_frame['locals']}.items() if k in {'lista','padre','actual','anterior'}} if active_frame else {}
       shown=page.locator('[data-sublist-pointer]').evaluate_all("xs=>Object.fromEntries(xs.map(x=>[x.dataset.sublistPointer,x.querySelector('code').textContent]))")
       assert shown==expected_alias
       assert page.locator('[data-sublist-frame]').evaluate_all('xs=>xs.map(x=>x.dataset.sublistFrame)')==[f['function'] for f in state['sublist_frames']]
       assert page.locator('[data-sublist-head]').get_attribute('data-sublist-head')==state['head']
       assert page.locator('[data-sublist-freed]').evaluate_all('xs=>xs.map(x=>x.dataset.sublistFreed)')==([state['freed_actual']] if state.get('freed_actual') else [])
       console=page.locator('#seq-printf-console .console-line:not(.muted)').all_text_contents();assert not console
       if case==8 and index>=0 and steps[index]['line_text'].strip() in {'padre->sub = actual->sgte;','free(actual);'} and direction=='forward':page.screenshot(path=str(tmp_path/f'sublist-child-{view}-{index}.png'),full_page=True)
       if view=='linked':
        rendered=page.locator('.stack-sublist-parent').evaluate_all("xs=>xs.map(x=>({parent:Number(x.querySelector('.stack-sublist-parent-node .stack-linked-field strong').textContent),children:[...x.querySelectorAll('.stack-sublist-child .stack-linked-field:not(.stack-linked-next) strong')].map(y=>Number(y.textContent))}))")
        assert rendered==actual
       else:assert page.locator('.viz-svg-node-text').all_text_contents()==[str(v) for x in actual for v in [x['parent'],*x['children']]]
       active=page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').evaluate_all('xs=>xs.map(x=>Number(x.dataset.line))');assert index<0 or steps[index]['line_index'] in active
       rows.append({'case':case,'view':view,'direction':direction,'index':index,'native_compared':index in oracle})
     page.click('#seq-step-mode');assert page.evaluate('window.auditState.items')==data['visual_state']['items'];page.click('#seq-step-mode')
    assert len(posts)==count;context.close()
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 assert not errors
 (tmp_path/'sublist-child-source-browser.json').write_text(json.dumps({'rows':rows,'errors':errors,'scope':'Full live parent/child heap, stable identity/fields, scopes and aliases, highlight/empty console, both views/replay for four successful cases; two failed-parent cases preserve disabled navigation'},indent=2),encoding='utf-8')

