#ifndef TAD_PILA_H
#define TAD_PILA_H

/**
 * @file tad_pila.h
 * @brief TAD Pila enlazada de enteros.
 * @details Define el tipo abstracto de datos Pila y sus operaciones basicas.
 */

/** @brief Nodo de la pila enlazada. */
typedef struct NodoPila {
    int nro;                  
    struct NodoPila *sgte;    
} *ptrPila;

/**
 * @brief Inserta un elemento en la cima de la pila.
 * @param[in,out] p Puntero a la pila.
 * @param[in] valor Valor a apilar.
 */
void pila_apilar(ptrPila *p, int valor);

/**
 * @brief Extrae el elemento en la cima de la pila.
 * @param[in,out] p Puntero a la pila.
 * @return Valor extraido, o -1 si no se puede extraer.
 */
int pila_desapilar(ptrPila *p);
int pila_cima(ptrPila p);

/**
 * @brief Muestra el contenido de la pila en orden de cima a fondo.
 * @param[in] p Pila a mostrar.
 */
void pila_mostrar(ptrPila p);

/**
 * @brief Libera todos los nodos de la pila.
 * @param[in,out] p Puntero a la pila.
 */
void pila_destruir(ptrPila *p);

#endif
