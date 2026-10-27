#ifndef TAD_GRAFO_H
#define TAD_GRAFO_H
#include <stddef.h>

typedef struct NodoV {
    int dato;
    struct NodoV *sig;
    int marcado;
} *ListaVertice;

typedef struct NodoA {
    int origen, destino, costo;
    struct NodoA *sig;
} *ListaArco;

typedef struct nodoGrafo {
    ListaVertice v;
    ListaArco a;
} Grafo;

typedef enum {
    GRAFO_OK, GRAFO_MEMORIA, GRAFO_NO_EXISTE,
    GRAFO_PESO_NEGATIVO, GRAFO_CICLO_NEGATIVO,
    GRAFO_DESCONECTADO, GRAFO_ARGUMENTO, GRAFO_RANGO
} GrafoEstado;


Grafo grafo_crear(void);

Grafo grafo_insertar_vertice(Grafo g, int x, GrafoEstado *estado);

Grafo grafo_insertar_arco(Grafo g, int x, int y, int z,
                        GrafoEstado *estado);

Grafo grafo_eliminar_vertice(Grafo g, int x);

Grafo grafo_eliminar_arco(Grafo g, int x, int y);

int grafo_existe_vertice(Grafo g, int x);

int grafo_existe_arco(Grafo g, int x, int y);

int grafo_costo_arco(Grafo g, int x, int y, int *salida);

int grafo_orden(Grafo g);

int grafo_tamano(Grafo g);

int grafo_grado_vertice(Grafo g, int x);

Grafo grafo_marcar_vertice(Grafo g, int x);

Grafo grafo_desmarcar_vertice(Grafo g, int x);

Grafo grafo_desmarcar(Grafo g);

int grafo_marcado_vertice(Grafo g, int x);

ListaVertice grafo_vertices(Grafo g);

ListaArco grafo_arcos(Grafo g);

ListaVertice grafo_sucesores(Grafo g, int x, GrafoEstado *estado);

ListaVertice grafo_predecesores(Grafo g, int x, GrafoEstado *estado);

void grafo_imprimir_vertices(Grafo g);

void grafo_imprimir_arcos(Grafo g);

void grafo_liberar_vertices(ListaVertice *lista);

void grafo_liberar_arcos(ListaArco *lista);

void grafo_destruir(Grafo *g);

ListaVertice grafo_bfs(Grafo g, int inicio, GrafoEstado *estado);

ListaVertice grafo_dfs(Grafo g, int inicio, GrafoEstado *estado);

ListaArco grafo_dijkstra(Grafo g, int inicio, int llegada,
                       GrafoEstado *estado);

ListaArco grafo_bellman_ford(Grafo g, int inicio, int llegada,
                           GrafoEstado *estado);

ListaArco grafo_prim(Grafo g, int inicio, GrafoEstado *estado);

ListaArco grafo_kruskal(Grafo g, GrafoEstado *estado);

#endif
