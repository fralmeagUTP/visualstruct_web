"""Real preview5051 Hash UI forward/back/replay and actual caller downloads."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path.cwd();E=ROOT/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-scope-fix-medium';B=E/'browser';B.mkdir(exist_ok=True)
BASE=ROOT/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-create-insert-baseline-low/native'
INJECT="""localStorage.setItem('didactic-mode','full');let runtime;Object.defineProperty(window,'InterpreterRuntime',{configurable:true,get:()=>runtime,set:v=>{runtime={...v,createTracePlayer:opts=>{const originalRender=opts.renderState;const originalCursor=opts.onCursorChange;const player=v.createTracePlayer({...opts,renderState:(state,step)=>{window.__hashRendered=JSON.parse(JSON.stringify(state));originalRender(state,step);},onCursorChange:event=>{window.__hashCursor=event.cursor;window.__hashTrace=event.trace;originalCursor(event);}});window.__hashPlayer=player;return player;}};}});"""
SNAP="""() => ({state:window.__hashRendered,cursor:window.__hashPlayer.getCursor(),active:Array.from(document.querySelectorAll('#op-pseudocode .sim-active')).map(x=>Array.from(document.querySelectorAll('#op-pseudocode .code-line')).indexOf(x)),visual:document.querySelector('#hash-visual-state').textContent,pointers:document.querySelector('#hash-pointers-view').textContent,memory:document.querySelector('#hash-memory-view').textContent,cost:document.querySelector('#hash-cost-view').textContent,console:document.querySelector('#hash-printf-console').textContent})"""
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True);reports=[]
 for name in ['collision_load_gt_one','update_middle','negative_extremes','node_null_repeat']:
  context=browser.new_context();page=context.new_page();page.add_init_script(INJECT);errors=[];posts=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None);page.goto('http://127.0.0.1:5051/hash/hash_table');page.wait_for_selector('#hash-operation-select');saved = {'responses': [{'operation':'create_table','payload':{'capacity':3}}, {'operation':'insert','payload':{'key':1,'value':10,'simulate_allocation_failure':True}}, {'operation':'insert','payload':{'key':1,'value':10,'simulate_allocation_failure':False}}, {'operation':'insert','payload':{'key':1,'value':10,'simulate_allocation_failure':False}}]} if name=='node_null_repeat' else json.loads((BASE/(name+'.json')).read_text(encoding='utf-8'));restorations=0;forward_checks=0
  for item in saved['responses']:
   page.select_option('#hash-operation-select',item['operation'])
   for k,v in item['payload'].items():
    if k=='simulate_allocation_failure':page.locator('#hash-field-'+k).set_checked(v)
    else:page.fill('#hash-field-'+k,str(v))
   with page.expect_response(lambda r:'/hash/hash_table/operate' in r.url and r.request.method=='POST') as response:page.click('#hash-sim-play')
   data=response.value.json();assert data['success']==(not item['payload'].get('simulate_allocation_failure',False));trace=data['execution_trace'];n=len(trace['steps']);assert page.evaluate('window.__hashPlayer.getTotalSteps()')==n
   post_count=len(posts);page.click('#hash-sim-step');assert page.evaluate('window.__hashPlayer.getCursor()')==-1
   assert page.evaluate('window.__hashRendered')==trace['steps'][0]['state_snapshot'];assert page.locator('#op-pseudocode .sim-active').count()==0
   snapshots=[]
   for i,frame in enumerate(trace['steps']):
    page.evaluate('(i)=>window.__hashPlayer.seek(i)',i);snap=page.evaluate(SNAP);assert snap['state']==frame['state_after'];assert snap['cursor']==i
    if frame['line_index']>=0:assert snap['active']==[frame['line_index']]
    else:assert not snap['active']
    if frame['event_type']=='init_entry':
     assert frame['pedagogy']['variables']['capacidad']==item['payload']['capacity']
     assert frame['pedagogy']['variables']['tabla->capacidad']==0
     assert 'capacidad' in snap['pointers'] and 'Antes de ejecutar' not in snap['pointers']
    if frame['debug']['call_stack']==['th_insertar','th_indice']:
     assert 'th_indice.tabla' in snap['pointers'] and 'const TablaHash *' in snap['pointers']
     assert frame['debug']['variables']['tabla']['value']==frame['debug']['variables']['th_indice.tabla']['value']
    if frame['event_type']=='index_return':assert 'th_indice.tabla' not in snap['pointers']
    snapshots.append(snap);forward_checks+=1
   for i in range(n-2,-1,-1):
    page.click('#hash-sim-prev');assert page.evaluate(SNAP)==snapshots[i];restorations+=1
   page.click('#hash-sim-step');assert page.evaluate('window.__hashPlayer.getCursor()')==n-1
   page.click('#hash-sim-step');assert page.evaluate('window.__hashPlayer.getCursor()')==-1
   page.click('#hash-sim-next');assert page.evaluate(SNAP)==snapshots[0]
   page.evaluate('window.__hashPlayer.seek(window.__hashPlayer.getTotalSteps()-1)');assert page.evaluate(SNAP)==snapshots[-1];assert len(posts)==post_count
   page.click('#hash-sim-step')
  directory=B/name;directory.mkdir(exist_ok=True);r=page.request.get('http://127.0.0.1:5051/help/source/hash_table/main');assert r.status==200;(directory/'main.c').write_bytes(r.body());
  if name=='node_null_repeat':assert r.body().count(b'th_insertar(&tabla, 1, 10)')==2
  page.screenshot(path=str(directory/'final.png'),full_page=True)
  last=page.evaluate('window.__hashTrace');before_reload=len(posts);page.reload();page.wait_for_selector('#hash-operation-select');assert page.evaluate('window.__hashTrace')==last;assert page.evaluate('window.__hashPlayer.getCursor()')==len(last['steps'])-1;page.click('#hash-sim-step');page.click('#hash-sim-next');assert len(posts)==before_reload
  reports.append({'case':name,'operations':len(saved['responses']),'forward_frames':forward_checks,'backward_restorations':restorations,'extra_navigation_POSTs':0,'reload_trace_equal':True,'sections':page.locator('.hash-stage').count(),'page_errors':errors,'download_main_status':r.status});assert not errors;context.close()
 browser.close();(B/'report.json').write_text(json.dumps(reports,indent=2),encoding='utf-8');print(json.dumps(reports))
