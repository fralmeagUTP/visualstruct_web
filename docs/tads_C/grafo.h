/**
 * @file grafo.h
 * @brief TAD Grafo para visualización y análisis de algoritmos de grafos.
 *
 * Este archivo define la API pública del TAD Grafo, que permite construir y
 * manipular grafos dirigidos y no dirigidos con aristas ponderadas.
 * Implementa algoritmos clásicos como BFS, DFS, Dijkstra, Bellman-Ford, Prim y Kruskal.
 *
 * El TAD Grafo es independiente de raylib y puede utilizarse en consola, tests o interfaz gráfica.
 *
 * @author Francisco Alejandro Medina Aguirre
 * @date 2026
 * @version 1.0
 */

#ifndef GRAFO_H
#define GRAFO_H

#include <stdbool.h>
#include <stddef.h>

/* ============================================================================
 * Tipo opaco del grafo
 * ============================================================================ */

/**
 * @brief Tipo opaco que representa un grafo.
 *
 * La estructura interna del grafo no es visible al usuario. Se accede
 * únicamente mediante las funciones públicas de esta API.
 */
typedef struct Grafo Grafo;

/* ============================================================================
 * Estados de error
 * ============================================================================ */

/**
 * @brief Enumeración de estados de error del TAD Grafo.
 */
typedef enum {
    GRAFO_OK = 0,                  /**< Operación finalizada correctamente */
    GRAFO_ERROR_NULO,              /**< Se recibió un puntero nulo */
    GRAFO_ERROR_MEMORIA,           /**< No fue posible reservar memoria dinámica */
    GRAFO_ERROR_NO_EXISTE,         /**< Vértice o arista inexistente */
    GRAFO_ERROR_YA_EXISTE,         /**< Vértice o arista duplicada */
    GRAFO_ERROR_PESO_NEGATIVO,     /**< El algoritmo no acepta pesos negativos */
    GRAFO_ERROR_CICLO_NEGATIVO     /**< Bellman-Ford detectó ciclo negativo */
} GrafoEstado;

/* ============================================================================
 * Estructuras de datos públicas
 * ============================================================================ */

/**
 * @brief Representa una arista pública.
 *
 * Contiene el origen, destino y peso de la arista.
 */
typedef struct {
    int origen;     /**< Vértice de origen */
    int destino;    /**< Vértice de destino */
    int peso;       /**< Peso de la arista */
} GrafoArista;

/**
 * @brief Resultado de un recorrido (BFS, DFS).
 *
 * Contiene el orden de visita de los vértices y el estado de la operación.
 */
typedef struct {
    int *vertices;          /**< Array dinámico de vértices visitados (en orden) */
    size_t cantidad;        /**< Cantidad de vértices en el recorrido */
    GrafoEstado estado;     /**< Estado de la operación */
} GrafoRecorrido;

/**
 * @brief Resultado de un camino mínimo o árbol de expansión mínima.
 *
 * Contiene las aristas que forman el camino o MST, su costo total,
 * y si existe solución.
 */
typedef struct {
    GrafoArista *aristas;   /**< Array dinámico de aristas del camino/MST */
    size_t cantidad;        /**< Cantidad de aristas */
    int costo_total;        /**< Costo total (suma de pesos) */
    bool existe;            /**< true si existe solución; false si no hay camino/MST */
    GrafoEstado estado;     /**< Estado de la operación */
} GrafoCamino;

/* ============================================================================
 * Creación y destrucción
 * ============================================================================ */

/**
 * @brief Crea un nuevo grafo.
 *
 * Reserva memoria para un nuevo grafo vacío (sin vértices ni aristas).
 *
 * @param[in] dirigido true para grafo dirigido; false para no dirigido
 * @return Puntero a grafo creado; NULL si falla la asignación de memoria
 *
 * @note El grafo retornado debe liberarse con @c grafo_destruir()
 */
Grafo *grafo_crear(bool dirigido);

/**
 * @brief Destruye un grafo y libera toda su memoria.
 *
 * Libera todos los vértices, aristas y la estructura principal.
 * Establece el puntero a NULL.
 *
 * @param[in,out] grafo Puntero al puntero del grafo a destruir
 *
 * @pre grafo no debe ser NULL
 * @post El grafo y todos sus datos son liberados; *grafo == NULL
 */
void grafo_destruir(Grafo **grafo);

/**
 * @brief Indica si el grafo es dirigido.
 *
 * @param[in] grafo Puntero al grafo
 * @return true si el grafo es dirigido; false si es no dirigido
 *
 * @pre grafo no debe ser NULL
 */
bool grafo_es_dirigido(const Grafo *grafo);

