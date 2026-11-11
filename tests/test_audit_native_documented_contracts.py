"""Native observations for documented downloaded sentinel/ownership contracts."""
import shutil
import subprocess
import pytest
from _graph_private_diagnostic_observer import instrument_private_diagnostics

@pytest.mark.skipif(shutil.which('gcc') is None, reason='gcc unavailable: downloaded native contracts unverified')
@pytest.mark.parametrize('tad,base,program,dependencies',[
 ('bst','tad_abb',r'''#include "tad_abb.h"
#include <assert.h>
#include <stddef.h>
#include <stdlib.h>
static int fail=0;
void *audit_malloc(size_t n){return fail?NULL:malloc(n);}
int main(void){assert(abb_encontrarMinimo(NULL)==NULL);assert(abb_encontrarMaximo(NULL)==NULL);fail=1;assert(abb_insertar(NULL,7)==NULL);fail=0;ABBNodo *r=abb_insertar(NULL,7);assert(r);fail=1;assert(abb_insertar(r,3)==r);assert(r->izquierdo==NULL);fail=0;abb_liberarArbol(r);return 0;}''',[]),
 ('graph','tad_grafo',r'''#include "tad_grafo.h"
#include <assert.h>
#include <stdlib.h>
#ifdef OBSERVED
extern int qa_status;
#define QA_STATUS(n) (qa_status == (n))
#else
/* The uninstrumented public API has no diagnostic output. */
#define QA_STATUS(n) 1
#endif
int main(void){Grafo g=grafo_crear();int output=42;assert(!grafo_costo_arco(g,1,2,&output)&&output==42);assert(!grafo_existe_arco(g,1,2));g=grafo_insertar_vertice(g,1);assert(QA_STATUS(0));g=grafo_insertar_vertice(g,2);assert(QA_STATUS(0));g=grafo_insertar_arco(g,1,2,-1);assert(QA_STATUS(0));assert(grafo_costo_arco(g,1,2,&output)&&output==-1);assert(grafo_existe_arco(g,1,2));assert(grafo_bfs(g,99)==NULL&&QA_STATUS(2));grafo_destruir(&g);assert(g.v==NULL&&g.a==NULL);return 0;}''',[]),
])
def test_downloaded_documented_sentinels(client,tmp_path,tad,base,program,dependencies):
 routes={'bst':'/help/source/abb/','graph':'/help/source/graph/','tad_cola':'/help/source/queue/'}
 for name in [base]+dependencies:
  route=routes[tad] if name==base else routes[name]
  for kind,ext in [('source','c'),('header','h')]:
   response=client.get(route+kind)
   assert response.status_code==200
   (tmp_path/(name+'.'+ext)).write_bytes(response.data)
 source=tmp_path/'probe.c';source.write_text(program,encoding='utf-8')
 gcc=shutil.which('gcc');objects=[]
 for name in [base]+dependencies:
  obj=tmp_path/(name+'.o');cmd=[gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror']
  if name=='tad_abb':cmd+=['-Dmalloc=audit_malloc']
  result=subprocess.run(cmd+['-c',str(tmp_path/(name+'.c')),'-o',str(obj)],capture_output=True,text=True)
  assert result.returncode==0,result.stderr
  objects.append(str(obj))
 exe=tmp_path/'probe.exe';result=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(source),*objects,'-o',str(exe)],capture_output=True,text=True)
 assert result.returncode==0,result.stderr
 result=subprocess.run([str(exe)],capture_output=True,text=True)
 assert result.returncode==0,result.stderr
 if tad=='graph':
  original_stdout=result.stdout
  original=tmp_path/'tad_grafo.c';observed=tmp_path/'observed.c'
  observed.write_text(instrument_private_diagnostics(original.read_text(encoding='utf-8-sig')))
  result=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror','-DOBSERVED',str(source),str(observed),'-o',str(exe)],capture_output=True,text=True)
  assert result.returncode==0,result.stderr
  result=subprocess.run([str(exe)],capture_output=True,text=True)
  assert result.returncode==0,result.stderr
  assert result.stdout==original_stdout
 header=(tmp_path/(base+'.h')).read_text(encoding='utf-8')
 if tad=='bst':assert 'o NULL si el árbol está vacío' in header and 'malloc falla' in header
 else:assert 'int *salida' in header and 'GrafoEstado' not in header and 'GRAFO_NO_EXISTE' in (tmp_path/'tad_grafo.c').read_text(encoding='utf-8') and 'void grafo_liberar_vertices' in header
