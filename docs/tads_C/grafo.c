/**
 * @file grafo.c
 * @brief ImplementaciÃ³n del TAD Grafo con algoritmos clÃ¡sicos.
 *
 * Implementa grafos dirigidos y no dirigidos usando lista de adyacencia.
 * Los vÃ©rtices se almacenan en una lista enlazada, y cada vÃ©rtice tiene
 * una lista enlazada de aristas salientes.
 *
 * @author Francisco Alejandro Medina Aguirre
 * @date 2026
 * @version 1.0
 */

#include "grafo.h"
#include <stdlib.h>
#include <string.h>
#include <limits.h>

/* ============================================================================
 * Estructuras internas (no visibles al usuario)
 * ============================================================================ */

/**
 * @brief Nodo de una arista en la lista de adyacencia.
 */
typedef struct NodoArista {
    int destino;                    /**< VÃ©rtice destino */
    int peso;                       /**< Peso de la arista */
    struct NodoArista *siguiente;   /**< Siguiente arista */
} NodoArista;

/**
 * @brief Nodo de un vÃ©rtice en la lista de vÃ©rtices.
 */
typedef struct NodoVertice {
    int vertice;                    /**< Identificador del vÃ©rtice */
    NodoArista *aristas;            /**< Lista de aristas salientes */
    struct NodoVertice *siguiente;  /**< Siguiente vÃ©rtice */
} NodoVertice;

/**
 * @brief Estructura interna del grafo.
 */
struct Grafo {
    NodoVertice *cabeza;            /**< Cabeza de la lista de vÃ©rtices */
    bool dirigido;                  /**< true si dirigido; false si no dirigido */
};

/**
 * @brief Busca el índice de un vértice en el arreglo de vértices.
 *
 * @param[in] vertices   Arreglo de identificadores de vértices.
 * @param[in] n          Número total de vértices en el arreglo.
 * @param[in] id_vertice Identificador a buscar.
 *
 * @return El índice del vértice si se encuentra, o -1 si no existe.
 *
 * @note Complejidad temporal: O(n).
 */
static int grafo_indice_vertice(const int *vertices, size_t n, int id_vertice)
{
    size_t i;
    if (vertices == NULL) return -1;
    for (i = 0; i < n; i++) {
        if (vertices[i] == id_vertice) {
            return (int)i;
        }
    }
    return -1;
}

/**
 * @brief Encuentra la raíz del conjunto al que pertenece el elemento (Union-Find).
 *
 * @details
 * Implementa la optimización de compresión de caminos (path compression) para
 * hacer futuras búsquedas más rápidas.
 *
 * @param[in,out] padre Arreglo de padres del Union-Find.
 * @param[in]     x     Elemento a buscar.
 *
 * @return La raíz del conjunto que contiene a x.
 *
 * @note Complejidad temporal: O(α(V)), donde α es la inversa de la función de Ackermann.
 */
static int uf_find(int *padre, int x)
{
    int raiz = x;
    while (padre[raiz] != raiz) {
        raiz = padre[raiz];
    }
    while (padre[x] != x) {
        int sig = padre[x];
        padre[x] = raiz;
        x = sig;
    }
    return raiz;
}

/**
 * @brief Une dos conjuntos disjuntos (Union-Find).
 *
 * @details
 * Implementa la optimización de unión por rango (union by rank) para mantener
 * el árbol lo más plano posible.
 *
 * @param[in,out] padre Arreglo de padres del Union-Find.
 * @param[in,out] rango Arreglo de rangos del Union-Find.
 * @param[in]     x     Elemento del primer conjunto.
 * @param[in]     y     Elemento del segundo conjunto.
 *
 * @note Complejidad temporal: O(α(V)).
 */
static void uf_union(int *padre, int *rango, int x, int y)
{
    int rx = uf_find(padre, x);
    int ry = uf_find(padre, y);
    if (rx == ry) return;

    if (rango[rx] < rango[ry]) {
        padre[rx] = ry;
    } else if (rango[rx] > rango[ry]) {
        padre[ry] = rx;
    } else {
        padre[ry] = rx;
        rango[rx]++;
    }
}

/* ============================================================================
 * Funciones auxiliares privadas
 * ============================================================================ */

/**
 * @brief Busca un vÃ©rtice en el grafo.
 *
 * @param[in] grafo Puntero al grafo
 * @param[in] vertice Identificador del vÃ©rtice
 * @return Puntero al nodo del vÃ©rtice; NULL si no existe
 */
static NodoVertice *grafo_buscar_vertice(const Grafo *grafo, int vertice)
{
    if (!grafo) return NULL;
    
    NodoVertice *actual = grafo->cabeza;
    while (actual) {
        if (actual->vertice == vertice) {
            return actual;
        }
        actual = actual->siguiente;
    }
    return NULL;
}

/**
 * @brief Busca una arista en la lista de adyacencia de un vÃ©rtice.
 *
 * @param[in] nodo_vertice Puntero al nodo del vÃ©rtice
 * @param[in] destino VÃ©rtice destino de la arista
 * @return Puntero a la arista; NULL si no existe
 */
static NodoArista *grafo_buscar_arista(const NodoVertice *nodo_vertice, int destino)
{
    if (!nodo_vertice) return NULL;
    
    NodoArista *actual = nodo_vertice->aristas;
    while (actual) {
        if (actual->destino == destino) {
            return actual;
        }
        actual = actual->siguiente;
    }
    return NULL;
}

/**
 * @brief Inserta una arista en la lista de adyacencia (sin validar duplicados).
 *
 * @param[in,out] nodo_vertice Puntero al nodo del vÃ©rtice
 * @param[in] destino VÃ©rtice destino
 * @param[in] peso Peso de la arista
 * @return true si la inserciÃ³n fue exitosa; false si falla asignaciÃ³n de memoria
 */
static bool grafo_insertar_arista_interna(NodoVertice *nodo_vertice, int destino, int peso)
{
    if (!nodo_vertice) return false;
    
    NodoArista *nueva = (NodoArista *)malloc(sizeof(NodoArista));
    if (!nueva) return false;
    
    nueva->destino = destino;
    nueva->peso = peso;
    nueva->siguiente = nodo_vertice->aristas;
    nodo_vertice->aristas = nueva;
    
    return true;
}

/**
 * @brief Elimina una arista de la lista de adyacencia.
 *
 * @param[in,out] nodo_vertice Puntero al nodo del vÃ©rtice
 * @param[in] destino VÃ©rtice destino de la arista a eliminar
 * @return true si se eliminÃ³; false si la arista no existe
 */
