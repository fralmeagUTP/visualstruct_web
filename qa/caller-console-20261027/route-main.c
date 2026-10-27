/* main.c: llamador de la app; tad_grafo.c/h son los originales del libro. */
#include "tad_grafo.h"
#include <stdio.h>

/* GrafoEstado: 0 OK, 1 MEMORIA, 2 NO_EXISTE, 3 PESO_NEGATIVO,
   4 CICLO_NEGATIVO, 5 DESCONECTADO, 6 ARGUMENTO, 7 RANGO. */
int main(void) {
    Grafo g = grafo_crear();

    /* Llamada 1: create_graph. */
    grafo_destruir(&g);
    g = grafo_crear();

    /* Llamada 2: insert_vertex. */
    GrafoEstado estado_2;
    g = grafo_insertar_vertice(g, 1, &estado_2);
    printf("insert_vertex: estado=%d\n", (int)estado_2);

    /* Llamada 3: insert_vertex. */
    GrafoEstado estado_3;
    g = grafo_insertar_vertice(g, 2, &estado_3);
    printf("insert_vertex: estado=%d\n", (int)estado_3);

    /* Llamada 4: insert_vertex. */
    GrafoEstado estado_4;
    g = grafo_insertar_vertice(g, 3, &estado_4);
    printf("insert_vertex: estado=%d\n", (int)estado_4);

    /* Llamada 5: insert_edge. */
    GrafoEstado estado_5;
    g = grafo_insertar_arco(g, 1, 2, 2, &estado_5);
    printf("insert_edge: estado=%d\n", (int)estado_5);

    /* Llamada 6: insert_edge. */
    GrafoEstado estado_6;
    g = grafo_insertar_arco(g, 2, 3, 3, &estado_6);
    printf("insert_edge: estado=%d\n", (int)estado_6);

    /* Llamada 7: run_dijkstra. */
    GrafoEstado estado_7;
    ListaArco lista_7 = grafo_dijkstra(g, 1, 3, &estado_7);
    printf("Dijkstra: estado=%d", (int)estado_7);
    if (estado_7 == GRAFO_OK) {
        long long total = 0;
        for (ListaArco it = lista_7; it != NULL; it = it->sig) {
            printf(" %d->%d(%d)", it->origen, it->destino, it->costo);
            total = total + (long long)it->costo;
        }
        if (lista_7 == NULL) printf(" (sin arcos; resultado valido)");
        printf(" | costo=%lld", total);
    }
    printf("\n");
    grafo_liberar_arcos(&lista_7);

    grafo_destruir(&g);
    return 0;
}