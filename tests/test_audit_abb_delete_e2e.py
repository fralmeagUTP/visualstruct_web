"""Existing tree/heap views and exact caller, bidirectional replay without POST."""
import json,threading,subprocess,shutil
from pathlib import Path
import pytest
from app import create_app
from werkzeug.serving import make_server
from test_audit_abb_delete_native import delete_baselines,events_for,matches
pytestmark=pytest.mark.e2e

@pytest.mark.parametrize('family,case',[(0,i) for i in range(11)]+[(1,i) for i in range(2)])
def test_delete_browser_native_views_replay_and_actual_caller(tmp_path,delete_baselines,family,case):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright
 meta=delete_baselines[family]['cases'][case];errors=[];rows=[]
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync() as p:
   browser=p.chromium.launch();context=browser.new_context(viewport={'width':1366,'height':1000});page=context.new_page();posts=[];page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
   for v in meta['seed']:assert context.request.post(base+'/hierarchical/abb/operate',data={'operation':'insertar','payload':{'value':v}}).json()['success']
   page.goto(base+'/hierarchical/abb',wait_until='networkidle');assert page.locator('#operation-select option').count()==12
   page.evaluate('''()=>{const old=renderHierState;renderHierState=function(...args){window.auditState=structuredClone(args[1]);return old(...args);};}''')
   page.locator('#hier-understand-toggle').click();page.select_option('#operation-select','eliminar');page.locator('[name="value"]').fill(str(meta['payload']['value']));page.click('#hier-step-mode')
   with page.expect_response(lambda resp:resp.url.endswith('/abb/operate') and resp.request.method=='POST') as pending:page.click('#hier-sim-play')
   actual=pending.value.json();assert actual['success']==meta['api_success'];count=len(posts);trace=actual['execution_trace'];compiled={}
   if meta['api_success']:
    steps=trace['steps'];pairing=matches(trace,events_for(delete_baselines[family],case));oracle={s['step_index']:e for e,s in pairing}
    for direction,selector,indices in [('forward','#hier-sim-step',range(len(steps))),('backward','#hier-sim-prev',range(len(steps)-2,-2,-1))]:
     for index in indices:
      assert page.locator(selector).is_enabled();page.locator(selector).evaluate('b=>b.click()');page.wait_for_function("n=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
      state=page.evaluate('window.auditState');expected=steps[index]['pedagogy']['memory_state'] if index>=0 else steps[0]['state_snapshot'];assert state==expected
      assert page.locator('#hier-printf-console').text_content()==state['console_stdout']==''
      assert page.locator('[data-abb-head]').get_attribute('data-abb-head')==state['head']
      heap=page.locator('[data-abb-node]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.abbNode,value:Number(x.dataset.abbValue),left:x.dataset.abbLeft,right:x.dataset.abbRight,status:x.dataset.abbStatus}))');assert heap==state['heap_nodes']
      assert page.locator('[data-abb-frame]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.abbFrame,depth:Number(x.dataset.abbDepth)}))')==[{'id':f['id'],'depth':f['depth']} for f in state['tree_frames']]
      aliases=page.locator('[data-abb-alias]').evaluate_all('xs=>xs.map(x=>({frame:x.dataset.abbAliasFrame,name:x.dataset.abbAlias,type:x.dataset.abbAliasType,target:x.dataset.abbAliasTarget}))');assert aliases==[{'frame':f['id'],'name':name,'type':'int' if name=='valor' else 'ABBNodo *','target':str(v)} for f in state['tree_frames'] for name,v in {**f['parameters'],**f['locals']}.items()]
      def values(root):return [] if root is None else [str(root['value']),*values(root['left']),*values(root['right'])]
      assert sorted(page.locator('.viz-tree-text').all_text_contents())==sorted(values(state['root']))
      ped=steps[index]['pedagogy'] if index>=0 else steps[0]['pedagogy']['initial_frame']
      assert page.locator('#hier-variables-view tbody tr').evaluate_all('xs=>xs.map(x=>({scope:x.querySelector("small").textContent,previous:x.children[1].textContent,value:x.children[2].textContent}))')==[{'scope':v['scope'],'previous':str(v['previous']),'value':str(v['value'])} for v in ped['variables']]
      assert page.locator('#hier-stack-view .hier-stack-frame').count()==len(ped['call_stack'])
      assert 'Vida de reservas y publicaciones pendientes' in page.locator('#hier-invariant-view').inner_text()
      if ped['call_stack']:assert 'raíz local: '+ped['call_stack'][0]['local_root_address'] in page.locator('#hier-stack-view .hier-stack-frame').first.inner_text()
      assert page.locator('[data-abb-retired-node]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.abbRetiredNode,value:Number(x.dataset.abbRetiredValue)}))')==[{'id':n['id'],'value':n['value']} for n in state['freed_nodes']]
      assert page.locator('[data-abb-unusable-count]').get_attribute('data-abb-unusable-count')==str(len(ped['memory']['unusable_reference_records']))
      if index>=0:
       assert steps[index]['line_index'] in page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').evaluate_all('xs=>xs.map(x=>Number(x.dataset.line))')
       if index in oracle:assert oracle[index]['phase'] in {'enter','condition','call','after','return','caller'}
       if family==0 and case==8 and direction=='forward' and steps[index]['pedagogy']['instruction_event']['phase']=='free':page.screenshot(path=str(tmp_path/'successor-free.png'),full_page=True)
      rows.append({'direction':direction,'index':index,'phase':ped.get('instruction_event',{}).get('phase'),'live_ids':[n['id'] for n in heap],'head':state['head'],'native_event_matched':index in oracle})
    assert page.locator('#hier-sim-prev').is_disabled()
   else:
    assert not any(s.get('pedagogy',{}).get('memory_state',{}).get('abb_delete_model') for s in trace['steps'])
   assert len(posts)==count
   actual_main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');assert actual_main.count('arbol = abb_eliminar(arbol,')==int(meta['api_success'])
   if meta['api_success']:
    for kind,suffix in [('source','c'),('header','h')]:
     response=context.request.get(base+'/help/source/abb/'+kind);assert response.status==200;(tmp_path/f'tad_abb.{suffix}').write_bytes(response.body())
    native=meta['native_endpoint'];nodes={n['id']:n for n in native['nodes']}
    def asserts(identity,expression='arbol'):
     if not identity:return [f'assert({expression} == NULL);']
     n=nodes[identity];return [f'assert({expression} != NULL);',f'assert(({expression})->valor == {n["value"]});',*asserts(n['left'],f'({expression})->izquierdo'),*asserts(n['right'],f'({expression})->derecho')]
    generated=actual_main.rsplit('    return 0;',1);assert len(generated)==2
    equivalent='int main(void)'+trace['source_code'].split('int main(void)',1)[1];eqparts=equivalent.rsplit('    return 0;',1)
    for name,parts in [('actual-main',generated),('equivalent-main',eqparts)]:
     source=tmp_path/(name+'.c');source.write_text('#include "tad_abb.h"\n#include <stdio.h>\n#include <stddef.h>\n#include <assert.h>\n'+parts[0]+'\n'+'\n'.join(asserts(native['root']))+'\nabb_liberarArbol(arbol);\n    return 0;'+parts[1],encoding='utf-8');exe=source.with_suffix('.exe')
     build=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'tad_abb.c'),str(source),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
     run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=5);assert run.returncode==0,run.stderr
     if name=='equivalent-main':assert run.stdout==''
     compiled[name]={'final_tree_assertions_passed':True,'stdout':run.stdout}
   assert not errors;context.close();browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (tmp_path/'abb-delete-browser-review.json').write_text(json.dumps({'family':family,'case':case,'api_success':meta['api_success'],'rows':rows,'compiled':compiled,'errors':errors,'extra_replay_posts':0,'limits':['Recorded case only; existing SVG and individual heap/scope panels, not a new selector.','Native event semantics compared in targeted native tests; browser renders the same event states.']},ensure_ascii=False,indent=2),encoding='utf-8')
 print('ABB delete replay/current caller verified',family,case,len(rows),flush=True)
