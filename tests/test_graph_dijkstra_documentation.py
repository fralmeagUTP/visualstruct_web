"""Fresh downloaded Dijkstra docs and independently invoked native helper contracts."""
from pathlib import Path
import subprocess,shutil,json,hashlib
from test_graph_bfs_documentation import run_doxygen

def test_dijkstra_download_contracts_helpers_and_guide(client,tmp_path):
 files=[]
 for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
  for part,ext in [('source','c'),('header','h')]:
   r=client.get('/help/source/'+tad+'/'+part);assert r.status_code==200;p=tmp_path/(stem+'.'+ext);p.write_bytes(r.data);files.append(p)
 for ext in ['c','h']:
  s=(tmp_path/('tad_grafo.'+ext)).read_text(encoding='utf-8-sig')
  assert 'INT_MAX es infinito' in s and 'primer índice con distancia mínima' in s
  assert 'componentes no alcanzables' in s and 'No se modifican sus marcas' in s
 for name in ['docs/USER_GUIDE.md','docs/qa/graph-teacher-guide.md']:
  s=(Path(__file__).resolve().parents[1]/name).read_text(encoding='utf-8')
  assert '## Dijkstra: contrato nativo del C descargado' in s and 'igual o mayor' in s
  section=s.split('## Dijkstra:',1)[1].split('\n## ',1)[0]
  assert 'pesos enteros no negativos' in section and 'archivo C de enteros' in section
  assert 'El usuario confirm\u00f3 conservar pesos enteros representables' in section
 run_doxygen(tmp_path,files)
 # Static helpers remain private in the student source; same translation unit
 # invokes their real bodies. No algorithm is reimplemented in this observer.
 main=r"""#include "tad_grafo.c"
#include <assert.h>
int main(void){
 int vertices[5]={-1,7,-1,9,99};
 assert(indiceVertice(vertices,4,-1)==0);assert(indiceVertice(vertices,4,9)==3);
 assert(indiceVertice(vertices,4,999)==-1);assert(indiceVertice(vertices,0,-1)==-1);
 Grafo g=grafo_crear();assert(grafo_tiene_peso_negativo(g)==0);
 assert(inicializarVectorVertices(g,vertices,0)==1);assert(inicializarVectorVertices(g,vertices,1)==0);
 g=grafo_insertar_vertice(g,-1);g=grafo_insertar_vertice(g,7);
 assert(inicializarVectorVertices(g,vertices,2)==1);assert(vertices[0]==7&&vertices[1]==-1);
 assert(inicializarVectorVertices(g,vertices,3)==0);assert(inicializarVectorVertices(g,vertices,1)==1);
 g=grafo_insertar_arco(g,-1,7,0);assert(grafo_tiene_peso_negativo(g)==0);
 g=grafo_insertar_arco(g,7,-1,-1);assert(grafo_tiene_peso_negativo(g)==1);
 liberarListaArcos(NULL);
 ListaArco a=malloc(sizeof(struct NodoA));assert(a);a->sig=malloc(sizeof(struct NodoA));assert(a->sig);a->sig->sig=NULL;liberarListaArcos(a);
 while(g.a){ListaArco a=g.a;g.a=a->sig;free(a);}while(g.v){ListaVertice v=g.v;g.v=v->sig;free(v);}
 return 0;}
"""
 (tmp_path/'helpers.c').write_text(main,encoding='utf-8');compiler=shutil.which('gcc');assert compiler
 built=subprocess.run([compiler,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'helpers.c'),str(tmp_path/'tad_cola.c'),'-o',str(tmp_path/'helpers.exe')],capture_output=True,text=True,timeout=30);assert built.returncode==0 and not built.stderr,built.stderr
 run=subprocess.run([str(tmp_path/'helpers.exe')],capture_output=True,text=True,timeout=10);assert run.returncode==0 and not run.stderr
 (tmp_path/'doc-review.json').write_text(json.dumps({'symbols':['grafo_dijkstra','grafo_tiene_peso_negativo','indiceVertice','inicializarVectorVertices','liberarListaArcos'],'native_helper_contracts':True,'strict_c17':True,'actual_http_files':4,'doxygen_warnings':0,'limits':['endpoint baseline is separate; no instruction signoff','normal allocation only'],'downloads_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},indent=2),encoding='utf-8')
