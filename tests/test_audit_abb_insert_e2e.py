"""Current ABB tree and individual reservations/scopes, forward/back without POST."""
import json,threading,re,subprocess,shutil
from pathlib import Path
import pytest
from app import create_app
from werkzeug.serving import make_server
from test_audit_abb_insert_native import abb_insert_native_review,identities,match_events
pytestmark=pytest.mark.e2e

def test_abb_insert_current_tree_heap_scopes_replay_and_displayed_caller(tmp_path,abb_insert_native_review):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[];errors=[];compiled=[]
 try:
  with sync() as p:
   browser=p.chromium.launch()
   for case in range(6):
    meta=abb_insert_native_review['cases'][case];context=browser.new_context(viewport={'width':1366,'height':1000});page=context.new_page();posts=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
    for value in meta['seed']:assert context.request.post(base+'/hierarchical/abb/operate',data={'operation':'insertar','payload':{'value':value}}).json()['success']
    page.goto(base+'/hierarchical/abb',wait_until='networkidle');assert page.locator('#operation-select option').count()==12
    page.evaluate('''()=>{const old=renderHierState;renderHierState=function(...args){window.auditState=structuredClone(args[1]);return old(...args);};}''')
    page.locator('#hier-understand-toggle').click();assert page.locator('#hier-variables-view').is_visible()
    page.select_option('#operation-select','insertar');page.locator('[name="value"]').fill(str(meta['payload']['value']));page.click('#hier-step-mode')
    with page.expect_response(lambda r:r.url.endswith('/abb/operate') and r.request.method=='POST') as response:page.click('#hier-sim-play')
    data=response.value.json();count=len(posts)
    if not data['success']:
     assert case==4 and data['visual_state']==meta['trace']['final_state']
     # Rejected operations retain their explanatory trace, never a successful insertion.
     page.wait_for_function("()=>!document.querySelector('#hier-sim-play').disabled")
     rejected=data['execution_trace']['steps'];assert rejected
     for step in rejected:assert step['state_snapshot']==data['visual_state'] and step['state_after']==data['visual_state']
     for index in range(len(rejected)):
      assert page.locator('#hier-sim-step').is_enabled();page.locator('#hier-sim-step').evaluate('b=>b.click()');page.wait_for_function("n=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
     assert page.locator('#hier-sim-step').is_disabled()
     for index in range(len(rejected)-2,-2,-1):
      assert page.locator('#hier-sim-prev').is_enabled();page.locator('#hier-sim-prev').evaluate('b=>b.click()');page.wait_for_function("n=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
     assert page.locator('#hier-sim-prev').is_disabled();assert len(posts)==count;rows.append({'case':case,'failure_preserved':True,'rejected_trace_replayed':len(rejected)});context.close();print('ABB duplicate UI rejection preserved',flush=True);continue
    trace=data['execution_trace'];steps=trace['steps'];events=[{**r['native'],'source_line':r['source_line']} for r in abb_insert_native_review['rows'] if r['native']['case']==case];events.append(meta['native_endpoint']);mapping=identities(events);oracle={s['step_index']:e for e,s in match_events(trace,events)}
    for direction,selector,indices in [('forward','#hier-sim-step',range(len(steps))),('backward','#hier-sim-prev',range(len(steps)-2,-2,-1))]:
     for index in indices:
      assert page.locator(selector).is_enabled();page.locator(selector).evaluate('b=>b.click()');page.wait_for_function("n=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
      state=page.evaluate('window.auditState');expected=steps[index]['pedagogy']['memory_state'] if index>=0 else steps[0]['state_snapshot'];assert state==expected
      actual_heap=page.locator('[data-abb-node]').evaluate_all("xs=>xs.map(x=>({id:x.dataset.abbNode,value:x.dataset.abbValue==='sin inicializar'?'sin inicializar':Number(x.dataset.abbValue),left:x.dataset.abbLeft,right:x.dataset.abbRight,status:x.dataset.abbStatus}))")
      assert actual_heap==state['heap_nodes']
      assert page.locator('[data-abb-head]').get_attribute('data-abb-head')==state['head']
      assert page.locator('[data-abb-frame]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.abbFrame,depth:Number(x.dataset.abbDepth)}))')==[{'id':f['id'],'depth':f['depth']} for f in state['tree_frames']]
      expected_alias=[{'frame':f['id'],'name':name,'type':'int' if name=='valor' else 'ABBNodo *','target':str(target)} for f in state['tree_frames'] for name,target in {**f['parameters'],**f['locals']}.items()]
      shown=page.locator('[data-abb-alias]').evaluate_all('xs=>xs.map(x=>({frame:x.dataset.abbAliasFrame,name:x.dataset.abbAlias,type:x.dataset.abbAliasType,target:x.dataset.abbAliasTarget}))');assert shown==expected_alias
      def values(root):return [] if root is None else [str(root['value']),*values(root['right']),*values(root['left'])]
      # Existing SVG flattens right first; compare complete multiset of visible values.
      assert sorted(page.locator('.viz-tree-text').all_text_contents())==sorted(values(state['root']))
      assert page.locator('#hier-printf-console').inner_text().strip() in {'','Sin salida printf en esta ruta.','(sin salida printf en esta ruta)'}
      if index<0:
       assert page.locator('#hier-variables-view tbody tr').count()==0;assert page.locator('[data-abb-frame]').count()==0;assert page.locator('[data-abb-caller]').count()==0;assert 'Ninguna instruccion ejecutada' in page.locator('#hier-pedagogy-summary').inner_text()
      else:
       step=steps[index];ped=step['pedagogy'];active=page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').evaluate_all('xs=>xs.map(x=>Number(x.dataset.line))');assert step['line_index'] in active
       if index in oracle:
        event=oracle[index];post=state
        if event['phase'] in {'after','enter','condition','call','caller'}:
         # Conditions/call entries do not mutate; entering an invocation is observed after parameter introduction.
         assert post['head']==mapping[event['root']]
         if event['phase']!='call':assert len(post['tree_frames'])==len(event['frames'])
       if case in [0,1,5] and direction=='forward' and ('malloc' in step['line_text'] or step['pedagogy']['instruction_event']['phase'] in {'link','caller'}):page.screenshot(path=str(tmp_path/f'abb-insert-{case}-{index}.png'),full_page=True)
      rows.append({'case':case,'direction':direction,'index':index,'native_compared':index in oracle,'head':state['head'],'heap':actual_heap,'frames':state['tree_frames']})
    assert len(posts)==count
    # Compile the actual displayed caller against the unchanged downloaded C/H.
    gcc=shutil.which('gcc');assert gcc
    for kind,suffix in [('source','c'),('header','h')]:
     response=context.request.get(base+'/help/source/abb/'+kind);assert response.status==200;(tmp_path/('tad_abb.'+suffix)).write_bytes(response.body())
    caller=trace['source_code'].split('void ejecutar_insercion',1)[1];caller='void ejecutar_insercion'+caller
    seed=''.join('root=abb_insertar(root,'+str(v)+');' for v in meta['seed']);main='#include "tad_abb.h"\n#include <stdio.h>\n'+caller+'\nint main(void){ABBNodo*root=NULL;'+seed+'ejecutar_insercion(&root);abb_inorden(root);abb_liberarArbol(root);return 0;}'
    source=tmp_path/f'main-{case}.c';source.write_text(main,encoding='utf-8');exe=tmp_path/'caller.exe';build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'tad_abb.c'),str(source),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr;run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=5);assert run.returncode==0;assert [int(v) for v in run.stdout.split()]==data['visual_state']['traversals']['inorden'];compiled.append({'case':case,'stdout':run.stdout,'caller':caller});context.close();print('ABB insertion browser/native caller verified',case,flush=True)
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 assert not errors
 (tmp_path/'abb-insert-browser-review.json').write_text(json.dumps({'rows':rows,'errors':errors,'extra_replay_posts':0,'compiled_callers':compiled,'representation':'Current tree SVG plus individual live reservation and recursive scope panels, not two invented mode switches.'},indent=2),encoding='utf-8')
