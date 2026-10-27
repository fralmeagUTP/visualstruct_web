"""ABB traversal tree/reservations/scopes, exact stdout and bidirectional replay."""
import json,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
from test_audit_abb_clear_native import abb_clear_native_review,clear_matches,clear_events
from test_audit_abb_insert_native import identities
pytestmark=pytest.mark.e2e

def test_clear_browser_free_alias_root_scopes_replay_and_actual_main(tmp_path,abb_clear_native_review):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[];errors=[];compiled=[]
 try:
  with sync() as p:
   browser=p.chromium.launch()
   for case in range(5):
    meta=abb_clear_native_review['cases'][case];context=browser.new_context(viewport={'width':1366,'height':1000});page=context.new_page();posts=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
    for value in meta['seed']:assert context.request.post(base+'/hierarchical/abb/operate',data={'operation':'insertar','payload':{'value':value}}).json()['success']
    page.goto(base+'/hierarchical/abb',wait_until='networkidle');assert page.locator('#operation-select option').count()==12
    page.evaluate('''()=>{const old=renderHierState;renderHierState=function(...args){window.auditState=structuredClone(args[1]);return old(...args);};}''')
    page.locator('#hier-understand-toggle').click();page.select_option('#operation-select','limpiar');page.click('#hier-step-mode')
    with page.expect_response(lambda r:r.url.endswith('/abb/operate') and r.request.method=='POST') as response:page.click('#hier-sim-play')
    data=response.value.json();assert data['success'];count=len(posts);trace=data['execution_trace'];steps=trace['steps']
    events=clear_events(abb_clear_native_review,case);oracle={s['step_index']:e for e,s in clear_matches(trace,events)};mapping=identities(events)
    for direction,selector,indices in [('forward','#hier-sim-step',range(len(steps))),('backward','#hier-sim-prev',range(len(steps)-2,-2,-1))]:
     for index in indices:
      assert page.locator(selector).is_enabled();page.locator(selector).evaluate('b=>b.click()');page.wait_for_function("n=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
      state=page.evaluate('window.auditState');expected=steps[index]['pedagogy']['memory_state'] if index>=0 else steps[0]['state_snapshot'];assert state==expected
      assert page.locator('#hier-printf-console').text_content()==state['console_stdout']
      heap=page.locator('[data-abb-node]').evaluate_all("xs=>xs.map(x=>({id:x.dataset.abbNode,value:Number(x.dataset.abbValue),left:x.dataset.abbLeft,right:x.dataset.abbRight,status:x.dataset.abbStatus}))");assert heap==state['heap_nodes'];assert page.locator('[data-abb-head]').get_attribute('data-abb-head')==state['head'];assert page.locator('[data-abb-caller]').count()==int(state['caller_frame'] is not None)
      assert page.locator('[data-abb-frame]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.abbFrame,depth:Number(x.dataset.abbDepth)}))')==[{'id':f['id'],'depth':f['depth']} for f in state['tree_frames']]
      aliases=page.locator('[data-abb-alias]').evaluate_all('xs=>xs.map(x=>({frame:x.dataset.abbAliasFrame,name:x.dataset.abbAlias,type:x.dataset.abbAliasType,target:x.dataset.abbAliasTarget}))');assert aliases==[{'frame':f['id'],'name':name,'type':'ABBNodo *' if name=='nodo' else 'int','target':str(target)} for f in state['tree_frames'] for name,target in {**f['parameters'],**f['locals']}.items()]
      def values(root):return [] if root is None else [str(root['value']),*values(root['left']),*values(root['right'])]
      assert sorted(page.locator('.viz-tree-text').all_text_contents())==sorted(values(state['root']))
      ped=steps[index]['pedagogy'] if index>=0 else steps[0]['pedagogy']['initial_frame']
      variables=page.locator('#hier-variables-view tbody tr').evaluate_all('xs=>xs.map(x=>({scope:x.querySelector("small").textContent,previous:x.children[1].textContent,value:x.children[2].textContent}))');assert variables==[{'scope':v['scope'],'previous':str(v['previous']),'value':str(v['value'])} for v in ped['variables']]
      assert page.locator('#hier-stack-view .hier-stack-frame').count()==len(ped['call_stack'])
      assert 'Vida de reservas y referencias' in page.locator('#hier-invariant-view').inner_text()
      if ped['call_stack']:
       assert 'raíz local: '+ped['call_stack'][0]['local_root_address'] in page.locator('#hier-stack-view .hier-stack-frame').first.inner_text()

      retired=page.locator('[data-abb-retired-node]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.abbRetiredNode,value:Number(x.dataset.abbRetiredValue)}))')
      assert retired==[{'id':n['id'],'value':n['value']} for n in state['freed_nodes']]
      assert page.locator('[data-abb-unusable-count]').get_attribute('data-abb-unusable-count')==str(len(ped['memory']['unusable_reference_records']))
      if any('valor indeterminado' in x['target'] for x in aliases):assert 'valor indeterminado' in page.locator('.abb-instruction-memory').inner_text()
      if index>=0 and ped['instruction_event']['phase']=='free':assert 'Liberados (identidades historicas)' in page.locator('#hier-memory-view').inner_text()

      assert 'Reconexión del retorno: no' in page.locator('#hier-relations-view').inner_text()
      if index>=0 and ped['instruction_event']['phase'] in {'return','caller_exit'}:assert 'terminado (contexto del retorno)' in page.locator('#hier-stack-view .hier-stack-frame').last.inner_text()
      if index>=0:
       active=page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').evaluate_all('xs=>xs.map(x=>Number(x.dataset.line))');assert steps[index]['line_index'] in active
       event=oracle.get(index)
       if event:
        assert state['console_stdout']==bytes.fromhex(event['console_hex']).decode('ascii')
        if event['phase']=='return':assert len(state['tree_frames'])==len(event['frames'])-1
        else:assert len(state['tree_frames'])==len(event['frames'])
        # Lifetime annotations are independently checked against native integer IDs in the native tests.
       if ped['instruction_event']['phase']=='caller_exit':assert not state['caller_frame'] and state['head']=='NULL'
      else:assert not variables and not state['tree_frames'] and state['console_stdout']==''
      if case in [3,4] and direction=='forward' and index>=0 and steps[index]['pedagogy']['instruction_event']['phase'] in {'call','return'} and len(state['tree_frames'])>=2:page.screenshot(path=str(tmp_path/f'abb-{meta["operation"]}-{case}-{index}.png'),full_page=True)
      rows.append({'case':case,'operation':meta['operation'],'direction':direction,'index':index,'console_stdout':state['console_stdout'],'frame_ids':[f['id'] for f in state['tree_frames']],'root_unchanged':True})
    assert page.locator('#hier-sim-prev').is_disabled();assert len(posts)==count;assert not page.locator('#hier-step-toggle').is_visible() if page.locator('#hier-step-toggle').count() else True
    # Read exact generated main from highlighted line boundaries, not flattened text.
    actual_main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','')
    assert 'abb_liberarArbol(arbol); arbol = NULL;' in actual_main
    import shutil,subprocess
    gcc=shutil.which('gcc');assert gcc
    for kind,suffix in [('source','c'),('header','h')]:
     downloaded=context.request.get(base+'/help/source/abb/'+kind);assert downloaded.status==200;(tmp_path/('tad_abb.'+suffix)).write_bytes(downloaded.body())
    hooks='static int allocated,freed;void*audit_malloc(size_t n){void*p=malloc(n);if(p)allocated++;return p;}void audit_free(void*p){if(p){printf("AUDIT_FREE:%d\\n",((ABBNodo*)p)->valor);freed++;}free(p);}'
    source=tmp_path/f'main-clear-{case}.c';exe=tmp_path/f'clear-caller-{case}.exe';obj=tmp_path/'abb-probed.o'
    # Actual generated calls remain intact; assert and observer hooks add evidence only.
    parts=actual_main.rsplit('    return 0;',1);assert len(parts)==2
    main='#include "tad_abb.h"\n#include <assert.h>\n#include <stdio.h>\n#include <stdlib.h>\n'+hooks+'\n'+parts[0]+f'    assert(arbol==NULL && allocated==freed && freed=={len(meta["seed"])});\n    return 0;'+parts[1]
    source.write_text(main,encoding='utf-8');flags=['-std=c17','-Wall','-Wextra','-Wpedantic','-Werror']
    build=subprocess.run([gcc,*flags,'-Dmalloc=audit_malloc','-Dfree=audit_free','-c',str(tmp_path/'tad_abb.c'),'-o',str(obj)],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
    build=subprocess.run([gcc,*flags,str(source),str(obj),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
    run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=5);assert run.returncode==0,run.stderr
    import re
    observed=[int(v) for v in re.findall(r'AUDIT_FREE:(-?\d+)',run.stdout)];expected=[n['value'] for n in steps[-1]['pedagogy']['memory_state']['freed_nodes']];assert observed==expected
    # The model's equivalent full main also compiles with the unchanged downloads.
    equivalent='int main(void)'+trace['source_code'].split('int main(void)',1)[1]
    eq=tmp_path/f'equivalent-main-{case}.c';eq.write_text('#include "tad_abb.h"\n#include <stddef.h>\n'+equivalent,encoding='utf-8');eqexe=tmp_path/f'equivalent-{case}.exe'
    build=subprocess.run([gcc,*flags,str(tmp_path/'tad_abb.c'),str(eq),'-o',str(eqexe)],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
    eqrun=subprocess.run([str(eqexe)],capture_output=True,text=True,timeout=5);assert eqrun.returncode==0 and eqrun.stdout==''
    compiled.append({'case':case,'actual_generated_main':actual_main,'observed_free_values':observed,'expected_free_values':expected,'allocations_equal_frees':len(meta['seed']),'root_null_assertion':True,'equivalent_main_stdout':eqrun.stdout});context.close();print('ABB clear replay/native actual caller verified',case,len(steps),flush=True)
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 assert not errors
 (tmp_path/'abb-clear-browser-review.json').write_text(json.dumps({'rows':rows,'cases':5,'errors':errors,'extra_replay_posts':0,'compiled_callers':compiled,'representation':'existing tree SVG plus individual heap identity and recursive-scope panels; no new view selector'},indent=2),encoding='utf-8')