static bool grafo_eliminar_arista_interna(NodoVertice *nodo_vertice, int destino)
{
    if (!nodo_vertice) return false;
    
    if (nodo_vertice->aristas && nodo_vertice->aristas->destino == destino) {
        NodoArista *temp = nodo_vertice->aristas;
        nodo_vertice->aristas = nodo_vertice->aristas->siguiente;
        free(temp);
        return true;
    }
    
    NodoArista *actual = nodo_vertice->aristas;
    while (actual && actual->siguiente) {
        if (actual->siguiente->destino == destino) {
            NodoArista *temp = actual->siguiente;
            actual->siguiente = actual->siguiente->siguiente;
            free(temp);
            return true;
        }
        actual = actual->siguiente;
    }
    
    return false;
}

/**
 * @brief Libera todas las aristas de un vÃ©rtice.
 *
 * @param[in,out] nodo_vertice Puntero al nodo del vÃ©rtice
 */
static void grafo_liberar_aristas(NodoVertice *nodo_vertice)
{
    if (!nodo_vertice) return;
    
    NodoArista *actual = nodo_vertice->aristas;
    while (actual) {
        NodoArista *temp = actual;
        actual = actual->siguiente;
        free(temp);
    }
    nodo_vertice->aristas = NULL;
}

/* ============================================================================
 * CreaciÃ³n y destrucciÃ³n
 * ============================================================================ */

/**
 * @brief Crea un nuevo grafo vacío.
 *
 * @param[in] dirigido true para grafo dirigido; false para no dirigido.
 *
 * @return Puntero a grafo creado; NULL si falla la asignación de memoria.
 *
 * @note El grafo retornado debe liberarse con grafo_destruir().
 * @note Complejidad temporal: O(1).
 */
Grafo *grafo_crear(bool dirigido)
{
    Grafo *nuevo = (Grafo *)malloc(sizeof(Grafo));
    if (!nuevo) return NULL;
    
    nuevo->cabeza = NULL;
    nuevo->dirigido = dirigido;
    
    return nuevo;
}

/**
 * @brief Destruye un grafo y libera toda su memoria.
 *
 * @param[in,out] grafo Puntero al puntero del grafo a destruir.
 *
 * @post El grafo y todos sus datos son liberados; *grafo == NULL.
 * @note Complejidad temporal: O(V + E).
 */
void grafo_destruir(Grafo **grafo)
{
    if (!grafo || !*grafo) return;
    
    NodoVertice *actual = (*grafo)->cabeza;
    while (actual) {
        NodoVertice *temp = actual;
        actual = actual->siguiente;
        grafo_liberar_aristas(temp);
        free(temp);
    }
    
    free(*grafo);
    *grafo = NULL;
}

/**
 * @brief Indica si el grafo es dirigido.
 *
 * @param[in] grafo Puntero al grafo.
 *
 * @return true si el grafo es dirigido; false si es no dirigido o nulo.
 *
 * @note Complejidad temporal: O(1).
 */
bool grafo_es_dirigido(const Grafo *grafo)
{
    if (!grafo) return false;
    return grafo->dirigido;
}

/* ============================================================================
 * Operaciones estructurales
 * ============================================================================ */

/**
 * @brief Inserta un vértice en el grafo.
 *
 * @param[in,out] grafo   Puntero al grafo.
 * @param[in]     vertice Identificador entero del vértice.
 *
 * @return Estado de la operación (GRAFO_OK, GRAFO_ERROR_YA_EXISTE, etc).
 *
 * @post El vértice se agrega al final de la lista de vértices si no existía.
 * @note Complejidad temporal: O(V).
 */
GrafoEstado grafo_insertar_vertice(Grafo *grafo, int vertice)
{
    if (!grafo) return GRAFO_ERROR_NULO;
    
    if (grafo_existe_vertice(grafo, vertice)) {
        return GRAFO_ERROR_YA_EXISTE;
    }
    
    NodoVertice *nuevo = (NodoVertice *)malloc(sizeof(NodoVertice));
    if (!nuevo) return GRAFO_ERROR_MEMORIA;
    
    nuevo->vertice = vertice;
    nuevo->aristas = NULL;
    nuevo->siguiente = grafo->cabeza;
    grafo->cabeza = nuevo;
    
    return GRAFO_OK;
}

/**
 * @brief Inserta una arista entre dos vértices.
 *
 * @param[in,out] grafo   Puntero al grafo.
 * @param[in]     origen  Vértice de origen.
 * @param[in]     destino Vértice de destino.
 * @param[in]     peso    Peso de la arista.
 *
 * @return Estado de la operación.
 *
 * @note Complejidad temporal: O(V) para buscar vértices + O(1) para insertar.
 */
GrafoEstado grafo_insertar_arista(Grafo *grafo, int origen, int destino, int peso)
{
    if (!grafo) return GRAFO_ERROR_NULO;
    
    NodoVertice *nodo_origen = grafo_buscar_vertice(grafo, origen);
    if (!nodo_origen) return GRAFO_ERROR_NO_EXISTE;
    
    NodoVertice *nodo_destino = grafo_buscar_vertice(grafo, destino);
    if (!nodo_destino) return GRAFO_ERROR_NO_EXISTE;
    
    if (grafo_existe_arista(grafo, origen, destino)) {
        return GRAFO_ERROR_YA_EXISTE;
    }
    
    if (!grafo_insertar_arista_interna(nodo_origen, destino, peso)) {
        return GRAFO_ERROR_MEMORIA;
    }
    
    if (!grafo->dirigido) {
        if (!grafo_insertar_arista_interna(nodo_destino, origen, peso)) {
            grafo_eliminar_arista_interna(nodo_origen, destino);
            return GRAFO_ERROR_MEMORIA;
        }
    }
    
    return GRAFO_OK;
}

/**
 * @brief Elimina un vértice y todas sus aristas incidentes.
 *
 * @param[in,out] grafo   Puntero al grafo.
 * @param[in]     vertice Identificador del vértice a eliminar.
 *
 * @return Estado de la operación.
 *
 * @note Complejidad temporal: O(V + E).
 */
GrafoEstado grafo_eliminar_vertice(Grafo *grafo, int vertice)
{
    if (!grafo) return GRAFO_ERROR_NULO;
    
    NodoVertice *nodo = grafo_buscar_vertice(grafo, vertice);
    if (!nodo) return GRAFO_ERROR_NO_EXISTE;
    
    /* Eliminar aristas incidentes de otros vÃ©rtices */
    NodoVertice *actual = grafo->cabeza;
    while (actual) {
        if (actual->vertice != vertice) {
            grafo_eliminar_arista_interna(actual, vertice);
        }
        actual = actual->siguiente;
    }
    
    /* Eliminar el vÃ©rtice de la lista */
    if (grafo->cabeza->vertice == vertice) {
        NodoVertice *temp = grafo->cabeza;
        grafo->cabeza = grafo->cabeza->siguiente;
        grafo_liberar_aristas(temp);
        free(temp);
    } else {
        NodoVertice *anterior = grafo->cabeza;
        while (anterior && anterior->siguiente->vertice != vertice) {
            anterior = anterior->siguiente;
        }
        if (anterior) {
            NodoVertice *temp = anterior->siguiente;
            anterior->siguiente = anterior->siguiente->siguiente;
            grafo_liberar_aristas(temp);
            free(temp);
        }
    }
    
    return GRAFO_OK;
}

