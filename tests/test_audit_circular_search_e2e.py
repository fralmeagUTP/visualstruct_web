"""Circular insertion UI: exact live heap/root/counter snapshots in both views/replay."""
import json,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
pytestmark=pytest.mark.e2e

def test_circular_search_both_views_instruction_heap_alias_output_and_replay(tmp_path):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright
 app=create_app();app.config.update(TESTING=False,SECRET_KEY='circle-audit');server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[];cases=[];errors=[]
 try:
  with sync() as p:
   browser=p.chromium.launch()
   for case,(operation,seed,value) in enumerate([('buscar_posiciones',seed,value) for seed,value in [([],7),([7],7),([7,8,9],8),([7,7,9],7),([7,8,9],99)]]):
    context=browser.new_context(viewport={'width':1366,'height':1000});page=context.new_page();posts=[];page.on('request',lambda request:posts.append(request.url) if request.method=='POST' else None);page.on('pageerror',lambda error:errors.append(str(error)))
    for seed_value in seed:assert context.request.post(base+'/sequential/circular_list/operate',data={'operation':'insertar_final','payload':{'value':seed_value}}).json()['success']
    page.goto(base+'/sequential/circular_list',wait_until='networkidle');assert set(page.locator('#operation-select option').evaluate_all('xs=>xs.map(x=>x.value)'))=={'insertar_inicio','insertar_final','eliminar_inicio','eliminar_primero','buscar_posiciones','invertir','limpiar'}
    page.evaluate('''()=>{window.auditRenderedState=null;const original=renderVisualState;renderVisualState=function(...args){window.auditRenderedState=structuredClone(args[1]);return original(...args);};}''');page.select_option('#operation-select',operation);page.fill('#field-value',str(value));page.click('#seq-step-mode')
    with page.expect_response(lambda r:r.url.endswith('/sequential/circular_list/operate') and r.request.method=='POST') as response:page.click('#seq-sim-execute')
    data=response.value.json();assert data['success'] and data['result']==[i+1 for i,v in enumerate(seed) if v==value];steps=data['execution_trace']['steps'];post_count=len(posts);page.wait_for_function("()=>document.querySelector('#seq-sim-counter').textContent.startsWith('Paso: 0/')")
    for view in ['current','linked']:
     page.click('#stack-view-'+view)
     for direction,selector,indices in [('forward','#seq-sim-step',range(len(steps))),('backward','#seq-sim-prev',range(len(steps)-2,-2,-1))]:
      for index in indices:
       page.click(selector);page.wait_for_function("n=>document.querySelector('#seq-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
       state=page.evaluate('window.auditRenderedState');canonical=steps[index]['state_after'] if index>=0 else steps[0]['state_snapshot'];expected=(steps[index]['pedagogy']['memory_state'] or canonical) if index>=0 else canonical
       assert state==expected;assert state['items']==canonical['items']
       active=page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').evaluate_all('xs=>xs.map(x=>Number(x.dataset.line))');assert index<0 or steps[index]['line_index'] in active
       roots=page.locator('[data-clear-pointer]').evaluate_all("els=>Object.fromEntries(els.map(el=>[el.dataset.clearPointer,el.querySelector('code').textContent]))");assert roots['lista']=='&lc' and roots['cabeza']==state['cabeza'] and roots['cola']==state['cola']
       for name in ['actual']:
        if name in state:assert roots.get(name)==state[name]
        else:assert name not in roots
       nodes=page.locator('[data-clear-node]').evaluate_all("els=>els.map(el=>({id:el.dataset.clearNode,next:el.dataset.clearNext,status:el.dataset.clearStatus,value:el.querySelector('.stack-linked-field strong').textContent==='sin inicializar'?'sin inicializar':Number(el.querySelector('.stack-linked-field strong').textContent)}))")
       assert sorted(nodes,key=lambda x:x['id'])==sorted(state['heap_nodes'],key=lambda x:x['id']);assert page.locator('[data-clear-node][data-clear-status=linked]').evaluate_all('xs=>xs.map(x=>x.dataset.clearNode)')==state['node_ids']
       freed=page.locator('[data-clear-freed]').evaluate_all('xs=>xs.map(x=>x.dataset.clearFreed)');assert freed==([state['freed_actual']] if state.get('freed_actual') else [])
       assert json.loads(page.locator('[data-circular-positions]').get_attribute('data-circular-positions'))==state['search_positions']
       counts=page.locator('[data-circular-count]').evaluate("el=>({quantity:Number(el.dataset.circularCount),reachable:Number(el.dataset.circularReachable)})");assert counts=={'quantity':state['cantidad'],'reachable':len(state['node_ids'])}
       console=page.locator('#seq-printf-console .console-line:not(.muted)').all_text_contents();assert [x.strip() for x in console]==[x.strip() for step in steps[:index+1] for x in step.get('console',[]) if x.strip()] if index>=0 else not console
       rows.append({'case':case,'operation':operation,'seed':seed,'value':value,'view':view,'direction':direction,'index':index,'roots':roots,'nodes':nodes,'counts':counts,'state_pass':state==expected,'highlight_pass':index<0 or steps[index]['line_index'] in active})
       if seed==[7,7,9] and index>=0 and steps[index]['line_text'].strip()=='destino[encontrados] = pos;' and direction=='forward':page.screenshot(path=str(tmp_path/f'circular-{operation}-{view}-publication.png'),full_page=True)
     page.click('#seq-step-mode');endpoint=page.evaluate('window.auditRenderedState');assert endpoint==steps[-1]['pedagogy']['memory_state'];assert endpoint['items']==data['visual_state']['items'];page.click('#stack-view-'+('linked' if view=='current' else 'current'));assert page.evaluate('window.auditRenderedState')==endpoint;page.click('#stack-view-'+view);page.click('#seq-step-mode');assert page.evaluate('window.auditRenderedState')==steps[0]['state_snapshot']
    assert len(posts)==post_count;cases.append({'case':case,'operation':operation,'seed':seed,'value':value,'steps':len(steps),'operation_posts':post_count,'replay_extra_posts':len(posts)-post_count});context.close()
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 assert not errors
 (tmp_path/'circular-search-browser-review.json').write_text(json.dumps({'scope':'Actual visible circular search method, both views forward/backward and endpoint, exact roots/all allocations/fields/quantity/line/console.','cases':cases,'rows':rows,'page_errors':errors},indent=2),encoding='utf-8');print(json.dumps({'cases':len(cases),'rows':len(rows),'errors':errors}))
