#ifndef COLA_PRIORIDAD_H
#define COLA_PRIORIDAD_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file cola_prioridad.h
 * @brief API de cola con prioridad (menor numero = mayor prioridad).
 */

typedef struct cp_nodo CPNodo;

typedef struct {
    CPNodo *delante;
    CPNodo *atras;
} ColaPrioridad;

/** @brief Inicializa una cola de prioridad vacia. */
void cp_inicializar(ColaPrioridad *cola);
/** @brief Encola un valor con prioridad asociada. */
bool cp_encolar(ColaPrioridad *cola, int valor, int prioridad);
/** @brief Desencola el elemento de mayor prioridad efectiva. */
bool cp_desencolar(ColaPrioridad *cola, int *valor, int *prioridad);
/** @brief Indica si la cola esta vacia. */
bool cp_vacia(const ColaPrioridad *cola);
/** @brief Retorna la cantidad de nodos. */
int cp_contar(const ColaPrioridad *cola);
/** @brief Copia valor/prioridad de cada elemento. */
int cp_copiar_items(const ColaPrioridad *cola, int *valores, int *prioridades, int capacidad);
/** @brief Genera una representacion textual de la cola. */
void cp_formatear(const ColaPrioridad *cola, char *destino, size_t capacidad);
/** @brief Libera todos los nodos de la cola. */
void cp_vaciar(ColaPrioridad *cola);

#endif