/**
 * @brief Elimina una arista entre dos vértices.
 *
 * @param[in,out] grafo   Puntero al grafo.
 * @param[in]     origen  Vértice de origen.
 * @param[in]     destino Vértice de destino.
 *
 * @return Estado de la operación.
 *
 * @note Complejidad temporal: O(V + E_v).
 */
GrafoEstado grafo_eliminar_arista(Grafo *grafo, int origen, int destino)
{
    if (!grafo) return GRAFO_ERROR_NULO;
    
    NodoVertice *nodo_origen = grafo_buscar_vertice(grafo, origen);
    if (!nodo_origen) return GRAFO_ERROR_NO_EXISTE;
    
    if (!grafo_existe_arista(grafo, origen, destino)) {
        return GRAFO_ERROR_NO_EXISTE;
    }
    
    grafo_eliminar_arista_interna(nodo_origen, destino);
    
    if (!grafo->dirigido) {
        NodoVertice *nodo_destino = grafo_buscar_vertice(grafo, destino);
        if (nodo_destino) {
            grafo_eliminar_arista_interna(nodo_destino, origen);
        }
    }
    
    return GRAFO_OK;
}

/* ============================================================================
 * Consultas
 * ============================================================================ */

/**
 * @brief Verifica si un vértice existe en el grafo.
 *
 * @param[in] grafo   Puntero al grafo.
 * @param[in] vertice Identificador del vértice.
 *
 * @return true si el vértice existe; false en caso contrario.
 *
 * @note Complejidad temporal: O(V).
 */
bool grafo_existe_vertice(const Grafo *grafo, int vertice)
{
    return grafo_buscar_vertice(grafo, vertice) != NULL;
}

/**
 * @brief Verifica si una arista existe en el grafo.
 *
 * @param[in] grafo   Puntero al grafo.
 * @param[in] origen  Vértice de origen.
 * @param[in] destino Vértice de destino.
 *
 * @return true si la arista existe; false en caso contrario.
 *
 * @note Complejidad temporal: O(V + E_v).
 */
bool grafo_existe_arista(const Grafo *grafo, int origen, int destino)
{
    if (!grafo) return false;
    
    NodoVertice *nodo_origen = grafo_buscar_vertice(grafo, origen);
    if (!nodo_origen) return false;
    
    return grafo_buscar_arista(nodo_origen, destino) != NULL;
}

/**
 * @brief Obtiene el peso de una arista.
 *
 * @param[in]  grafo   Puntero al grafo.
 * @param[in]  origen  Vértice de origen.
 * @param[in]  destino Vértice de destino.
 * @param[out] peso    Puntero donde se almacenará el peso.
 *
 * @return Estado de la operación.
 *
 * @note Complejidad temporal: O(V + E_v).
 */
GrafoEstado grafo_obtener_peso(const Grafo *grafo, int origen, int destino, int *peso)
{
    if (!grafo || !peso) return GRAFO_ERROR_NULO;
    
    NodoVertice *nodo_origen = grafo_buscar_vertice(grafo, origen);
    if (!nodo_origen) return GRAFO_ERROR_NO_EXISTE;
    
    NodoArista *arista = grafo_buscar_arista(nodo_origen, destino);
    if (!arista) return GRAFO_ERROR_NO_EXISTE;
    
    *peso = arista->peso;
    return GRAFO_OK;
}

/**
 * @brief Retorna el orden del grafo (cantidad de vértices).
 *
 * @param[in] grafo Puntero al grafo.
 *
 * @return Cantidad de vértices en el grafo.
 *
 * @note Complejidad temporal: O(V).
 */
size_t grafo_orden(const Grafo *grafo)
{
    if (!grafo) return 0;
    
    size_t cantidad = 0;
    NodoVertice *actual = grafo->cabeza;
    while (actual) {
        cantidad++;
        actual = actual->siguiente;
    }
    return cantidad;
}

/**
 * @brief Retorna el tamaño del grafo (cantidad de aristas).
 *
 * @param[in] grafo Puntero al grafo.
 *
 * @return Cantidad de aristas en el grafo. En grafos no dirigidos, cuenta cada arista una vez.
 *
 * @note Complejidad temporal: O(V + E).
 */
size_t grafo_tamano(const Grafo *grafo)
{
    if (!grafo) return 0;
    
    size_t cantidad = 0;
    NodoVertice *actual = grafo->cabeza;
    while (actual) {
        NodoArista *arista = actual->aristas;
        while (arista) {
            cantidad++;
            arista = arista->siguiente;
        }
        actual = actual->siguiente;
    }
    
    /* En grafos no dirigidos, cada arista se cuenta dos veces */
    if (!grafo->dirigido) {
        cantidad /= 2;
    }
    
    return cantidad;
}

/**
 * @brief Obtiene el grado de salida de un vértice.
 *
 * @param[in]  grafo   Puntero al grafo.
 * @param[in]  vertice Identificador del vértice.
 * @param[out] grado   Puntero al grado de salida.
 *
 * @return Estado de la operación.
 *
 * @note Complejidad temporal: O(V + E_v).
 */
GrafoEstado grafo_grado_salida(const Grafo *grafo, int vertice, size_t *grado)
{
    if (!grafo || !grado) return GRAFO_ERROR_NULO;
    
    NodoVertice *nodo = grafo_buscar_vertice(grafo, vertice);
    if (!nodo) return GRAFO_ERROR_NO_EXISTE;
    
    *grado = 0;
    NodoArista *actual = nodo->aristas;
    while (actual) {
        (*grado)++;
        actual = actual->siguiente;
    }
    
    return GRAFO_OK;
}

/**
 * @brief Obtiene el grado de entrada de un vértice.
 *
 * @param[in]  grafo   Puntero al grafo.
 * @param[in]  vertice Identificador del vértice.
 * @param[out] grado   Puntero al grado de entrada.
 *
 * @return Estado de la operación.
 *
 * @note Complejidad temporal: O(V + E).
 */
GrafoEstado grafo_grado_entrada(const Grafo *grafo, int vertice, size_t *grado)
{
    if (!grafo || !grado) return GRAFO_ERROR_NULO;
    
    if (!grafo_existe_vertice(grafo, vertice)) {
        return GRAFO_ERROR_NO_EXISTE;
    }
    
    *grado = 0;
    NodoVertice *actual = grafo->cabeza;
    while (actual) {
        if (grafo_existe_arista(grafo, actual->vertice, vertice)) {
            (*grado)++;
        }
        actual = actual->siguiente;
    }
    
    return GRAFO_OK;
}

