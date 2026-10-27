"""Actual RBT insertion views/replay; raw failure cases use an explicit test-only route."""
import copy,json,threading
import pytest
from flask import jsonify
from app import create_app
from werkzeug.serving import make_server
from test_audit_rbt_delete_instruction_native import rbt_delete_instruction_native,pairs,check,prepare_case
from test_audit_avl_validate_e2e import COLLECT as BASE
pytestmark=pytest.mark.e2e
COLLECT=BASE.replace('value:Number(x.dataset.abbValue)',"value:x.dataset.abbValue==='sin inicializar'?'sin inicializar':Number(x.dataset.abbValue)").replace('records.push({direction:dir,index,state:',"records.push({conditionText:document.querySelector('#hier-path-view').textContent,retired:[...document.querySelectorAll('[data-abb-retired-node]')].map(x=>({id:x.dataset.abbRetiredNode,value:Number(x.dataset.abbRetiredValue)})),unusable:[...document.querySelectorAll('[data-abb-alias-usable=false]')].map(x=>({frame:x.dataset.abbAliasFrame,name:x.dataset.abbAlias,target:x.dataset.abbAliasTarget})),svgNodes:[...document.querySelectorAll('[data-rbt-svg-node]')].map(x=>({id:x.dataset.rbtSvgNode,parent:x.dataset.rbtSvgParent,color:x.dataset.rbtSvgColor,initialized:Number(x.dataset.rbtSvgInitialized),red:x.classList.contains('red'),black:x.classList.contains('black')})),svgEdges:[...document.querySelectorAll('[data-rbt-svg-from]')].map(x=>({from:x.dataset.rbtSvgFrom,to:x.dataset.rbtSvgTo,side:x.dataset.rbtSvgSide})),nulls:document.querySelectorAll('.viz-tree-node.nil').length,direction:dir,index,state:")
@pytest.mark.parametrize('case',[70,24,49,32,1,25,0,3,4,9,13,21,6,79,80,81,73])
def test_rbt_delete_actual_views_native_replay(tmp_path,rbt_delete_instruction_native,case):
 report=rbt_delete_instruction_native;meta=prepare_case(report,case);fixture=not meta['present'];app=create_app()
 if fixture:
  data=copy.deepcopy(meta['data']);data.update(success=True,message='Fixture C nativo no-op (no solicitud de producto)',visual_state=meta['instruction_trace']['final_state'],execution_trace=meta['instruction_trace'])
  app.add_url_rule('/audit-native-delete-fixture','audit_native_delete_fixture',lambda:jsonify(data),methods=['POST'])
 server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';errors=[]
 try:
  with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
   browser=p.chromium.launch();context=browser.new_context(viewport={'width':1366,'height':1100});page=context.new_page();posts=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
   for v in meta['seed']:assert context.request.post(base+'/hierarchical/red_black/operate',data={'operation':'insertar','payload':{'value':v}}).json()['success']
   page.goto(base+'/hierarchical/red_black',wait_until='networkidle');assert page.locator('#operation-select option').count()==7
   page.evaluate('()=>{const old=renderHierState;renderHierState=function(...args){window.auditState=structuredClone(args[1]);return old(...args);};}')
   page.locator('#hier-understand-toggle').click();page.select_option('#operation-select','eliminar');page.locator('[name="value"]').fill(str(meta['value']));page.click('#hier-step-mode')
   if fixture:page.evaluate("()=>document.querySelector('form[data-operate-url]').dataset.operateUrl='/audit-native-delete-fixture'")
   endpoint='/audit-native-delete-fixture' if fixture else '/red_black/operate'
   with page.expect_response(lambda r:r.url.endswith(endpoint) and r.request.method=='POST') as response:page.click('#hier-sim-play')
   data=response.value.json();assert data['success'];trace=data['execution_trace'];steps=trace['steps'];events=[e for e in report['events'] if e['case']==case]
   for step,event in pairs(trace,events,report):check(step,event)
   assert set(page.locator('#hier-function-list button').all_text_contents())=={'colorOf','rbt_rotar_dcha','rbt_rotar_izda','transplantar','minimo','arreglarEliminacion','rbt_eliminar','ejecutar_eliminacion'}
   count=len(posts);pending='Eliminacion preparada: resultado pendiente hasta completar la traza.';assert page.locator('#message-box').inner_text()==pending;rows=page.evaluate(COLLECT,{'steps':len(steps)})
   for row in rows:
    i=row['index'];ped=steps[i]['pedagogy'] if i>=0 else steps[0]['pedagogy']['initial_frame'];st=ped['memory_state'];assert row['state']==st
    if ped['condition']:assert ped['condition']['substituted'] in row['conditionText'] and str(ped['condition']['result']).lower() in row['conditionText']
    assert row['stdout']==st['console_stdout'];assert row['message']==(data['message'] if i==len(steps)-1 else pending)
    assert row['nodes']==[{k:n[k] for k in ['id','value','left','right','status']} for n in st['heap_nodes']]
    assert row['svgNodes']==[{'id':n['id'],'parent':n['parent'],'color':n['color'],'initialized':n['initialized'],'red':n['color']=='RED','black':n['color']=='BLACK'} for n in st['heap_nodes']]
    live={n['id'] for n in st['heap_nodes']};edges=[{'from':n['id'],'to':n[side],'side':side} for n in st['heap_nodes'] for side in ['left','right'] if n[side] in live or n[side]=='NULL'];assert sorted((e['from'],e['side'],e['to']) for e in row['svgEdges'])==sorted((e['from'],e['side'],e['to']) for e in edges);assert row['nulls']==sum(e['to']=='NULL' for e in edges)
    assert sorted(x for x in row['treeValues'] if x!='NULL')==sorted(str(n['value']) for n in st['heap_nodes'])
    for n,card in zip(st['heap_nodes'],row['cards']):assert 'padre: '+n['parent'] in card and 'color: '+n['color'] in card
    assert row['aliases']==[{'frame':f['id'],'name':name,'type':'int' if name in ['key','es_izq'] else 'char' if name=='y_color_original' else 'RBT *' if name in ['arbol','root','r'] else 'RBT','target':str(v)} for f in st['tree_frames'] for name,v in {**f['parameters'],**f['locals']}.items()]
    assert row['retired']==[{'id':n['id'],'value':n['value']} for n in st['freed_nodes']]
    assert row['unusable']==[{'frame':f['id'],'name':name,'target':str(v)} for f in st['tree_frames'] for name,v in {**f['parameters'],**f['locals']}.items() if 'valor indeterminado' in str(v)]
    assert row['variables']==[{'scope':v['scope'],'previous':str(v['previous']),'value':str(v['value']),'type':v['type']+' '+v['name']} for v in ped['variables']];assert row['stack']==len(ped['call_stack'])
    if i>=0:assert steps[i]['line_index'] in row['highlighted']
    assert st['validation'] is None  and not ped['return_propagation']['reconnects_subtree']
   assert len(posts)==count and not errors
   if case in [1,9,13,70]:page.screenshot(path=str(tmp_path/f'rbt-delete-{case}.png'),full_page=True)
   context.close();browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (tmp_path/'rbt-delete-browser-review.json').write_text(json.dumps({'case':case,'native_fixture_only':fixture,'rows':len(rows),'steps':len(steps),'extra_replay_posts':0,'errors':errors,'ownership_cleanup':'outside observed deletion; prior actual-main ownership check closed separately'},indent=2),encoding='utf-8');print('RBT delete actual views verified',case,len(rows),flush=True)
