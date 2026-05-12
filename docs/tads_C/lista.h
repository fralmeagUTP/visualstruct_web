#ifndef LISTA_H
#define LISTA_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file lista.h
 * @brief API de lista enlazada simple con cabeza.
 */

typedef struct nodo Nodo;

typedef struct {
    Nodo *cabeza;
} Lista;

/** @brief Inicializa una lista vacia. */
void lista_inicializar(Lista *lista);
/** @brief Inserta un valor al inicio. */
bool lista_insertar_inicio(Lista *lista, int valor);
/** @brief Inserta un valor al final. */
bool lista_insertar_final(Lista *lista, int valor);
/** @brief Inserta un valor exactamente en la posicion indicada (1-based). */
bool lista_insertar_posicion(Lista *lista, int valor, int pos);
/** @brief Busca un valor y copia posiciones de coincidencia. */
int lista_buscar_posiciones(const Lista *lista, int valor, int *destino, int capacidad);
/** @brief Elimina la primera ocurrencia de un valor. */
bool lista_eliminar_primero(Lista *lista, int valor);
/** @brief Elimina todas las ocurrencias de un valor. */
int lista_eliminar_todos(Lista *lista, int valor);
/** @brief Invierte el orden de los nodos. */
void lista_invertir(Lista *lista);
/** @brief Calcula el promedio de la lista si no esta vacia. */
bool lista_promedio(const Lista *lista, float *resultado);
/** @brief Obtiene el mayor valor de la lista si no esta vacia. */
bool lista_mayor(const Lista *lista, int *resultado);
/** @brief Verifica si la lista esta en orden ascendente. */
bool lista_orden_asc(const Lista *lista);
/** @brief Indica si la lista esta vacia. */
bool lista_vacia(const Lista *lista);
/** @brief Retorna la cantidad de nodos. */
int lista_contar(const Lista *lista);
/** @brief Copia valores de la lista en un arreglo destino. */
int lista_copiar_valores(const Lista *lista, int *destino, int capacidad);
/** @brief Genera una representacion textual de la lista. */
void lista_formatear(const Lista *lista, char *destino, size_t capacidad);
/** @brief Libera toda la memoria de la lista. */
void lista_destruir(Lista *lista);

#endif