/* ============================================================================
 * Copias pÃºblicas de datos
 * ============================================================================ */

/**
 * @brief Obtiene una copia dinámica del array de vértices del grafo.
 *
 * @param[in]  grafo    Puntero al grafo.
 * @param[out] vertices Puntero al arreglo dinámico de vértices.
 * @param[out] cantidad Puntero a la cantidad de vértices copiados.
 *
 * @return Estado de la operación.
 *
 * @post El usuario es responsable de liberar el arreglo con free().
 * @note Complejidad temporal: O(V).
 */
GrafoEstado grafo_obtener_vertices(const Grafo *grafo, int **vertices, size_t *cantidad)
{
    if (!grafo || !vertices || !cantidad) return GRAFO_ERROR_NULO;
    
    *cantidad = grafo_orden(grafo);
    if (*cantidad == 0) {
        *vertices = NULL;
        return GRAFO_OK;
    }
    
    *vertices = (int *)malloc((*cantidad) * sizeof(int));
    if (!*vertices) return GRAFO_ERROR_MEMORIA;
    
    size_t idx = 0;
    NodoVertice *actual = grafo->cabeza;
    while (actual) {
        (*vertices)[idx++] = actual->vertice;
        actual = actual->siguiente;
    }
    
    return GRAFO_OK;
}

/**
 * @brief Obtiene una copia dinámica del array de aristas del grafo.
 *
 * @param[in]  grafo    Puntero al grafo.
 * @param[out] aristas  Puntero al arreglo dinámico de aristas.
 * @param[out] cantidad Puntero a la cantidad de aristas copiadas.
 *
 * @return Estado de la operación.
 *
 * @post El usuario es responsable de liberar el arreglo con free().
 * @note Complejidad temporal: O(V + E).
 */
GrafoEstado grafo_obtener_aristas(const Grafo *grafo, GrafoArista **aristas, size_t *cantidad)
{
    if (!grafo || !aristas || !cantidad) return GRAFO_ERROR_NULO;
    
    *cantidad = grafo_tamano(grafo);
    if (*cantidad == 0) {
        *aristas = NULL;
        return GRAFO_OK;
    }
    
    *aristas = (GrafoArista *)malloc((*cantidad) * sizeof(GrafoArista));
    if (!*aristas) return GRAFO_ERROR_MEMORIA;
    
    size_t idx = 0;
    NodoVertice *actual = grafo->cabeza;
    while (actual) {
        NodoArista *arista = actual->aristas;
        while (arista) {
            if (grafo->dirigido || actual->vertice < arista->destino) {
                (*aristas)[idx].origen = actual->vertice;
                (*aristas)[idx].destino = arista->destino;
                (*aristas)[idx].peso = arista->peso;
                idx++;
            }
            arista = arista->siguiente;
        }
        actual = actual->siguiente;
    }
    
    return GRAFO_OK;
}

/**
 * @brief Obtiene los sucesores directos de un vértice.
 *
 * @param[in]  grafo     Puntero al grafo.
 * @param[in]  vertice   Identificador del vértice origen.
 * @param[out] sucesores Puntero al arreglo dinámico de vértices sucesores.
 * @param[out] cantidad  Puntero a la cantidad de sucesores.
 *
 * @return Estado de la operación.
 *
 * @post El usuario es responsable de liberar el arreglo con free().
 * @note Complejidad temporal: O(V + E_v).
 */
GrafoEstado grafo_sucesores(const Grafo *grafo, int vertice, int **sucesores, size_t *cantidad)
{
    if (!grafo || !sucesores || !cantidad) return GRAFO_ERROR_NULO;
    
    NodoVertice *nodo = grafo_buscar_vertice(grafo, vertice);
    if (!nodo) return GRAFO_ERROR_NO_EXISTE;
    
    *cantidad = 0;
    NodoArista *arista = nodo->aristas;
    while (arista) {
        (*cantidad)++;
        arista = arista->siguiente;
    }
    
    if (*cantidad == 0) {
        *sucesores = NULL;
        return GRAFO_OK;
    }
    
    *sucesores = (int *)malloc((*cantidad) * sizeof(int));
    if (!*sucesores) return GRAFO_ERROR_MEMORIA;
    
    size_t idx = 0;
    arista = nodo->aristas;
    while (arista) {
        (*sucesores)[idx++] = arista->destino;
        arista = arista->siguiente;
    }
    
    return GRAFO_OK;
}

/**
 * @brief Obtiene los predecesores directos de un vértice.
 *
 * @param[in]  grafo        Puntero al grafo.
 * @param[in]  vertice      Identificador del vértice destino.
 * @param[out] predecesores Puntero al arreglo dinámico de vértices predecesores.
 * @param[out] cantidad     Puntero a la cantidad de predecesores.
 *
 * @return Estado de la operación.
 *
 * @post El usuario es responsable de liberar el arreglo con free().
 * @note Complejidad temporal: O(V + E).
 */
GrafoEstado grafo_predecesores(const Grafo *grafo, int vertice, int **predecesores, size_t *cantidad)
{
    if (!grafo || !predecesores || !cantidad) return GRAFO_ERROR_NULO;
    
    if (!grafo_existe_vertice(grafo, vertice)) {
        return GRAFO_ERROR_NO_EXISTE;
    }
    
    *cantidad = 0;
    NodoVertice *actual = grafo->cabeza;
    while (actual) {
        if (grafo_existe_arista(grafo, actual->vertice, vertice)) {
            (*cantidad)++;
        }
        actual = actual->siguiente;
    }
    
    if (*cantidad == 0) {
        *predecesores = NULL;
        return GRAFO_OK;
    }
    
    *predecesores = (int *)malloc((*cantidad) * sizeof(int));
    if (!*predecesores) return GRAFO_ERROR_MEMORIA;
    
    size_t idx = 0;
    actual = grafo->cabeza;
    while (actual) {
        if (grafo_existe_arista(grafo, actual->vertice, vertice)) {
            (*predecesores)[idx++] = actual->vertice;
        }
        actual = actual->siguiente;
    }
    
    return GRAFO_OK;
}

/* ============================================================================
 * Algoritmos
 * ============================================================================ */

/**
 * @brief Ejecuta BFS (búsqueda en amplitud) desde un vértice inicial.
 *
 * @param[in] grafo  Puntero al grafo.
 * @param[in] inicio Vértice de inicio.
 *
 * @return Estructura GrafoRecorrido con el orden de visita.
 *
 * @note Complejidad temporal: O(V + E).
 */
