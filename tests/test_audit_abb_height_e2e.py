"""ABB traversal tree/reservations/scopes, exact stdout and bidirectional replay."""
import json,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
from test_audit_abb_height_native import abb_height_native_review,height_matches
from test_audit_abb_insert_native import identities
pytestmark=pytest.mark.e2e

def test_height_browser_locals_scopes_numeric_returns_and_replay(tmp_path,abb_height_native_review):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[];errors=[];compiled=[]
 try:
  with sync() as p:
   browser=p.chromium.launch()
   for case in range(5):
    meta=abb_height_native_review['cases'][case];context=browser.new_context(viewport={'width':1366,'height':1000});page=context.new_page();posts=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
    for value in meta['seed']:assert context.request.post(base+'/hierarchical/abb/operate',data={'operation':'insertar','payload':{'value':value}}).json()['success']
    page.goto(base+'/hierarchical/abb',wait_until='networkidle');assert page.locator('#operation-select option').count()==12
    page.evaluate('''()=>{const old=renderHierState;renderHierState=function(...args){window.auditState=structuredClone(args[1]);return old(...args);};}''')
    page.locator('#hier-understand-toggle').click();page.select_option('#operation-select','altura');page.click('#hier-step-mode')
    with page.expect_response(lambda r:r.url.endswith('/abb/operate') and r.request.method=='POST') as response:page.click('#hier-sim-play')
    data=response.value.json();assert data['success'];count=len(posts);trace=data['execution_trace'];steps=trace['steps']
    events=[{**r['native'],'source_line':r['source_line']} for r in abb_height_native_review['rows'] if r['native']['case']==case];events.append(meta['native_endpoint']);oracle={s['step_index']:e for e,s in height_matches(trace,events)};mapping=identities(events)
    for direction,selector,indices in [('forward','#hier-sim-step',range(len(steps))),('backward','#hier-sim-prev',range(len(steps)-2,-2,-1))]:
     for index in indices:
      assert page.locator(selector).is_enabled();page.locator(selector).evaluate('b=>b.click()');page.wait_for_function("n=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
      state=page.evaluate('window.auditState');expected=steps[index]['pedagogy']['memory_state'] if index>=0 else steps[0]['state_snapshot'];assert state==expected
      assert state['root']==data['visual_state']['root'];assert page.locator('#hier-printf-console').text_content()==state['console_stdout']
      heap=page.locator('[data-abb-node]').evaluate_all("xs=>xs.map(x=>({id:x.dataset.abbNode,value:Number(x.dataset.abbValue),left:x.dataset.abbLeft,right:x.dataset.abbRight,status:x.dataset.abbStatus}))");assert heap==state['heap_nodes'];assert page.locator('[data-abb-head]').get_attribute('data-abb-head')==state['head'];assert page.locator('[data-abb-caller]').count()==int(state['caller_frame'] is not None)
      assert page.locator('[data-abb-frame]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.abbFrame,depth:Number(x.dataset.abbDepth)}))')==[{'id':f['id'],'depth':f['depth']} for f in state['tree_frames']]
      aliases=page.locator('[data-abb-alias]').evaluate_all('xs=>xs.map(x=>({frame:x.dataset.abbAliasFrame,name:x.dataset.abbAlias,type:x.dataset.abbAliasType,target:x.dataset.abbAliasTarget}))');assert aliases==[{'frame':f['id'],'name':name,'type':'ABBNodo *' if name=='nodo' else 'int','target':str(target)} for f in state['tree_frames'] for name,target in {**f['parameters'],**f['locals']}.items()]
      def values(root):return [] if root is None else [str(root['value']),*values(root['left']),*values(root['right'])]
      assert sorted(page.locator('.viz-tree-text').all_text_contents())==sorted(values(state['root']))
      ped=steps[index]['pedagogy'] if index>=0 else steps[0]['pedagogy']['initial_frame']
      variables=page.locator('#hier-variables-view tbody tr').evaluate_all('xs=>xs.map(x=>({scope:x.querySelector("small").textContent,previous:x.children[1].textContent,value:x.children[2].textContent}))');assert variables==[{'scope':v['scope'],'previous':str(v['previous']),'value':str(v['value'])} for v in ped['variables']]
      assert page.locator('#hier-stack-view .hier-stack-frame').count()==len(ped['call_stack'])
      assert 'Reconexión del retorno: no' in page.locator('#hier-relations-view').inner_text()
      if index>=0 and ped['instruction_event']['phase'] in {'return','caller_result'}:assert 'terminado (contexto del retorno)' in page.locator('#hier-stack-view .hier-stack-frame').last.inner_text()
      if index>=0:
       active=page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').evaluate_all('xs=>xs.map(x=>Number(x.dataset.line))');assert steps[index]['line_index'] in active
       event=oracle.get(index)
       if event:
        assert state['console_stdout']==bytes.fromhex(event['console_hex']).decode('ascii')
        if event['phase']=='return':assert len(state['tree_frames'])==len(event['frames'])-1
        elif event['phase']!='caller':assert len(state['tree_frames'])==len(event['frames'])
        assert state['head']==mapping[event['root']]
       if ped['instruction_event']['phase']=='caller_result':assert state['wrapper_result']==data['result'] and not state['caller_frame']
      else:assert not variables and not state['tree_frames'] and state['console_stdout']==''
      if case in [3,4] and direction=='forward' and index>=0 and steps[index]['pedagogy']['instruction_event']['phase'] in {'call','return'} and len(state['tree_frames'])>=2:page.screenshot(path=str(tmp_path/f'abb-{meta["operation"]}-{case}-{index}.png'),full_page=True)
      rows.append({'case':case,'operation':meta['operation'],'direction':direction,'index':index,'console_stdout':state['console_stdout'],'frame_ids':[f['id'] for f in state['tree_frames']],'root_unchanged':True})
    assert page.locator('#hier-sim-prev').is_disabled();assert len(posts)==count;assert not page.locator('#hier-step-toggle').is_visible() if page.locator('#hier-step-toggle').count() else True
    # The actual displayed caller compiles against the actual downloaded C/H.
    import shutil,subprocess
    gcc=shutil.which('gcc');assert gcc
    for kind,suffix in [('source','c'),('header','h')]:
     downloaded=context.request.get(base+'/help/source/abb/'+kind);assert downloaded.status==200;(tmp_path/('tad_abb.'+suffix)).write_bytes(downloaded.body())
    caller='int ejecutar_altura'+trace['source_code'].split('int ejecutar_altura',1)[1]
    seed=''.join('root=abb_insertar(root,'+str(value)+');' for value in meta['seed'])
    main='#include "tad_abb.h"\n#include <stdio.h>\n'+caller+'\nint main(void){ABBNodo*root=NULL;'+seed+'int found=ejecutar_altura(root);printf("%d\\n",found);abb_inorden(root);abb_liberarArbol(root);return 0;}'
    source=tmp_path/f'main-height-{case}.c';source.write_text(main,encoding='utf-8');exe=tmp_path/'height-caller.exe';build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'tad_abb.c'),str(source),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
    run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=5);assert run.returncode==0;expected=str(data['result'])+'\n'+''.join(str(value)+' ' for value in data['visual_state']['traversals']['inorden']);assert run.stdout==expected
    compiled.append({'case':case,'caller':caller,'stdout':run.stdout,'expected_height':data['result']});context.close();print('ABB height browser/native caller verified',case,len(steps),flush=True)
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 assert not errors
 (tmp_path/'abb-height-browser-review.json').write_text(json.dumps({'rows':rows,'cases':5,'errors':errors,'extra_replay_posts':0,'compiled_callers':compiled,'representation':'existing tree SVG plus individual heap identity and recursive-scope panels; no new view selector'},indent=2),encoding='utf-8')
