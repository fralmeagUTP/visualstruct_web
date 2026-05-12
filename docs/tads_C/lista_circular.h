#ifndef LISTA_CIRCULAR_H
#define LISTA_CIRCULAR_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file lista_circular.h
 * @brief API de lista circular simplemente enlazada (con cabeza y cola).
 */

typedef struct lcir_nodo LCirNodo;

typedef struct {
    LCirNodo *cabeza;
    LCirNodo *cola;
} ListaCircular;

/** @brief Inicializa la lista circular vacia. */
void lcir_inicializar(ListaCircular *lista);
/** @brief Inserta un valor al inicio. */
bool lcir_insertar_inicio(ListaCircular *lista, int valor);
/** @brief Inserta un valor al final. */
bool lcir_insertar_final(ListaCircular *lista, int valor);
/** @brief Busca un valor y copia posiciones de coincidencia (1-based). */
int lcir_buscar_posiciones(const ListaCircular *lista, int valor, int *destino, int capacidad);
/** @brief Elimina la primera ocurrencia del valor. */
bool lcir_eliminar_primero(ListaCircular *lista, int valor);
/** @brief Invierte la direccion de la lista circular. */
void lcir_invertir(ListaCircular *lista);
/** @brief Indica si la lista circular esta vacia. */
bool lcir_vacia(const ListaCircular *lista);
/** @brief Retorna la cantidad de nodos. */
int lcir_contar(const ListaCircular *lista);
/** @brief Copia los valores de la lista en un arreglo destino. */
int lcir_copiar_valores(const ListaCircular *lista, int *destino, int capacidad);
/** @brief Genera una representacion textual de la lista circular. */
void lcir_formatear(const ListaCircular *lista, char *destino, size_t capacidad);
/** @brief Libera toda la memoria de la lista circular. */
void lcir_destruir(ListaCircular *lista);

#endif