GrafoRecorrido grafo_bfs(const Grafo *grafo, int inicio)
{
    GrafoRecorrido resultado = {NULL, 0, GRAFO_ERROR_NULO};
    
    if (!grafo) return resultado;
    
    if (!grafo_existe_vertice(grafo, inicio)) {
        resultado.estado = GRAFO_ERROR_NO_EXISTE;
        return resultado;
    }
    
    size_t orden = grafo_orden(grafo);
    if (orden == 0) {
        resultado.estado = GRAFO_OK;
        return resultado;
    }
    
    /* Arrays auxiliares */
    bool *visitado = (bool *)calloc(5000, sizeof(bool));
    int *cola = (int *)malloc(orden * sizeof(int));
    resultado.vertices = (int *)malloc(orden * sizeof(int));
    
    if (!visitado || !cola || !resultado.vertices) {
        free(visitado);
        free(cola);
        free(resultado.vertices);
        resultado.vertices = NULL;
        resultado.estado = GRAFO_ERROR_MEMORIA;
        return resultado;
    }
    
    /* BFS */
    int frente = 0, atras = 0;
    visitado[inicio] = true;
    cola[atras++] = inicio;
    
    while (frente < atras) {
        int actual = cola[frente++];
        resultado.vertices[resultado.cantidad++] = actual;
        
        int *sucesores = NULL;
        size_t cant_sucesores = 0;
        if (grafo_sucesores(grafo, actual, &sucesores, &cant_sucesores) == GRAFO_OK && sucesores) {
            for (size_t i = 0; i < cant_sucesores; i++) {
                if (!visitado[sucesores[i]]) {
                    visitado[sucesores[i]] = true;
                    cola[atras++] = sucesores[i];
                }
            }
            free(sucesores);
        }
    }
    
    free(visitado);
    free(cola);
    resultado.estado = GRAFO_OK;
    return resultado;
}

/**
 * @brief Ejecuta DFS (búsqueda en profundidad) desde un vértice inicial.
 *
 * @param[in] grafo  Puntero al grafo.
 * @param[in] inicio Vértice de inicio.
 *
 * @return Estructura GrafoRecorrido con el orden de visita.
 *
 * @note Complejidad temporal: O(V + E).
 */
GrafoRecorrido grafo_dfs(const Grafo *grafo, int inicio)
{
    GrafoRecorrido resultado = {NULL, 0, GRAFO_ERROR_NULO};
    
    if (!grafo) return resultado;
    
    if (!grafo_existe_vertice(grafo, inicio)) {
        resultado.estado = GRAFO_ERROR_NO_EXISTE;
        return resultado;
    }
    
    size_t orden = grafo_orden(grafo);
    if (orden == 0) {
        resultado.estado = GRAFO_OK;
        return resultado;
    }
    
    /* Arrays auxiliares */
    bool *visitado = (bool *)calloc(5000, sizeof(bool));
    int *pila = (int *)malloc(orden * sizeof(int));
    resultado.vertices = (int *)malloc(orden * sizeof(int));
    
    if (!visitado || !pila || !resultado.vertices) {
        free(visitado);
        free(pila);
        free(resultado.vertices);
        resultado.vertices = NULL;
        resultado.estado = GRAFO_ERROR_MEMORIA;
        return resultado;
    }
    
    /* DFS iterativo */
    int tope = 0;
    visitado[inicio] = true;
    pila[tope++] = inicio;
    
    while (tope > 0) {
        int actual = pila[--tope];
        resultado.vertices[resultado.cantidad++] = actual;
        
        int *sucesores = NULL;
        size_t cant_sucesores = 0;
        if (grafo_sucesores(grafo, actual, &sucesores, &cant_sucesores) == GRAFO_OK && sucesores) {
            for (size_t i = 0; i < cant_sucesores; i++) {
                if (!visitado[sucesores[i]]) {
                    visitado[sucesores[i]] = true;
                    pila[tope++] = sucesores[i];
                }
            }
            free(sucesores);
        }
    }
    
    free(visitado);
    free(pila);
    resultado.estado = GRAFO_OK;
    return resultado;
}

/**
 * @brief Función auxiliar para encontrar el índice de un vértice en un arreglo temporal.
 *
 * @param[in] vertices Arreglo de vértices.
 * @param[in] cantidad Tamaño del arreglo.
 * @param[in] id       Identificador buscado.
 *
 * @return El índice si existe, -1 en caso contrario.
 *
 * @note Complejidad temporal: O(N).
 */
static int grafo_idx_vertice_id(const int *vertices, size_t cantidad, int id) {
    size_t i;
    if (vertices == NULL) {
        return -1;
    }
    for (i = 0; i < cantidad; i++) {
        if (vertices[i] == id) {
            return (int)i;
        }
    }
    return -1;
}
/**
 * @brief Calcula el camino mínimo entre dos vértices con Dijkstra.
 *
 * @param[in] grafo   Puntero al grafo.
 * @param[in] origen  Vértice de origen.
 * @param[in] destino Vértice de destino.
 *
 * @return Estructura GrafoCamino con el camino y costo total.
 *
 * @note No acepta pesos negativos.
 * @note Complejidad temporal: O(V² + E).
 */
