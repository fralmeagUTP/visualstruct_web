"""Heap clear lifetime in the real array/tree DOM, forward/back and downloads."""
from pathlib import Path
import json,shutil,subprocess,threading
import pytest
from app import create_app
from app.domain.hierarchical.tad_wrappers import MonticuloBinario
from werkzeug.serving import make_server
from test_audit_heap_clear_instruction_native import heap_clear_native,CASES,fail_clear
from test_audit_heap_list_download import compile_download
pytestmark=pytest.mark.e2e

def test_heap_clear_views_replay_callers_and_reserve_failure(tmp_path,heap_clear_native,monkeypatch):
 original=MonticuloBinario.limpiar;fault={'enabled':False}
 def clear(self):return fail_clear(self) if fault['enabled'] else original(self)
 monkeypatch.setattr(MonticuloBinario,'limpiar',clear)
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
 rows=[];programs=[];errors=[];executions=0
 try:
  with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
   browser=p.chromium.launch()
   for case,(seed,repeats,fail) in enumerate(CASES):
    fault['enabled']=False;context=browser.new_context(viewport={'width':1366,'height':1100});page=context.new_page();posts=[]
    page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
    for value in seed:assert context.request.post(base+'/hierarchical/binary_heap/operate',data={'operation':'insertar','payload':{'value':value}}).json()['success']
    page.goto(base+'/hierarchical/binary_heap',wait_until='networkidle');assert page.locator('#operation-select option').count()==5
    page.evaluate('''()=>{const original=renderHierState;renderHierState=function(...args){window.auditState=structuredClone(args[1]);return original(...args);};}''')
    page.locator('#hier-understand-toggle').click();page.select_option('#operation-select','limpiar');page.click('#hier-step-mode');fault['enabled']=fail
    for iteration in range(repeats):
     with page.expect_response(lambda r:r.url.endswith('/binary_heap/operate') and r.request.method=='POST') as response:page.click('#hier-sim-play')
     data=response.value.json();assert data['success'];steps=data['execution_trace']['steps'];native=[e for e in heap_clear_native['events'] if e['case']==case and e['iteration']==iteration]
     assert len(steps)==len(native);nposts=len(posts);executions+=1
     assert page.locator('#message-box').inner_text()=='Limpieza preparada: resultado pendiente hasta completar la traza.'
     for direction,selector,indices in [('forward','#hier-sim-step',range(len(steps))),('backward','#hier-sim-prev',range(len(steps)-2,-2,-1))]:
      for index in indices:
       assert page.locator(selector).is_enabled();page.locator(selector).evaluate('b=>b.click()');page.wait_for_function("n=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
       state=page.evaluate('window.auditState');expected=steps[index]['pedagogy']['memory_state'] if index>=0 else steps[0]['state_snapshot'];assert state==expected
       assert page.locator('#hier-printf-console').text_content()==state['console_stdout']==''
       assert page.locator('[data-heap-source-index]').all_text_contents()==[f'[{i}] {v}' for i,v in enumerate(state['array'])]
       assert sorted(page.locator('.viz-tree-text').all_text_contents())==sorted(map(str,state['array']))
       assert page.locator('[data-heap-source-index].sim-active,[data-heap-tree-index].sim-active').count()==0
       storage=page.locator('[data-heap-clear-storage]');assert storage.get_attribute('data-heap-count')==str(state['size']) and storage.get_attribute('data-heap-capacity')==str(state['capacity']) and storage.get_attribute('data-heap-reference')==state['heap_data_reference']
       actual=page.locator('[data-heap-clear-allocation]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.heapClearAllocation,capacity:Number(x.dataset.heapClearCapacity)}))')
       assert actual==[{'id':o['id'],'capacity':o['capacity']} for o in state['heap_allocations'] if o['live']]
       cells=page.locator('[data-heap-clear-cell]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.heapClearOwner,index:Number(x.dataset.heapClearCell),initialized:x.dataset.heapInitialized,value:x.dataset.heapValue}))')
       assert cells==[{'id':o['id'],'index':c['index'],'initialized':'desconocido' if c['initialized'] is None else str(c['initialized']).lower(),'value':str(c['value']) if c['initialized'] is True else 'sin inicializar' if c['initialized'] is False else 'no observado'} for o in state['heap_allocations'] if o['live'] for c in o['cells']]
       retired=page.locator('[data-heap-clear-retired-index]').evaluate_all('xs=>xs.map(x=>({index:Number(x.dataset.heapClearRetiredIndex),value:Number(x.dataset.heapRetiredValue)}))')
       assert retired==[{'index':c['index'],'value':c['value']} for o in state['heap_retired'] for c in o['cells'] if c['initialized'] is True]
       assert page.locator('[data-heap-clear-retired]').count()==len(state['heap_retired'])
       frames=page.locator('[data-heap-frame]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.heapFrame,function:x.dataset.heapFunction}))');assert frames==[{'id':f['id'],'function':f['function']} for f in state['query_frames']]
       local=page.locator('[data-heap-local]').evaluate_all('xs=>xs.map(x=>({frame:x.dataset.heapLocalFrame,name:x.dataset.heapLocal,value:x.dataset.heapLocalValue}))')
       def display(v):return str(v).lower() if isinstance(v,bool) else str(v)
       assert local==[{'frame':f['id'],'name':k,'value':display(v)} for f in state['query_frames'] for k,v in {**f['parameters'],**f['locals']}.items()]
       ped=steps[index]['pedagogy'] if index>=0 else steps[0]['pedagogy']['initial_frame']
       assert 'Estado intermedio de vida de memoria' in page.locator('#hier-invariant-view').inner_text()
       assert 'forma completa y padre' not in page.locator('#hier-invariant-view').inner_text()
       variables=page.locator('#hier-variables-view tbody tr').evaluate_all('xs=>xs.map(x=>({scope:x.querySelector("small").textContent,previous:x.children[1].textContent,value:x.children[2].textContent}))');assert variables==[{'scope':v['scope'],'previous':display(v['previous']),'value':display(v['value'])} for v in ped['variables']]
       assert page.locator('#hier-stack-view .hier-stack-frame').count()==len(ped['call_stack'])
       assert page.locator('#message-box').inner_text()==(data['message'] if index==len(steps)-1 else 'Limpieza preparada: resultado pendiente hasta completar la traza.')
       if index>=0:
        event=native[index];assert steps[index]['line_text'].strip()==event['text'] and state['capacity']==event['capacity'] and state['size']==event['quantity']
        assert state['array']==event['array'];assert ped['instruction_event']['phase']==event['phase']
        active=page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').evaluate_all('xs=>xs.map(x=>Number(x.dataset.line))');assert steps[index]['line_index'] in active
        if event['phase']=='return':assert 'terminado (contexto del retorno)' in page.locator('#hier-stack-view .hier-stack-frame').last.inner_text()
        if ped['condition']:assert display(ped['condition']['result']) in page.locator('#hier-path-view').text_content()
        if direction=='forward' and iteration==0 and case in [0,2,6] and event['phase'] in ['free','allocation']:page.screenshot(path=str(tmp_path/f'clear-{case}-{index}.png'),full_page=True)
       else:assert not state['query_frames'] and not state['heap_retired'] and not any(o['id']=='A2' for o in state['heap_allocations'])
       rows.append({'case':case,'iteration':iteration,'direction':direction,'index':index,'reference':state['heap_data_reference'],'quantity':state['size'],'capacity':state['capacity'],'live':[o['id'] for o in state['heap_allocations'] if o['live']]})
     assert len(posts)==nposts and page.locator('#hier-sim-prev').is_disabled() and not errors
    # Download current actual history main before/after reload without any new operation.
    mains=[]
    for label in ['before','after']:
     main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','')
     assert main.count('monticulo_destruir(&monticulo); monticulo_inicializar(&monticulo, MONTICULO_MIN, 16);')==repeats
     stdout=compile_download(main,context,base,tmp_path/f'history-{case}-{label}');assert stdout.splitlines().count('LIMPIAR')==repeats;mains.append(main)
     if label=='before':nposts=len(posts);page.reload(wait_until='networkidle');assert len(posts)==nposts
    assert mains[0]==mains[1]
    # The equivalent caller displayed in the trace also links to the downloaded C/H.
    caller='void ejecutar_limpiar'+data['execution_trace']['source_code'].split('void ejecutar_limpiar',1)[1];assert caller.strip()==heap_clear_native['caller']
    target=tmp_path/f'caller-{case}';target.mkdir()
    for kind,suffix in [('source','c'),('header','h')]:
     raw=context.request.get(base+'/help/source/binary_heap/'+kind).body();assert raw==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_monticulo_binario.'+suffix)).read_bytes();(target/('tad_monticulo_binario.'+suffix)).write_bytes(raw)
    # Failure is injected ONLY after normal preparation, matching the native oracle.
    cfile=target/'tad_monticulo_binario.c'
    if fail:
     shim='''\n#include <stdlib.h>\nextern int audit_fail;\nstatic void *audit_alloc(void *p,size_t n){return audit_fail?NULL:realloc(p,n);}\n#define realloc audit_alloc\n'''
     cfile.write_text(shim+cfile.read_text(encoding='utf-8-sig'),encoding='utf-8')
    program='#include <assert.h>\n#include "tad_monticulo_binario.h"\nint audit_fail=0;\n'+caller+'\nint main(void){MonticuloBinario m;monticulo_inicializar(&m,MONTICULO_MIN,16);'+''.join(f'monticulo_insertar(&m,{v});' for v in seed)+'audit_fail='+str(int(fail))+';'
    program+=''.join('ejecutar_limpiar(&m);assert(m.cantidad==0&&m.capacidad=='+str(0 if fail else 20)+'&&(m.datos==NULL)=='+str(int(fail))+');' for _ in range(repeats))+'monticulo_destruir(&m);return 0;}'
    (target/'main.c').write_text(program,encoding='utf-8');gcc=shutil.which('gcc');assert gcc
    run=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(target/'main.c'),str(cfile),'-o',str(target/'main.exe')],capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr
    run=subprocess.run([str(target/'main.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0,run.stderr
    programs.append({'case':case,'repeats':repeats,'fail':fail,'actual_history_mains':2,'actual_mains_doxygen_warnings':0,'equivalent_caller':True,'failure_injection_after_preparation':fail})
    context.close();print('Heap clear verified',case,repeats,'OOM' if fail else 'normal',flush=True)
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (tmp_path/'heap-clear-browser-review.json').write_text(json.dumps({'cases':8,'executions':executions,'rows':rows,'programs':programs,'extra_replay_posts':0,'errors':errors,'limits':['Real allocator internals opaque; injected failure confined to clear in isolated test server, not preview.','Before/after downloaded mains run in normal allocator; equivalent caller additionally runs in each injected mode.','Recorded cases, not all possible paths.']},indent=2),encoding='utf-8')
