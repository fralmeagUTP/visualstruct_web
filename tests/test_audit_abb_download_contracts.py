"""Per-symbol ABB contracts against actual HTTP C/H, strict native compile and guide."""
import shutil,subprocess,json
from pathlib import Path
import pytest

PROGRAM=r'''#include "tad_abb.h"
#include <assert.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
static int fail=0,allocated=0,freed=0;
void *audit_malloc(size_t n){if(fail)return NULL;void*p=malloc(n);if(p)allocated++;return p;}
void audit_free(void*p){if(p)freed++;free(p);}
int main(void){
 assert(!abb_buscar(NULL,7));assert(!abb_encontrarMinimo(NULL));assert(!abb_encontrarMaximo(NULL));
 assert(abb_altura(NULL)==0&&abb_contarNiveles(NULL)==0);abb_liberarArbol(NULL);abb_preorden(NULL);abb_inorden(NULL);abb_postorden(NULL);abb_mostrarArbol(NULL,0);
 fail=1;assert(!abb_insertar(NULL,7));fail=0;
 ABBNodo*r=abb_insertar(NULL,10);assert(r&&r->valor==10&&r->izquierdo==NULL&&r->derecho==NULL);assert(abb_altura(r)==1&&abb_contarNiveles(r)==1);
 fail=1;assert(abb_insertar(r,3)==r&&!r->izquierdo);fail=0;
 int before=allocated;assert(abb_insertar(r,10)==r&&allocated==before);assert(abb_eliminar(r,99)==r&&freed==0);
 int seed[]={5,15,3,7,12,18};for(int i=0;i<6;i++)r=abb_insertar(r,seed[i]);assert(allocated==7);
 assert(abb_buscar(r,7)==r->izquierdo->derecho&&!abb_buscar(r,6));assert(abb_encontrarMinimo(r)==r->izquierdo->izquierdo);assert(abb_encontrarMaximo(r)==r->derecho->derecho);
 assert(abb_altura(r)==3&&abb_contarNiveles(r)==3);
 printf("PRE:");abb_preorden(r);printf("\nIN:");abb_inorden(r);printf("\nPOST:");abb_postorden(r);printf("\nSHOW:");abb_mostrarArbol(r,0);printf("ENDSHOW\n");
 ABBNodo*same=r;r=abb_eliminar(r,10);assert(r==same&&r->valor==12&&freed==1&&r->derecho->izquierdo==NULL);
 r=abb_eliminar(r,3);assert(r->izquierdo->izquierdo==NULL&&freed==2);ABBNodo*child=r->izquierdo->derecho;r=abb_eliminar(r,5);assert(r->izquierdo==child&&freed==3);
 abb_liberarArbol(r);r=NULL;assert(allocated==freed);assert(!r);
 r=abb_insertar(NULL,1);r=abb_insertar(r,2);r=abb_insertar(r,3);assert(abb_altura(r)==3&&abb_contarNiveles(r)==3);abb_liberarArbol(r);r=NULL;assert(allocated==freed);
 printf("ALLOCATION:%d FREE:%d\n",allocated,freed);return 0;
}'''

def test_all_downloaded_abb_symbol_contracts_and_native_output(client,tmp_path):
 gcc=shutil.which('gcc')
 if not gcc:pytest.skip('GCC unavailable: native documentation contracts unverified')
 for kind,suffix in [('source','c'),('header','h')]:
  response=client.get('/help/source/abb/'+kind);assert response.status_code==200
  raw=response.data;assert raw==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_abb.'+suffix)).read_bytes();(tmp_path/('tad_abb.'+suffix)).write_bytes(raw)
  text=raw.decode('utf-8-sig');assert 'alias prestado' in text and 'sin agregar salto de linea' in text and 'no pone a NULL la raiz del llamador' in text and 'Cuenta niveles' in text and 'Un duplicado conserva' in text
 (tmp_path/'probe.c').write_text(PROGRAM,encoding='utf-8')
 flags=['-std=c17','-Wall','-Wextra','-Wpedantic','-Werror'];obj=tmp_path/'abb.o';exe=tmp_path/'probe.exe'
 run=subprocess.run([gcc,*flags,'-Dmalloc=audit_malloc','-Dfree=audit_free','-c',str(tmp_path/'tad_abb.c'),'-o',str(obj)],capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr
 run=subprocess.run([gcc,*flags,str(tmp_path/'probe.c'),str(obj),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr
 run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr
 assert run.stdout=='PRE:10 5 3 7 15 12 18 \nIN:3 5 7 10 12 15 18 \nPOST:3 7 5 12 18 15 10 \nSHOW:\n          18\n\n     15\n\n          12\n\n10\n\n          7\n\n     5\n\n          3\nENDSHOW\nALLOCATION:10 FREE:10\n'
 (tmp_path/'downloaded-abb-contract-review.json').write_text(json.dumps({'native_stdout':run.stdout,'strict_c17':True,'allocations':10,'frees':10,'symbols_reviewed':12,'limits':['Recorded documented cases, not every C path.','C/H lacks the two service-generated helpers for UI Contar hojas and Validar.']},indent=2),encoding='utf-8')

def test_abb_guide_differentiates_c_and_interface_contracts(client):
 response=client.get('/help/hierarchical/abb');assert response.status_code==200
 text=response.data.decode('utf-8');assert 'Buscar retorna un puntero prestado o NULL en C' in text and 'como booleano, sin error por ausencia' in text and 'no agrega otro metodo al C/H descargado' in text; assert 'sin recursion ni mutacion' in text and 'un alias prestado' in text and 'arbol vacio retorna NULL' in text and 'convierte ese retorno en un error de interfaz' in text; assert 'altura cuenta niveles' in text and 'llamador debe ponerla a NULL' in text and 'auxiliares' in text and 'no estan declarados en el C/H descargado' in text
