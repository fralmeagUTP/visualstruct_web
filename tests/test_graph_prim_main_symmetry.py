"""Actual private browser download: symmetric caller, zero/selfloop and native C17."""
import pytest
import threading,subprocess,shutil
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright

@pytest.mark.e2e
def test_non_directed_main_update_remove_zero_and_self_loop(app,client,tmp_path):
 server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
 history=[('create_graph',{'directed':False}),('insert_vertex',{'vertex':1}),('insert_vertex',{'vertex':2}),('insert_edge',{'origin':1,'target':2,'weight':4}),('insert_edge',{'origin':2,'target':1,'weight':0}),('remove_edge',{'origin':1,'target':2}),('insert_edge',{'origin':1,'target':1,'weight':0}),('run_prim',{'start':1})]
 downloaded={}
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch()
   for directed in [False,True]:
    context=browser.new_context()
    for operation,payload in history:
     payload={**payload,'directed':directed} if operation=='create_graph' else payload
     response=context.request.post(base+'/graph/graph/operate',data={'operation':operation,'payload':payload})
     reject=directed and operation=='run_prim'
     assert response.status==(400 if reject else 200)
     assert response.json()['success'] is (not reject)
    page=context.new_page();page.goto(base+'/graph/graph/expansion-minima',wait_until='networkidle')
    page.locator('#didactic-mode-switch').check()
    page.locator('details.graph-stage').filter(has=page.locator('a[href="/help/source/graph/main"]')).locator('summary').click()
    with page.expect_download() as pending:page.locator('a[href="/help/source/graph/main"]').click()
    path=tmp_path/('directed.c' if directed else 'main.c');pending.value.save_as(path)
    assert path.read_bytes()==context.request.get(base+'/help/source/graph/main').body()
    downloaded[directed]=path.read_text(encoding='utf-8');context.close()
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 main=downloaded[False];directed=downloaded[True]
 assert main.count('grafo_insertar_arco(g, 1, 2, 4)')==1 and main.count('grafo_insertar_arco(g, 2, 1, 4)')==1
 assert main.count('grafo_insertar_arco(g, 1, 2, 0)')==1 and main.count('grafo_insertar_arco(g, 2, 1, 0)')==1
 assert main.count('grafo_insertar_arco(g, 1, 1, 0)')==1
 assert main.count('grafo_eliminar_arco(g, 1, 2)')==1 and main.count('grafo_eliminar_arco(g, 2, 1)')==1
 assert 'grafo_insertar_arco(g, 2, 1, 4)' not in directed and 'grafo_eliminar_arco(g, 2, 1)' not in directed
 assert '= grafo_prim(' not in directed
 for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
  for kind,ext in [('source','c'),('header','h')]:
   response=client.get('/help/source/'+tad+'/'+kind);assert response.status_code==200;(tmp_path/(stem+'.'+ext)).write_bytes(response.data)
 exe=tmp_path/'main.exe';built=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'main.c'),str(tmp_path/'tad_grafo.c'),str(tmp_path/'tad_cola.c'),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert built.returncode==0 and not built.stderr,built.stderr
 run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert run.returncode==0 and run.stdout=='\n el arco a borrar es 1   2Prim: | costo=0\n'
