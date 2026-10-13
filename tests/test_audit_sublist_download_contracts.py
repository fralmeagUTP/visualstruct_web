"""Individual downloadable Sublista C/H contracts, not a UI instruction certificate."""
import json,shutil,subprocess
from pathlib import Path
import pytest
from app import create_app

def test_sublist_downloaded_symbol_contracts_null_capacity_first_match_ownership_and_malloc_failure(tmp_path):
 gcc=shutil.which('gcc')
 if not gcc:pytest.skip('GCC unavailable: downloaded contract checks require C17 compiler')
 client=create_app().test_client()
 for kind,suffix in [('source','.c'),('header','.h')]:
  response=client.get('/help/source/sublist/'+kind);assert response.status_code==200;(tmp_path/('tad_sublista'+suffix)).write_bytes(response.data)
 harness=r'''
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
static void* allocated[128];static int live[128],allocated_count,malloc_fail,malloc_calls,free_order[128],free_count;
static void *checked_malloc(size_t bytes){malloc_calls++;if(malloc_fail)return NULL;void*p=malloc(bytes);assert(p);allocated[allocated_count]=p;live[allocated_count++]=1;return p;}
static int id_of(const void*p){for(int i=0;i<allocated_count;i++)if(live[i]&&allocated[i]==p)return i+1;assert(!"unknown live allocation");return 0;}
static void checked_free(void*p){if(!p)return;int id=id_of(p);live[id-1]=0;free_order[free_count++]=id;free(p);}
#define malloc checked_malloc
#define free checked_free
#include "tad_sublista.c"
#undef malloc
#undef free
int main(void){
 Nodo*root=NULL;sublista_inicializar(NULL);sublista_inicializar(&root);assert(root==NULL);
 malloc_fail=1;assert(crear_padre(7)==NULL);assert(crear_hijo(3)==NULL);assert(sublista_insertar_padre_final(&root,7)==NULL);assert(root==NULL);assert(sublista_insertar_padre_final(NULL,7)==NULL);malloc_fail=0;
 Nodo*first=sublista_insertar_padre_final(&root,7);Nodo*duplicate=sublista_insertar_padre_final(&root,7);Nodo*last=sublista_insertar_padre_final(&root,8);
 assert(root==first&&first->nro==7&&first->sgte==duplicate&&duplicate->sgte==last&&last->sgte==NULL&&first->sub==NULL);
 assert(sublista_buscar_padre(root,7)==first);assert(sublista_buscar_padre(NULL,7)==NULL);assert(sublista_buscar_padre(root,99)==NULL);assert(sublista_contar_padres(root)==3&&sublista_contar_padres(NULL)==0);
 assert(!sublista_insertar_hijo_final(NULL,3));assert(!sublista_insertar_hijo(NULL,7,3));assert(!sublista_insertar_hijo(root,99,3));
 malloc_fail=1;int before_malloc=malloc_calls;assert(!sublista_insertar_hijo(root,7,3));assert(malloc_calls==before_malloc+1&&first->sub==NULL&&duplicate->sub==NULL);malloc_fail=0;
 assert(sublista_insertar_hijo(root,7,3));assert(sublista_insertar_hijo(root,7,3));assert(sublista_insertar_hijo(root,7,5));assert(sublista_insertar_hijo_final(duplicate,4));assert(sublista_insertar_hijo(root,8,9));
 Sublista*c1=first->sub;Sublista*c2=c1->sgte;Sublista*c3=c2->sgte;assert(c1->nro==3&&c1!=c2&&c3->nro==5&&c3->sgte==NULL&&duplicate->sub->nro==4);
 assert(sublista_buscar_hijo(first->sub,3)==c1);assert(sublista_buscar_hijo(NULL,3)==NULL&&sublista_buscar_hijo(first->sub,99)==NULL);assert(sublista_contar_hijos(first)==3&&sublista_contar_hijos(NULL)==0);
 struct{int left;int values[2];int right;}buffer={111,{-8,-9},222};
 assert(sublista_copiar_hijos(first,buffer.values,2)==2&&buffer.values[0]==3&&buffer.values[1]==3&&buffer.left==111&&buffer.right==222);
 buffer.values[0]=-8;buffer.values[1]=-9;
 assert(sublista_copiar_hijos(first,buffer.values,0)==0&&sublista_copiar_hijos(first,buffer.values,-1)==0&&sublista_copiar_hijos(first,NULL,2)==0&&sublista_copiar_hijos(NULL,buffer.values,2)==0);assert(buffer.values[0]==-8&&buffer.values[1]==-9);
 assert(sublista_obtener_hijos(root,7,buffer.values,2)==2&&buffer.values[0]==3&&buffer.values[1]==3);assert(sublista_obtener_hijos(root,99,NULL,0)==-1&&sublista_obtener_hijos(root,7,NULL,0)==0&&sublista_obtener_hijos(NULL,7,NULL,0)==-1);
 assert(root==first&&first->sub==c1&&c1->sgte==c2&&c2->sgte==c3);char full[256];sublista_formatear(root,full,sizeof(full));assert(strcmp(full,"P(7): [3] -> [3] -> [5]\nP(7): [4]\nP(8): [9]")==0);
 struct{char left;char out[6];char right;}text={'L',{'x','x','x','x','x','x'},'R'};sublista_formatear(root,text.out,0);assert(text.out[0]=='x');sublista_formatear(root,NULL,6);sublista_formatear(root,text.out,sizeof(text.out));assert(text.left=='L'&&text.right=='R'&&text.out[5]=='\0');sublista_formatear(NULL,full,sizeof(full));assert(strcmp(full,"Lista padre vacia")==0);
 size_t used=0;char tiny[4];sublista_append_text(tiny,sizeof(tiny),&used,"abcdef");assert(used==4&&strcmp(tiny,"abc")==0);sublista_append_text(tiny,sizeof(tiny),&used,"X");assert(strcmp(tiny,"abc")==0);used=0;sublista_append_text(NULL,4,&used,"X");assert(used==0);sublista_append_text(tiny,4,NULL,"X");
 int removed_id=id_of(c1),prior_frees=free_count;assert(sublista_eliminar_hijo(root,7,3));assert(free_count==prior_frees+1&&free_order[prior_frees]==removed_id&&first->sub==c2&&c2->sgte==c3);
 prior_frees=free_count;assert(!sublista_eliminar_hijo(root,7,99)&&!sublista_eliminar_hijo(root,99,3)&&!sublista_eliminar_hijo_primero(NULL,3));assert(free_count==prior_frees);
 int parent_id=id_of(first),second_child=id_of(c2),third_child=id_of(c3);prior_frees=free_count;assert(sublista_eliminar_padre_primero(&root,7));assert(root==duplicate&&free_count==prior_frees+3);assert(free_order[prior_frees]==second_child&&free_order[prior_frees+1]==third_child&&free_order[prior_frees+2]==parent_id);assert(duplicate->sub->nro==4&&last->sub->nro==9);
 prior_frees=free_count;assert(!sublista_eliminar_padre_primero(NULL,7)&&!sublista_eliminar_padre_primero(&root,99));assert(free_count==prior_frees);destruir_hijos(NULL);destruir_hijos(&duplicate->sub);assert(duplicate->sub==NULL&&root==duplicate);
 sublista_destruir(NULL);sublista_destruir(&root);assert(root==NULL);prior_frees=free_count;sublista_destruir(&root);assert(free_count==prior_frees);
 for(int i=0;i<allocated_count;i++)assert(!live[i]);
 Nodo*saved=crear_padre(-7);assert(saved->nro==-7&&saved->sgte==NULL&&saved->sub==NULL);Nodo*reset=saved;prior_frees=free_count;sublista_inicializar(&reset);assert(reset==NULL&&free_count==prior_frees);sublista_destruir(&saved);
 printf("AUDIT contracts allocations=%d frees=%d\n",allocated_count,free_count);return 0;
}
'''.replace('#include <stdint.h>','#include <stdint.h>\n#include <string.h>')
 source=tmp_path/'contracts.c';source.write_text(harness,encoding='utf-8');exe=tmp_path/'contracts.exe';build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(source),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr;run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr;assert run.stdout.startswith('AUDIT contracts')
 (tmp_path/'sublist-download-contract-review.json').write_text(json.dumps({'stdout':run.stdout,'compiler_exit':build.returncode,'native_exit':run.returncode,'limits':['Symbol contracts and tested guard/failure/bounds paths only; no exhaustive-path or instruction/UI certificate.','Only live allocations inspected; free IDs saved before freeing.']},indent=2),encoding='utf-8')
