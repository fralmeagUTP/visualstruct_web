"""Six reviewed downloaded contracts; rotations/mutations remain decision-held."""
import shutil,subprocess,json
from pathlib import Path

PROGRAM=r'''#include "tad_avl.h"
#include <assert.h>
#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
static int allocated,freed;
void *audit_malloc(size_t n){void*p=malloc(n);if(p)allocated++;return p;}
void audit_free(void*p){if(p)freed++;free(p);}
int main(void){
 assert(avl_esHoja(NULL)==0 && avl_altura(NULL)==0 && avl_buscar(NULL,7)==NULL);
 avl_verArbol(NULL,0);avl_liberarAVL(NULL);
 AVL r=NULL;avl_insertar(&r,10);avl_insertar(&r,5);avl_insertar(&r,15);
 assert(r && !avl_esHoja(r) && avl_esHoja(r->izq) && avl_esHoja(r->der));
 assert(avl_altura(r)==2 && avl_altura(r->izq)==1);
 assert(avl_buscar(r,5)==r->izq && avl_buscar(r,99)==NULL && avl_minimo(r)==r->izq);
 assert(allocated==3 && freed==0);avl_verArbol(r,0);
 avl_liberarAVL(r);r=NULL;assert(r==NULL && freed==allocated);
 printf("FREE:%d\n",freed);return 0;}'''

def test_six_downloaded_avl_contracts_and_exact_stdout(client,tmp_path):
 for kind,suffix in [('source','c'),('header','h')]:
  response=client.get('/help/source/avl/'+kind);assert response.status_code==200;raw=response.data
  assert raw==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_avl.'+suffix)).read_bytes();(tmp_path/('tad_avl.'+suffix)).write_bytes(raw)
  text=raw.decode('utf-8-sig');assert 'alias prestado' in text and 'no pone a NULL la raiz del llamador' in text and 'No es recorrido inorden ascendente' in text
 (tmp_path/'probe.c').write_text(PROGRAM,encoding='utf-8');gcc=shutil.which('gcc');assert gcc
 flags=['-std=c17','-Wall','-Wextra','-Wpedantic','-Werror'];obj=tmp_path/'avl.o';exe=tmp_path/'probe.exe'
 for command in [[gcc,*flags,'-Dmalloc=audit_malloc','-Dfree=audit_free','-c',str(tmp_path/'tad_avl.c'),'-o',str(obj)],[gcc,*flags,str(tmp_path/'probe.c'),str(obj),'-o',str(exe)]]:
  run=subprocess.run(command,capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr
 run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=5);assert run.returncode==0 and run.stdout=='   15\n10\n   5\nFREE:3\n'
 (tmp_path/'six-avl-contracts.json').write_text(json.dumps({'reviewed':['avl_verArbol','avl_esHoja','avl_altura','avl_buscar','avl_minimo','avl_liberarAVL'],'stdout':run.stdout,'allocations':3,'frees':3,'limits':['Uses insertion only to prepare nonrotating tree; does not sign off insertion/elimination/rotation invariants.','No all-path or sanitizer certificate.']},indent=2),encoding='utf-8')
