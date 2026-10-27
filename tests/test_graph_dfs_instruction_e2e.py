"""Actual DFS browser drawing/cards, scopes, forward/back and generated caller."""
import json,threading,subprocess,shutil,re
import pytest
from app import create_app
from werkzeug.serving import make_server
from _audit_graph_bfs_native_observer import CASES
pytestmark=pytest.mark.e2e

COLLECT=r'''async(count)=>{
 const p=window.bfsPlayer;const rows=[];
 function record(index,direction){rows.push({index,direction,
  heap:[...document.querySelectorAll('[data-bfs-live-node]')].map(n=>({id:n.dataset.bfsLiveNode,next:n.dataset.bfsNext,value:n.dataset.bfsValue,mark:n.dataset.bfsMark})),
  cards:[...document.querySelectorAll('[data-bfs-node]')].map(n=>n.dataset.bfsNode),
  stack:[...document.querySelectorAll('[data-bfs-frame]')].map(n=>n.dataset.bfsFrame),
  variables:[...document.querySelectorAll('[data-bfs-variable]')].map(n=>({name:n.dataset.bfsVariable,scope:n.dataset.bfsScope,text:n.textContent})),
  queue:document.querySelector('[data-bfs-queue]')?.textContent,
  output:document.querySelector('[data-bfs-output]')?.textContent,
  condition:document.querySelector('#graph-condition-view').textContent,
  stdout:document.querySelector('#graph-printf-console').textContent,
  message:document.querySelector('#graph-message-box')?.textContent,
  head:document.querySelector('[data-dfs-head-storage]')?.textContent,liveHead:document.querySelector('[data-dfs-live-head]')?.textContent,
  highlighted:[...document.querySelectorAll('#op-pseudocode .code-line.sim-active')].map(n=>Number(n.dataset.line)),
  svgNodes:document.querySelectorAll('#graph-visual-state circle.viz-graph-node').length});}
 p.reset();record(-1,'initial');
 for(let i=0;i<count;i++){await p.step();record(i,'forward');}
 for(let i=count-2;i>=-1;i--){p.prev();record(i,'back');}
 p.seek(count-1);record(count-1,'seek');return rows;
}'''