GrafoCamino grafo_dijkstra(const Grafo *grafo, int origen, int destino)
{
    GrafoCamino resultado = {NULL, 0, 0, false, GRAFO_ERROR_NULO};
    int *vertices = NULL;
    size_t n_vertices = 0;
    int *dist = NULL;
    int *predecesor = NULL;
    bool *visitado = NULL;
    int *camino_aux = NULL;
    int idx_origen;
    int idx_destino;
    size_t i;
    if (!grafo) return resultado;
    if (!grafo_existe_vertice(grafo, origen) || !grafo_existe_vertice(grafo, destino)) {
        resultado.estado = GRAFO_ERROR_NO_EXISTE;
        return resultado;
    }
    if (grafo_obtener_vertices(grafo, &vertices, &n_vertices) != GRAFO_OK || vertices == NULL) {
        resultado.estado = GRAFO_ERROR_MEMORIA;
        return resultado;
    }
    idx_origen = grafo_idx_vertice_id(vertices, n_vertices, origen);
    idx_destino = grafo_idx_vertice_id(vertices, n_vertices, destino);
    if (idx_origen < 0 || idx_destino < 0) {
        free(vertices);
        resultado.estado = GRAFO_ERROR_NO_EXISTE;
        return resultado;
    }
    dist = (int *)malloc(n_vertices * sizeof(int));
    predecesor = (int *)malloc(n_vertices * sizeof(int));
    visitado = (bool *)calloc(n_vertices, sizeof(bool));
    camino_aux = (int *)malloc(n_vertices * sizeof(int));
    if (dist == NULL || predecesor == NULL || visitado == NULL || camino_aux == NULL) {
        free(vertices);
        free(dist);
        free(predecesor);
        free(visitado);
        free(camino_aux);
        resultado.estado = GRAFO_ERROR_MEMORIA;
        return resultado;
    }
    for (i = 0; i < n_vertices; i++) {
        dist[i] = INT_MAX;
        predecesor[i] = -1;
    }
    dist[idx_origen] = 0;
    for (i = 0; i < n_vertices; i++) {
        int min_dist = INT_MAX;
        int u_idx = -1;
        size_t j;
        for (j = 0; j < n_vertices; j++) {
            if (!visitado[j] && dist[j] < min_dist) {
                min_dist = dist[j];
                u_idx = (int)j;
            }
        }
        if (u_idx < 0) {
            break;
        }
        visitado[u_idx] = true;
        {
            int u_id = vertices[u_idx];
            int *sucesores = NULL;
            size_t cant = 0;
            if (grafo_sucesores(grafo, u_id, &sucesores, &cant) == GRAFO_OK && sucesores != NULL) {
                for (j = 0; j < cant; j++) {
                    int v_id = sucesores[j];
                    int v_idx = grafo_idx_vertice_id(vertices, n_vertices, v_id);
                    int peso = 0;
                    if (v_idx < 0) {
                        continue;
                    }
                    if (grafo_obtener_peso(grafo, u_id, v_id, &peso) != GRAFO_OK) {
                        continue;
                    }
                    if (peso < 0) {
                        free(vertices);
                        free(dist);
                        free(predecesor);
                        free(visitado);
                        free(camino_aux);
                        free(sucesores);
                        resultado.estado = GRAFO_ERROR_PESO_NEGATIVO;
                        return resultado;
                    }
                    if (dist[u_idx] != INT_MAX) {
                        long long candidato = (long long)dist[u_idx] + (long long)peso;
                        if (candidato < (long long)dist[v_idx]) {
                            dist[v_idx] = (int)candidato;
                            predecesor[v_idx] = u_idx;
                        }
                    }
                }
                free(sucesores);
            }
        }
    }
    if (dist[idx_destino] == INT_MAX) {
        free(vertices);
        free(dist);
        free(predecesor);
        free(visitado);
        free(camino_aux);
        resultado.estado = GRAFO_OK;
        resultado.existe = false;
        return resultado;
    }
    {
        int tope = 0;
        int actual = idx_destino;
        while (actual != -1 && tope < (int)n_vertices) {
            camino_aux[tope++] = vertices[actual];
            actual = predecesor[actual];
        }
        if (tope <= 0 || camino_aux[tope - 1] != origen) {
            free(vertices);
            free(dist);
            free(predecesor);
            free(visitado);
            free(camino_aux);
            resultado.estado = GRAFO_OK;
            resultado.existe = false;
            return resultado;
        }
        resultado.cantidad = (size_t)(tope - 1);
        if (resultado.cantidad > 0) {
            int k;
            resultado.aristas = (GrafoArista *)malloc(resultado.cantidad * sizeof(GrafoArista));
            if (resultado.aristas == NULL) {
                free(vertices);
                free(dist);
                free(predecesor);
                free(visitado);
                free(camino_aux);
                resultado.estado = GRAFO_ERROR_MEMORIA;
                return resultado;
            }
            for (k = tope - 1; k > 0; k--) {
                int u = camino_aux[k];
                int v = camino_aux[k - 1];
                int peso = 0;
                grafo_obtener_peso(grafo, u, v, &peso);
                resultado.aristas[tope - 1 - k].origen = u;
                resultado.aristas[tope - 1 - k].destino = v;
                resultado.aristas[tope - 1 - k].peso = peso;
            }
        }
    }
    resultado.costo_total = dist[idx_destino];
    resultado.existe = true;
    resultado.estado = GRAFO_OK;
    free(vertices);
    free(dist);
    free(predecesor);
    free(visitado);
    free(camino_aux);
    return resultado;
}
/**
 * @brief Calcula el camino mínimo con Bellman-Ford.
 *
 * @param[in] grafo   Puntero al grafo.
 * @param[in] origen  Vértice de origen.
 * @param[in] destino Vértice de destino.
 *
 * @return Estructura GrafoCamino con el camino y costo total.
 *
 * @note Acepta pesos negativos y detecta ciclos negativos.
 * @note Complejidad temporal: O(V * E).
 */
