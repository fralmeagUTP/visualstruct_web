"""Both existing representations, scopes, highlight, stdout and bidirectional replay."""
import json,os
from pathlib import Path
import pytest
from test_audit_avl_main_e2e import avl_server
from test_audit_rbt_query_instruction_native import rbt_query_native,match,NUMERIC
pytestmark=pytest.mark.e2e
@pytest.fixture(scope='session')
def rbt_query_records(request):
 cache=os.environ.get('AUDIT_RBT_NATIVE_RECORDS')
 if not cache:return request.getfixturevalue('rbt_query_native')
 path=Path(cache);data=json.loads(path.read_text());assert data['cases']==19
 root=Path(__file__).resolve().parents[1];assert (path.parent/'case0/tad_rojo_negro.c').read_bytes().replace(b'\r\r\n',b'\r\n')==(root/'docs/tads_C/tad_rojo_negro.c').read_bytes();assert (path.parent/'case0/tad_rojo_negro.h').read_bytes()==(root/'docs/tads_C/tad_rojo_negro.h').read_bytes()
 return data['records']
@pytest.mark.parametrize('case',[0,1,2,3,8,9,10,11,12,13,14,15,17,18])
def test_rbt_query_browser_instruction_and_replay(avl_server,rbt_query_records,tmp_path,case):
 record=rbt_query_records[case];seed=record['seed'];op=record['operation'];value=record['value'];rows=[]
 with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
  browser=p.chromium.launch();context=browser.new_context(viewport={'width':1366,'height':1000});page=context.new_page();posts=[];errors=[];page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
  for v in seed:assert context.request.post(avl_server+'/hierarchical/red_black/operate',data={'operation':'insertar','payload':{'value':v}}).json()['success']
  page.goto(avl_server+'/hierarchical/red_black',wait_until='networkidle');assert page.locator('#operation-select option').count()==7
  page.evaluate('''()=>{const old=renderHierState;renderHierState=function(...args){window.auditState=structuredClone(args[1]);return old(...args);};}''')
  page.locator('#hier-understand-toggle').click();page.select_option('#operation-select',op)
  if op=='buscar':page.locator('[name="value"]').fill(str(value))
  page.click('#hier-step-mode')
  with page.expect_response(lambda resp:resp.url.endswith('/red_black/operate') and resp.request.method=='POST') as pending:page.click('#hier-sim-play')
  data=pending.value.json();assert data['success'];trace=data['execution_trace'];match(trace,record['events']);steps=trace['steps'];count=len(posts)
  for direction,selector,indices in [('forward','#hier-sim-step',range(len(steps))),('backward','#hier-sim-prev',range(len(steps)-2,-2,-1))]:
   for index in indices:
    assert page.locator(selector).is_enabled();page.locator(selector).evaluate('b=>b.click()');page.wait_for_function("n=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
    state=page.evaluate('window.auditState');expected=steps[index]['pedagogy']['memory_state'] if index>=0 else steps[0]['state_snapshot'];assert state==expected
    assert state['root']==data['visual_state']['root'];assert page.locator('#hier-printf-console').text_content()==state['console_stdout']
    heap=page.locator('[data-abb-node]').evaluate_all("xs=>xs.map(x=>({id:x.dataset.abbNode,value:Number(x.dataset.abbValue),left:x.dataset.abbLeft,right:x.dataset.abbRight}))");assert heap==[{k:n[k] for k in ['id','value','left','right']} for n in state['heap_nodes']]
    for n in state['heap_nodes']:
     text=page.locator('[data-abb-node="'+n['id']+'"]').inner_text();assert 'padre: '+n['parent'] in text and 'color: '+n['color'] in text
    aliases=page.locator('[data-abb-alias]').evaluate_all('xs=>xs.map(x=>({frame:x.dataset.abbAliasFrame,name:x.dataset.abbAlias,type:x.dataset.abbAliasType,target:x.dataset.abbAliasTarget}))');assert aliases==[{'frame':f['id'],'name':k,'type':'int' if k in NUMERIC else 'RBT','target':str(v)} for f in state['tree_frames'] for k,v in {**f['parameters'],**f['locals']}.items()]
    def values(root):return [] if root is None else [str(root['value']),*values(root['left']),*values(root['right'])]
    assert sorted(page.locator('.viz-tree-text').all_text_contents())==sorted(values(state['root'])+(['NULL']*(len(state['heap_nodes'])+1) if state['root'] else []))
    for color in ['RED','BLACK']:assert page.locator('.viz-tree-node.'+color.lower()+':not(.nil)').count()==sum(n['color']==color for n in state['heap_nodes'])
    assert page.locator('.viz-tree-edge').count()==2*len(state['heap_nodes'])
    edges=page.locator('.viz-tree-svg').evaluate_all("""svgs=>svgs.flatMap(svg=>{const nodes=[...svg.querySelectorAll('circle.viz-tree-node')].map(c=>({x:Number(c.getAttribute('cx')),y:Number(c.getAttribute('cy')),nil:c.classList.contains('nil'),label:c.nextElementSibling.textContent}));return [...svg.querySelectorAll('line.viz-tree-edge')].map(e=>{const x1=Number(e.getAttribute('x1')),y1=Number(e.getAttribute('y1')),x2=Number(e.getAttribute('x2')),y2=Number(e.getAttribute('y2'));const a=nodes.find(n=>n.x===x1&&n.y===y1-18),b=nodes.find(n=>n.x===x2&&n.y===y2+(n.nil?14:18));return [a.label,x2<x1?'left':'right',b.label];});})""")
    by_id={n['id']:n for n in state['heap_nodes']};assert sorted(edges)==sorted([[str(n['value']),side,'NULL' if n[side]=='NULL' else str(by_id[n[side]]['value'])] for n in state['heap_nodes'] for side in ['left','right']])
    assert ('resultado pendiente' in page.locator('#message-box').inner_text())==(index<len(steps)-1)
    ped=steps[index]['pedagogy'] if index>=0 else steps[0]['pedagogy']['initial_frame'];variables=page.locator('#hier-variables-view tbody tr').evaluate_all('xs=>xs.map(x=>({scope:x.querySelector("small").textContent,previous:x.children[1].textContent,value:x.children[2].textContent}))');assert variables==[{'scope':v['scope'],'previous':str(v['previous']),'value':str(v['value'])} for v in ped['variables']]
    assert page.locator('#hier-stack-view .hier-stack-frame').count()==len(ped['call_stack'])
    if op=='validar':
     contract=page.locator('[data-rbt-validator-contract]').inner_text();assert 'altura negra y enlaces por identidad' in contract;assert ('pendiente' in contract)==(state['wrapper_result'] is None)
    if index>=0:
     active=page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').evaluate_all('xs=>xs.map(x=>Number(x.dataset.line))');assert steps[index]['line_index'] in active
     if ped['instruction_event']['phase']=='return':assert 'terminado (contexto del retorno)' in page.locator('#hier-stack-view .hier-stack-frame').last.inner_text()
    else:assert not state['tree_frames'] and not variables and state['console_stdout']==''
    rows.append({'direction':direction,'index':index,'frames':[f['id'] for f in state['tree_frames']],'stdout':state['console_stdout']})
  assert len(posts)==count and not errors;context.close();browser.close()
 (tmp_path/'rbt-query-browser-review.json').write_text(json.dumps({'case':case,'operation':op,'seed':seed,'value':value,'rows':rows,'errors':errors,'extra_replay_posts':0},indent=2));print('RBT query browser verified',case,op,len(rows),flush=True)
