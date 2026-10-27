/* Regression driver for the delivered, unchanged graph-book C contract. */
#include "tad_grafo.h"
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

static size_t attempts, fail_at, live;
void *book_qa_malloc(size_t size) {
    if (++attempts == fail_at) return NULL;
    void *p = malloc(size); if (p != NULL) ++live; return p;
}
void *book_qa_calloc(size_t count, size_t size) {
    if (++attempts == fail_at) return NULL;
    void *p = calloc(count, size); if (p != NULL) ++live; return p;
}
void book_qa_free(void *p) { if (p != NULL) { assert(live > 0); --live; } free(p); }
static void injection(size_t nth) { attempts = 0; fail_at = nth; }
static Grafo add(Grafo g, int from, int to, int cost) {
    GrafoEstado status; g = grafo_insertar_arco(g, from, to, cost, &status);
    assert(status == GRAFO_OK); return g;
}
static long long total(ListaArco list) {
    long long cost = 0; for (; list != NULL; list = list->sig) cost += list->costo;
    return cost;
}
static void atomic_insertions(void) {
    for (size_t nth = 1; nth <= 3; ++nth) {
        Grafo g = grafo_crear(); GrafoEstado status;
        injection(nth); g = grafo_insertar_arco(g, 1, 2, 7, &status);
        assert(status == GRAFO_MEMORIA && g.v == NULL && g.a == NULL && live == 0);
        grafo_destruir(&g);
    }
    injection(0); Grafo g = add(grafo_crear(), 1, 2, 7);
    ListaVertice vertices = g.v; ListaArco arcs = g.a; size_t base = live;
    for (size_t nth = 1; nth <= 3; ++nth) {
        GrafoEstado status; injection(nth);
        g = grafo_insertar_arco(g, 3, 4, 8, &status);
        assert(status == GRAFO_MEMORIA && g.v == vertices && g.a == arcs && live == base);
        assert(!grafo_existe_vertice(g, 3) && !grafo_existe_vertice(g, 4));
    }
    injection(0); grafo_destruir(&g); assert(live == 0);
}
static void algorithm_memory(void) {
    Grafo g = add(grafo_crear(), 1, 2, 3); g = add(g, 2, 1, 3);
    g = add(g, 2, 3, 4); g = add(g, 3, 2, 4);
    g = grafo_marcar_vertice(g, 1);
    ListaVertice vertices = g.v; ListaArco arcs = g.a; size_t base = live;
    for (int kind = 0; kind < 8; ++kind) {
        size_t count = 0;
        /* First discover the successful allocation count, then fail every
           actual allocation once. A changed algorithm cannot evade a slot. */
        for (size_t nth = 0; nth <= count; ++nth) {
            GrafoEstado status; ListaVertice vr = NULL; ListaArco ar = NULL;
            g = grafo_desmarcar(g); g = grafo_marcar_vertice(g, 1);
            injection(nth);
            switch (kind) {
                case 0: vr = grafo_bfs(g, 1, &status); break;
                case 1: vr = grafo_dfs(g, 1, &status); break;
                case 2: ar = grafo_dijkstra(g, 1, 3, &status); break;
                case 3: ar = grafo_bellman_ford(g, 1, 3, &status); break;
                case 4: ar = grafo_prim(g, 1, &status); break;
                case 5: ar = grafo_kruskal(g, &status); break;
                case 6: vr = grafo_sucesores(g, 2, &status); break;
                default: vr = grafo_predecesores(g, 2, &status); break;
            }
            if (nth == 0) { assert(status == GRAFO_OK); count = attempts; assert(count > 0); }
            else { assert(status == GRAFO_MEMORIA && vr == NULL && ar == NULL); }
            grafo_liberar_vertices(&vr); grafo_liberar_arcos(&ar);
            assert(live == base && g.v == vertices && g.a == arcs);
            assert(grafo_marcado_vertice(g, 1));
            if (nth == 0 && kind < 2) assert(grafo_marcado_vertice(g, 2) && grafo_marcado_vertice(g, 3));
            else assert(!grafo_marcado_vertice(g, 2) && !grafo_marcado_vertice(g, 3));
        }
    }
    injection(0); grafo_destruir(&g); assert(live == 0);
}
static void numeric_and_absence(void) {
    GrafoEstado status; Grafo g = add(grafo_crear(), 1, 2, INT_MAX);
    g = add(g, 2, 3, INT_MAX);
    ListaArco result = grafo_dijkstra(g, 1, 3, &status);
    assert(status == GRAFO_OK && total(result) == 4294967294LL); grafo_liberar_arcos(&result);
    result = grafo_bellman_ford(g, 1, 3, &status);
    assert(status == GRAFO_OK && total(result) == 4294967294LL); grafo_liberar_arcos(&result);
    int output = 123; assert(!grafo_costo_arco(g, 3, 1, &output) && output == 123);
    assert(!grafo_costo_arco(g, 1, 2, NULL));
    assert(grafo_costo_arco(g, 1, 2, &output) && output == INT_MAX);
    g = add(g, 1, 2, 0); assert(grafo_tamano(g) == 2);
    assert(grafo_costo_arco(g, 1, 2, &output) && output == 0);
    result = grafo_dijkstra(g, 1, 1, &status); assert(result == NULL && status == GRAFO_OK);
    result = grafo_dijkstra(g, 3, 1, &status); assert(result == NULL && status == GRAFO_NO_EXISTE);
    ListaVertice traversal = grafo_bfs(g, 99, &status); assert(traversal == NULL && status == GRAFO_NO_EXISTE);
    grafo_destruir(&g); assert(g.v == NULL && g.a == NULL && live == 0);
}
static void connectivity(void) {
    GrafoEstado status; Grafo g = grafo_crear();
    g = grafo_insertar_vertice(g, 1, &status); assert(status == GRAFO_OK);
    ListaArco result = grafo_prim(g, 1, &status); assert(result == NULL && status == GRAFO_OK);
    result = grafo_kruskal(g, &status); assert(result == NULL && status == GRAFO_OK);
    g = grafo_insertar_vertice(g, 2, &status); assert(status == GRAFO_OK);
    result = grafo_prim(g, 1, &status); assert(result == NULL && status == GRAFO_DESCONECTADO);
    result = grafo_kruskal(g, &status); assert(result == NULL && status == GRAFO_DESCONECTADO);
    g = add(g, 1, 2, 7);
    result = grafo_prim(g, 1, &status); assert(result == NULL && status == GRAFO_ARGUMENTO);
    g = add(g, 2, 1, 7);
    result = grafo_prim(g, 1, &status); assert(status == GRAFO_OK && total(result) == 7); grafo_liberar_arcos(&result);
    result = grafo_kruskal(g, &status); assert(status == GRAFO_OK && total(result) == 7); grafo_liberar_arcos(&result);
    grafo_destruir(&g); assert(live == 0);
}
int main(void) {
    injection(0); atomic_insertions(); injection(0); algorithm_memory();
    injection(0); numeric_and_absence(); injection(0); connectivity();
    puts("graph-book: numeric absence connectivity atomicity allocation-cleanup PASS");
    return 0;
}
