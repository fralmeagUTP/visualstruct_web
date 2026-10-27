import pytest
@pytest.mark.parametrize('weight',[None,'','  '])
def test_existing_adapter_default_weight_has_faithful_C_caller(client,weight,tmp_path):
 from app.adapters.graph_adapter import GraphAdapter
 assert GraphAdapter._parse_weight({'weight':weight})==1
 assert client.post('/graph/graph/operate',json={'operation':'create_graph','payload':{'directed':True}}).status_code==200
 response=client.post('/graph/graph/operate',json={'operation':'insert_edge','payload':{'origin':1,'target':2,'weight':weight}})
 assert response.status_code==200
 body=response.get_json();assert body['success'] and body['visual_state']['edges'][0]['weight']==1
 assert 'Grafo grafo_insertar_arco' in body['execution_trace']['source_code']
 assert 'GrafoEstado *estado' in body['execution_trace']['source_code']
 import subprocess,shutil
 response=client.get('/help/source/graph/main');assert response.status_code==200
 main=response.data.decode('utf-8');assert main==body['main_c'] and 'grafo_insertar_arco(g, 1, 2, 1, &estado_' in main
 for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
  for kind,ext in [('source','c'),('header','h')]:
   response=client.get('/help/source/'+tad+'/'+kind);assert response.status_code==200;(tmp_path/(stem+'.'+ext)).write_bytes(response.data)
 marker='    grafo_destruir(&g);';index=main.rfind(marker);assert index>=0
 observed=main[:index]+'    for (ListaArco it = g.a; it != NULL; it = it->sig) printf("DEFAULT %d\\n", it->costo);\n'+main[index:]
 for name,code in [('actual',main),('observer',observed)]:
  path=tmp_path/(name+'.c');path.write_text(code,encoding='utf-8');exe=tmp_path/(name+'.exe')
  built=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(path),str(tmp_path/'tad_grafo.c'),str(tmp_path/'tad_cola.c'),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert built.returncode==0 and not built.stderr,built.stderr
  run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert run.returncode==0 and not run.stderr
  assert run.stdout==('insert_edge: estado=0\nDEFAULT 1\n' if name=='observer' else 'insert_edge: estado=0\n')
