"""Actual Bellman-Ford UI callers, statuses and compiled allocation ownership."""
import json
import pytest
from _canonical_graph_browser_contract import private_server,seed,install_player_capture,operate_ui,reload_main_twice,compile_downloaded_main
from _book_frame_oracle import assert_book_body
pytestmark=pytest.mark.e2e
CASES={
 'same_vertex':{'vertices':[-1],'arcs':[],'start':-1,'end':-1,'status':0},
 'negative_alternative':{'vertices':[1,2,3],'arcs':[(1,2,4),(1,3,1),(3,2,-5)],'start':1,'end':2,'status':0},
 'reachable_negative_cycle':{'vertices':[1,2,3,4],'arcs':[(1,2,1),(2,3,-3),(3,2,1),(3,4,1)],'start':1,'end':4,'status':4},
}

@pytest.mark.parametrize('case',list(CASES))
def test_actual_bellman_ford_history_download_and_ownership(tmp_path,case):
 from playwright.sync_api import sync_playwright
 from test_graph_bfs_documentation import run_doxygen
 record=CASES[case];payload={'start':record['start'],'end':record['end']}
 with private_server(tmp_path) as base,sync_playwright() as pw:
  browser=pw.chromium.launch();context=browser.new_context();page=context.new_page();posts=[];errors=[]
  page.on('pageerror',lambda error:errors.append(str(error)))
  page.on('request',lambda request:posts.append(request.url) if request.method=='POST' else None)
  seed(context,base,record['vertices'],record['arcs'])
  install_player_capture(page);page.goto(base+'/graph/graph/camino-minimo',wait_until='networkidle')
  results=[]
  for _ in range(2):
   body,status=operate_ui(page,'run_bellman_ford',payload)
   assert body['c_status']==record['status'] and status==(200 if record['status']==0 else 400)
   assert body['success'] is (record['status']==0)
   assert_book_body(body);results.append(body['result']);before=len(posts)
   page.evaluate('async()=>{const p=window.auditGraphPlayer;p.reset();await p.step();p.prev();p.seek(p.getTotalSteps()-1);}')
   assert len(posts)==before
  assert results[0]==results[1]
  failed,failed_status=operate_ui(page,'run_bellman_ford',{'start':999,'end':record['end']})
  assert failed_status==400 and failed['c_status']==2 and not failed['success']
  assert failed['history'][:-1]==body['history'] and failed['history'][-1]['source_contract']=='graph-book/v1'
  program=reload_main_twice(page,context,base,posts)
  assert program.count('= grafo_bellman_ford(')==3
  assert program.count('grafo_liberar_arcos(&lista_')==3
  native=compile_downloaded_main(context,base,program,tmp_path/'download')
  lines=[line for line in native['stdout'].splitlines() if line.startswith('Bellman-Ford:')]
  if record['status']==4:expected='Bellman-Ford: estado=4'
  elif results[0]['path_arcs']:
   expected='Bellman-Ford: estado=0'+''.join(f' {a}->{b}({w})' for a,b,w in results[0]['path_arcs'])+' | costo='+str(results[0]['distance_to_destination'])
  else:expected='Bellman-Ford: estado=0 (sin arcos; resultado valido) | costo=0'
  assert lines==[expected,expected,'Bellman-Ford: estado=2']
  assert 'Bellman-Ford desde' not in program and not errors
  run_doxygen(tmp_path/'download',[tmp_path/'download/main.c'])
  (tmp_path/'browser-report.json').write_text(json.dumps({'case':case,'actual_calls':3,'repeated_C_calls':2,'failed_C_call_retained':True,'source_contract':'graph-book/v1','replay_reload_POSTs':0,'native':native,'page_errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
  context.close();browser.close()
