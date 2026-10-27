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
 from _canonical_graph_browser_contract import verify_player as canonical_verify
 from _graph_trace_contract import decode_graph_http_trace
 data={**data,'execution_trace':decode_graph_http_trace(data['execution_trace'])}
 return canonical_verify(page,data,posts,collector=COLLECT)

@pytest.mark.parametrize('algorithm',['bellman_ford','prim','dijkstra','kruskal'])
def test_numeric_actual_browser_player_history_downloaded_caller(tmp_path,algorithm):
 from _canonical_graph_browser_contract import private_server,seed,install_player_capture,operate_ui,current_main,reload_main_twice,compile_downloaded_main
 from playwright.sync_api import sync_playwright
 out=tmp_path/algorithm;out.mkdir()
 with private_server(out) as base,sync_playwright() as pw:
  browser=pw.chromium.launch();context=browser.new_context(viewport={'width':1366,'height':1000});page=context.new_page();posts=[];errors=[]
  page.on('pageerror',lambda error:errors.append(str(error)))
  page.on('request',lambda request:posts.append(request.url) if request.method=='POST' else None)
  directed=algorithm in {'bellman_ford','dijkstra'};weight=-2147483648 if algorithm=='kruskal' else 2147483647
  seed(context,base,[1,2],[(1,2,weight)],directed)
  install_player_capture(page);page.goto(base+'/graph/graph/'+('camino-minimo' if directed else 'expansion-minima'),wait_until='networkidle')
  operation='run_'+algorithm;payload={} if algorithm=='kruskal' else {'start':1}
  if directed:payload['end']=2
  data,status=operate_ui(page,operation,payload);assert status==200 and data['success'] and data['c_status']==0
  success_report=verify_player(page,data,posts,2)
  second=context.request.post(base+'/graph/graph/operate',data={'operation':operation,'payload':payload,'execution_mode':'normal'}).json()
  assert second['success'] and second['result']==data['result']
  program=reload_main_twice(page,context,base,posts);function='grafo_'+algorithm
  assert program.count('= '+function+'(')==2
  assert program.count('grafo_liberar_arcos(&lista_')==2
  before=len(posts)
  for _ in range(2):assert current_main(page,context,base)==program and len(posts)==before
  other=browser.new_context();empty=other.request.get(base+'/help/source/graph/main')
  assert empty.status==200 and ('= '+function+'(').encode() not in empty.body();other.close()
  native=compile_downloaded_main(context,base,program,out/'download',optimize=True)
  title={'bellman_ford':'Bellman-Ford','dijkstra':'Dijkstra','prim':'Prim','kruskal':'Kruskal'}[algorithm]
  result=data['result'];arcs=result['path_arcs'] if directed else result['mst_edges']
  expected=title+': estado=0'+''.join(f' {a}->{b}({w})' for a,b,w in arcs)+' | costo='+str(result['distance_to_destination'] if directed else result['total_weight'])
  assert native['stdout'].splitlines().count(expected)==2,(expected,native['stdout'])
  cycle_report=None
  if algorithm=='bellman_ford':
   for a,b in [(1,2),(2,1)]:
    response=context.request.post(base+'/graph/graph/operate',data={'operation':'insert_edge','payload':{'origin':a,'target':b,'weight':-2147483648},'execution_mode':'normal'})
    assert response.status==200 and response.json()['success']
   page.reload(wait_until='networkidle')
   cycle,cycle_status=operate_ui(page,operation,payload)
   assert cycle_status==400 and not cycle['success'] and cycle['c_status']==4 and cycle['result']['has_negative_cycle']
   cycle_report=verify_player(page,cycle,posts,2)
   cycle_program=reload_main_twice(page,context,base,posts)
   assert cycle_program.count('= '+function+'(')==3
   assert cycle['history'][-1]['source_contract']=='graph-book/v1'
   cycle_native=compile_downloaded_main(context,base,cycle_program,out/'cycle-download',optimize=True)
   assert cycle_native['stdout'].splitlines().count('Bellman-Ford: estado=4')==1
  assert not errors
  page.screenshot(path=str(out/'page.png'),full_page=True)
  report={'algorithm':algorithm,'source_contract':'graph-book/v1','success_trace':success_report,'cycle_trace':cycle_report,'successful_calls_preserved':2,'failed_C_calls_retained':True,'reload_POSTs':0,'page_errors':errors,'downloaded_main':native,'session_isolated':True}
  (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
  context.close();browser.close()
