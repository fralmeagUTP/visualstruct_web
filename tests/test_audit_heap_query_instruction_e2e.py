"""Both existing heap representations and destination lifetime against native C."""
from pathlib import Path
import collections,json,shutil,subprocess,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
from test_audit_heap_query_instruction_native import heap_query_native,CASES,matched
from test_audit_heap_list_download import compile_download
pytestmark=pytest.mark.e2e

def test_heap_queries_both_representations_forward_backward_native(tmp_path,heap_query_native):
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[];programs=[];errors=[]
 try:
  with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
   browser=p.chromium.launch()
   for case,(operation,seed,pops) in enumerate(CASES):
    context=browser.new_context(viewport={'width':1366,'height':1100});page=context.new_page();posts=[];page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
    for value in seed:assert context.request.post(base+'/hierarchical/binary_heap/operate',data={'operation':'insertar','payload':{'value':value}}).json()['success']
    for _ in range(pops):assert context.request.post(base+'/hierarchical/binary_heap/operate',data={'operation':'extraer_raiz','payload':{}}).json()['success']
    page.goto(base+'/hierarchical/binary_heap',wait_until='networkidle');assert page.locator('#operation-select option').count()==5
    page.evaluate('''()=>{const original=renderHierState;renderHierState=function(...args){window.auditState=structuredClone(args[1]);return original(...args);};}''')
    page.locator('#hier-understand-toggle').click();page.select_option('#operation-select',operation);page.click('#hier-step-mode')
    with page.expect_response(lambda r:r.url.endswith('/binary_heap/operate') and r.request.method=='POST') as response:page.click('#hier-sim-play')
    data=response.value.json();trace=data['execution_trace'];steps=trace['steps'];native=[e for e in heap_query_native['events'] if e['case']==case];oracle={s['step_index']:e for s,e in matched(trace,native)};nposts=len(posts)
    assert page.locator('#message-box').inner_text()=='Consulta preparada: resultado pendiente hasta completar la traza.'
    for direction,selector,indices in [('forward','#hier-sim-step',range(len(steps))),('backward','#hier-sim-prev',range(len(steps)-2,-2,-1))]:
     for index in indices:
      assert page.locator(selector).is_enabled();page.locator(selector).evaluate('b=>b.click()');page.wait_for_function("n=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
      state=page.evaluate('window.auditState');expected=steps[index]['pedagogy']['memory_state'] if index>=0 else steps[0]['state_snapshot'];assert state==expected
      assert page.locator('#hier-printf-console').text_content()==state['console_stdout']==''
      assert state['array']==native[0]['array'] and state['capacity']==native[0]['capacity']
      assert page.locator('[data-heap-source-index]').all_text_contents()==[f'[{i}] {v}' for i,v in enumerate(state['array'])]
      assert sorted(page.locator('.viz-tree-text').all_text_contents())==sorted(map(str,state['array']))
      storage=page.locator('[data-heap-storage]');assert storage.get_attribute('data-heap-count')==str(state['size']) and storage.get_attribute('data-heap-capacity')==str(state['capacity'])
      frames=page.locator('[data-heap-frame]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.heapFrame,function:x.dataset.heapFunction}))');assert frames==[{'id':f['id'],'function':f['function']} for f in state['query_frames']]
      locals_dom=page.locator('[data-heap-local]').evaluate_all('xs=>xs.map(x=>({frame:x.dataset.heapLocalFrame,name:x.dataset.heapLocal,value:x.dataset.heapLocalValue}))')
      def display(value):return str(value).lower() if isinstance(value,bool) else str(value)
      assert locals_dom==[{'frame':f['id'],'name':k,'value':display(v)} for f in state['query_frames'] for k,v in {**f['parameters'],**f['locals']}.items()]
      cells=page.locator('[data-heap-destination-index]').evaluate_all('xs=>xs.map(x=>({index:Number(x.dataset.heapDestinationIndex),initialized:x.dataset.heapInitialized==="true",value:x.dataset.heapValue}))')
      assert cells==[{'index':c['index'],'initialized':c['initialized'],'value':str(c['value']) if c['initialized'] else 'sin inicializar'} for c in state['destination']['cells']] if state['destination'] else cells==[]
      assert page.locator('[data-heap-destination]').count()==int(state['destination'] is not None)
      retired=page.locator('[data-heap-retired-index]').evaluate_all('xs=>xs.map(x=>({index:Number(x.dataset.heapRetiredIndex),value:Number(x.dataset.heapRetiredValue)}))')
      assert retired==[{'index':c['index'],'value':c['value']} for c in state['retired_destination']['cells']] if state['retired_destination'] else retired==[]
      if operation=='raiz':
       output=page.locator('[data-heap-output]');assert output.get_attribute('data-heap-output-initialized')==str(state['caller_output']['initialized']).lower();assert output.get_attribute('data-heap-output-value')==(str(state['caller_output']['value']) if state['caller_output']['initialized'] else 'sin inicializar')
      else:assert page.locator('[data-heap-output]').count()==0
      ped=steps[index]['pedagogy'] if index>=0 else steps[0]['pedagogy']['initial_frame']
      variables=page.locator('#hier-variables-view tbody tr').evaluate_all('xs=>xs.map(x=>({scope:x.querySelector("small").textContent,previous:x.children[1].textContent,value:x.children[2].textContent}))');assert variables==[{'scope':v['scope'],'previous':display(v['previous']),'value':display(v['value'])} for v in ped['variables']]
      assert page.locator('#hier-stack-view .hier-stack-frame').count()==len(ped['call_stack'])
      assert page.locator('#message-box').inner_text()==(data['message'] if index==len(steps)-1 else 'Consulta preparada: resultado pendiente hasta completar la traza.')
      if index>=0:
       event=oracle[index];assert ped['instruction_event']['phase']==event['phase']
       expected_active=event['ci'] if event['scope']=='copy' and event['source_line']=='destino[i] = m->datos[i];' else 0 if event['scope']=='root' and event['source_line']=='*resultado = m->datos[0];' else None
       assert state['active_copy_index']==expected_active
       assert page.locator('[data-heap-source-index].sim-active').evaluate_all('xs=>xs.map(x=>Number(x.dataset.heapSourceIndex))')==([] if expected_active is None else [expected_active])
       assert page.locator('[data-heap-destination-index].sim-active').evaluate_all('xs=>xs.map(x=>Number(x.dataset.heapDestinationIndex))')==([] if expected_active is None or operation=='raiz' else [expected_active])
       assert page.locator('[data-heap-tree-index].sim-active').evaluate_all('xs=>xs.map(x=>Number(x.dataset.heapTreeIndex))')==([] if expected_active is None else [expected_active])
       active=page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').evaluate_all('xs=>xs.map(x=>Number(x.dataset.line))');assert steps[index]['line_index'] in active
       if event['phase']=='return':assert 'terminado (contexto del retorno)' in page.locator('#hier-stack-view .hier-stack-frame').last.inner_text()
       if ped['condition']:assert display(ped['condition']['result']) in page.locator('#hier-path-view').text_content()
      else:assert not state['query_frames'] and not state['caller_output']['initialized'] and state['destination'] is None and state['observed_result'] is None
      if case in [1,5,7,9] and direction=='forward' and index>=0 and (steps[index]['pedagogy']['instruction_event']['phase'] in {'allocation','free'} or (operation=='raiz' and steps[index]['pedagogy']['instruction_event']['phase']=='assignment')):page.screenshot(path=str(tmp_path/f'heap-{operation}-{case}-{index}.png'),full_page=True)
      rows.append({'case':case,'operation':operation,'direction':direction,'index':index,'source_array_unchanged':True,'destination_initialized':sum(c['initialized'] for c in (state['destination'] or {}).get('cells',[])),'retired':state['retired_destination'] is not None})
    assert len(posts)==nposts and page.locator('#hier-sim-prev').is_disabled();assert not errors
    # Canonical actual C function bodies are shown; equivalent caller is isolated for linking with the downloads.
    for scope in ['root'] if operation=='raiz' else ['count','copy']:assert heap_query_native['originals'][scope] in trace['source_code']
    signature='bool ejecutar_raiz' if operation=='raiz' else 'int ejecutar_a_lista';caller=signature+trace['source_code'].split(signature,1)[1];assert caller.strip()==heap_query_native['callers'][operation].strip()
    target=tmp_path/f'caller-{case}';target.mkdir()
    for kind,suffix in [('source','c'),('header','h')]:
     r=context.request.get(base+'/help/source/binary_heap/'+kind);assert r.status==200;(target/('tad_monticulo_binario.'+suffix)).write_bytes(r.body())
    preparation='monticulo_inicializar(&m,MONTICULO_MIN,16);'+''.join(f'monticulo_insertar(&m,{v});' for v in seed)+''.join('monticulo_extraer_raiz(&m,&ignored);' for _ in range(pops))
    invoke='int output;bool ok=ejecutar_raiz(&m,&output);if(ok)printf("ROOT:%d\\n",output);else printf("EMPTY\\n");' if operation=='raiz' else 'int status=ejecutar_a_lista(&m);printf("STATUS:%d\\n",status);'
    program='#include <stdio.h>\n#include <stdlib.h>\n#include "tad_monticulo_binario.h"\n'+caller+'\nint main(void){MonticuloBinario m;int ignored=0;(void)ignored;'+preparation+invoke+'printf("COUNT:%d CAP:%d\\n",m.cantidad,m.capacidad);monticulo_destruir(&m);return 0;}'
    (target/'main.c').write_text(program,encoding='utf-8');gcc=shutil.which('gcc');assert gcc
    build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(target/'main.c'),str(target/'tad_monticulo_binario.c'),'-o',str(target/'main.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
    run=subprocess.run([str(target/'main.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0
    expected=('ROOT:'+str(data['result'])+'\n' if data['success'] else 'EMPTY\n') if operation=='raiz' else 'STATUS:0\n'
    assert run.stdout==expected+f'COUNT:{native[0]["quantity"]} CAP:{native[0]["capacity"]}\n'
    actual='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');stdout=compile_download(actual,context,base,tmp_path/f'actual-history-{case}')
    if operation=='raiz':assert ('RAIZ: '+str(data['result'])+'\n' in stdout) if data['success'] else 'RAIZ:' not in stdout
    else:assert 'A LISTA: '+str(data['result'])+'\n' in stdout
    programs.append({'case':case,'caller_stdout':run.stdout,'actual_main_doxygen_warnings':0,'actual_main_stdout':stdout});context.close();print('Heap queries native/both views/caller/main verified',case,len(steps),flush=True)
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (tmp_path/'heap-query-browser-review.json').write_text(json.dumps({'rows':rows,'cases':10,'programs':programs,'errors':errors,'extra_replay_posts':0,'representation':'Existing source array and source SVG tree plus independent output/destination/scope cards; no new operation or view selector.'},indent=2),encoding='utf-8')
