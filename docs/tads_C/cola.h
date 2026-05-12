#ifndef COLA_H
#define COLA_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file cola.h
 * @brief API de cola FIFO basada en lista enlazada.
 */

typedef struct nodo Nodo;

typedef struct {
    Nodo *delante;
    Nodo *atras;
} Cola;

/** @brief Inicializa una cola vacia. */
void cola_inicializar(Cola *cola);
/** @brief Inserta un valor al final de la cola. */
bool cola_encolar(Cola *cola, int valor);
/** @brief Extrae el valor del frente si existe. */
bool cola_desencolar(Cola *cola, int *valor);
/** @brief Elimina todos los elementos de la cola. */
void cola_vaciar(Cola *cola);
/** @brief Indica si la cola esta vacia. */
bool cola_vacia(const Cola *cola);
/** @brief Retorna la cantidad de nodos. */
int cola_contar(const Cola *cola);
/** @brief Copia los valores de la cola en un arreglo destino. */
int cola_copiar_valores(const Cola *cola, int *destino, int capacidad);
/** @brief Genera una representacion textual de la cola. */
void cola_formatear(const Cola *cola, char *destino, size_t capacidad);

#endif