GrafoCamino grafo_bellman_ford(const Grafo *grafo, int origen, int destino)
{
    GrafoCamino resultado = {NULL, 0, 0, false, GRAFO_ERROR_NULO};
    int *vertices = NULL;
    size_t n_vertices = 0;
    int *dist = NULL;
    int *predecesor = NULL;
    int *camino_aux = NULL;
    int idx_origen;
    int idx_destino;
    size_t i;
    if (!grafo) return resultado;
    if (!grafo_existe_vertice(grafo, origen) || !grafo_existe_vertice(grafo, destino)) {
        resultado.estado = GRAFO_ERROR_NO_EXISTE;
        return resultado;
    }
    if (grafo_obtener_vertices(grafo, &vertices, &n_vertices) != GRAFO_OK || vertices == NULL) {
        resultado.estado = GRAFO_ERROR_MEMORIA;
        return resultado;
    }
    idx_origen = grafo_idx_vertice_id(vertices, n_vertices, origen);
    idx_destino = grafo_idx_vertice_id(vertices, n_vertices, destino);
    if (idx_origen < 0 || idx_destino < 0) {
        free(vertices);
        resultado.estado = GRAFO_ERROR_NO_EXISTE;
        return resultado;
    }
    dist = (int *)malloc(n_vertices * sizeof(int));
    predecesor = (int *)malloc(n_vertices * sizeof(int));
    camino_aux = (int *)malloc(n_vertices * sizeof(int));
    if (dist == NULL || predecesor == NULL || camino_aux == NULL) {
        free(vertices);
        free(dist);
        free(predecesor);
        free(camino_aux);
        resultado.estado = GRAFO_ERROR_MEMORIA;
        return resultado;
    }
    for (i = 0; i < n_vertices; i++) {
        dist[i] = INT_MAX;
        predecesor[i] = -1;
    }
    dist[idx_origen] = 0;
    for (i = 1; i < n_vertices; i++) {
        bool hubo_cambio = false;
        size_t j;
        for (j = 0; j < n_vertices; j++) {
            int u_id = vertices[j];
            int *sucesores = NULL;
            size_t cant = 0;
            if (grafo_sucesores(grafo, u_id, &sucesores, &cant) == GRAFO_OK && sucesores != NULL) {
                size_t k;
                for (k = 0; k < cant; k++) {
                    int v_id = sucesores[k];
                    int v_idx = grafo_idx_vertice_id(vertices, n_vertices, v_id);
                    int peso = 0;
                    if (v_idx < 0 || grafo_obtener_peso(grafo, u_id, v_id, &peso) != GRAFO_OK) {
                        continue;
                    }
                    if (dist[j] != INT_MAX) {
                        long long candidato = (long long)dist[j] + (long long)peso;
                        if (candidato < (long long)dist[v_idx]) {
                            dist[v_idx] = (int)candidato;
                            predecesor[v_idx] = (int)j;
                            hubo_cambio = true;
                        }
                    }
                }
                free(sucesores);
            }
        }
        if (!hubo_cambio) {
            break;
        }
    }
    for (i = 0; i < n_vertices; i++) {
        int u_id = vertices[i];
        int *sucesores = NULL;
        size_t cant = 0;
        if (grafo_sucesores(grafo, u_id, &sucesores, &cant) == GRAFO_OK && sucesores != NULL) {
            size_t k;
            for (k = 0; k < cant; k++) {
                int v_id = sucesores[k];
                int v_idx = grafo_idx_vertice_id(vertices, n_vertices, v_id);
                int peso = 0;
                if (v_idx < 0 || grafo_obtener_peso(grafo, u_id, v_id, &peso) != GRAFO_OK) {
                    continue;
                }
                if (dist[i] != INT_MAX) {
                    long long candidato = (long long)dist[i] + (long long)peso;
                    if (candidato < (long long)dist[v_idx]) {
                        free(vertices);
                        free(dist);
                        free(predecesor);
                        free(camino_aux);
                        free(sucesores);
                        resultado.estado = GRAFO_ERROR_CICLO_NEGATIVO;
                        return resultado;
                    }
                }
            }
            free(sucesores);
        }
    }
    if (dist[idx_destino] == INT_MAX) {
        free(vertices);
        free(dist);
        free(predecesor);
        free(camino_aux);
        resultado.estado = GRAFO_OK;
        resultado.existe = false;
        return resultado;
    }
    {
        int tope = 0;
        int actual = idx_destino;
        while (actual != -1 && tope < (int)n_vertices) {
            camino_aux[tope++] = vertices[actual];
            actual = predecesor[actual];
        }
        if (tope <= 0 || camino_aux[tope - 1] != origen) {
            free(vertices);
            free(dist);
            free(predecesor);
            free(camino_aux);
            resultado.estado = GRAFO_OK;
            resultado.existe = false;
            return resultado;
        }
        resultado.cantidad = (size_t)(tope - 1);
        if (resultado.cantidad > 0) {
            int k;
            resultado.aristas = (GrafoArista *)malloc(resultado.cantidad * sizeof(GrafoArista));
            if (resultado.aristas == NULL) {
                free(vertices);
                free(dist);
                free(predecesor);
                free(camino_aux);
                resultado.estado = GRAFO_ERROR_MEMORIA;
                return resultado;
            }
            for (k = tope - 1; k > 0; k--) {
                int u = camino_aux[k];
                int v = camino_aux[k - 1];
                int peso = 0;
                grafo_obtener_peso(grafo, u, v, &peso);
                resultado.aristas[tope - 1 - k].origen = u;
                resultado.aristas[tope - 1 - k].destino = v;
                resultado.aristas[tope - 1 - k].peso = peso;
            }
        }
    }
    resultado.costo_total = dist[idx_destino];
    resultado.existe = true;
    resultado.estado = GRAFO_OK;
    free(vertices);
    free(dist);
    free(predecesor);
    free(camino_aux);
    return resultado;
}

/**
 * @brief Calcula el árbol de expansión mínima con algoritmo de Prim.
 *
 * @param[in] grafo  Puntero al grafo no dirigido.
 * @param[in] inicio Vértice de inicio arbitrario.
 *
 * @return Estructura GrafoCamino con las aristas del MST.
 *
 * @note Complejidad temporal: O(V² + E).
 */
GrafoCamino grafo_prim(const Grafo *grafo, int inicio)
{
    GrafoCamino resultado = {NULL, 0, 0, false, GRAFO_ERROR_NULO};
    int *vertices = NULL;
    size_t n = 0;
    int idx_inicio;
    bool *en_mst = NULL;
    int *clave = NULL;
    int *padre = NULL;
    size_t i;
    int aristas_count = 0;
    int idx = 0;
    int costo = 0;

    if (!grafo) return resultado;
    if (grafo->dirigido) {
        resultado.estado = GRAFO_ERROR_YA_EXISTE;
        return resultado;
    }
    
    if (!grafo_existe_vertice(grafo, inicio)) {
        resultado.estado = GRAFO_ERROR_NO_EXISTE;
        return resultado;
    }

    n = grafo_orden(grafo);
    if (n == 0) {
        resultado.estado = GRAFO_OK;
        return resultado;
    }

    if (grafo_obtener_vertices(grafo, &vertices, &n) != GRAFO_OK || vertices == NULL) {
        resultado.estado = GRAFO_ERROR_MEMORIA;
        return resultado;
    }

    idx_inicio = grafo_indice_vertice(vertices, n, inicio);
    if (idx_inicio < 0) {
        free(vertices);
        resultado.estado = GRAFO_ERROR_NO_EXISTE;
        return resultado;
    }

    en_mst = (bool *)calloc(n, sizeof(bool));
    clave = (int *)malloc(n * sizeof(int));
    padre = (int *)malloc(n * sizeof(int));
    if (en_mst == NULL || clave == NULL || padre == NULL) {
        free(vertices);
        free(en_mst);
        free(clave);
        free(padre);
        resultado.estado = GRAFO_ERROR_MEMORIA;
        return resultado;
    }

    for (i = 0; i < n; i++) {
        clave[i] = INT_MAX;
        padre[i] = -1;
    }
    clave[idx_inicio] = 0;

    for (i = 0; i < n; i++) {
        int min_clave = INT_MAX;
        int u_idx = -1;
        int u_id;
        int *sucesores = NULL;
        size_t cant = 0;
        size_t j;

        for (j = 0; j < n; j++) {
            if (!en_mst[j] && clave[j] < min_clave) {
                min_clave = clave[j];
                u_idx = (int)j;
            }
        }
        if (u_idx < 0 || min_clave == INT_MAX) break;

        en_mst[u_idx] = true;
        u_id = vertices[u_idx];

        if (grafo_sucesores(grafo, u_id, &sucesores, &cant) == GRAFO_OK && sucesores) {
            for (j = 0; j < cant; j++) {
                int v_id = sucesores[j];
                int v_idx = grafo_indice_vertice(vertices, n, v_id);
                int peso = 0;
                if (v_idx < 0) {
                    continue;
                }
                grafo_obtener_peso(grafo, u_id, v_id, &peso);

                if (!en_mst[v_idx] && peso < clave[v_idx]) {
                    clave[v_idx] = peso;
                    padre[v_idx] = u_idx;
                }
            }
            free(sucesores);
        }
    }

    /* Contar aristas del MST */
    for (i = 0; i < n; i++) {
        if (padre[i] != -1) aristas_count++;
    }

    resultado.cantidad = aristas_count;
    resultado.aristas = (GrafoArista *)malloc(resultado.cantidad * sizeof(GrafoArista));
    if (!resultado.aristas && resultado.cantidad > 0) {
        free(vertices);
        free(en_mst);
        free(clave);
        free(padre);
        resultado.estado = GRAFO_ERROR_MEMORIA;
        return resultado;
    }

    for (i = 0; i < n; i++) {
        if (padre[i] != -1) {
            resultado.aristas[idx].origen = vertices[padre[i]];
            resultado.aristas[idx].destino = vertices[i];
            resultado.aristas[idx].peso = clave[i];
            costo += clave[i];
            idx++;
        }
    }

    free(vertices);
    free(en_mst);
    free(clave);
    free(padre);
    resultado.costo_total = costo;
    resultado.existe = (aristas_count == (int)n - 1);
    resultado.estado = GRAFO_OK;
    return resultado;
}

