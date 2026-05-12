#ifndef PILA_H
#define PILA_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file pila.h
 * @brief API de pila LIFO basada en lista enlazada simple.
 */

typedef struct nodo Nodo;

typedef struct {
    Nodo *tope;
} Pila;

/** @brief Inicializa una pila vacia. */
void pila_inicializar(Pila *pila);
/** @brief Inserta un valor en el tope de la pila. */
bool pila_push(Pila *pila, int valor);
/** @brief Extrae el valor del tope si existe. */
bool pila_pop(Pila *pila, int *valor);
/** @brief Libera todos los nodos de la pila. */
void pila_destruir(Pila *pila);
/** @brief Retorna la cantidad de nodos. */
int pila_contar(const Pila *pila);
/** @brief Indica si la pila esta vacia. */
bool pila_vacia(const Pila *pila);
/** @brief Copia los valores de la pila en un arreglo destino. */
int pila_copiar_valores(const Pila *pila, int *destino, int capacidad);
/** @brief Genera una representacion textual de la pila. */
void pila_formatear(const Pila *pila, char *destino, size_t capacidad);

#endif
