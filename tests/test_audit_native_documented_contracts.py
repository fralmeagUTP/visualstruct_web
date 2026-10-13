"""Native observations for documented downloaded sentinel/ownership contracts."""
import shutil
import subprocess
import pytest

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
int main(void){Grafo g=grafo_crear();assert(grafo_costo_arco(g,1,2)==-1);assert(!grafo_existe_arco(g,1,2));g=grafo_insertar_vertice(g,1);g=grafo_insertar_vertice(g,2);g=grafo_insertar_arco(g,1,2,-1);assert(grafo_costo_arco(g,1,2)==-1);assert(grafo_existe_arco(g,1,2));assert(grafo_bfs(g,99)==NULL);while(g.a){ListaArco n=g.a->sig;free(g.a);g.a=n;}while(g.v){ListaVertice n=g.v->sig;free(g.v);g.v=n;}return 0;}''',['tad_cola']),
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
 header=(tmp_path/(base+'.h')).read_text(encoding='utf-8')
 if tad=='bst':assert 'o NULL si el árbol está vacío' in header and 'malloc falla' in header
 else:assert 'un arco válido también puede tener costo -1' in header and 'El llamador libera los nodos' in header
