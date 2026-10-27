#include "tad_grafo.h"
#include <stdio.h>
#include <stdlib.h>
static int calls, fail_at, live;
void *__real_malloc(size_t n);
void __real_free(void *p);
void *__wrap_malloc(size_t n) { calls++; if (fail_at && calls==fail_at) return NULL; void *p=__real_malloc(n); if(p)live++; return p; }
void __wrap_free(void *p) { if(p)live--; __real_free(p); }
static void clear(Grafo *g) { while(g->a) { ListaArco n=g->a->sig;free(g->a);g->a=n; } while(g->v) { ListaVertice n=g->v->sig;free(g->v);g->v=n; } }
int main(void) { int failed=0;
 for(int scenario=0;scenario<6;scenario++)for(int fault=0;fault<=4;fault++) {
  calls=0;fail_at=0;Grafo g=grafo_crear();
  if(scenario==1||scenario==3)g=grafo_insertar_vertice(g,1);
  if(scenario==2||scenario==3)g=grafo_insertar_vertice(g,2);
  if(scenario==5)g=grafo_insertar_arco(g,1,2,3);
  calls=0;fail_at=fault;g=grafo_insertar_arco(g,1,scenario==4?1:2,9);
  int invariant=1;for(ListaArco a=g.a;a;a=a->sig)if(!grafo_existe_vertice(g,a->origen)||!grafo_existe_vertice(g,a->destino))invariant=0;
  int normal_ok=fault!=0||(grafo_tamano(g)==1&&grafo_costo_arco(g,1,scenario==4?1:2)==9);
  int vertices=grafo_orden(g), edges=grafo_tamano(g);
  fail_at=0;clear(&g);int ok=invariant&&normal_ok&&live==0;
  printf("scenario=%d fault=%d endpoints=%d vertices=%d edges=%d live_after_cleanup=%d result=%s\n",scenario,fault,invariant,vertices,edges,live,ok?"PASS":"FAIL");failed+=!ok;
 }
 return failed?1:0;
}
