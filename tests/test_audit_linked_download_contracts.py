"""Downloaded linked-list Doxygen claims include failure and ownership semantics."""
import re,shutil,subprocess
import pytest

def test_downloaded_visible_linked_contracts_null_malloc_position_and_ownership(client,tmp_path):
    if not shutil.which('gcc'):pytest.skip('gcc unavailable: memory contract unverified')
    files={}
    functions=['lista_insertar_inicio','lista_insertar_final','lista_insertar_elemento','lista_buscar_elemento','lista_eliminar_elemento','lista_eliminar_repetidos','lista_limpiar']
    for kind,ext in [('source','c'),('header','h')]:
        response=client.get('/help/source/linked_list/'+kind);assert response.status_code==200
        files[ext]=response.data.decode('utf-8-sig')
        (tmp_path/('tad_lista.'+ext)).write_bytes(response.data)
    for function in functions:
        docs=[]
        for text in files.values():
            match=re.search(r'/\*\*(?:(?!/\*\*).)*?\*/(?=\s*void\s+'+function+r'\s*\()',text,re.S)
            assert match,function
            docs.append(match.group())
        assert docs[0]==docs[1],function
    assert 'no devuelve un contador en C' in files['h']
    assert '1 incluso en lista vacía' in files['h']
    assert 'valor es indeterminado' in files['h']
    program=r'''#include "tad_lista.h"
#include <stdlib.h>
#include <stddef.h>
#include <assert.h>
static int fail=0,live=0,calls=0;
void *audit_malloc(size_t n){calls++;if(fail)return NULL;void *p=malloc(n);if(p)live++;return p;}
void audit_free(void *p){if(p)live--;free(p);}
int main(void){Tlista l=NULL;int before=calls;
lista_insertar_inicio(NULL,7);lista_insertar_final(NULL,7);lista_insertar_elemento(NULL,7,1);assert(calls==before);
lista_insertar_final(&l,1);lista_insertar_final(&l,2);Tlista original=l;assert(live==2);
fail=1;lista_insertar_inicio(&l,7);lista_insertar_final(&l,7);lista_insertar_elemento(&l,7,1);
assert(l==original&&l->nro==1&&l->sgte->nro==2&&l->sgte->sgte==NULL&&live==2);
fail=0;before=calls;lista_insertar_elemento(&l,7,0);assert(calls==before&&l==original&&live==2);
lista_insertar_elemento(&l,7,3);assert(l==original&&live==2&&l->sgte->sgte==NULL);
lista_limpiar(NULL);assert(live==2);lista_limpiar(&l);assert(l==NULL&&live==0);lista_limpiar(&l);assert(live==0);return 0;}'''
    (tmp_path/'probe.c').write_text(program,encoding='utf-8');obj=tmp_path/'tad.o';exe=tmp_path/'probe.exe'
    gcc=shutil.which('gcc')
    first=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror','-Dmalloc=audit_malloc','-Dfree=audit_free','-c',str(tmp_path/'tad_lista.c'),'-o',str(obj)],capture_output=True,text=True)
    assert first.returncode==0,first.stderr
    second=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'probe.c'),str(obj),'-o',str(exe)],capture_output=True,text=True)
    assert second.returncode==0,second.stderr
    run=subprocess.run([str(exe)],capture_output=True,text=True);assert run.returncode==0,run.stderr
    assert run.stdout.count('no se pudo asignar memoria')==3
    assert 'Posicion no encontrada' in run.stdout
