"""Fresh downloaded Dijkstra docs and independently invoked native helper contracts."""
from pathlib import Path
import subprocess,shutil,json,hashlib
from test_graph_bfs_documentation import run_doxygen

def test_dijkstra_download_contracts_helpers_and_guide(client,tmp_path):
 files=[]
 for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
  for part,ext in [('source','c'),('header','h')]:
   r=client.get('/help/source/'+tad+'/'+part);assert r.status_code==200;p=tmp_path/(stem+'.'+ext);p.write_bytes(r.data);files.append(p)
 root=Path(__file__).resolve().parents[1]
 for p in files:
  assert p.read_bytes()==(root/'docs'/'tads_C'/p.name).read_bytes()
 source=(tmp_path/'tad_grafo.c').read_text(encoding='utf-8-sig')
 header=(tmp_path/'tad_grafo.h').read_text(encoding='utf-8-sig')
 assert 'grafo_dijkstra(' in source and 'GrafoEstado *estado' in header
 assert 'GRAFO_PESO_NEGATIVO' in source and 'sumar_seguro' in source
 guide=(root/'docs/USER_GUIDE.md').read_text(encoding='utf-8')
 assert 'GrafoEstado' in guide and 'Dijkstra' in guide
 run_doxygen(tmp_path,files)
 # Static helpers remain private in the student source; same translation unit
 # invokes their real bodies. No algorithm is reimplemented in this observer.
 main=r"""#include "tad_grafo.c"
#include <assert.h>
int main(void){
 GrafoEstado estado=GRAFO_OK; Grafo g=grafo_crear(); Trabajo t;
 assert(!preparar(g,&t,&estado));assert(estado==GRAFO_NO_EXISTE&&t.n==0);liberar_trabajo(&t);
 g=grafo_insertar_vertice(g,-1,&estado);assert(estado==GRAFO_OK);
 g=grafo_insertar_vertice(g,7,&estado);assert(estado==GRAFO_OK);
 assert(preparar(g,&t,&estado));assert(t.n==2);
 assert(indiceVertice(&t,7)==0);assert(indiceVertice(&t,-1)==1);
 assert(indiceVertice(&t,999)==-1);liberar_trabajo(&t);
 /* liberar_trabajo frees its private workspace; it does not promise pointer reset. */
 long long salida=77;assert(sumar_seguro(0,INT_MAX,&salida));assert(salida==INT_MAX);
 assert(!sumar_seguro(LLONG_MAX,1,&salida));assert(salida==INT_MAX);
 g=grafo_insertar_arco(g,-1,7,0,&estado);assert(estado==GRAFO_OK);
 ListaArco camino=grafo_dijkstra(g,-1,7,&estado);assert(estado==GRAFO_OK&&camino&&camino->costo==0);grafo_liberar_arcos(&camino);assert(camino==NULL);
 g=grafo_insertar_arco(g,7,-1,-1,&estado);
 camino=grafo_dijkstra(g,-1,7,&estado);assert(estado==GRAFO_PESO_NEGATIVO&&camino==NULL);
 grafo_destruir(&g);assert(g.a==NULL&&g.v==NULL);
 return 0;}
"""
 (tmp_path/'helpers.c').write_text(main,encoding='utf-8');compiler=shutil.which('gcc');assert compiler
 built=subprocess.run([compiler,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'helpers.c'),str(tmp_path/'tad_cola.c'),'-o',str(tmp_path/'helpers.exe')],capture_output=True,text=True,timeout=30);assert built.returncode==0 and not built.stderr,built.stderr
 run=subprocess.run([str(tmp_path/'helpers.exe')],capture_output=True,text=True,timeout=10);assert run.returncode==0 and not run.stderr
 (tmp_path/'doc-review.json').write_text(json.dumps({'symbols':['grafo_dijkstra','preparar','indiceVertice','liberar_trabajo','sumar_seguro','grafo_liberar_arcos','grafo_destruir'],'native_helper_contracts':True,'strict_c17':True,'actual_http_files':4,'doxygen_warnings':0,'limits':['endpoint baseline is separate; no instruction signoff','normal allocation only'],'downloads_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},indent=2),encoding='utf-8')
