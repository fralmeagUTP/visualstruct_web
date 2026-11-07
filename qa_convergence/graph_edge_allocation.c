#include "tad_grafo.h"
#include <stdio.h>
#include <stdlib.h>

static int calls, fail_at, live;
void *__real_malloc(size_t n);
void __real_free(void *p);
void *__wrap_malloc(size_t n) {
    calls++;
    if (fail_at && calls == fail_at) return NULL;
    void *p = __real_malloc(n);
    if (p) live++;
    return p;
}
void __wrap_free(void *p) {
    if (p) live--;
    __real_free(p);
}

int main(void) {
    int failed = 0;
    for (int scenario = 0; scenario < 6; scenario++) {
        for (int fault = 0; fault <= 4; fault++) {
            calls = 0; fail_at = 0;
            Grafo g = grafo_crear(); GrafoEstado status = GRAFO_OK;
            if (scenario == 1 || scenario == 3) g = grafo_insertar_vertice(g, 1, &status);
            if (scenario == 2 || scenario == 3) g = grafo_insertar_vertice(g, 2, &status);
            if (scenario == 5) g = grafo_insertar_arco(g, 1, 2, 3, &status);
            Grafo before = g;
            calls = 0; fail_at = fault;
            g = grafo_insertar_arco(g, 1, scenario == 4 ? 1 : 2, 9, &status);
            int invariant = 1;
            for (ListaArco a = g.a; a; a = a->sig) {
                if (!grafo_existe_vertice(g, a->origen) || !grafo_existe_vertice(g, a->destino)) invariant = 0;
            }
            int cost = 0;
            int exists = grafo_costo_arco(g, 1, scenario == 4 ? 1 : 2, &cost);
            int normal_ok = fault != 0 || (grafo_tamano(g) == 1 && exists && cost == 9);
            int atomic = status != GRAFO_MEMORIA || (g.v == before.v && g.a == before.a);
            int vertices = grafo_orden(g), edges = grafo_tamano(g);
            fail_at = 0; grafo_destruir(&g);
            int ok = invariant && normal_ok && atomic && live == 0 && g.v == NULL && g.a == NULL;
            printf("scenario=%d fault=%d endpoints=%d vertices=%d edges=%d status=%d cost=%d live_after_cleanup=%d result=%s\n",
                   scenario, fault, invariant, vertices, edges, (int)status, exists ? cost : 0, live, ok ? "PASS" : "FAIL");
            failed += !ok;
        }
    }
    return failed ? 1 : 0;
}