/* ============================================================================
 * Operaciones estructurales
 * ============================================================================ */

/**
 * @brief Inserta un vértice en el grafo.
 *
 * Crea un nuevo vértice identificado por un entero.
 * Si el vértice ya existe, retorna @c GRAFO_ERROR_YA_EXISTE.
 *
 * @param[in,out] grafo Puntero al grafo
 * @param[in] vertice Identificador entero del vértice
 * @return Estado de la operación
 *
 * @pre grafo no debe ser NULL
 * @post El vértice se agrega al grafo si no existía
 */
GrafoEstado grafo_insertar_vertice(Grafo *grafo, int vertice);

/**
 * @brief Inserta una arista entre dos vértices.
 *
 * Si alguno de los vértices no existe, retorna @c GRAFO_ERROR_NO_EXISTE.
 * Si la arista ya existe, retorna @c GRAFO_ERROR_YA_EXISTE.
 * En grafos no dirigidos, la arista se almacena en ambas direcciones.
 *
 * @param[in,out] grafo Puntero al grafo
 * @param[in] origen Vértice de origen
 * @param[in] destino Vértice de destino
 * @param[in] peso Peso de la arista
 * @return Estado de la operación
 *
 * @pre grafo no debe ser NULL
 * @post La arista se agrega si los vértices existen y la arista no existe
 */
GrafoEstado grafo_insertar_arista(Grafo *grafo, int origen, int destino, int peso);

/**
 * @brief Elimina un vértice y todas sus aristas incidentes.
 *
 * Si el vértice no existe, retorna @c GRAFO_ERROR_NO_EXISTE.
 *
 * @param[in,out] grafo Puntero al grafo
 * @param[in] vertice Identificador del vértice a eliminar
 * @return Estado de la operación
 *
 * @pre grafo no debe ser NULL
 * @post El vértice y sus aristas se eliminan si existía
 */
GrafoEstado grafo_eliminar_vertice(Grafo *grafo, int vertice);

/**
 * @brief Elimina una arista entre dos vértices.
 *
 * Si la arista no existe, retorna @c GRAFO_ERROR_NO_EXISTE.
 *
 * @param[in,out] grafo Puntero al grafo
 * @param[in] origen Vértice de origen
 * @param[in] destino Vértice de destino
 * @return Estado de la operación
 *
 * @pre grafo no debe ser NULL
 * @post La arista se elimina si existía
 */
GrafoEstado grafo_eliminar_arista(Grafo *grafo, int origen, int destino);

/* ============================================================================
 * Consultas
 * ============================================================================ */

/**
 * @brief Verifica si un vértice existe en el grafo.
 *
 * @param[in] grafo Puntero al grafo
 * @param[in] vertice Identificador del vértice
 * @return true si el vértice existe; false en caso contrario
 *
 * @pre grafo no debe ser NULL
 */
bool grafo_existe_vertice(const Grafo *grafo, int vertice);

/**
 * @brief Verifica si una arista existe en el grafo.
 *
 * @param[in] grafo Puntero al grafo
 * @param[in] origen Vértice de origen
 * @param[in] destino Vértice de destino
 * @return true si la arista existe; false en caso contrario
 *
 * @pre grafo no debe ser NULL
 */
bool grafo_existe_arista(const Grafo *grafo, int origen, int destino);

/**
 * @brief Obtiene el peso de una arista.
 *
 * Si la arista no existe, retorna @c GRAFO_ERROR_NO_EXISTE.
 *
 * @param[in] grafo Puntero al grafo
 * @param[in] origen Vértice de origen
 * @param[in] destino Vértice de destino
 * @param[out] peso Puntero al peso (solo se modifica si la operación es exitosa)
 * @return Estado de la operación
 *
 * @pre grafo y peso no deben ser NULL
 */
GrafoEstado grafo_obtener_peso(const Grafo *grafo, int origen, int destino, int *peso);

/**
 * @brief Retorna el orden del grafo (cantidad de vértices).
 *
 * @param[in] grafo Puntero al grafo
 * @return Cantidad de vértices en el grafo
 *
 * @pre grafo no debe ser NULL
 */
size_t grafo_orden(const Grafo *grafo);

/**
 * @brief Retorna el tamaño del grafo (cantidad de aristas).
 *
 * En grafos no dirigidos, cuenta cada arista una sola vez (lógicamente).
 *
 * @param[in] grafo Puntero al grafo
 * @return Cantidad de aristas en el grafo
 *
 * @pre grafo no debe ser NULL
 */
size_t grafo_tamano(const Grafo *grafo);

