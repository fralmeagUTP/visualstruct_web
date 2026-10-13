"""Both views and replay: visible parent removal, exact C heap and scoped aliases."""
import json,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
from test_audit_sublist_insertions_native import sublist_native_review,insertion_identity_map
from test_audit_sublist_child_source_e2e import values
pytestmark=pytest.mark.e2e

def test_insertions_both_views_replay_scopes_initialization_highlight_console(tmp_path,sublist_native_review):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[];errors=[]
 try:
  with sync() as p:
   browser=p.chromium.launch()
   for case in [0,17,1,2,3,18]:
    meta=sublist_native_review['cases'][case];context=browser.new_context(viewport={'width':1366,'height':1000});page=context.new_page();posts=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
    for parent,children in meta['seed']:
     assert context.request.post(base+'/sequential/sublist/operate',data={'operation':'insertar_padre','payload':{'parent':parent}}).json()['success']
     for child in children:assert context.request.post(base+'/sequential/sublist/operate',data={'operation':'insertar_hijo','payload':{'parent':parent,'child':child}}).json()['success']
    page.goto(base+'/sequential/sublist',wait_until='networkidle');page.evaluate('''()=>{const old=renderVisualState;renderVisualState=function(...args){window.auditState=structuredClone(args[1]);return old(...args);};}''');page.locator('.seq-understand button').filter(has_text='Mostrar').click();assert page.locator('#seq-variable-view').is_visible();page.select_option('#operation-select',meta['operation']);
    form_payload={'parent':meta['payload']['parent']}
    if meta['operation']=='insertar_hijo':form_payload['child']=meta['payload']['child']
    for name,value in form_payload.items():page.locator(f'[name="{name}"]').fill(str(value))
    page.click('#seq-step-mode')
    with page.expect_response(lambda r:r.url.endswith('/sublist/operate') and r.request.method=='POST') as response:page.click('#seq-sim-execute')
    data=response.value.json();count=len(posts)
    if not data['success']:
     assert case in [3,18]
     page.wait_for_function("()=>!document.querySelector('#seq-sim-execute').disabled")
     assert page.locator('#seq-sim-step').is_disabled() and page.locator('#seq-sim-prev').is_disabled()
     assert len(posts)==count
     rows.append({'case':case,'view':'failure','direction':'none','index':None,'native_compared':False,'failure_preserved':True})
     context.close();print('Insertion rejected without added replay',case,flush=True);continue
    steps=data['execution_trace']['steps']
    native_rows=[r for r in sublist_native_review['rows'] if r['native']['case']==case];mapping=insertion_identity_map(native_rows);oracle={};used=set()
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
       heap=page.locator('[data-sublist-node]').evaluate_all("xs=>xs.map(x=>({id:x.dataset.sublistNode,kind:x.dataset.sublistKind,status:x.dataset.sublistStatus,value:x.dataset.sublistValue==='sin inicializar'?'sin inicializar':Number(x.dataset.sublistValue),next:x.dataset.sublistNext,...(x.dataset.sublistKind==='parent'?{sub:x.dataset.sublistSub}:{})}))")
       assert sorted(heap,key=lambda n:n['id'])==sorted(state['heap_nodes'],key=lambda n:n['id'])
       expected_locals=[{'scope':f['function'],'name':name,'target':str(target),'type':'int' if name=='usados' else 'const Sublista *' if f['function']=='sublista_copiar_hijos' else 'Sublista *' if f['function'] in {'destruir_hijos','crear_hijo','sublista_insertar_hijo_final'} else 'Nodo *'} for f in state['sublist_frames'] for name,target in f['locals'].items()]
       locals_ui=page.locator('[data-sublist-scoped-local]').evaluate_all("xs=>xs.map(x=>({scope:x.dataset.sublistLocalScope,name:x.dataset.sublistScopedLocal,target:x.dataset.sublistLocalTarget,type:x.dataset.sublistLocalType}))")
       assert locals_ui==expected_locals
       assert page.locator('[data-sublist-frame]').evaluate_all('xs=>xs.map(x=>x.dataset.sublistFrame)')==[f['function'] for f in state['sublist_frames']]
       assert page.locator('[data-sublist-head]').get_attribute('data-sublist-head')==state['head']
       dereference=page.locator('[data-sublist-owner]')
       if state.get('owner_parent'):
        assert dereference.get_attribute('data-sublist-owner')==state['owner_parent'];assert dereference.get_attribute('data-sublist-child-root')==state['sub_head']
       else:assert dereference.count()==0
       active_frame=state['sublist_frames'][-1] if state['sublist_frames'] else None
       expected_alias={name:target for name,target in {**active_frame['parameters'],**active_frame['locals']}.items() if name in {'lista','padre','actual','anterior','next','lista_hijos','destino','nuevo'}} if active_frame else {}
       aliases=page.locator('[data-sublist-pointer]').evaluate_all("xs=>Object.fromEntries(xs.map(x=>[x.dataset.sublistPointer,x.querySelector('code').textContent]))")
       assert aliases==expected_alias
       if meta['operation']=='hijos_de':
        assert page.locator('[data-sublist-buffer-capacity]').get_attribute('data-sublist-buffer-capacity')=='1024'
        copied=page.locator('[data-sublist-buffer-index]').evaluate_all("xs=>xs.map(x=>({index:Number(x.dataset.sublistBufferIndex),value:Number(x.dataset.sublistBufferValue)}))")
        assert copied==[{'index':i,'value':v} for i,v in enumerate(state['buffer_values'])]
        if index in oracle:
         native=oracle[index]['native']
         # Return/call completion changes scopes but never adds a write.
         assert copied==native['writes']
       if index<0:
        assert page.locator('#seq-variable-view [data-seq-variable]').count()==0
        assert 'ninguna instrucción ejecutada' in page.locator('#seq-pedagogy-summary').inner_text()
       if index>=0:
        if meta['operation']=='hijos_de' and steps[index]['line_text'].strip()=='destino[usados] = actual->nro;':
         assert 'Copia' in page.locator('#seq-pedagogy-summary').inner_text() and 'link' not in page.locator('#seq-pedagogy-summary').inner_text()
        ped=steps[index]['pedagogy'];shown=page.locator('#seq-variable-view [data-seq-variable]').evaluate_all("xs=>xs.map(x=>({scope:x.dataset.seqVariableScope,name:x.dataset.seqVariable,type:x.dataset.seqVariableType,value:x.querySelector('[data-seq-variable-value]').textContent.replace(/ Δ$/, '')}))")
        expected=[{'scope':v['scope'],'name':v['name'],'type':v['type'],'value':'NULL' if v['value'] is None else str(v['value'])} for v in ped['variables']];assert shown==expected
        active=page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').evaluate_all('xs=>xs.map(x=>Number(x.dataset.line))');assert steps[index]['line_index'] in active
       assert not page.locator('#seq-printf-console .console-line:not(.muted)').all_text_contents()
       if view=='linked':
        rendered=page.locator('.stack-sublist-parent').evaluate_all("xs=>xs.map(x=>({parent:Number(x.querySelector('.stack-sublist-parent-node .stack-linked-field strong').textContent),children:[...x.querySelectorAll('.stack-sublist-child .stack-linked-field:not(.stack-linked-next) strong')].map(y=>Number(y.textContent))}))");assert rendered==actual
       else:assert page.locator('.viz-svg-node-text').all_text_contents()==[str(v) for x in actual for v in [x['parent'],*x['children']]]
       if case in [0,1] and direction=='forward' and index>=0 and (steps[index]['line_text'].strip() in {'return nuevo;','nuevo->nro = valor;','*lista = nuevo;','padre->sub = nuevo;'}):
        page.screenshot(path=str(tmp_path/f'sublist-insertions-{case}-{view}-{index}.png'),full_page=True)
       rows.append({'case':case,'view':view,'direction':direction,'index':index,'native_compared':index in oracle})
     page.click('#seq-step-mode');assert page.evaluate('window.auditState.items')==data['visual_state']['items'];page.click('#seq-step-mode')
    assert len(posts)==count;context.close();print('Insertions browser case verified',case,flush=True)
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 assert not errors
 (tmp_path/'sublist-insertions-browser.json').write_text(json.dumps({'rows':rows,'errors':errors,'extra_replay_posts':0,'cases':[0,17,1,2,3,18]},indent=2),encoding='utf-8')
