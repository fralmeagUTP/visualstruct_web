"""Actual SVG plus reservations/frames panels: all native steps and bidirectional replay."""
from pathlib import Path
import json,threading,shutil,subprocess
import pytest
from app import create_app
from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.services.c_code_service import CCodeService
from werkzeug.serving import make_server
from test_audit_avl_validate_native import avl_validate_native,CASES,fixture
from test_audit_avl_main_e2e import compile_main
pytestmark=pytest.mark.e2e
COLLECT=r'''async ({steps})=>{
 const records=[];const selectors=['#hier-sim-step','#hier-sim-prev'];
 const treeValues=n=>n?[String(n.value),...treeValues(n.left),...treeValues(n.right)]:[];
 for(const dir of ['forward','backward']){
  const indices=dir==='forward'?Array.from({length:steps},(_,i)=>i):Array.from({length:steps},(_,i)=>steps-2-i);
  for(const index of indices){
   const button=document.querySelector(selectors[dir==='forward'?0:1]);
   const start=performance.now();while(button.disabled){if(performance.now()-start>5000)throw Error('disabled '+dir+' '+index);await new Promise(r=>setTimeout(r,5));}
   button.click();const text='Paso: '+(index+1)+'/';
   while(!document.querySelector('#hier-sim-counter').textContent.startsWith(text)){if(performance.now()-start>5000)throw Error('counter '+dir+' '+index);await new Promise(r=>setTimeout(r,5));}
   records.push({direction:dir,index,state:structuredClone(window.auditState),
    nodes:[...document.querySelectorAll('[data-abb-node]')].map(x=>({id:x.dataset.abbNode,value:Number(x.dataset.abbValue),left:x.dataset.abbLeft,right:x.dataset.abbRight,status:x.dataset.abbStatus})),
    cards:[...document.querySelectorAll('[data-abb-node]')].map(x=>x.textContent),
    frames:[...document.querySelectorAll('[data-abb-frame]')].map(x=>({id:x.dataset.abbFrame,depth:Number(x.dataset.abbDepth)})),
    aliases:[...document.querySelectorAll('[data-abb-alias]')].map(x=>({frame:x.dataset.abbAliasFrame,name:x.dataset.abbAlias,type:x.dataset.abbAliasType,target:x.dataset.abbAliasTarget})),
    variables:[...document.querySelectorAll('#hier-variables-view tbody tr')].map(x=>({scope:x.querySelector('small').textContent,previous:x.children[1].textContent,value:x.children[2].textContent,type:x.children[0].querySelector('code').textContent})),
    stack:document.querySelectorAll('#hier-stack-view .hier-stack-frame').length,
    stdout:document.querySelector('#hier-printf-console').textContent,
    message:document.querySelector('#message-box').textContent,
    highlighted:[...document.querySelectorAll('#op-pseudocode .sim-active,#op-pseudocode .sim-done')].map(x=>Number(x.dataset.line)),
    treeValues:[...document.querySelectorAll('.viz-tree-text')].map(x=>x.textContent),
    heightResult:document.querySelector('[data-avl-height-result]')?.textContent??null,
    backendResult:document.querySelector('[data-avl-backend-validation]')?.textContent??null});
  }
 }
 return records;
}'''
@pytest.mark.parametrize('case',range(len(CASES)))
def test_avl_validar_native_views_and_replay(tmp_path,avl_validate_native,monkeypatch,case):
 meta=CASES[case];forged='tree' in meta;errors=[];programs=[]
 if forged:
  original=HierarchicalStructureService._new_adapter
  monkeypatch.setattr(HierarchicalStructureService,'_new_adapter',staticmethod(lambda sid:fixture(case) if sid=='avl' else original(sid)))
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
   browser=p.chromium.launch();context=browser.new_context(viewport={'width':1366,'height':1100});page=context.new_page();posts=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
   for v in meta.get('seed',[]):assert context.request.post(base+'/hierarchical/avl/operate',data={'operation':'insertar','payload':{'value':v}}).json()['success']
   page.goto(base+'/hierarchical/avl',wait_until='networkidle');assert page.locator('#operation-select option').count()==9
   page.evaluate('()=>{const old=renderHierState;renderHierState=function(...args){window.auditState=structuredClone(args[1]);return old(...args);};}')
   page.locator('#hier-understand-toggle').click();page.select_option('#operation-select','validar');page.click('#hier-step-mode')
   with page.expect_response(lambda r:r.url.endswith('/avl/operate') and r.request.method=='POST') as resp:page.click('#hier-sim-play')
   data=resp.value.json();assert data['success'];steps=data['execution_trace']['steps'];native=[e for e in avl_validate_native['events'] if e['case']==case];assert len(steps)==len(native);count=len(posts)
   pending='Validacion preparada: resultado pendiente hasta completar la traza.';assert page.locator('#message-box').inner_text()==pending
   rows=page.evaluate(COLLECT,{'steps':len(steps)})
   for row in rows:
    i=row['index'];st=row['state'];ped=steps[i]['pedagogy'] if i>=0 else steps[0]['pedagogy']['initial_frame'];expected=ped['memory_state'];assert st==expected
    assert row['nodes']==[{k:v for k,v in n.items() if k not in ['parent','balance_factor']} for n in st['heap_nodes']]
    for n,card in zip(st['heap_nodes'],row['cards']):assert 'padre: '+n['parent'] in card and 'FE: '+str(n['balance_factor']) in card
    assert row['frames']==[{'id':f['id'],'depth':f['depth']} for f in st['tree_frames']]
    assert row['aliases']==[{'frame':f['id'],'name':name,'type':'AVL' if name in ['arbol','nodo'] else 'int','target':str(v)} for f in st['tree_frames'] for name,v in {**f['parameters'],**f['locals']}.items()]
    assert row['variables']==[{'scope':v['scope'],'previous':str(v['previous']),'value':str(v['value']),'type':v['type']+' '+v['name']} for v in ped['variables']]
    assert row['stack']==len(ped['call_stack']) and row['stdout']==st['console_stdout']==''
    def values(n):return [] if n is None else [str(n['value']),*values(n['left']),*values(n['right'])]
    assert sorted(row['treeValues'])==sorted(values(st['root'])) and st['root']==data['visual_state']['root']
    assert row['message']==(data['message'] if i==len(steps)-1 else pending)
    if i>=0:
     e=native[i];assert st['tree_frames']==e['frames'] and steps[i]['line_index']==e['source_index'] and e['source_index'] in row['highlighted']
    if st['wrapper_result'] is None:assert row['heightResult'] is None and row['backendResult'] is None
    else:
     assert ('correcto' if st['wrapper_result'] else 'incorrecto') in row['heightResult'];assert ('OK' if data['result'] else 'ERROR') in row['backendResult']
   assert len(posts)==count and not errors and page.locator('#hier-sim-prev').is_disabled()
   # Actual shown canonical helper/caller, excluding duplicate public-height definition, compiles with HTTP C/H.
   caller=data['execution_trace']['source_code'].split('/**\n * @brief Expone equilibrio',1)[1];caller='/**\n * @brief Expone equilibrio'+caller
   helper=CCodeService.get_structure_data('avl')['operations']['validar'];main='#include "tad_avl.h"\n#include <stdio.h>\n'+helper+'\n'+caller+'\nint main(void){AVL root=NULL;'+''.join('avl_insertar(&root,'+str(v)+');' for v in meta.get('seed',[]))+'printf("%d\\n",ejecutar_equilibrio(root));avl_liberarAVL(root);return 0;}'
   if not forged:
    review=compile_main(main,context,base,tmp_path/'shown-caller');assert review['stdout']=='1\n';programs.append({'shown_caller':review})
    page.click('#hier-step-mode');page.wait_for_function("()=>!document.querySelector('#hier-sim-play').disabled")
    with page.expect_response(lambda r:r.url.endswith('/avl/operate') and r.request.method=='POST'):page.click('#hier-sim-play')
    page.wait_for_function("()=>!document.querySelector('#hier-sim-play').disabled")
    mains=[]
    for label in ['before','after']:
     main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');assert main.count(helper)==1 and main.count('= avl_validar_fes(arbol);')==2
     result=compile_main(main,context,base,tmp_path/('history-'+label));assert result['stdout'].splitlines().count('EQUILIBRIO POR ALTURAS: correcto')==2;programs.append({label:result});mains.append(main)
     if label=='before':count=len(posts);page.reload(wait_until='networkidle');assert len(posts)==count
    assert mains[0]==mains[1]
   if case in [6,9]:page.screenshot(path=str(tmp_path/f'validar-{case}.png'),full_page=True)
   context.close();browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (tmp_path/'avl-validate-browser-review.json').write_text(json.dumps({'case':case,'rows':[{'index':x['index'],'direction':x['direction'],'frames':len(x['state']['tree_frames']),'height_result':x['heightResult'],'backend_result':x['backendResult']} for x in rows],'programs':programs,'errors':errors,'extra_replay_posts':0,'forged':forged},indent=2),encoding='utf-8');print('AVL validar browser verified',case,len(rows),flush=True)
