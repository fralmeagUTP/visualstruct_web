"""BFS must accept -1 as vertex data while empty FIFO keeps its error contract."""
import json
import shutil
import subprocess
import pytest
from _graph_private_diagnostic_observer import instrument_private_diagnostics

@pytest.mark.skipif(shutil.which('gcc') is None,reason='gcc unavailable: native BFS equivalence unverified')
def test_downloaded_bfs_negative_vertices_and_empty_queue(client,tmp_path):
 for tad,base in [('graph','tad_grafo'),('queue','tad_cola')]:
  for kind,ext in [('source','c'),('header','h')]:
   response=client.get('/help/source/'+tad+'/'+kind)
   assert response.status_code==200
   (tmp_path/(base+'.'+ext)).write_bytes(response.data)
 code=r'''
#include "tad_grafo.h"
#include "tad_cola.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#ifdef OBSERVED
extern int qa_status;
#define QA_STATUS(n) (qa_status == (n))
#else
/* The uninstrumented public API has no diagnostic output. */
#define QA_STATUS(n) 1
#endif
int main(void){
 struct Cola q={NULL,NULL};assert(cola_desencolar(&q)==-1);assert(q.delante==NULL&&q.atras==NULL);
 cola_encolar(&q,-1);assert(q.delante!=NULL);assert(cola_desencolar(&q)==-1);assert(q.delante==NULL&&q.atras==NULL);
 int starts[]={-1,1,1,-1},targets[]={2,-1,2,-1};
 for(int c=0;c<4;c++){
  Grafo g=grafo_crear();assert(grafo_bfs(g,99)==NULL&&QA_STATUS(2));g=grafo_insertar_vertice(g,starts[c]);assert(QA_STATUS(0));
  if(targets[c]!=starts[c])g=grafo_insertar_vertice(g,targets[c]);
  g=grafo_insertar_arco(g,starts[c],targets[c],1);assert(QA_STATUS(0));
  assert(grafo_bfs(g,99)==NULL&&QA_STATUS(2));ListaVertice result=grafo_bfs(g,starts[c]);assert(QA_STATUS(0));printf("[");int comma=0;
  for(ListaVertice n=result;n;n=n->sig){if(comma)printf(",");printf("%d",n->dato);comma=1;}puts("]");
  grafo_liberar_vertices(&result);assert(result==NULL);grafo_destruir(&g);assert(g.v==NULL&&g.a==NULL);
 }
 return 0;
}
'''
 p=tmp_path/'oracle.c';p.write_text(code,encoding='utf-8');exe=tmp_path/'oracle.exe'
 original=tmp_path/'tad_grafo.c';observed=tmp_path/'observed.c'
 observed.write_text(instrument_private_diagnostics(original.read_text(encoding='utf-8-sig')))
 outputs=[]
 for source,macros in [(original,[]),(observed,['-DOBSERVED'])]:
  compiled=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',*macros,str(p),str(source),str(tmp_path/'tad_cola.c'),'-o',str(exe)],capture_output=True,text=True)
  assert compiled.returncode==0,compiled.stderr
  run=subprocess.run([str(exe)],capture_output=True,text=True);assert run.returncode==0,run.stderr
  outputs.append(run.stdout)
 assert outputs[0]==outputs[1]
 native=[json.loads(line) for line in run.stdout.splitlines() if line.startswith('[')]
 expected=[[-1,2],[1,-1],[1,2],[-1]];assert native==expected
 assert 'No se puede desencolar' in run.stdout
 for index,(start,target) in enumerate([(-1,2),(1,-1),(1,2),(-1,-1)]):
  client.post('/graph/graph/reset')
  operations=[('create_graph',{'directed':True}),('insert_vertex',{'vertex':start})]
  if target!=start:operations.append(('insert_vertex',{'vertex':target}))
  operations.append(('insert_edge',{'origin':start,'target':target,'weight':1}))
  for operation,payload in operations:
   result=client.post('/graph/graph/operate',json={'operation':operation,'payload':payload}).get_json();assert result['success'],result
  result=client.post('/graph/graph/operate',json={'operation':'run_bfs','payload':{'start':start}}).get_json()
  assert result['success'] and result['result']==native[index]==expected[index]
