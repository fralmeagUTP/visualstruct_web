"""Rojo-Negro cleanup lifetime records, recursive scopes, true caller NULL and replay."""
import json,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
from test_audit_rbt_clear_instruction_native import rbt_clear_native,clear_matches,case_events
from test_audit_rbt_queries_main_e2e import compile_main
from test_audit_rbt_clear_main_e2e import observe_program_memory
pytestmark=pytest.mark.e2e

def test_clear_browser_free_alias_root_scopes_replay_and_actual_main(tmp_path,rbt_clear_native):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[];errors=[];compiled=[]
 try:
  with sync() as p:
   browser=p.chromium.launch()
   for case in range(10):
    meta=rbt_clear_native['cases'][case%5];context=browser.new_context(viewport={'width':1366,'height':1000});page=context.new_page();posts=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
    for value in meta['seed']:assert context.request.post(base+'/hierarchical/red_black/operate',data={'operation':'insertar','payload':{'value':value}}).json()['success']
    if case>=5:assert context.request.post(base+'/hierarchical/red_black/operate',data={'operation':'limpiar','payload':{}}).json()['success']
    page.goto(base+'/hierarchical/red_black',wait_until='networkidle');assert page.locator('#operation-select option').count()==7
    page.evaluate('''()=>{const old=renderHierState;renderHierState=function(...args){window.auditState=structuredClone(args[1]);return old(...args);};}''')
    page.locator('#hier-understand-toggle').click();page.select_option('#operation-select','limpiar');page.click('#hier-step-mode')
    with page.expect_response(lambda r:r.url.endswith('/red_black/operate') and r.request.method=='POST') as response:page.click('#hier-sim-play')
    data=response.value.json();assert data['success'];count=len(posts);trace=data['execution_trace'];steps=trace['steps'];assert page.locator('#message-box').inner_text()=='Limpieza preparada: resultado pendiente hasta completar la traza.'
    events=case_events(rbt_clear_native,case);oracle={s['step_index']:e for e,s in clear_matches(trace,events)}
    for direction,selector,indices in [('forward','#hier-sim-step',range(len(steps))),('backward','#hier-sim-prev',range(len(steps)-2,-2,-1))]:
     for index in indices:
      assert page.locator(selector).is_enabled();page.locator(selector).evaluate('b=>b.click()');page.wait_for_function("n=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
      state=page.evaluate('window.auditState');expected=steps[index]['pedagogy']['memory_state'] if index>=0 else steps[0]['state_snapshot'];assert state==expected
      assert page.locator('#hier-printf-console').text_content()==state['console_stdout']
      assert page.locator('#message-box').inner_text()==(data['message'] if index==len(steps)-1 else 'Limpieza preparada: resultado pendiente hasta completar la traza.')
      heap=page.locator('[data-abb-node]').evaluate_all("xs=>xs.map(x=>({id:x.dataset.abbNode,value:Number(x.dataset.abbValue),left:x.dataset.abbLeft,right:x.dataset.abbRight,status:x.dataset.abbStatus}))");assert heap==[{k:v for k,v in n.items() if k not in ['parent','color']} for n in state['heap_nodes']];assert page.locator('[data-abb-head]').get_attribute('data-abb-head')==state['head'];assert page.locator('[data-abb-caller]').count()==int(state['caller_frame'] is not None)
      for n in state['heap_nodes']:
       card=page.locator('[data-abb-node="'+n['id']+'"]').inner_text();assert 'padre: '+n['parent'] in card and 'color: '+n['color'] in card
      assert page.locator('[data-abb-frame]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.abbFrame,depth:Number(x.dataset.abbDepth)}))')==[{'id':f['id'],'depth':f['depth']} for f in state['tree_frames']]
      aliases=page.locator('[data-abb-alias]').evaluate_all('xs=>xs.map(x=>({frame:x.dataset.abbAliasFrame,name:x.dataset.abbAlias,type:x.dataset.abbAliasType,target:x.dataset.abbAliasTarget}))');assert aliases==[{'frame':f['id'],'name':name,'type':'RBT','target':str(target)} for f in state['tree_frames'] for name,target in {**f['parameters'],**f['locals']}.items()]
      circles=page.locator('[data-rbt-svg-node]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.rbtSvgNode,parent:x.dataset.rbtSvgParent,color:x.dataset.rbtSvgColor,red:x.classList.contains("red"),black:x.classList.contains("black")}))')
      assert circles==[{'id':n['id'],'parent':n['parent'],'color':n['color'],'red':n['color']=='RED','black':n['color']=='BLACK'} for n in state['heap_nodes']]
      live={n['id'] for n in state['heap_nodes']};edges=[]
      for n in state['heap_nodes']:
       for side in ['left','right']:
        if n[side] in live or n[side]=='NULL':edges.append((n['id'],side,n[side]))
      actual_edges=page.locator('[data-rbt-svg-from]').evaluate_all('xs=>xs.map(x=>[x.dataset.rbtSvgFrom,x.dataset.rbtSvgSide,x.dataset.rbtSvgTo])');assert sorted(map(tuple,actual_edges))==sorted(edges)
      assert page.locator('.viz-tree-node.nil').count()==sum(to=='NULL' for _,_,to in edges)
      assert sorted(page.locator('.viz-tree-text:not(.nil)').all_text_contents())==sorted(str(n['value']) for n in state['heap_nodes'])
      assert page.locator('[data-rbt-clear-graph]').count()==1 and state['validation'] is None
      assert page.locator('[data-abb-alias]').evaluate_all('xs=>xs.map(x=>x.dataset.abbAliasUsable)')==[str('valor indeterminado' not in x['target']).lower() for x in aliases]
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
        assert state['console_stdout']==''
        if event['phase']=='return':assert len(state['tree_frames'])==len(event['frames'])-1
        else:assert len(state['tree_frames'])==len(event['frames'])
        # Lifetime annotations are independently checked against native integer IDs in the native tests.
       if ped['instruction_event']['phase']=='caller_exit':assert not state['caller_frame'] and state['head']=='NULL'
      else:assert not variables and not state['tree_frames'] and state['console_stdout']==''
      if case in [2,3] and direction=='forward' and index>=0 and steps[index]['pedagogy']['instruction_event']['phase'] in {'free','caller_resume','caller_assign'}:page.screenshot(path=str(tmp_path/f'rbt-limpiar-{case}-{index}.png'),full_page=True)
      rows.append({'case':case,'operation':'limpiar','direction':direction,'index':index,'console_stdout':state['console_stdout'],'frame_ids':[f['id'] for f in state['tree_frames']],'live_visual_projection':True})
    assert page.locator('#hier-sim-prev').is_disabled();assert len(posts)==count;assert not page.locator('#hier-step-toggle').is_visible() if page.locator('#hier-step-toggle').count() else True
    actual_main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','')
    assert 'rbt_liberar(arbol); arbol = NULL;' in actual_main
    target=tmp_path/f'actual-main-{case}';docs=compile_main(actual_main,context,base,target);assert docs['doxygen_warnings']==0
    operations=1 if case<5 else 2;expected_stdout='\tEl numero ha sido insertado\n'*len(meta['seed'])+'LIMPIAR\n'*operations
    assert docs['stdout']==expected_stdout
    variant=observe_program_memory(target,len(meta['seed']),expected_stdout)
    from test_audit_rbt_clear_equivalent import verify_equivalent
    equivalent=verify_equivalent(trace,rbt_clear_native,case,tmp_path/f'equivalent-{case}',target/'tad_rojo_negro.h')
    compiled.append({'case':case,'actual_generated_main':actual_main,'actual_main':docs,'memory_variant':variant,'equivalent':equivalent});context.close();print('RBT clear replay/callers verified',case,len(steps),flush=True)
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 assert not errors
 (tmp_path/'rbt-clear-browser-review.json').write_text(json.dumps({'rows':rows,'cases':10,'errors':errors,'extra_replay_posts':0,'compiled_callers':compiled,'representation':'existing tree SVG plus individual heap identity and recursive-scope panels; no new view selector'},indent=2),encoding='utf-8')
