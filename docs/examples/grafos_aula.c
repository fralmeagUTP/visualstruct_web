/* Ejemplo de aula: compilar junto con docs/tads_C/tad_grafo.c. */
#include <assert.h>
#include <stdio.h>
#include "tad_grafo.h"

static void mostrar_vertices(const char *titulo, ListaVertice lista) {
    printf("%s:", titulo);
    for (ListaVertice p = lista; p != NULL; p = p->sig)
        printf(" %d", p->dato);
    puts("");
}

static long long mostrar_arcos(const char *titulo, ListaArco lista) {
    long long total = 0;
    printf("%s:", titulo);
    for (ListaArco p = lista; p != NULL; p = p->sig) {
        printf(" %d->%d(%d)", p->origen, p->destino, p->costo);
        total += p->costo;
    }
    printf("; peso total = %lld\n", total);
    return total;
}

int main(void) {
    Grafo g = grafo_crear();
    g = grafo_insertar_vertice(g, 1);
    g = grafo_insertar_vertice(g, 2);
    g = grafo_insertar_vertice(g, 3);
    assert(grafo_orden(g) == 3);

    /* Cada arco C tiene dirección. Para el ejemplo no dirigido se insertan
       ambos sentidos con el mismo peso. */
    g = grafo_insertar_arco(g, 1, 2, 4);
    g = grafo_insertar_arco(g, 2, 1, 4);
    g = grafo_insertar_arco(g, 2, 3, 2);
    g = grafo_insertar_arco(g, 3, 2, 2);
    g = grafo_insertar_arco(g, 1, 3, 9);
    g = grafo_insertar_arco(g, 3, 1, 9);
    assert(grafo_tamano(g) == 6);

    /* Listas prestadas: no liberar ni modificar sus nodos por separado. */
    ListaVertice vertices = grafo_vertices(g);
    ListaArco arcos = grafo_arcos(g);
    mostrar_vertices("Vertices del grafo", vertices);
    assert(arcos != NULL);

    ListaVertice sucesores = grafo_sucesores(g, 1);
    mostrar_vertices("Sucesores de 1", sucesores);
    grafo_liberar_vertices(&sucesores);
    ListaVertice predecesores = grafo_predecesores(g, 1);
    mostrar_vertices("Predecesores de 1", predecesores);
    grafo_liberar_vertices(&predecesores);

    ListaVertice bfs = grafo_bfs(g, 1);
    mostrar_vertices("BFS desde 1", bfs);
    grafo_liberar_vertices(&bfs);
    ListaVertice dfs = grafo_dfs(g, 1);
    mostrar_vertices("DFS desde 1", dfs);
    grafo_liberar_vertices(&dfs);

    ListaArco camino = grafo_dijkstra(g, 1, 3);
    assert(camino != NULL); /* En este ejemplo conocido existe un camino. */
    long long total = mostrar_arcos("Dijkstra 1 a 3", camino);
    assert(total == 6);
    grafo_liberar_arcos(&camino);
    camino = grafo_bellman_ford(g, 1, 3);
    assert(camino != NULL);
    total = mostrar_arcos("Bellman-Ford 1 a 3", camino);
    assert(total == 6);
    grafo_liberar_arcos(&camino);

    ListaArco arbol = grafo_prim(g, 1);
    assert(arbol != NULL);
    total = mostrar_arcos("Prim", arbol);
    assert(total == 6);
    grafo_liberar_arcos(&arbol);
    arbol = grafo_kruskal(g);
    assert(arbol != NULL);
    total = mostrar_arcos("Kruskal", arbol);
    assert(total == 6);
    grafo_liberar_arcos(&arbol);

    grafo_destruir(&g); /* Invalida tambien las referencias prestadas. */
    vertices = NULL;
    arcos = NULL;
    assert(grafo_orden(g) == 0);
    return 0;
}
