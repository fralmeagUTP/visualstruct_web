#ifndef SUBLISTA_H
#define SUBLISTA_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file sublista.h
 * @brief TAD de lista de nodos con sublista asociada por nodo padre.
 */

/* El elemento "hijo" */
typedef struct sublista {
    int nro;
    struct sublista *sgte;
} Sublista;

/* El elemento "padre" */
typedef struct nodo {
    int nro;
    struct nodo *sgte;
    Sublista *sub; /* Puntero al inicio de la sublista */
} Nodo;

/** @brief Inicializa la lista de nodos padre. */
void sublista_inicializar(Nodo **lista);
/** @brief Inserta un nodo padre al final y retorna su direccion (o NULL si falla). */
Nodo *sublista_insertar_padre_final(Nodo **lista, int valor_padre);
/** @brief Busca un nodo padre por valor. */
Nodo *sublista_buscar_padre(Nodo *lista, int valor_padre);
/** @brief Elimina la primera ocurrencia de un nodo padre por valor. */
bool sublista_eliminar_padre_primero(Nodo **lista, int valor_padre);
/** @brief Cuenta nodos padre. */
int sublista_contar_padres(const Nodo *lista);

/** @brief Inserta un nodo hijo al final de la sublista de un padre dado. */
bool sublista_insertar_hijo_final(Nodo *padre, int valor_hijo);
/** @brief Busca un nodo hijo por valor en la sublista de un padre. */
Sublista *sublista_buscar_hijo(Sublista *lista_hijos, int valor_hijo);
/** @brief Elimina la primera ocurrencia de un hijo en la sublista de un padre. */
bool sublista_eliminar_hijo_primero(Nodo *padre, int valor_hijo);
/** @brief Cuenta nodos hijo de un padre. */
int sublista_contar_hijos(const Nodo *padre);
/** @brief Copia los valores de la sublista de un padre a un arreglo destino. */
int sublista_copiar_hijos(const Nodo *padre, int *destino, int capacidad);

/** @brief Genera representacion textual de toda la estructura padre->sublista. */
void sublista_formatear(const Nodo *lista, char *destino, size_t capacidad);
/** @brief Libera por completo toda la estructura (padres e hijos). */
void sublista_destruir(Nodo **lista);

#endif
