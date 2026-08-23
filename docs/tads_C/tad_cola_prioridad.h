#ifndef COLA_PRIORIDAD_H
#define COLA_PRIORIDAD_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file tad_cola_prioridad.h
 * @brief TAD Cola de prioridad basada en lista enlazada.
 */

/** @brief Nodo interno de la cola de prioridad. */
typedef struct cp_nodo CPNodo;

/** @brief Estructura principal de cola de prioridad. */
typedef struct {
    CPNodo *delante;  
    CPNodo *atras;    
    int cantidad;    
} ColaPrioridad;

void cp_inicializar(ColaPrioridad *cola);
bool cp_encolar(ColaPrioridad *cola, int valor, int prioridad);
bool cp_desencolar(ColaPrioridad *cola, int *valor, int *prioridad);
bool cp_frente(const ColaPrioridad *cola, int *valor, int *prioridad);
bool cp_vacia(const ColaPrioridad *cola);
int cp_contar(const ColaPrioridad *cola);
int cp_copiar_items(const ColaPrioridad *cola, int *valores, int *prioridades, int capacidad);
void cp_formatear(const ColaPrioridad *cola, char *destino, size_t capacidad);
void cp_vaciar(ColaPrioridad *cola);

#endif
