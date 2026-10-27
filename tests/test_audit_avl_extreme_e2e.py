"""AVL public minimum and auxiliary maximum: guarded callers and full replay."""
import json,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
from test_audit_avl_extreme_native import avl_extreme_native,extreme_matches,CASES
from test_audit_avl_main_e2e import compile_main
pytestmark=pytest.mark.e2e

def test_extreme_browser_guard_alias_output_and_replay(tmp_path,avl_extreme_native):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[];errors=[];compiled=[]
 try:
  with sync() as p:
   browser=p.chromium.launch()
   for case in range(10):
    meta={'seed':CASES[case][1],'operation':CASES[case][0]};context=browser.new_context(viewport={'width':1366,'height':1000});page=context.new_page();posts=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
    for value in meta['seed']:assert context.request.post(base+'/hierarchical/avl/operate',data={'operation':'insertar','payload':{'value':value}}).json()['success']
    page.goto(base+'/hierarchical/avl',wait_until='networkidle');assert page.locator('#operation-select option').count()==9
    page.evaluate('''()=>{const old=renderHierState;renderHierState=function(...args){window.auditState=structuredClone(args[1]);return old(...args);};}''')
    page.locator('#hier-understand-toggle').click();page.select_option('#operation-select',meta['operation']);page.click('#hier-step-mode')
    with page.expect_response(lambda r:r.url.endswith('/avl/operate') and r.request.method=='POST') as response:page.click('#hier-sim-play')
    data=response.value.json();assert data['success']==bool(meta['seed']);count=len(posts);trace=data['execution_trace'];steps=trace['steps'];assert page.locator('#message-box').inner_text()=='Consulta preparada: resultado pendiente hasta completar la traza.'
    events=[e for e in avl_extreme_native['events'] if e['case']==case];oracle={s['step_index']:e for e,s in extreme_matches(trace,events)}
    for direction,selector,indices in [('forward','#hier-sim-step',range(len(steps))),('backward','#hier-sim-prev',range(len(steps)-2,-2,-1))]:
     for index in indices:
      assert page.locator(selector).is_enabled();page.locator(selector).evaluate('b=>b.click()');page.wait_for_function("n=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
      state=page.evaluate('window.auditState');expected=steps[index]['pedagogy']['memory_state'] if index>=0 else steps[0]['state_snapshot'];assert state==expected
      assert state['root']==data['visual_state']['root'];assert page.locator('#hier-printf-console').text_content()==state['console_stdout']
      scalar=page.locator('[data-avl-output]');assert scalar.get_attribute('data-avl-output-initialized')==str(state['caller_output']['initialized']).lower();assert scalar.get_attribute('data-avl-output-value')==(str(state['caller_output']['value']) if state['caller_output']['initialized'] else 'sin inicializar')
      assert page.locator('#message-box').inner_text()==(data['message'] if index==len(steps)-1 else 'Consulta preparada: resultado pendiente hasta completar la traza.')
      heap=page.locator('[data-abb-node]').evaluate_all("xs=>xs.map(x=>({id:x.dataset.abbNode,value:Number(x.dataset.abbValue),left:x.dataset.abbLeft,right:x.dataset.abbRight,status:x.dataset.abbStatus}))");assert heap==[{k:v for k,v in n.items() if k not in ['parent','balance_factor']} for n in state['heap_nodes']];assert page.locator('[data-abb-head]').get_attribute('data-abb-head')==state['head'];assert page.locator('[data-abb-caller]').count()==int(state['caller_frame'] is not None)
      for n in state['heap_nodes']:
       card=page.locator('[data-abb-node="'+n['id']+'"]').inner_text();assert 'padre: '+n['parent'] in card and 'FE: '+str(n['balance_factor']) in card
      assert page.locator('[data-abb-frame]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.abbFrame,depth:Number(x.dataset.abbDepth)}))')==[{'id':f['id'],'depth':f['depth']} for f in state['tree_frames']]
      aliases=page.locator('[data-abb-alias]').evaluate_all('xs=>xs.map(x=>({frame:x.dataset.abbAliasFrame,name:x.dataset.abbAlias,type:x.dataset.abbAliasType,target:x.dataset.abbAliasTarget}))');assert aliases==[{'frame':f['id'],'name':name,'type':'AVL','target':str(target)} for f in state['tree_frames'] for name,target in {**f['parameters'],**f['locals']}.items()]
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
        assert state['console_stdout']==''
        assert len(state['tree_frames'])==event['callee']-(1 if event['phase']=='return' else 0)
        assert state['head']==steps[0]['state_snapshot']['head']
       if ped['instruction_event']['phase']=='caller_result':assert state['wrapper_result']==int(data['success']) and not state['caller_frame']
      else:assert not variables and not state['tree_frames'] and state['console_stdout']==''
      if case in [0,2,7] and direction=='forward' and index>=0 and steps[index]['pedagogy']['instruction_event']['phase'] in {'assignment','caller_store','caller_result'}:page.screenshot(path=str(tmp_path/f'avl-{meta["operation"]}-{case}-{index}.png'),full_page=True)
      rows.append({'case':case,'operation':meta['operation'],'direction':direction,'index':index,'console_stdout':state['console_stdout'],'frame_ids':[f['id'] for f in state['tree_frames']],'root_unchanged':True})
    assert page.locator('#hier-sim-prev').is_disabled();assert len(posts)==count;assert not page.locator('#hier-step-toggle').is_visible() if page.locator('#hier-step-toggle').count() else True
    # The actual displayed caller compiles against the actual downloaded C/H.
    import shutil,subprocess
    gcc=shutil.which('gcc');assert gcc
    for kind,suffix in [('source','c'),('header','h')]:
     downloaded=context.request.get(base+'/help/source/avl/'+kind);assert downloaded.status==200;(tmp_path/('tad_avl.'+suffix)).write_bytes(downloaded.body())
    caller='int ejecutar_'+meta['operation']+trace['source_code'].split('int ejecutar_'+meta['operation'],1)[1]
    assert caller.strip()==avl_extreme_native['callers'][meta['operation']].strip()
    helper=avl_extreme_native['snippets']['maximo'] if meta['operation']=='maximo' else ''
    seed=''.join('avl_insertar(&root,'+str(value)+');' for value in meta['seed'])
    main='#include "tad_avl.h"\n#include <stdio.h>\n'+helper+'\n'+caller+'\nint main(void){AVL root=NULL;'+seed+'int output;int ok=ejecutar_'+meta['operation']+'(root,&output);if(ok)printf("%d\\n",output);else printf("VACIO\\n");avl_liberarAVL(root);return 0;}'
    source=tmp_path/f'main-extreme-{case}.c';source.write_text(main,encoding='utf-8');exe=tmp_path/'extreme-caller.exe';build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'tad_avl.c'),str(source),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
    run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=5);assert run.returncode==0;expected=(str(data['result']) if data['success'] else 'VACIO')+'\n';assert run.stdout==expected
    actual_main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');actual=compile_main(actual_main,context,base,tmp_path/f'actual-history-{case}')
    if meta['seed']:assert meta['operation'].upper()+': '+str(data['result'])+'\n' in actual['stdout']
    else:assert not any(line.strip().startswith('avl_'+meta['operation']+'(') for line in actual_main.splitlines())
    compiled.append({'case':case,'caller':caller,'stdout':run.stdout,'api_success':data['success'],'api_value':data.get('result'),'api_result_present':'result' in data,'actual_history_main':actual});context.close();print('AVL extreme browser/native caller and actual main verified',case,len(steps),flush=True)
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 assert not errors
 (tmp_path/'avl-extreme-browser-review.json').write_text(json.dumps({'rows':rows,'cases':10,'errors':errors,'extra_replay_posts':0,'compiled_programs':compiled,'representation':'existing tree SVG plus individual heap identity and recursive-scope panels; no new view selector'},indent=2),encoding='utf-8')
