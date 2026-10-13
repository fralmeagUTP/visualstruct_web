"""Actual insertion SVG/reservations/scopes and instruction replay against native fields."""
from pathlib import Path
import json,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
from test_audit_avl_insert_native import avl_insert_native,mapping,native_pairs,check
from test_audit_avl_main_e2e import compile_main
from test_audit_avl_validate_e2e import COLLECT as VALIDATOR_COLLECT
pytestmark=pytest.mark.e2e
COLLECT=VALIDATOR_COLLECT.replace("value:Number(x.dataset.abbValue)","value:x.dataset.abbValue==='sin inicializar'?'sin inicializar':Number(x.dataset.abbValue)").replace("records.push({direction:dir,index,state:","records.push({svgNodes:[...document.querySelectorAll('[data-avl-svg-node]')].map(x=>({id:x.dataset.avlSvgNode,status:x.dataset.avlSvgStatus,parent:x.dataset.avlSvgParent,fe:x.dataset.avlSvgFe})),svgEdges:[...document.querySelectorAll('[data-avl-svg-from]')].map(x=>({from:x.dataset.avlSvgFrom,to:x.dataset.avlSvgTo,side:x.dataset.avlSvgSide})),direction:dir,index,state:")
VISIBLE=[i for i in range(12) if i!=9]
@pytest.mark.parametrize('case',VISIBLE)
def test_avl_insert_native_views_replay_caller_main(tmp_path,avl_insert_native,case):
 meta=avl_insert_native['cases'][case];errors=[];programs=[];server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
   browser=p.chromium.launch();context=browser.new_context(viewport={'width':1366,'height':1100});page=context.new_page();posts=[];page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
   for v in meta['seed']:assert context.request.post(base+'/hierarchical/avl/operate',data={'operation':'insertar','payload':{'value':v}}).json()['success']
   page.goto(base+'/hierarchical/avl',wait_until='networkidle');assert page.locator('#operation-select option').count()==9;page.evaluate('()=>{const old=renderHierState;renderHierState=function(...args){window.auditState=structuredClone(args[1]);return old(...args);};}');page.locator('#hier-understand-toggle').click();page.select_option('#operation-select','insertar');page.locator('[name="value"]').fill(str(meta['value']));page.click('#hier-step-mode')
   with page.expect_response(lambda r:r.url.endswith('/avl/operate') and r.request.method=='POST') as resp:page.click('#hier-sim-play')
   data=resp.value.json();assert data['success'];steps=data['execution_trace']['steps'];events=[e for e in avl_insert_native['events'] if e['case']==case];ids=mapping(events);base_id=events[1]['frames'][0]['id']-1;oracle={s['step_index']:e for s,e in native_pairs(data['execution_trace'],events,avl_insert_native['source_lines'])};count=len(posts)
   pending='Insercion preparada: resultado pendiente hasta completar la traza.';assert page.locator('#message-box').inner_text()==pending;rows=page.evaluate(COLLECT,{'steps':len(steps)})
   for row in rows:
    i=row['index'];ped=steps[i]['pedagogy'] if i>=0 else steps[0]['pedagogy']['initial_frame'];st=row['state'];assert st==ped['memory_state'];assert row['stdout']=='';assert row['message']==(data['message'] if i==len(steps)-1 else pending)
    assert row['nodes']==[{k:v for k,v in n.items() if k not in ['parent','balance_factor']} for n in st['heap_nodes']]
    assert row['svgNodes']==[{'id':n['id'],'status':n['status'],'parent':str(n['parent']),'fe':str(n['balance_factor'])} for n in st['heap_nodes']]
    expectedEdges=[{'from':n['id'],'to':n[side],'side':side} for n in st['heap_nodes'] for side in ['left','right'] if n[side] in {q['id'] for q in st['heap_nodes']}];assert row['svgEdges']==expectedEdges
    assert sorted(row['treeValues'])==sorted(str(n['value']) for n in st['heap_nodes'])
    for n,card in zip(st['heap_nodes'],row['cards']):assert 'padre: '+n['parent'] in card and 'FE: '+str(n['balance_factor']) in card
    assert row['aliases']==[{'frame':f['id'],'name':name,'type':'int' if name=='x' else 'AVL *' if name in ['raiz','r'] else 'AVL','target':str(v)} for f in st['tree_frames'] for name,v in {**f['parameters'],**f['locals']}.items()]
    assert row['variables']==[{'scope':v['scope'],'previous':str(v['previous']),'value':str(v['value']),'type':v['type']+' '+v['name']} for v in ped['variables']];assert row['stack']==len(ped['call_stack'])
    if i>=0:
     assert steps[i]['line_index'] in row['highlighted']
     if i in oracle:steps[i]['_source_lines']=data['execution_trace']['source_code'].splitlines();check(steps[i],oracle[i],ids,base_id,avl_insert_native['source_lines'])
    assert ped['invariant']['holds'] is None
   assert len(posts)==count and not errors
   # Exact displayed void caller compiles against current downloaded implementation.
   caller='/**\n * @brief Llama al TAD'+data['execution_trace']['source_code'].split('/**\n * @brief Llama al TAD',1)[1]
   main='#include "tad_avl.h"\n#include <stdio.h>\n'+caller+'\n/** @brief Reproduce el estado inicial y llama a Insertar. @return 0. */\nint main(void){AVL root=NULL;'+''.join('avl_insertar(&root,'+str(v)+');' for v in meta['seed'])+'ejecutar_insercion(&root);avl_verArbol(root,0);avl_liberarAVL(root);return 0;}'
   caller_program=compile_main(main,context,base,tmp_path/'shown-caller')
   def printed(n,depth=0):return '' if n is None else printed(n['right'],depth+1)+'   '*depth+str(n['value'])+'\n'+printed(n['left'],depth+1)
   assert caller_program['stdout']==printed(data['visual_state']['root']);programs.append({'caller':caller_program})
   mains=[]
   for label in ['before','after']:
    main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');assert main.count('avl_insertar(&arbol,')==len(meta['seed'])+1;program=compile_main(main,context,base,tmp_path/('history-'+label));assert program['stdout'].splitlines()==['INSERTAR invocado: '+str(v) for v in [*meta['seed'],meta['value']]];programs.append({label:program});mains.append(main)
    if label=='before':count=len(posts);page.reload(wait_until='networkidle');assert len(posts)==count
   assert mains[0]==mains[1]
   if case in [0,5,7]:page.screenshot(path=str(tmp_path/f'insertion-{case}.png'),full_page=True)
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (tmp_path/'avl-insert-browser-review.json').write_text(json.dumps({'case':case,'rows':[{'direction':x['direction'],'index':x['index'],'nodes':len(x['state']['heap_nodes']),'root':x['state']['head'],'frames':len(x['state']['tree_frames'])} for x in rows],'programs':programs,'errors':errors,'extra_replay_posts':0},indent=2),encoding='utf-8');print('AVL insert browser verified',case,len(rows),flush=True)