/**
 * @brief Obtiene el grado de salida de un vértice.
 *
 * El grado de salida es la cantidad de aristas que salen del vértice.
 * En grafos no dirigidos, es el número de aristas incidentes.
 *
 * @param[in] grafo Puntero al grafo
 * @param[in] vertice Identificador del vértice
 * @param[out] grado Puntero al grado (solo se modifica si la operación es exitosa)
 * @return Estado de la operación
 *
 * @pre grafo y grado no deben ser NULL
 */
GrafoEstado grafo_grado_salida(const Grafo *grafo, int vertice, size_t *grado);

/**
 * @brief Obtiene el grado de entrada de un vértice (solo en dirigidos).
 *
 * El grado de entrada es la cantidad de aristas que llegan al vértice.
 * En grafos no dirigidos, es igual al grado de salida.
 *
 * @param[in] grafo Puntero al grafo
 * @param[in] vertice Identificador del vértice
 * @param[out] grado Puntero al grado (solo se modifica si la operación es exitosa)
 * @return Estado de la operación
 *
 * @pre grafo y grado no deben ser NULL
 */
GrafoEstado grafo_grado_entrada(const Grafo *grafo, int vertice, size_t *grado);

/* ============================================================================
 * Copias públicas de datos
 * ============================================================================ */

/**
 * @brief Obtiene una copia del array de vértices del grafo.
 *
 * Retorna un array dinámico de vértices. El usuario es responsable de
 * liberar este array con @c free().
 *
 * @param[in] grafo Puntero al grafo
 * @param[out] vertices Puntero al puntero del array de vértices
 * @param[out] cantidad Puntero a la cantidad de vértices
 * @return Estado de la operación
 *
 * @pre grafo, vertices y cantidad no deben ser NULL
 * @post Se retorna un array dinámico de enteros; el usuario debe liberarlo
 */
GrafoEstado grafo_obtener_vertices(const Grafo *grafo, int **vertices, size_t *cantidad);

/**
 * @brief Obtiene una copia del array de aristas del grafo.
 *
 * Retorna un array dinámico de @c GrafoArista. El usuario es responsable
 * de liberar este array con @c free().
 *
 * @param[in] grafo Puntero al grafo
 * @param[out] aristas Puntero al puntero del array de aristas
 * @param[out] cantidad Puntero a la cantidad de aristas
 * @return Estado de la operación
 *
 * @pre grafo, aristas y cantidad no deben ser NULL
 * @post Se retorna un array dinámico; el usuario debe liberarlo
 */
GrafoEstado grafo_obtener_aristas(const Grafo *grafo, GrafoArista **aristas, size_t *cantidad);

/**
 * @brief Obtiene los sucesores de un vértice.
 *
 * Los sucesores son los vértices a los que se puede llegar directamente.
 * Retorna un array dinámico de enteros que el usuario debe liberar con @c free().
 *
 * @param[in] grafo Puntero al grafo
 * @param[in] vertice Identificador del vértice
 * @param[out] sucesores Puntero al puntero del array de sucesores
 * @param[out] cantidad Puntero a la cantidad de sucesores
 * @return Estado de la operación
 *
 * @pre grafo, sucesores y cantidad no deben ser NULL
 */
GrafoEstado grafo_sucesores(const Grafo *grafo, int vertice, int **sucesores, size_t *cantidad);

/**
 * @brief Obtiene los predecesores de un vértice.
 *
 * Los predecesores son los vértices desde los que se puede llegar directamente.
 * En grafos no dirigidos, predecesores = sucesores.
 * Retorna un array dinámico que el usuario debe liberar con @c free().
 *
 * @param[in] grafo Puntero al grafo
 * @param[in] vertice Identificador del vértice
 * @param[out] predecesores Puntero al puntero del array de predecesores
 * @param[out] cantidad Puntero a la cantidad de predecesores
 * @return Estado de la operación
 *
 * @pre grafo, predecesores y cantidad no deben ser NULL
 */
GrafoEstado grafo_predecesores(const Grafo *grafo, int vertice, int **predecesores, size_t *cantidad);

/* ============================================================================
 * Algoritmos
 * ============================================================================ */

/**
 * @brief Ejecuta BFS (búsqueda en amplitud) desde un vértice inicial.
 *
 * @param[in] grafo Puntero al grafo
 * @param[in] inicio Vértice de inicio
 * @return Estructura @c GrafoRecorrido con el orden de visita
 *
 * @pre grafo no debe ser NULL
 * @note El usuario debe liberar el array de vértices con @c grafo_liberar_recorrido()
 *
 * **Complejidad:** O(V + E)
 */
GrafoRecorrido grafo_bfs(const Grafo *grafo, int inicio);

