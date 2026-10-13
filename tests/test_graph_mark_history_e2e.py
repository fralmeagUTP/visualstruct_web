"""Actual cross-call DFS input marks, reload, mutation and replay without POST."""
import json,threading,subprocess,shutil
import pytest
from app import create_app
from werkzeug.serving import make_server
pytestmark=pytest.mark.e2e

@pytest.mark.parametrize("algorithm", ["dfs", "bfs"])
def test_actual_browser_cross_call_mark_context(tmp_path,algorithm):
 operation="run_"+algorithm;label=algorithm.upper()
 app=create_app();server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
   browser=p.chromium.launch();context=browser.new_context();page=context.new_page();posts=[];errors=[]
   page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
   for op,payload in [('create_graph',{'directed':True}),('insert_vertex',{'vertex':-1}),('insert_vertex',{'vertex':2}),('insert_edge',{'origin':-1,'target':2,'weight':1})]:assert context.request.post(base+'/graph/graph/operate',data={'operation':op,'payload':payload}).json()['success']
   page.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const old=window.InterpreterRuntime.createTracePlayer;window.InterpreterRuntime.createTracePlayer=function(options){const player=old(options);window.markPlayer=player;return player;};});")
   page.goto(base+'/graph/graph/recorridos',wait_until='networkidle');page.select_option('#graph-algorithm-select',operation);page.locator('#g-alg-field-start').fill('-1')
   responses=[]
   for _ in range(2):
    with page.expect_response(lambda r:r.url.endswith('/graph/graph/operate') and r.request.method=='POST') as response:page.click('#graph-sim-play')
    data=response.value.json();assert data['success'];responses.append(data)
   second=responses[-1];assert [n['marked'] for n in second['execution_trace']['steps'][0]['state_snapshot']['nodes']]==[1,1]
   count=len(posts);page.evaluate("()=>{const t=document.querySelector('#graph-step-toggle');if(!t.checked){t.checked=true;t.dispatchEvent(new Event('change'));}window.markPlayer.pause();window.markPlayer.reset();}")
   assert page.locator('[data-bfs-live-node="V-1"]').get_attribute('data-bfs-mark')=='1'
   assert page.locator('[data-bfs-live-node="V2"]').get_attribute('data-bfs-mark')=='1'
   steps=second['execution_trace']['steps'];ix=next(i for i,s in enumerate(steps) if s['pedagogy']['instruction_event']['function']=='grafo_desmarcar' and s['line_text'].strip()=='k->marcado = 0;')
   page.evaluate('(i)=>window.markPlayer.seek(i)',ix)
   assert page.locator('[data-bfs-live-node="V2"]').get_attribute('data-bfs-mark')=='0'
   page.evaluate('(i)=>window.markPlayer.seek(i)',ix-1)
   assert page.locator('[data-bfs-live-node="V2"]').get_attribute('data-bfs-mark')=='1'
   assert len(posts)==count
   for _ in range(2):page.reload(wait_until='networkidle')
   # Native mutations preserve old vertex marks; only the newly allocated
   # vertex starts at zero. The following actual DFS input must show that.
   mutation=context.request.post(base+'/graph/graph/operate',data={'operation':'insert_vertex','payload':{'vertex':99}}).json()
   assert {n['id']:n['marked'] for n in mutation['visual_state']['nodes']}=={'-1':1,'2':1,'99':0}
   page.reload(wait_until='networkidle');page.select_option('#graph-algorithm-select',operation);page.locator('#g-alg-field-start').fill('99')
   with page.expect_response(lambda r:r.url.endswith('/graph/graph/operate') and r.request.method=='POST') as response:page.click('#graph-sim-play')
   third=response.value.json();assert third['result']==[99]
   assert {n['id']:n['marked'] for n in third['execution_trace']['steps'][0]['state_snapshot']['nodes']}=={'-1':1,'2':1,'99':0}
   assert {n['id']:n['marked'] for n in third['visual_state']['nodes']}=={'-1':0,'2':0,'99':1}
   before=len(posts);page.reload(wait_until='networkidle');main='\n'.join(page.locator('.didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');assert main.count('= grafo_'+algorithm+'(')==3
   assert len(posts)==before==3 and not errors
   for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
    for kind,ext in [('source','c'),('header','h')]:
     response=context.request.get(base+'/help/source/'+tad+'/'+kind);assert response.status==200;(tmp_path/(stem+'.'+ext)).write_bytes(response.body())
   (tmp_path/'main.c').write_text(main,encoding='utf-8');exe=tmp_path/'main.exe';built=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'main.c'),str(tmp_path/'tad_grafo.c'),str(tmp_path/'tad_cola.c'),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert built.returncode==0 and not built.stderr,built.stderr
   run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert run.returncode==0;assert [l for l in run.stdout.splitlines() if l.startswith(label+':')]==[label+': -1 2',label+': -1 2',label+': 99']
   (tmp_path/'context-report.json').write_text(json.dumps({'algorithm':algorithm,'calls':3,'extra_replay_reload_POSTs':0,'second_input_marks':[1,1],'after_mutation_input':{'-1':1,'2':1,'99':0},'mark_reset_forward_backward':True,'main_strict_c17':True,'computed_stdout':run.stdout,'errors':errors},indent=2))
   context.close();browser.close()
 finally:server.shutdown();thread.join(timeout=5)
