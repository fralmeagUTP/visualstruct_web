"""Bounded actual browser QA for four source-derived numeric C traces."""
from pathlib import Path
import json,threading,subprocess,shutil,os
import pytest
from app import create_app
from app.domain.graph.snapshot_pool import expand_graph_trace
from werkzeug.serving import make_server
pytestmark=pytest.mark.e2e

COLLECT=r"""async(count)=>{
 const p=window.auditGraphPlayer,rows=[];
 function record(index,direction){rows.push({index,direction,
 heap:[...document.querySelectorAll('[data-graph-memory-node]')].map(n=>({id:n.dataset.graphMemoryNode,kind:n.dataset.graphMemoryKind,contents:n.querySelector('code').textContent})),
 stack:[...document.querySelectorAll('[data-graph-frame]')].map(n=>({id:n.dataset.graphFrame,text:n.textContent})),
 variables:[...document.querySelectorAll('[data-graph-variable]')].map(n=>({name:n.dataset.graphVariable,scope:n.dataset.graphScope,text:n.textContent})),
 heads:document.querySelector('[data-graph-heads]')?.textContent,retired:document.querySelector('[data-graph-retired]')?.textContent,
 condition:document.querySelector('#graph-condition-view').textContent,
 stdout:document.querySelector('#graph-printf-console').textContent,message:document.querySelector('#graph-message-box').textContent,
 highlighted:[...document.querySelectorAll('#op-pseudocode .code-line.sim-active')].map(n=>Number(n.dataset.line)),
 svgNodes:document.querySelectorAll('#graph-visual-state circle.viz-graph-node').length});}
 p.reset();record(-1,'initial');
 for(let i=0;i<count;i++){await p.step();record(i,'forward');}
 for(let i=count-2;i>=-1;i--){p.prev();record(i,'back');}
 p.seek(count-1);record(count-1,'seek');return rows;
}"""

def compact(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'))

def verify_player(page,data,posts,vertices):
 trace=expand_graph_trace(data['execution_trace']);steps=trace['steps'];assert trace['execution_started']
 page.wait_for_function('(n)=>window.auditGraphPlayer.getTotalSteps()===n',arg=len(steps));page.evaluate('()=>window.auditGraphPlayer.pause()')
 before=len(posts);rows=page.evaluate(COLLECT,len(steps))
 for row in rows:
  i=row['index'];ped=steps[i]['pedagogy'] if i>=0 else steps[0]['pedagogy']['initial_frame'];st=ped['memory_state']
  assert row['heap']==[{'id':n['id'],'kind':n['kind'],'contents':compact(n.get('fields',n.get('items')))} for n in st['heap_nodes']],(i,row['direction'])
  assert row['heads']=='Grafo prestado: '+compact(st['graph'])
  assert row['retired']=='Retiradas (sólo registro histórico): '+compact(st['retired_objects'])
  assert row['stack']==[{'id':f['frame_id'],'text':f["function"]+': '+f['scope_status']} for f in ped['call_stack']]
  assert len(row['variables'])==len(ped['variables'])
  for got,v in zip(row['variables'],ped['variables']):
   assert got['scope']==v['scope'] and got['name']==v['name']
   assert compact(v['previous']) in got['text'] and compact(v['value']) in got['text']
  if ped['condition']:assert ped['condition']['substituted'] in row['condition'] and str(ped['condition']['result']).lower() in row['condition']
  stdout='\n'.join(line for step in steps[:i+1] for line in step['console']) if i>=0 else ''
  assert row['stdout']==(stdout or '(sin salida printf en esta ruta)'),(i,row['stdout'],stdout)
  assert row['message']==(data['message'] if i==len(steps)-1 else 'Algoritmo preparado: resultado pendiente hasta completar la traza.'),(i,row['message'])
  assert row['svgNodes']==vertices
  if i>=0:assert steps[i]['line_index'] in row['highlighted']
 assert len(posts)==before
 assert not steps[0]['pedagogy']['initial_frame']['memory_state']['frames']
 assert all(s['state_after']['last_result'] is None for s in steps[:-1])
 return {'C_events':len(trace['C_instruction_events']),'steps':len(steps),'DOM_boundaries_verified':len(rows),'replay_POSTs':0,'stdout_event_indices':[i for i,s in enumerate(steps) if s['console']]}

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
   main=lambda:'\n'.join(page.locator('.didactic-history-main .code-line').all_text_contents()).replace('\u00a0','')
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
    assert main()==prior and main().count('= '+function+'(')==2
    assert context.request.get(base+'/help/source/graph/main').body()==prior.encode('utf-8')
    before=len(posts);page.reload(wait_until='networkidle');assert main()==prior and len(posts)==before
   assert not errors;page.screenshot(path=str(out/'page.png'),full_page=True);(out/'page.html').write_text(page.content(),encoding='utf-8')
   for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
    for part,ext in [('source','c'),('header','h')]:
     r=context.request.get(base+'/help/source/'+tad+'/'+part);assert r.status==200;body=r.body();assert body==Path('docs/tads_C',stem+'.'+ext).read_bytes();(out/(stem+'.'+ext)).write_bytes(body)
   build=subprocess.run([shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'main.c'),str(out/'tad_grafo.c'),str(out/'tad_cola.c'),'-o',str(out/'main.exe')],capture_output=True,text=True,timeout=30);(out/'compile.log').write_text(build.stdout+build.stderr,encoding='utf-8');assert build.returncode==0 and not build.stderr,build.stderr
   run=subprocess.run([str(out/'main.exe')],capture_output=True,text=True,encoding='utf-8',timeout=10);assert run.returncode==0;(out/'main.stdout.log').write_text(run.stdout+run.stderr,encoding='utf-8')
   result=data['result'];title={'bellman_ford':'Bellman-Ford','dijkstra':'Dijkstra','prim':'Prim','kruskal':'Kruskal'}[algorithm]
   if directed:
    if result['path_edges']:expected=title+': '+str(result['path_edges'][0][0])+''.join(' -> '+str(a[1]) for a in result['path_edges'])+' | costo='+str(result['distance_to_destination'])
    else:expected=title+': NULL (sin arcos, sin ruta'+(', ciclo negativo' if algorithm=='bellman_ford' else '')+' o error de entrada/memoria)'
   else:expected=title+':'+''.join(f' {a}-{b}({w})' for a,b,w in result['mst_edges'])+' | costo='+str(result['total_weight'])
   assert run.stdout.splitlines().count(expected)==2,(expected,run.stdout)
   report={'algorithm':algorithm,'success_trace':success_report,'cycle_trace':cycle_report,'successful_calls_preserved':2,'reload_POSTs':0,'page_errors':errors,'download_C_H_canonical_bytes':True,'DOM_main_C17_O2_output_equal_API':True,'main_HTTP_download_tested':True,'DOM_HTTP_bytes_equal':True,'session_isolated':True}
   (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');context.close();browser.close()
 finally:server.shutdown();thread.join(timeout=5)