/**
 * @brief Ejecuta DFS (búsqueda en profundidad) desde un vértice inicial.
 *
 * @param[in] grafo Puntero al grafo
 * @param[in] inicio Vértice de inicio
 * @return Estructura @c GrafoRecorrido con el orden de visita
 *
 * @pre grafo no debe ser NULL
 * @note El usuario debe liberar con @c grafo_liberar_recorrido()
 *
 * **Complejidad:** O(V + E)
 */
GrafoRecorrido grafo_dfs(const Grafo *grafo, int inicio);

/**
 * @brief Calcula el camino mínimo entre dos vértices con Dijkstra.
 *
 * No acepta pesos negativos. Si el grafo contiene pesos negativos,
 * retorna @c GRAFO_ERROR_PESO_NEGATIVO.
 *
 * @param[in] grafo Puntero al grafo
 * @param[in] origen Vértice de origen
 * @param[in] destino Vértice de destino
 * @return Estructura @c GrafoCamino con el camino y costo
 *
 * @pre grafo no debe ser NULL
 * @note El usuario debe liberar con @c grafo_liberar_camino()
 *
 * **Complejidad:** O(V² + E·V) con selección lineal (sin heap)
 */
GrafoCamino grafo_dijkstra(const Grafo *grafo, int origen, int destino);

/**
 * @brief Calcula el camino mínimo con Bellman-Ford (acepta pesos negativos).
 *
 * Detecta ciclos negativos y reporta el error.
 * Más lento que Dijkstra pero tolerante con pesos negativos.
 *
 * @param[in] grafo Puntero al grafo
 * @param[in] origen Vértice de origen
 * @param[in] destino Vértice de destino
 * @return Estructura @c GrafoCamino; puede retornar @c GRAFO_ERROR_CICLO_NEGATIVO
 *
 * @pre grafo no debe ser NULL
 * @note El usuario debe liberar con @c grafo_liberar_camino()
 *
 * **Complejidad:** O(V·E) con búsquedas lineales
 */
GrafoCamino grafo_bellman_ford(const Grafo *grafo, int origen, int destino);

/**
 * @brief Calcula el árbol de expansión mínima con Prim.
 *
 * Solo funciona en grafos no dirigidos. Si el grafo es dirigido,
 * retorna @c GRAFO_ERROR_YA_EXISTE.
 *
 * @param[in] grafo Puntero al grafo
 * @param[in] inicio Vértice de inicio
 * @return Estructura @c GrafoCamino con las aristas del MST
 *
 * @pre grafo no debe ser NULL
 * @pre El grafo debe ser no dirigido
 * @note El usuario debe liberar con @c grafo_liberar_camino()
 *
 * **Complejidad:** O(V² + E·V) con selección lineal
 */
GrafoCamino grafo_prim(const Grafo *grafo, int inicio);

/**
 * @brief Calcula el árbol de expansión mínima con Kruskal.
 *
 * Solo funciona en grafos no dirigidos. Utiliza Union-Find para detectar ciclos.
 *
 * @param[in] grafo Puntero al grafo
 * @return Estructura @c GrafoCamino con las aristas del MST
 *
 * @pre grafo no debe ser NULL
 * @pre El grafo debe ser no dirigido
 * @note El usuario debe liberar con @c grafo_liberar_camino()
 *
 * **Complejidad:** O(E log E + E·α(V)) con búsquedas lineales de índices
 */
GrafoCamino grafo_kruskal(const Grafo *grafo);

/* ============================================================================
 * Liberación de resultados dinámicos
 * ============================================================================ */

/**
 * @brief Libera un recorrido (BFS/DFS) y su array de vértices.
 *
 * @param[in,out] recorrido Puntero al recorrido a liberar
 *
 * @pre recorrido no debe ser NULL
 * @post El array de vértices es liberado y los campos se anulan
 */
void grafo_liberar_recorrido(GrafoRecorrido *recorrido);

/**
 * @brief Libera un camino mínimo/MST y su array de aristas.
 *
 * @param[in,out] camino Puntero al camino a liberar
 *
 * @pre camino no debe ser NULL
 * @post El array de aristas es liberado y los campos se anulan
 */
void grafo_liberar_camino(GrafoCamino *camino);

/**
 * @brief Convierte un estado a cadena de texto legible.
 *
 * Útil para depuración y mensajes de error.
 *
 * @param[in] estado Estado a convertir
 * @return Cadena de texto descriptiva (ej: "GRAFO_OK", "GRAFO_ERROR_NO_EXISTE")
 *
 * @note La cadena retornada es estática y no debe liberarse
 */
const char *grafo_estado_cadena(GrafoEstado estado);

#endif /* GRAFO_H */
