#ifndef TAD_GRAFO_H
#define TAD_GRAFO_H

/**
 * @file tad_grafo.h
 * @brief TAD Grafo dirigido ponderado implementado con listas enlazadas.
 */

/** @brief Nodo de vertice. */
typedef struct NodoV {
    int dato;               
    struct NodoV* sig;     
    int marcado;           
} *ListaVertice;

/** @brief Nodo de arco. */
typedef struct NodoA {
    int origen;             
    int destino;           
    int costo;             
    struct NodoA* sig;      
} *ListaArco;

/** @brief Estructura principal del grafo. */
typedef struct nodoGrafo {
    ListaVertice v;         
    ListaArco a;           
} Grafo;

/** @brief Estructura auxiliar para Union-Find. */
typedef struct Conjunto {
    int *padre;             
    int n;                 
} Conjunto;

Grafo grafo_crear(void);
Grafo grafo_insertar_vertice(Grafo g, int x);
Grafo grafo_insertar_arco(Grafo g, int x, int y, int z);
void grafo_imprimir_vertices(Grafo g);
void grafo_imprimir_arcos(Grafo g);
ListaVertice grafo_vertices(Grafo g);
ListaArco grafo_arcos(Grafo g);
Grafo grafo_cambiar_vertices(Grafo g, ListaVertice k);
Grafo grafo_cambiar_arcos(Grafo g, ListaArco k);
int grafo_vacio(Grafo g);
int grafo_existe_vertice(Grafo g, int x);
int grafo_existe_arco(Grafo g, int x, int y);
Grafo grafo_eliminar_vertice(Grafo g, int x);
Grafo grafo_eliminar_arco(Grafo g, int x, int y);
int grafo_costo_arco(Grafo g, int x, int y);
int grafo_orden(Grafo g);
int grafo_tamano(Grafo g);
int grafo_grado_vertice(Grafo g, int x);
Grafo grafo_desmarcar_vertice(Grafo g, int x);
Grafo grafo_desmarcar(Grafo g);
Grafo grafo_marcar_vertice(Grafo g, int x);
int grafo_marcado_vertice(Grafo g, int x);
ListaVertice grafo_sucesores(Grafo g, int x);
ListaVertice grafo_predecesores(Grafo g, int x);
ListaVertice grafo_bfs(Grafo g, int inicio);
void grafo_dfs_recursivo(Grafo g, int actual, ListaVertice *recorrido);
ListaVertice grafo_dfs(Grafo g, int inicio);
ListaArco grafo_dijkstra(Grafo g, int inicio, int llegada);
ListaArco grafo_bellman_ford(Grafo g, int inicio, int llegada);
ListaArco grafo_prim(Grafo g, int inicio);
int grafo_encontrar_conjunto(Conjunto *c, int x);
void grafo_unir_conjuntos(Conjunto *c, int x, int y);
ListaArco grafo_kruskal(Grafo g);

#endif
