#ifndef TAD_ABB_H
#define TAD_ABB_H

/**
 * @file tad_abb.h
 * @brief TAD Arbol Binario de Busqueda (ABB) de enteros.
 */

/** @brief ABBNodo del ABB. */
typedef struct ABBNodo {
    int valor;                
    struct ABBNodo *izquierdo;   
    struct ABBNodo *derecho;     
} ABBNodo;

/** @brief Inserta un valor en el ABB. */
ABBNodo* abb_insertar(ABBNodo* nodo, int valor);
/** @brief Busca un valor en el ABB. */
ABBNodo* abb_buscar(ABBNodo* nodo, int valor);
/** @brief Retorna el nodo con valor minimo del subarbol. */
ABBNodo* abb_encontrarMinimo(ABBNodo* nodo);
/** @brief Retorna el nodo con valor maximo del subarbol. */
ABBNodo* abb_encontrarMaximo(ABBNodo* nodo);
/** @brief Elimina un valor del ABB. */
ABBNodo* abb_eliminar(ABBNodo* nodo, int valor);
/** @brief Recorre en abb_preorden. */
void abb_preorden(ABBNodo* nodo);
/** @brief Recorre en abb_inorden. */
void abb_inorden(ABBNodo* nodo);
/** @brief Recorre en abb_postorden. */
void abb_postorden(ABBNodo* nodo);
/** @brief Libera toda la memoria del ABB. */
void abb_liberarArbol(ABBNodo* nodo);
/** @brief Muestra el arbol con formato jerarquico. */
void abb_mostrarArbol(ABBNodo* nodo, int espacio);
/** @brief Calcula la abb_altura del arbol. */
int abb_altura(ABBNodo* nodo);
/** @brief Calcula niveles del arbol. */
int abb_contarNiveles(ABBNodo* nodo);

#endif
