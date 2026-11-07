"""Bounded actual browser QA for four source-derived numeric C traces."""
from pathlib import Path
import json,threading,subprocess,shutil,os
import pytest
from app import create_app
from app.domain.graph.snapshot_pool import expand_graph_trace
from werkzeug.serving import make_server
pytestmark=pytest.mark.e2e

from _book_graph_browser_contract import main_text, verify_player

@pytest.mark.parametrize('algorithm',['bellman_ford','prim','dijkstra','kruskal'])
def test_numeric_actual_browser_player_history_downloaded_caller(tmp_path,algorithm):
 out=Path(os.environ.get('GRAPH_TRACE_QA_OUT',str(tmp_path)))/algorithm;out.mkdir(parents=True,exist_ok=True)
 app=create_app();server=make_server('127.0.0.1',0,app,threaded=True);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
   browser=p.chromium.launch();context=browser.new_context(viewport={'width':1366,'height':1000});page=context.new_page();posts=[];errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
   def post(operation,payload,success=True):
    r=context.request.post(base+'/graph/graph/operate',data={'operation':operation,'payload':payload});d=r.json();assert d['success']==success;return d
   directed=algorithm in {'bellman_ford','dijkstra'};weight=2147483647 if algorithm!='kruskal' else -2147483648
   post('create_graph',{'directed':directed})
   for v in [1,2]:post('insert_vertex',{'vertex':v})
   post('insert_edge',{'origin':1,'target':2,'weight':weight})
   operation='run_'+algorithm;payload={} if algorithm=='kruskal' else {'start':1}
   if directed:payload['end']=2
   page.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const old=window.InterpreterRuntime.createTracePlayer;window.InterpreterRuntime.createTracePlayer=function(options){const player=old(options);window.auditGraphPlayer=player;return player;};});")
   phase='camino-minimo' if directed else 'expansion-minima'
   page.goto(base+'/graph/graph/'+phase,wait_until='networkidle');page.select_option('#graph-algorithm-select',operation)
   if algorithm!='kruskal':page.locator('#g-alg-field-start').fill('1')
   if directed:page.locator('#g-alg-field-end').fill('2')
   page.evaluate("()=>{const b=document.querySelector('#graph-step-toggle');b.checked=true;b.dispatchEvent(new Event('change'));}")
   with page.expect_response(lambda r:r.url.endswith('/graph/graph/operate') and r.request.method=='POST') as response:page.click('#graph-sim-play')
   data=response.value.json();assert data['success'];success_report=verify_player(page,data,posts,2)
   second=post(operation,payload);assert second['success'];function='grafo_'+algorithm
   main=lambda:main_text(page)
   before=len(posts);programs=[]
   for _ in range(2):
    page.reload(wait_until='networkidle');programs.append(main());assert main().count('= '+function+'(')==2 and len(posts)==before
   assert programs[0]==programs[1]
   for _ in range(2):
    download=context.request.get(base+'/help/source/graph/main');assert download.status==200
    assert download.body()==main().encode('utf-8');assert 'main.c' in download.headers['content-disposition']
    assert download.headers['cache-control']=='private, no-store';assert len(posts)==before
   other=browser.new_context();empty=other.request.get(base+'/help/source/graph/main');assert empty.status==200 and ('= '+function+'(').encode() not in empty.body();other.close()
   text=programs[0];(out/'main.c').write_text(text,encoding='utf-8')
   cycle_report=None
   if algorithm=='bellman_ford':
    post('insert_edge',{'origin':1,'target':2,'weight':-2147483648});post('insert_edge',{'origin':2,'target':1,'weight':-2147483648})
    page.reload(wait_until='networkidle');prior=main();page.select_option('#graph-algorithm-select',operation);page.locator('#g-alg-field-start').fill('1');page.locator('#g-alg-field-end').fill('2')
    page.evaluate("()=>{const b=document.querySelector('#graph-step-toggle');b.checked=true;b.dispatchEvent(new Event('change'));}")
    with page.expect_response(lambda r:r.url.endswith('/graph/graph/operate') and r.request.method=='POST') as response:page.click('#graph-sim-play')
    cycle=response.value.json();assert response.value.status==400 and not cycle['success'] and cycle['result']['has_negative_cycle'];cycle_report=verify_player(page,cycle,posts,2)
    assert main()!=prior and main().count('= '+function+'(')==3
    assert cycle['history'][-1]['operation']==operation and cycle['c_status']==4
    prior=main()
    assert context.request.get(base+'/help/source/graph/main').body()==prior.encode('utf-8')
    before=len(posts);page.reload(wait_until='networkidle');assert main()==prior and len(posts)==before
   assert not errors;page.screenshot(path=str(out/'page.png'),full_page=True);(out/'page.html').write_text(page.content(),encoding='utf-8')
   for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
    for part,ext in [('source','c'),('header','h')]:
     r=context.request.get(base+'/help/source/'+tad+'/'+part);assert r.status==200;body=r.body();assert body==Path('docs/tads_C',stem+'.'+ext).read_bytes();(out/(stem+'.'+ext)).write_bytes(body)
   build=subprocess.run([shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'main.c'),str(out/'tad_grafo.c'),str(out/'tad_cola.c'),'-o',str(out/'main.exe')],capture_output=True,text=True,timeout=30);(out/'compile.log').write_text(build.stdout+build.stderr,encoding='utf-8');assert build.returncode==0 and not build.stderr,build.stderr
   run=subprocess.run([str(out/'main.exe')],capture_output=True,text=True,encoding='utf-8',timeout=10);assert run.returncode==0;(out/'main.stdout.log').write_text(run.stdout+run.stderr,encoding='utf-8')
   result=data['result'];title={'bellman_ford':'Bellman-Ford','dijkstra':'Dijkstra','prim':'Prim','kruskal':'Kruskal'}[algorithm]
   arcs=result['path_arcs'] if directed else result['mst_edges']
   cost=result['distance_to_destination'] if directed else result['total_weight']
   assert arcs  # All four fixtures have one actual result arc.
   expected=title+': estado=0'+''.join(f' {a}->{b}({w})' for a,b,w in arcs)+' | costo='+str(cost)
   assert run.stdout.splitlines().count(expected)==2,(expected,run.stdout)
   assert run.stdout==second['console_prefix']+second['console_stdout']
   report={'algorithm':algorithm,'success_trace':success_report,'cycle_trace':cycle_report,'successful_calls_preserved':2,'reload_POSTs':0,'page_errors':errors,'download_C_H_canonical_bytes':True,'DOM_main_C17_O2_output_equal_API':True,'main_HTTP_download_tested':True,'DOM_HTTP_bytes_equal':True,'session_isolated':True}
   (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');context.close();browser.close()
 finally:server.shutdown();thread.join(timeout=5)
