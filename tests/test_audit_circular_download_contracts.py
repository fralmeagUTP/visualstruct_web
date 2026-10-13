"""Circular downloaded C/H: meaningful boundary and ownership contracts, not Doxygen-only."""
import json,shutil,subprocess
from pathlib import Path
import pytest

def test_downloaded_circular_contracts_and_manual(client,tmp_path):
 gcc=shutil.which('gcc')
 if not gcc:pytest.skip('GCC unavailable; actual C download contracts unverified')
 for kind,name in [('source','tad_lista_circular.c'),('header','tad_lista_circular.h')]:
  response=client.get('/help/source/circular_list/'+kind);assert response.status_code==200;(tmp_path/name).write_bytes(response.data)
 program=r'''
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int fail_next,allocations,releases;
static void *observed_malloc(size_t n){if(fail_next){fail_next=0;return NULL;}void *p=malloc(n);if(p)allocations++;return p;}
static void observed_free(void *p){if(p)releases++;free(p);}
#define malloc observed_malloc
#define free observed_free
#include "tad_lista_circular.c"
#undef malloc
#undef free
int main(void){
 ListaCircular lc;lcir_inicializar(&lc);lcir_inicializar(NULL);lcir_destruir(NULL);
 assert(lcir_vacia(NULL)&&lcir_vacia(&lc)&&lcir_contar(NULL)==0);
 assert(!lcir_eliminar_inicio(NULL)&&!lcir_eliminar_primero(NULL,7));lcir_invertir(NULL);
 int out[4]={-9,-9,-9,-9};assert(lcir_buscar_posiciones(NULL,7,out,4)==0);assert(lcir_copiar_valores(NULL,out,4)==0);
 fail_next=1;assert(lcir_crear_nodo(7)==NULL);fail_next=1;assert(!lcir_insertar_inicio(&lc,7));assert(lc.cabeza==NULL&&lc.cola==NULL&&lc.cantidad==0);
 assert(lcir_insertar_final(&lc,7));assert(lcir_insertar_final(&lc,7));assert(lcir_insertar_final(&lc,9));
 LCirNodo *a=lc.cabeza,*b=a->sgte,*c=lc.cola;int allocated=allocations;
 fail_next=1;assert(!lcir_insertar_final(&lc,99));assert(lc.cabeza==a&&lc.cola==c&&lc.cantidad==3&&c->sgte==a&&allocations==allocated);
 assert(lcir_buscar_posiciones(&lc,7,out,1)==2);assert(out[0]==1&&out[1]==-9);out[0]=-9;
 assert(lcir_buscar_posiciones(&lc,7,out,0)==2&&out[0]==-9);assert(lcir_buscar_posiciones(&lc,7,out,-1)==2&&out[0]==-9);assert(lcir_buscar_posiciones(&lc,7,NULL,4)==2);
 assert(lcir_copiar_valores(&lc,out,2)==2&&out[0]==7&&out[1]==7&&out[2]==-9);assert(lcir_copiar_valores(&lc,NULL,3)==0);assert(lcir_copiar_valores(&lc,out,0)==0);
 char text[128];lcir_formatear(&lc,text,sizeof text);assert(strcmp(text,"HEAD -> [1]=7 -> [2]=7 -> [3]=9 -> (vuelve a HEAD)")==0);
 struct{char data[8];unsigned char canary;} small={{0},123};lcir_formatear(&lc,small.data,sizeof small.data);assert(small.data[7]=='\0'&&small.canary==123);
 char tiny[1]={'X'};lcir_formatear(&lc,tiny,1);assert(tiny[0]=='\0');tiny[0]='X';lcir_formatear(&lc,tiny,0);assert(tiny[0]=='X');lcir_formatear(&lc,NULL,4);
 lcir_formatear(NULL,text,sizeof text);assert(strcmp(text,"Lista circular vacia")==0);
 size_t used=0;lcir_append_text(tiny,1,&used,"abc");assert(tiny[0]=='\0'&&used==1);lcir_append_text(NULL,0,&used,"abc");lcir_append_text(text,sizeof text,NULL,"abc");
 lcir_invertir(&lc);assert(lc.cabeza==c&&lc.cola==a&&c->sgte==b&&b->sgte==a&&a->sgte==c&&lc.cantidad==3&&allocations==allocated&&releases==0);lcir_invertir(&lc);
 assert(!lcir_eliminar_primero(&lc,99)&&lc.cabeza==a&&releases==0);assert(lcir_eliminar_primero(&lc,7)&&lc.cabeza==b&&lc.cola==c&&lc.cantidad==2&&c->sgte==b&&releases==1);
 assert(lcir_eliminar_inicio(&lc)&&lc.cabeza==c&&lc.cola==c&&lc.cantidad==1&&c->sgte==c&&releases==2);lcir_invertir(&lc);assert(lc.cabeza==c&&lc.cantidad==1);
 lcir_destruir(&lc);assert(lc.cabeza==NULL&&lc.cola==NULL&&lc.cantidad==0&&allocations==releases);assert(!lcir_eliminar_inicio(&lc));lcir_destruir(&lc);
 ListaCircular transient={NULL,NULL,2};assert(!lcir_vacia(&transient)&&lcir_contar(&transient)==2);lcir_destruir(&transient);assert(transient.cantidad==2);
 puts("Circular contracts verified: NULL guards; malloc failure; full-count bounded-output search; copy bounds; format truncation/canary; stored quantity; inversion identity; first-occurrence release; destruction ownership.");return 0;
}
'''
 (tmp_path/'contracts.c').write_text(program,encoding='utf-8');exe=tmp_path/'contracts.exe';build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'contracts.c'),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr;run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr
 guide=client.get('/help/sequential/circular_list');assert guide.status_code==200;html=guide.data.decode('utf-8');assert 'Contratos C y resultados' in html and 'NULL y capacidad 0' in html and 'true/false' in html and 'cola-&gt;sgte == cabeza al terminar' in html
 (tmp_path/'contracts-report.json').write_text(json.dumps({'gcc_exit':build.returncode,'native_exit':run.returncode,'stdout':run.stdout,'guide_http':guide.status_code,'limits':['No sanitizer run; ownership counters are instrumentation, not ASan.','Documentation signoff does not certify instruction UI of remaining circular methods.']},indent=2),encoding='utf-8')
