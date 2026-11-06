"""Actual private browser download: symmetric caller, zero/selfloop and native C17."""
import pytest
import threading,subprocess,shutil
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
from test_residual97_navigation import reveal_with_public_control

@pytest.mark.e2e
def test_non_directed_main_update_remove_zero_and_self_loop(app,client,tmp_path):
 server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
 history=[('create_graph',{'directed':False}),('insert_vertex',{'vertex':1}),('insert_vertex',{'vertex':2}),('insert_edge',{'origin':1,'target':2,'weight':4}),('insert_edge',{'origin':2,'target':1,'weight':0}),('remove_edge',{'origin':1,'target':2}),('insert_edge',{'origin':1,'target':1,'weight':0}),('run_prim',{'start':1})]
 downloaded={};stdout={}
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch()
   for directed in [False,True]:
    context=browser.new_context()
    for operation,payload in history:
     payload={**payload,'directed':directed} if operation=='create_graph' else payload
     response=context.request.post(base+'/graph/graph/operate',data={'operation':operation,'payload':payload})
     reject=operation=='run_prim'
     assert response.status==(400 if reject else 200)
     data=response.json();assert data['success'] is (not reject)
     if reject:
      assert data['c_status']==(6 if directed else 5)
      assert data['history'][-1]['operation']=='run_prim'
    stdout[directed]=data['console_prefix']+data['console_stdout']
    page=context.new_page();page.goto(base+'/graph/graph/expansion-minima',wait_until='networkidle')
    link=page.locator('#graph-download-main')
    reveal_with_public_control(page,link)
    with page.expect_download() as pending:link.click()
    path=tmp_path/('directed.c' if directed else 'main.c');pending.value.save_as(path)
    assert path.read_bytes()==context.request.get(base+'/help/source/graph/main').body()
    downloaded[directed]=path.read_text(encoding='utf-8');context.close()
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 main=downloaded[False];directed=downloaded[True]
 assert main.count('grafo_insertar_arco(g, 1, 2, 4, &estado_')==1 and main.count('grafo_insertar_arco(g, 2, 1, 4, &estado_')==1
 assert main.count('grafo_insertar_arco(g, 1, 2, 0, &estado_')==1 and main.count('grafo_insertar_arco(g, 2, 1, 0, &estado_')==1
 assert main.count('grafo_insertar_arco(g, 1, 1, 0, &estado_')==1
 assert main.count('grafo_eliminar_arco(g, 1, 2)')==1 and main.count('grafo_eliminar_arco(g, 2, 1)')==1
 assert 'grafo_insertar_arco(g, 2, 1, 4, &estado_' not in directed and 'grafo_eliminar_arco(g, 2, 1)' not in directed
 assert main.count('= grafo_prim(')==directed.count('= grafo_prim(')==1
 for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
  for kind,ext in [('source','c'),('header','h')]:
   response=client.get('/help/source/'+tad+'/'+kind);assert response.status_code==200;(tmp_path/(stem+'.'+ext)).write_bytes(response.data)
 for directed_flag,filename in [(False,'main.c'),(True,'directed.c')]:
  exe=tmp_path/(filename+'.exe');built=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/filename),str(tmp_path/'tad_grafo.c'),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert built.returncode==0 and not built.stderr,built.stderr
  run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert run.returncode==0 and not run.stderr
  assert run.stdout==stdout[directed_flag]
  assert run.stdout.splitlines()[-1]==('Prim: estado=6' if directed_flag else 'Prim: estado=5')