@pytest.mark.parametrize('case',[1,3,4,5,6,7,8,9])
def test_dfs_actual_browser_views_and_caller(tmp_path,case):
 c=CASES[case];app=create_app();server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';errors=[]
 try:
  with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
   browser=p.chromium.launch();context=browser.new_context(viewport={'width':1366,'height':1000});page=context.new_page();posts=[]
   page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
   assert context.request.post(base+'/graph/graph/operate',data={'operation':'create_graph','payload':{'directed':True}}).json()['success']
   for v in c['vertices']:assert context.request.post(base+'/graph/graph/operate',data={'operation':'insert_vertex','payload':{'vertex':v}}).json()['success']
   for a,b in c['edges']:assert context.request.post(base+'/graph/graph/operate',data={'operation':'insert_edge','payload':{'origin':a,'target':b,'weight':1}}).json()['success']
   page.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const old=window.InterpreterRuntime.createTracePlayer;window.InterpreterRuntime.createTracePlayer=function(options){const player=old(options);window.bfsPlayer=player;return player;};});")
   page.goto(base+'/graph/graph/recorridos',wait_until='networkidle');page.select_option('#graph-algorithm-select','run_dfs');page.locator('#g-alg-field-start').fill(str(c['start']))
   # Execute through the actual transport handler, then stop automatic playback
   # at a verified instruction boundary; history is recorded exactly once.
   page.evaluate("()=>{const button=document.querySelector('#graph-step-toggle');if(!button.checked){button.checked=true;button.dispatchEvent(new Event('change'));}}")
   with page.expect_response(lambda r:r.url.endswith('/graph/graph/operate') and r.request.method=='POST') as response:page.click('#graph-sim-play')
   data=response.value.json();assert data['success'];trace=data['execution_trace'];steps=trace['steps'];page.evaluate('()=>window.bfsPlayer.pause()');count=len(posts)
   rows=page.evaluate(COLLECT,len(steps))
   for row in rows:
    i=row['index'];ped=steps[i]['pedagogy'] if i>=0 else steps[0]['pedagogy']['initial_frame'];st=ped['memory_state'];heap=st['heap_nodes']
    assert row['heap']==[{'id':n['id'],'next':str(n['next']),'value':str(n.get('value','-')),'mark':str(n.get('mark','-'))} for n in heap]
    assert row['cards']==[n['id'] for n in heap]
    expectedHead=json.dumps(st['head_storage'],ensure_ascii=False,separators=(',',':'));assert row['head']==row['liveHead']==expectedHead
    assert row['stack']==[f['frame_id'] for f in ped['call_stack']]
    assert len(row['variables'])==len(ped['variables'])
    for got,v in zip(row['variables'],ped['variables']):
     assert got['scope']==v['scope'] and got['name']==v['name']
     assert json.dumps(v['previous'],ensure_ascii=False,separators=(',',':')) in got['text']
     assert json.dumps(v['value'],ensure_ascii=False,separators=(',',':')) in got['text']
    assert row['queue']==json.dumps(st['queue'],ensure_ascii=False,separators=(',',':'))
    assert 'Recorrido publicado: '+json.dumps([n['value'] for n in st['result_nodes']],separators=(',',':'))==row['output']
    if ped['condition']:assert ped['condition']['substituted'] in row['condition'] and str(ped['condition']['result']).lower() in row['condition']
    assert row['stdout']=='(sin salida printf en esta ruta)'
    assert row['message']==(data['message'] if i==len(steps)-1 else 'DFS preparado: resultado pendiente hasta completar la traza.')
    assert row['svgNodes']==len(c['vertices'])
    if i>=0:assert steps[i]['line_index'] in row['highlighted']
   assert len(posts)==count and not errors
   # Persist a second identical SUCCESSFUL call; reload preserves two callers,
   # and an invalid start never enters the student program.
   second=context.request.post(base+'/graph/graph/operate',data={'operation':'run_dfs','payload':{'start':c['start']}}).json();assert second['success']
   failure=context.request.post(base+'/graph/graph/operate',data={'operation':'run_dfs','payload':{'start':999}}).json();assert not failure['success'] and failure['history']==second['history']
   programs=[]
   for _ in range(2):
    page.reload(wait_until='networkidle');main='\n'.join(page.locator('.didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');assert main.count('= grafo_dfs(')==2;programs.append(main)
   assert programs[0]==programs[1]
   for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
    for kind,ext in [('source','c'),('header','h')]:
     response=context.request.get(base+'/help/source/'+tad+'/'+kind);assert response.status==200;(tmp_path/(stem+'.'+ext)).write_bytes(response.body())
   (tmp_path/'main.c').write_text(programs[0],encoding='utf-8');exe=tmp_path/'main.exe'
   built=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'main.c'),str(tmp_path/'tad_grafo.c'),str(tmp_path/'tad_cola.c'),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert built.returncode==0 and not built.stderr,built.stderr
   run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert run.returncode==0
   expected='DFS:'+''.join(' '+str(v) for v in data['result']);assert run.stdout.splitlines().count(expected)==2
   if case==1:
    # Reload resets the picker; target DFS explicitly for its rejection case.
    page.select_option('#graph-algorithm-select','run_dfs')
    page.locator('#g-alg-field-start').fill('999')
    page.evaluate("()=>{const button=document.querySelector('#graph-step-toggle');if(!button.checked){button.checked=true;button.dispatchEvent(new Event('change'));}}")
    with page.expect_response(lambda r:r.url.endswith('/graph/graph/operate') and r.request.method=='POST') as rejected:page.click('#graph-sim-play')
    error=rejected.value.json();assert not error['success'] and error['execution_trace']['dfs_application_rejection']
    assert len(error['execution_trace']['steps'])==1 and error['execution_trace']['steps'][0]['pedagogy']['call_stack']==[]
    page.evaluate('()=>{window.bfsPlayer.pause();window.bfsPlayer.seek(0);}')
    assert page.locator('#graph-printf-console').text_content()=='(sin salida printf en esta ruta)'
    current='\n'.join(page.locator('.didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');assert current==programs[0]
    count=len(posts);page.evaluate('()=>{window.bfsPlayer.prev();window.bfsPlayer.seek(0);}')
    assert len(posts)==count and not errors

   (tmp_path/'browser-report.json').write_text(json.dumps({'case':case,'steps':len(steps),'rows':len(rows),'extra_replay_posts':0,'errors':errors,'actual_main_strict_c17':True,'reloaded_identical_calls':2,'stdout':run.stdout},indent=2),encoding='utf-8')
   print('DFS browser/caller',case,len(rows),'states verified',flush=True)
   context.close();browser.close()
 finally:server.shutdown();thread.join(timeout=5)
