"""Both views and replay: visible parent removal, exact C heap and scoped aliases."""
import json,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
from test_audit_sublist_child_source_native import sublist_native_review,sublist_identity_map
from test_audit_sublist_child_source_e2e import values
pytestmark=pytest.mark.e2e

def test_parent_removal_both_views_replay_scopes_types_highlight_console(tmp_path,sublist_native_review):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[];errors=[]
 try:
  with sync() as p:
   browser=p.chromium.launch()
   for case in [4,5,6,7,19,23]:
    meta=sublist_native_review['cases'][case];context=browser.new_context(viewport={'width':1366,'height':1000});page=context.new_page();posts=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
    for parent,children in meta['seed']:
     assert context.request.post(base+'/sequential/sublist/operate',data={'operation':'insertar_padre','payload':{'parent':parent}}).json()['success']
     for child in children:assert context.request.post(base+'/sequential/sublist/operate',data={'operation':'insertar_hijo','payload':{'parent':parent,'child':child}}).json()['success']
    page.goto(base+'/sequential/sublist',wait_until='networkidle');page.evaluate('''()=>{const old=renderVisualState;renderVisualState=function(...args){window.auditState=structuredClone(args[1]);return old(...args);};}''');page.locator('.seq-understand button').filter(has_text='Mostrar').click();assert page.locator('#seq-variable-view').is_visible();page.select_option('#operation-select','eliminar_padre');page.locator('[name="parent"]').fill(str(meta['payload']['parent']));page.click('#seq-step-mode')
    with page.expect_response(lambda r:r.url.endswith('/sublist/operate') and r.request.method=='POST') as response:page.click('#seq-sim-execute')
    data=response.value.json();assert data['success'];steps=data['execution_trace']['steps'];count=len(posts)
    native_rows=[r for r in sublist_native_review['rows'] if r['native']['case']==case];mapping=sublist_identity_map(native_rows);oracle={};used=set()
    for native in native_rows:
     for index,step in enumerate(steps):
      if index not in used and step['line_index']==native['step']['line_index']:
       used.add(index);oracle[index]=native;break
    assert len(oracle)==len(native_rows)
    for view in ['current','linked']:
     page.click('#stack-view-'+view)
     for direction,selector,indices in [('forward','#seq-sim-step',range(len(steps))),('backward','#seq-sim-prev',range(len(steps)-2,-2,-1))]:
      for index in indices:
       assert page.locator(selector).is_enabled();page.locator(selector).evaluate("button=>button.click()");page.wait_for_function("n=>document.querySelector('#seq-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
       state=page.evaluate('window.auditState');actual=[{'parent':x['parent'],'children':x['children']} for x in state['items']]
       canonical=steps[index]['pedagogy']['memory_state'] if index>=0 else steps[0]['state_snapshot'];assert state==canonical
       if index in oracle:assert actual==values(oracle[index]['native'])
       heap=page.locator('[data-sublist-node]').evaluate_all("xs=>xs.map(x=>({id:x.dataset.sublistNode,kind:x.dataset.sublistKind,status:x.dataset.sublistStatus,value:Number(x.dataset.sublistValue),next:x.dataset.sublistNext,...(x.dataset.sublistKind==='parent'?{sub:x.dataset.sublistSub}:{})}))")
       assert sorted(heap,key=lambda n:n['id'])==sorted(state['heap_nodes'],key=lambda n:n['id'])
       expected_locals=[{'scope':f['function'],'name':name,'target':target,'type':'Sublista *' if f['function']=='destruir_hijos' else 'Nodo *'} for f in state['sublist_frames'] for name,target in f['locals'].items()]
       locals_ui=page.locator('[data-sublist-scoped-local]').evaluate_all("xs=>xs.map(x=>({scope:x.dataset.sublistLocalScope,name:x.dataset.sublistScopedLocal,target:x.dataset.sublistLocalTarget,type:x.dataset.sublistLocalType}))")
       assert locals_ui==expected_locals
       assert page.locator('[data-sublist-frame]').evaluate_all('xs=>xs.map(x=>x.dataset.sublistFrame)')==[f['function'] for f in state['sublist_frames']]
       assert page.locator('[data-sublist-head]').get_attribute('data-sublist-head')==state['head']
       dereference=page.locator('[data-sublist-owner]')
       if state.get('owner_parent'):
        assert dereference.get_attribute('data-sublist-owner')==state['owner_parent'];assert dereference.get_attribute('data-sublist-child-root')==state['sub_head']
       else:assert dereference.count()==0
       active_frame=state['sublist_frames'][-1] if state['sublist_frames'] else None
       expected_alias={name:target for name,target in {**active_frame['parameters'],**active_frame['locals']}.items() if name in {'lista','actual','anterior','next','lista_hijos'}} if active_frame else {}
       aliases=page.locator('[data-sublist-pointer]').evaluate_all("xs=>Object.fromEntries(xs.map(x=>[x.dataset.sublistPointer,x.querySelector('code').textContent]))")
       assert aliases==expected_alias
       if index<0:
        assert page.locator('#seq-variable-view [data-seq-variable]').count()==0
        assert 'ninguna instrucción ejecutada' in page.locator('#seq-pedagogy-summary').inner_text()
       if index>=0:
        ped=steps[index]['pedagogy'];shown=page.locator('#seq-variable-view [data-seq-variable]').evaluate_all("xs=>xs.map(x=>({scope:x.dataset.seqVariableScope,name:x.dataset.seqVariable,type:x.dataset.seqVariableType,value:x.querySelector('[data-seq-variable-value]').textContent.replace(/ Δ$/, '')}))")
        expected=[{'scope':v['scope'],'name':v['name'],'type':v['type'],'value':'NULL' if v['value'] is None else str(v['value'])} for v in ped['variables']];assert shown==expected
        active=page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').evaluate_all('xs=>xs.map(x=>Number(x.dataset.line))');assert steps[index]['line_index'] in active
       assert not page.locator('#seq-printf-console .console-line:not(.muted)').all_text_contents()
       if view=='linked':
        rendered=page.locator('.stack-sublist-parent').evaluate_all("xs=>xs.map(x=>({parent:Number(x.querySelector('.stack-sublist-parent-node .stack-linked-field strong').textContent),children:[...x.querySelectorAll('.stack-sublist-child .stack-linked-field:not(.stack-linked-next) strong')].map(y=>Number(y.textContent))}))");assert rendered==actual
       else:assert page.locator('.viz-svg-node-text').all_text_contents()==[str(v) for x in actual for v in [x['parent'],*x['children']]]
       if case==4 and direction=='forward' and index>=0 and (steps[index]['line_text'].strip()=='*lista = actual->sgte;' or steps[index]['line_text'].strip()=='free(actual);'):
        page.screenshot(path=str(tmp_path/f'sublist-parent-{view}-{index}.png'),full_page=True)
       rows.append({'case':case,'view':view,'direction':direction,'index':index,'native_compared':index in oracle})
     page.click('#seq-step-mode');assert page.evaluate('window.auditState.items')==data['visual_state']['items'];page.click('#seq-step-mode')
    assert len(posts)==count;context.close();print('Parent browser case verified',case,flush=True)
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 assert not errors
 (tmp_path/'sublist-parent-browser.json').write_text(json.dumps({'rows':rows,'errors':errors,'extra_replay_posts':0,'cases':[4,5,6,7,19,23]},indent=2),encoding='utf-8')
