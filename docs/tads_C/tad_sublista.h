#ifndef SUBLISTA_H
#define SUBLISTA_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file tad_sublista.h
 * @brief TAD Lista de padres con sublista de hijos.
 */

/** @brief Nodo hijo de una sublista. */
typedef struct Sublista {
    int nro;                
    struct Sublista *sgte;  
} Sublista;

/** @brief Nodo padre de la lista principal. */
typedef struct Nodo {
    int nro;              
    struct Nodo *sgte;    
    Sublista *sub;        
} Nodo;

void sublista_inicializar(Nodo **lista);
Nodo *sublista_insertar_padre_final(Nodo **lista, int valor_padre);
Nodo *sublista_buscar_padre(Nodo *lista, int valor_padre);
bool sublista_eliminar_padre_primero(Nodo **lista, int valor_padre);
int sublista_contar_padres(const Nodo *lista);
bool sublista_insertar_hijo_final(Nodo *padre, int valor_hijo);
Sublista *sublista_buscar_hijo(Sublista *lista_hijos, int valor_hijo);
bool sublista_eliminar_hijo_primero(Nodo *padre, int valor_hijo);
int sublista_contar_hijos(const Nodo *padre);
int sublista_copiar_hijos(const Nodo *padre, int *destino, int capacidad);
void sublista_formatear(const Nodo *lista, char *destino, size_t capacidad);
void sublista_destruir(Nodo **lista);

#endif
