"""Actual extraction views, output, physical tail, scopes and no-POST replay."""
from pathlib import Path
import json,shutil,subprocess,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
from test_audit_heap_extract_instruction_native import heap_extract_native,CASES
from test_audit_heap_list_download import compile_download
pytestmark=pytest.mark.e2e

@pytest.mark.parametrize('case',range(9))
def test_heap_extract_views_replay_and_downloads(tmp_path,heap_extract_native,case):
 seed=CASES[case];rows=[];programs=[];errors=[]
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
   browser=p.chromium.launch()
   for selected_case in [case]:
    context=browser.new_context(viewport={'width':1366,'height':1100});page=context.new_page();posts=[];page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
    for v in seed:assert context.request.post(base+'/hierarchical/binary_heap/operate',data={'operation':'insertar','payload':{'value':v}}).json()['success']
    page.goto(base+'/hierarchical/binary_heap',wait_until='networkidle');assert page.locator('#operation-select option').count()==5
    page.evaluate("()=>{const original=renderHierState;renderHierState=function(...args){window.auditState=structuredClone(args[1]);return original(...args);};}")
    page.locator('#hier-understand-toggle').click();page.select_option('#operation-select','extraer_raiz');page.click('#hier-step-mode')
    with page.expect_response(lambda r:r.url.endswith('/binary_heap/operate') and r.request.method=='POST') as response:page.click('#hier-sim-play')
    d=response.value.json();assert d['success']==bool(seed);trace=d['execution_trace'];steps=trace['steps'];native=[e for e in heap_extract_native['events'] if e['case']==case];assert len(steps)==len(native);nposts=len(posts)
    pending='Extraccion preparada: resultado pendiente hasta completar la traza.';assert page.locator('#message-box').inner_text()==pending
    for direction,selector,indices in [('forward','#hier-sim-step',range(len(steps))),('backward','#hier-sim-prev',range(len(steps)-2,-2,-1))]:
     for index in indices:
      assert page.locator(selector).is_enabled();page.locator(selector).evaluate('b=>b.click()');page.wait_for_function("n=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
      state=page.evaluate('window.auditState');expected=steps[index]['pedagogy']['memory_state'] if index>=0 else steps[0]['state_snapshot'];assert state==expected
      assert page.locator('#hier-printf-console').text_content()==state['console_stdout']==''
      assert page.locator('[data-heap-source-index]').all_text_contents()==[f'[{i}] {v}' for i,v in enumerate(state['array'])]
      assert sorted(page.locator('.viz-tree-text').all_text_contents())==sorted(map(str,state['array']))
      suspended=state['heap_data_reference'].startswith('indeterminado');assert page.locator('[data-heap-drawing-suspended]').count()==(2 if suspended else 0)
      assert page.locator('[data-heap-source-owner]').evaluate_all('xs=>xs.map(x=>x.dataset.heapSourceOwner)')==[state['heap_data_reference']]*len(state['array'])
      assert page.locator('[data-heap-tree-owner]').evaluate_all('xs=>xs.map(x=>x.dataset.heapTreeOwner)')==[state['heap_data_reference']]*len(state['array'])
      assert page.locator('[data-heap-source-index].sim-active').evaluate_all('xs=>xs.map(x=>Number(x.dataset.heapSourceIndex))')==sorted([i for i in state['heap_active_indices'] if i<state['size']])
      assert sorted(page.locator('[data-heap-tree-index].sim-active').evaluate_all('xs=>xs.map(x=>Number(x.dataset.heapTreeIndex))'))==sorted([i for i in state['heap_active_indices'] if i<state['size']])
      output=page.locator('[data-heap-extract-output]');assert output.get_attribute('data-heap-output-initialized')==str(state['caller_output']['initialized']).lower();assert output.get_attribute('data-heap-output-value')==(str(state['caller_output']['value']) if state['caller_output']['initialized'] else 'sin inicializar')
      assert page.locator('[data-heap-extract-views]').count()==1
      storage=page.locator('[data-heap-clear-storage]');assert storage.get_attribute('data-heap-count')==str(state['size']) and storage.get_attribute('data-heap-capacity')==str(state['capacity']) and storage.get_attribute('data-heap-reference')==state['heap_data_reference']
      actual=page.locator('[data-heap-clear-allocation]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.heapClearAllocation,capacity:Number(x.dataset.heapClearCapacity)}))');assert actual==[{'id':o['id'],'capacity':o['capacity']} for o in state['heap_allocations'] if o['live']]
      cells=page.locator('[data-heap-clear-cell]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.heapClearOwner,index:Number(x.dataset.heapClearCell),initialized:x.dataset.heapInitialized,value:x.dataset.heapValue}))');assert cells==[{'id':o['id'],'index':c['index'],'initialized':'desconocido' if c['initialized'] is None else str(c['initialized']).lower(),'value':str(c['value']) if c['initialized'] is True else 'sin inicializar' if c['initialized'] is False else 'no observado'} for o in state['heap_allocations'] if o['live'] for c in o['cells']]
      retired=page.locator('[data-heap-clear-retired-index]').evaluate_all('xs=>xs.map(x=>({index:Number(x.dataset.heapClearRetiredIndex),value:Number(x.dataset.heapRetiredValue)}))');assert retired==[{'index':c['index'],'value':c['value']} for o in state['heap_retired'] for c in o['cells'] if c['initialized'] is True]
      assert page.locator('[data-heap-clear-retired]').count()==len(state['heap_retired'])
      frames=page.locator('[data-heap-frame]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.heapFrame,function:x.dataset.heapFunction}))');assert frames==[{'id':f['id'],'function':f['function']} for f in state['query_frames']]
      def display(v):return str(v).lower() if isinstance(v,bool) else str(v)
      local=page.locator('[data-heap-local]').evaluate_all('xs=>xs.map(x=>({frame:x.dataset.heapLocalFrame,name:x.dataset.heapLocal,value:x.dataset.heapLocalValue}))');assert local==[{'frame':f['id'],'name':k,'value':display(v)} for f in state['query_frames'] for k,v in {**f['parameters'],**f['locals']}.items()]
      ped=steps[index]['pedagogy'] if index>=0 else steps[0]['pedagogy']['initial_frame'];assert 'Estado intermedio de Extraer' in page.locator('#hier-invariant-view').inner_text()
      variables=page.locator('#hier-variables-view tbody tr').evaluate_all('xs=>xs.map(x=>({scope:x.querySelector("small").textContent,previous:x.children[1].textContent,value:x.children[2].textContent,type:x.children[0].querySelector("code").textContent}))');assert variables==[{'scope':v['scope'],'previous':display(v['previous']),'value':display(v['value']),'type':v['type']+' '+v['name']} for v in ped['variables']]
      assert page.locator('#hier-stack-view .hier-stack-frame').count()==len(ped['call_stack']);assert page.locator('#message-box').inner_text()==(d['message'] if index==len(steps)-1 else pending)
      if index>=0:
       event=native[index];assert steps[index]['line_text'].strip()==event['text'] and state['array']==event['array'] and state['size']==event['quantity'] and state['capacity']==event['capacity']
       active=page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').evaluate_all('xs=>xs.map(x=>Number(x.dataset.line))');assert steps[index]['line_index'] in active
       if event['phase']=='return':assert 'terminado (contexto del retorno)' in page.locator('#hier-stack-view .hier-stack-frame').last.inner_text()
       if ped['condition']:assert display(ped['condition']['result']) in page.locator('#hier-path-view').text_content()
       if direction=='forward' and case in [3,6,8] and event['scope']=='swap' and event['text']=='*a = *b;':page.screenshot(path=str(tmp_path/f'extract-{case}-{index}.png'),full_page=True)
      else:assert not state['caller_output']['initialized'] and not state['query_frames'] and state['heap_pending_index'] is None and not state['heap_retired'] and not any(o['id']=='A2' for o in state['heap_allocations'])
      rows.append({'case':case,'direction':direction,'index':index,'quantity':state['size'],'capacity':state['capacity'],'reference':state['heap_data_reference'],'written':state['heap_written'],'pending':state['heap_pending_index']})
    assert len(posts)==nposts and not errors and page.locator('#hier-sim-prev').is_disabled()
    mains=[]
    for label in ['before','after']:
     actual='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','')
     if not seed and label=='after':
      assert actual=='' and page.locator('#action-history .didactic-history-main').count()==0
      actual=page.evaluate('()=>buildHierMainCode("binary_heap",[],window.HIER_VIEW_MODEL.didactic)')
     stdout=compile_download(actual,context,base,tmp_path/f'history-{case}-{label}')
     expected=[f'INSERTAR: {v}' for v in seed]+([f"EXTRAIDO: {native[-1]['output_value']}"] if seed else []);assert stdout.splitlines()==expected;mains.append(actual)
     if label=='before':nposts=len(posts);page.reload(wait_until='networkidle');assert len(posts)==nposts
    annotation='    /* Operacion fallida en la interfaz: no forma parte de la reproduccion ejecutable. */\n'
    if not seed:
     assert mains[0].count(annotation)==1 and annotation not in mains[1];assert mains[0].replace(annotation,'')==mains[1];assert 'monticulo_extraer_raiz(&monticulo' not in mains[0]
    else:assert mains[0]==mains[1]
    caller='bool ejecutar_extraer'+trace['source_code'].split('bool ejecutar_extraer',1)[1];assert caller.strip()==heap_extract_native['caller'];target=tmp_path/f'caller-{case}';target.mkdir()
    for kind,suffix in [('source','c'),('header','h')]:
     raw=context.request.get(base+'/help/source/binary_heap/'+kind).body();assert raw==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_monticulo_binario.'+suffix)).read_bytes();(target/('tad_monticulo_binario.'+suffix)).write_bytes(raw)
    final=native[-1];asserts=f"assert(m.cantidad=={final['quantity']}&&m.capacidad=={final['capacity']});"+''.join(f'assert(m.datos[{i}]=={v});' for i,v in enumerate(final['physical']))
    output=final['output_value'] if seed else 123456
    program='#include <assert.h>\n#include "tad_monticulo_binario.h"\n'+caller+'\nint main(void){MonticuloBinario m;monticulo_inicializar(&m,MONTICULO_MIN,16);'+''.join(f'monticulo_insertar(&m,{v});' for v in seed)+f'int output=123456;int *old=m.datos;bool ok=ejecutar_extraer(&m,&output);assert(ok=={int(bool(seed))});assert(output=={output}&&m.datos==old);'+asserts+'monticulo_destruir(&m);return 0;}'
    (target/'main.c').write_text(program,encoding='utf-8');gcc=shutil.which('gcc');assert gcc
    run=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(target/'main.c'),str(target/'tad_monticulo_binario.c'),'-o',str(target/'main.exe')],capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr
    run=subprocess.run([str(target/'main.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0,run.stderr
    programs.append({'case':case,'actual_history_mains':2 if seed else 1,'empty_history_generator_program':not bool(seed),'doxygen_warnings':0,'equivalent_caller_native_state_assertions':True});context.close();print('Heap Extraer verified',case,len(steps),flush=True)
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (tmp_path/'heap-extract-browser-review.json').write_text(json.dumps({'cases':1,'case_ids':[case],'rows':rows,'programs':programs,'errors':errors,'extra_replay_posts':0},indent=2),encoding='utf-8')
