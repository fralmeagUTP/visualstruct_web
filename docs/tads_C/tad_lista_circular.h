#ifndef LISTA_CIRCULAR_H
#define LISTA_CIRCULAR_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file tad_lista_circular.h
 * @brief TAD Lista circular simple de enteros.
 */

/** @brief Nodo interno de la lista circular. */
typedef struct lcir_nodo LCirNodo;

/** @brief Estructura principal de lista circular. */
typedef struct {
    LCirNodo *cabeza;  
    LCirNodo *cola;    
    int cantidad;      
} ListaCircular;

void lcir_inicializar(ListaCircular *lista);
bool lcir_insertar_inicio(ListaCircular *lista, int valor);
bool lcir_insertar_final(ListaCircular *lista, int valor);
int lcir_buscar_posiciones(const ListaCircular *lista, int valor, int *destino, int capacidad);
bool lcir_eliminar_primero(ListaCircular *lista, int valor);
void lcir_invertir(ListaCircular *lista);
bool lcir_vacia(const ListaCircular *lista);
int lcir_contar(const ListaCircular *lista);
int lcir_copiar_valores(const ListaCircular *lista, int *destino, int capacidad);
void lcir_formatear(const ListaCircular *lista, char *destino, size_t capacidad);
void lcir_destruir(ListaCircular *lista);

#endif
