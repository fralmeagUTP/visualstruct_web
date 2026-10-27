"""Actual deletion SVG/reservations/scopes and instruction replay against native fields."""
from pathlib import Path
import json,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
from test_audit_avl_delete_native import avl_delete_native,check,native_pairs
from test_audit_avl_insert_native import mapping
from test_audit_avl_main_e2e import compile_main
from test_audit_avl_insert_e2e import COLLECT as INSERT_COLLECT
pytestmark=pytest.mark.e2e
COLLECT=INSERT_COLLECT.replace("records.push({svgNodes:","records.push({aliasUsability:[...document.querySelectorAll('[data-abb-alias]')].map(x=>({usable:x.dataset.abbAliasUsable,text:x.textContent})),retiredNodes:[...document.querySelectorAll('[data-abb-retired-node]')].map(x=>({id:x.dataset.abbRetiredNode,value:Number(x.dataset.abbRetiredValue)})),svgNodes:")
VISIBLE=list(range(2,17))
@pytest.mark.parametrize('case',VISIBLE)
def test_avl_delete_native_views_replay_caller_main(tmp_path,avl_delete_native,case):
 meta=avl_delete_native['cases'][case];errors=[];programs=[];server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
   browser=p.chromium.launch();context=browser.new_context(viewport={'width':1366,'height':1100});page=context.new_page();posts=[];page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
   for v in meta['seed']:assert context.request.post(base+'/hierarchical/avl/operate',data={'operation':'insertar','payload':{'value':v}}).json()['success']
   page.goto(base+'/hierarchical/avl',wait_until='networkidle');assert page.locator('#operation-select option').count()==9;page.evaluate('()=>{const old=renderHierState;renderHierState=function(...args){window.auditState=structuredClone(args[1]);return old(...args);};}');page.locator('#hier-understand-toggle').click();page.select_option('#operation-select','eliminar');page.locator('[name="value"]').fill(str(meta['value']));page.click('#hier-step-mode')
   with page.expect_response(lambda r:r.url.endswith('/avl/operate') and r.request.method=='POST') as resp:page.click('#hier-sim-play')
   data=resp.value.json();assert data['success'];steps=data['execution_trace']['steps'];events=[e for e in avl_delete_native['events'] if e['case']==case];ids=mapping(events);base_id=events[1]['frames'][0]['id']-1;oracle={s['step_index']:e for s,e in native_pairs(data['execution_trace'],events,avl_delete_native['source_lines'])};count=len(posts)
   pending='Eliminacion preparada: resultado pendiente hasta completar la traza.';assert page.locator('#message-box').inner_text()==pending;rows=page.evaluate(COLLECT,{'steps':len(steps)})
   for row in rows:
    i=row['index'];ped=steps[i]['pedagogy'] if i>=0 else steps[0]['pedagogy']['initial_frame'];st=row['state'];assert st==ped['memory_state'];assert row['stdout']=='';assert row['message']==(data['message'] if i==len(steps)-1 else pending)
    assert row['nodes']==[{k:v for k,v in n.items() if k not in ['parent','balance_factor']} for n in st['heap_nodes']]
    assert row['svgNodes']==[{'id':n['id'],'status':n['status'],'parent':str(n['parent']),'fe':str(n['balance_factor'])} for n in st['heap_nodes']]
    expectedEdges=[{'from':n['id'],'to':n[side],'side':side} for n in st['heap_nodes'] for side in ['left','right'] if n[side] in {q['id'] for q in st['heap_nodes']}];assert row['svgEdges']==expectedEdges
    assert sorted(row['treeValues'])==sorted(str(n['value']) for n in st['heap_nodes'])
    for n,card in zip(st['heap_nodes'],row['cards']):assert 'padre: '+n['parent'] in card and 'FE: '+str(n['balance_factor']) in card
    assert row['aliases']==[{'frame':f['id'],'name':name,'type':'int' if name in ['x','tmp','feL','feR','altIzq','altDer'] else 'AVL *' if name=='r' or (name=='raiz' and f['function'] in ['avl_eliminar','rebalancearTrasEliminar']) else 'AVL','target':str(v)} for f in st['tree_frames'] for name,v in {**f['parameters'],**f['locals']}.items()]
    assert row['retiredNodes']==[{'id':n['id'],'value':n['value']} for n in st['freed_nodes']]
    flat=[v for f in st['tree_frames'] for v in {**f['parameters'],**f['locals']}.values()];dead={n['id'] for n in st['freed_nodes']}
    assert [x['usable'] for x in row['aliasUsability']]==['false' if v in dead else 'true' for v in flat]
    for v,x in zip(flat,row['aliasUsability']):assert ('vida terminada; no desreferenciar' in x['text'])==(v in dead)
    assert row['variables']==[{'scope':v['scope'],'previous':str(v['previous']),'value':str(v['value']),'type':v['type']+' '+v['name']} for v in ped['variables']];assert row['stack']==len(ped['call_stack'])
    if i>=0:
     assert steps[i]['line_index'] in row['highlighted']
     if i in oracle:steps[i]['_source_lines']=data['execution_trace']['source_code'].splitlines();check(steps[i],oracle[i],ids,base_id,avl_delete_native['source_lines'],data['execution_trace']['source_code'].splitlines())
    assert ped['invariant']['holds'] is None
   assert len(posts)==count and not errors
   # Exact displayed void caller compiles against current downloaded implementation.
   caller='/**\n * @brief Invoca Eliminar'+data['execution_trace']['source_code'].split('/**\n * @brief Invoca Eliminar',1)[1]
   main='#include "tad_avl.h"\n#include <stdio.h>\n'+caller+'\n/** @brief Reproduce el estado inicial y llama a Eliminar. @return 0. */\nint main(void){AVL root=NULL;'+''.join('avl_insertar(&root,'+str(v)+');' for v in meta['seed'])+'ejecutar_eliminacion(&root);avl_verArbol(root,0);avl_liberarAVL(root);return 0;}'
   caller_program=compile_main(main,context,base,tmp_path/'shown-caller')
   def printed(n,depth=0):return '' if n is None else printed(n['right'],depth+1)+'   '*depth+str(n['value'])+'\n'+printed(n['left'],depth+1)
   assert caller_program['stdout']==printed(data['visual_state']['root']);programs.append({'caller':caller_program})
   mains=[]
   for label in ['before','after']:
    main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');assert main.count('avl_insertar(&arbol,')==len(meta['seed']) and main.count('avl_eliminar(&arbol,')==1;program=compile_main(main,context,base,tmp_path/('history-'+label));assert program['stdout'].splitlines()==['INSERTAR invocado: '+str(v) for v in meta['seed']]+['ELIMINAR invocado: '+str(meta['value'])];programs.append({label:program});mains.append(main)
    if label=='before':count=len(posts);page.reload(wait_until='networkidle');assert len(posts)==count
   assert mains[0]==mains[1]
   if case in [0,5,7]:page.screenshot(path=str(tmp_path/f'deletion-{case}.png'),full_page=True)
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (tmp_path/'avl-delete-browser-review.json').write_text(json.dumps({'case':case,'rows':[{'direction':x['direction'],'index':x['index'],'nodes':len(x['state']['heap_nodes']),'root':x['state']['head'],'frames':len(x['state']['tree_frames'])} for x in rows],'programs':programs,'errors':errors,'extra_replay_posts':0},indent=2),encoding='utf-8');print('AVL delete browser verified',case,len(rows),flush=True)

@pytest.mark.parametrize('seed,target',[([],7),([10],99),([10,5,15],99)])
def test_avl_delete_rejected_request_is_application_explanation(tmp_path,seed,target):
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
   browser=p.chromium.launch();context=browser.new_context();page=context.new_page();posts=[];errors=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
   for v in seed:assert context.request.post(base+'/hierarchical/avl/operate',data={'operation':'insertar','payload':{'value':v}}).json()['success']
   page.goto(base+'/hierarchical/avl',wait_until='networkidle');page.select_option('#operation-select','eliminar');page.locator('[name="value"]').fill(str(target));page.click('#hier-step-mode')
   with page.expect_response(lambda r:r.url.endswith('/avl/operate') and r.request.method=='POST') as response:page.click('#hier-sim-play')
   assert response.value.status==400;data=response.value.json();assert not data['success'] and data['execution_trace']['application_precondition_rejected'];count=len(posts)
   page.click('#hier-sim-step');assert page.locator('#hier-sim-counter').inner_text().startswith('Paso: 1/1');assert page.locator('#message-box').inner_text()==data['message'];assert page.locator('#hier-stack-view .hier-stack-frame').count()==0;assert page.locator('#hier-printf-console').inner_text()=='(sin salida printf en esta ruta)';assert all(step['console']==[] for step in data['execution_trace']['steps'])
   assert page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').all_text_contents()==[data['execution_trace']['steps'][0]['line_text']]
   page.click('#hier-sim-prev');assert page.locator('#hier-sim-counter').inner_text().startswith('Paso: 0/1') and len(posts)==count;assert not errors
   main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');assert 'avl_eliminar(&arbol,' not in main and main.count('avl_insertar(&arbol,')==len(seed);program=compile_main(main,context,base,tmp_path/'rejection-main')
   assert program['stdout'].splitlines()==['INSERTAR invocado: '+str(v) for v in seed]
   context.close();browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (tmp_path/'avl-delete-rejection-browser-review.json').write_text(json.dumps({'seed':seed,'target':target,'C_invoked':False,'forward_backward_explanation_states':2,'extra_posts':0,'program':program,'errors':errors},indent=2),encoding='utf-8')
