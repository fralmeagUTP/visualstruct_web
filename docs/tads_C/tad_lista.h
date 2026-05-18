#ifndef TAD_LISTA_H
#define TAD_LISTA_H

/**
 * @file tad_lista.h
 * @brief TAD Lista simplemente enlazada de enteros.
 */

/** @brief Nodo de la lista enlazada. */
typedef struct NodoLista {
    int nro;                    
    struct NodoLista *sgte;     
} *Tlista;

/**
 * @brief Inserta al inicio.
 * @param[in,out] lista Lista destino.
 * @param[in] valor Valor a insertar.
 */
void lista_insertar_inicio(Tlista *lista, int valor);

/**
 * @brief Inserta al final.
 * @param[in,out] lista Lista destino.
 * @param[in] valor Valor a insertar.
 */
void lista_insertar_final(Tlista *lista, int valor);

/**
 * @brief Inserta en una posicion base.
 * @param[in,out] lista Lista destino.
 * @param[in] valor Valor a insertar.
 * @param[in] pos Posicion base (1..n).
 *
 * Regla:
 * - pos == 1: inserta al inicio.
 * - pos > 1 : inserta despues del nodo ubicado en `pos`.
 */
void lista_insertar_elemento(Tlista *lista, int valor, int pos);

/**
 * @brief Busca e imprime posiciones de un valor.
 * @param[in] lista Lista origen.
 * @param[in] valor Valor buscado.
 */
void lista_buscar_elemento(Tlista lista, int valor);

/**
 * @brief Imprime todos los elementos de la lista.
 * @param[in] lista Lista a mostrar.
 */
void lista_mostrar(Tlista lista);

/**
 * @brief Elimina la primera ocurrencia de un valor.
 * @param[in,out] lista Lista origen.
 * @param[in] valor Valor a eliminar.
 */
void lista_eliminar_elemento(Tlista *lista, int valor);

/**
 * @brief Elimina todas las ocurrencias de un valor.
 * @param[in,out] lista Lista origen.
 * @param[in] valor Valor a eliminar.
 */
void lista_eliminar_repetidos(Tlista *lista, int valor);

#endif