/**
 * @brief Calcula el árbol de expansión mínima con algoritmo de Kruskal.
 *
 * @param[in] grafo Puntero al grafo no dirigido.
 *
 * @return Estructura GrafoCamino con las aristas del MST.
 *
 * @note Complejidad temporal: O(E log E).
 */
GrafoCamino grafo_kruskal(const Grafo *grafo)
{
    GrafoCamino resultado = {NULL, 0, 0, false, GRAFO_ERROR_NULO};
    int *vertices = NULL;
    int *padre_uf = NULL;
    int *rango_uf = NULL;
    
    if (!grafo) return resultado;
    if (grafo->dirigido) {
        resultado.estado = GRAFO_ERROR_YA_EXISTE;
        return resultado;
    }
    
    size_t n = grafo_orden(grafo);
    if (n == 0) {
        resultado.estado = GRAFO_OK;
        return resultado;
    }

    if (grafo_obtener_vertices(grafo, &vertices, &n) != GRAFO_OK || vertices == NULL) {
        resultado.estado = GRAFO_ERROR_MEMORIA;
        return resultado;
    }
    
    /* Obtener aristas */
    GrafoArista *aristas = NULL;
    size_t m = 0;
    if (grafo_obtener_aristas(grafo, &aristas, &m) != GRAFO_OK) {
        free(vertices);
        resultado.estado = GRAFO_ERROR_MEMORIA;
        return resultado;
    }
    
    /* Ordenar aristas por peso (burbuja simple para grafos pequeÃ±os) */
    for (size_t i = 0; i < m; i++) {
        for (size_t j = i + 1; j < m; j++) {
            if (aristas[j].peso < aristas[i].peso) {
                GrafoArista temp = aristas[i];
                aristas[i] = aristas[j];
                aristas[j] = temp;
            }
        }
    }
    
    /* Union-Find */
    padre_uf = (int *)malloc(n * sizeof(int));
    rango_uf = (int *)calloc(n, sizeof(int));
    if (padre_uf == NULL || rango_uf == NULL) {
        free(vertices);
        free(aristas);
        free(padre_uf);
        free(rango_uf);
        resultado.estado = GRAFO_ERROR_MEMORIA;
        return resultado;
    }
    for (size_t i = 0; i < n; i++) padre_uf[i] = (int)i;
    
    resultado.aristas = (GrafoArista *)malloc(n * sizeof(GrafoArista));
    if (!resultado.aristas && n > 0) {
        free(vertices);
        free(aristas);
        free(padre_uf);
        free(rango_uf);
        resultado.estado = GRAFO_ERROR_MEMORIA;
        return resultado;
    }
    
    int costo = 0;
    for (size_t i = 0; i < m && resultado.cantidad < n - 1; i++) {
        int u_idx = grafo_indice_vertice(vertices, n, aristas[i].origen);
        int v_idx = grafo_indice_vertice(vertices, n, aristas[i].destino);
        if (u_idx < 0 || v_idx < 0) {
            continue;
        }

        if (uf_find(padre_uf, u_idx) != uf_find(padre_uf, v_idx)) {
            uf_union(padre_uf, rango_uf, u_idx, v_idx);
            resultado.aristas[resultado.cantidad] = aristas[i];
            costo += aristas[i].peso;
            resultado.cantidad++;
        }
    }
    
    free(vertices);
    free(aristas);
    free(padre_uf);
    free(rango_uf);
    resultado.costo_total = costo;
    resultado.existe = (resultado.cantidad == n - 1);
    resultado.estado = GRAFO_OK;
    return resultado;
}

/* ============================================================================
 * LiberaciÃ³n de resultados
 * ============================================================================ */

/**
 * @brief Libera la memoria de una estructura GrafoRecorrido.
 *
 * @param[in,out] recorrido Puntero al recorrido a liberar.
 *
 * @note Complejidad temporal: O(1).
 */
void grafo_liberar_recorrido(GrafoRecorrido *recorrido)
{
    if (!recorrido) return;
    
    if (recorrido->vertices) {
        free(recorrido->vertices);
        recorrido->vertices = NULL;
    }
    recorrido->cantidad = 0;
    recorrido->estado = GRAFO_OK;
}

/**
 * @brief Libera la memoria de una estructura GrafoCamino.
 *
 * @param[in,out] camino Puntero al camino a liberar.
 *
 * @note Complejidad temporal: O(1).
 */
void grafo_liberar_camino(GrafoCamino *camino)
{
    if (!camino) return;
    
    if (camino->aristas) {
        free(camino->aristas);
        camino->aristas = NULL;
    }
    camino->cantidad = 0;
    camino->costo_total = 0;
    camino->existe = false;
    camino->estado = GRAFO_OK;
}

/**
 * @brief Convierte un código GrafoEstado a una cadena de texto legible.
 *
 * @param[in] estado Estado a convertir.
 *
 * @return Cadena de caracteres estática correspondiente.
 *
 * @note Complejidad temporal: O(1).
 */
const char *grafo_estado_cadena(GrafoEstado estado)
{
    switch (estado) {
        case GRAFO_OK:
            return "GRAFO_OK";
        case GRAFO_ERROR_NULO:
            return "GRAFO_ERROR_NULO";
        case GRAFO_ERROR_MEMORIA:
            return "GRAFO_ERROR_MEMORIA";
        case GRAFO_ERROR_NO_EXISTE:
            return "GRAFO_ERROR_NO_EXISTE";
        case GRAFO_ERROR_YA_EXISTE:
            return "GRAFO_ERROR_YA_EXISTE";
        case GRAFO_ERROR_PESO_NEGATIVO:
            return "GRAFO_ERROR_PESO_NEGATIVO";
        case GRAFO_ERROR_CICLO_NEGATIVO:
            return "GRAFO_ERROR_CICLO_NEGATIVO";
        default:
            return "GRAFO_ERROR_DESCONOCIDO";
    }
}

