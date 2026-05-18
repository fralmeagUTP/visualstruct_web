/**
 * @file ABB_V2.c
 * @brief Implementación de un Árbol Binario de Búsqueda (ABB) en C estándar.
 */

#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#ifdef _WIN32
#include <windows.h>
#endif

/**
 * @struct ABBNodo
 * @brief Estructura para un nodo del árbol binario de búsqueda.
 */
typedef struct ABBNodo {
    int valor;                 
    struct ABBNodo* izquierdo;    
    struct ABBNodo* derecho;      
} ABBNodo;

/**
 * @brief Inserta un valor en el árbol binario de búsqueda.
 * @param nodo Puntero a la raíz del árbol.
 * @param valor Valor a abb_insertar.
 * @return Puntero a la raíz actualizada.
 */
ABBNodo* abb_insertar(ABBNodo* nodo, int valor) {
    if (nodo == NULL) {
        ABBNodo* nuevo = malloc(sizeof *nuevo);
        if (nuevo == NULL) {
            return NULL;
        }
        nuevo->valor = valor;
        nuevo->izquierdo = nuevo->derecho = NULL;
        return nuevo;
    }
    if (valor < nodo->valor)
        nodo->izquierdo = abb_insertar(nodo->izquierdo, valor);
    else if (valor > nodo->valor)
        nodo->derecho = abb_insertar(nodo->derecho, valor);
    return nodo;
}

/**
 * @brief Busca un valor en el árbol binario de búsqueda.
 * @param nodo Puntero a la raíz del árbol.
 * @param valor Valor a abb_buscar.
 * @return Puntero al nodo encontrado o NULL si no existe.
 */
ABBNodo* abb_buscar(ABBNodo* nodo, int valor) {
    if (nodo == NULL || nodo->valor == valor)
        return nodo;
    if (valor < nodo->valor)
        return abb_buscar(nodo->izquierdo, valor);
    else
        return abb_buscar(nodo->derecho, valor);
}

/**
 * @brief Encuentra el nodo con el valor mínimo en el árbol.
 * @param nodo Puntero a la raíz del árbol.
 * @return Puntero al nodo con el valor mínimo.
 */
ABBNodo* abb_encontrarMinimo(ABBNodo* nodo) {
    if (nodo == NULL) {
        return NULL;
    }

    while (nodo->izquierdo != NULL)
        nodo = nodo->izquierdo;
    return nodo;
}

/**
 * @brief Encuentra el nodo con el valor máximo en el árbol.
 * @param nodo Puntero a la raíz del árbol.
 * @return Puntero al nodo con el valor máximo.
 */
ABBNodo* abb_encontrarMaximo(ABBNodo* nodo) {
    while (nodo != NULL && nodo->derecho != NULL)
        nodo = nodo->derecho;
    return nodo;
}

/**
 * @brief Elimina un valor del árbol binario de búsqueda.
 * @param nodo Puntero a la raíz del árbol.
 * @param valor Valor a abb_eliminar.
 * @return Puntero a la raíz actualizada.
 */
ABBNodo* abb_eliminar(ABBNodo* nodo, int valor) {
    if (nodo == NULL) return nodo;
    if (valor < nodo->valor)
        nodo->izquierdo = abb_eliminar(nodo->izquierdo, valor);
    else if (valor > nodo->valor)
        nodo->derecho = abb_eliminar(nodo->derecho, valor);
    else {
        if (nodo->izquierdo == NULL) {
            ABBNodo* temp = nodo->derecho;
            free(nodo);
            return temp;
        } else if (nodo->derecho == NULL) {
            ABBNodo* temp = nodo->izquierdo;
            free(nodo);
            return temp;
        }
        ABBNodo* temp = abb_encontrarMinimo(nodo->derecho);
        nodo->valor = temp->valor;
        nodo->derecho = abb_eliminar(nodo->derecho, temp->valor);
    }
    return nodo;
}

/**
 * @brief Realiza un recorrido en abb_preorden del árbol.
 * @param nodo Puntero a la raíz del árbol.
 */
void abb_preorden(ABBNodo* nodo) {
    if (nodo != NULL) {
        printf("%d ", nodo->valor);
        abb_preorden(nodo->izquierdo);
        abb_preorden(nodo->derecho);
    }
}

/**
 * @brief Realiza un recorrido en abb_inorden del árbol.
 * @param nodo Puntero a la raíz del árbol.
 */
void abb_inorden(ABBNodo* nodo) {
    if (nodo != NULL) {
        abb_inorden(nodo->izquierdo);
        printf("%d ", nodo->valor);
        abb_inorden(nodo->derecho);
    }
}

/**
 * @brief Realiza un recorrido en abb_postorden del árbol.
 * @param nodo Puntero a la raíz del árbol.
 */
void abb_postorden(ABBNodo* nodo) {
    if (nodo != NULL) {
        abb_postorden(nodo->izquierdo);
        abb_postorden(nodo->derecho);
        printf("%d ", nodo->valor);
    }
}

/**
 * @brief Libera toda la memoria del árbol (abb_postorden).
 * @param nodo Raíz del árbol o subárbol a liberar.
 */
void abb_liberarArbol(ABBNodo* nodo) {
    if (nodo == NULL) return;
    abb_liberarArbol(nodo->izquierdo);
    abb_liberarArbol(nodo->derecho);
    free(nodo);
}

/**
 * @brief Muestra el árbol en forma jerárquica.
 * @param nodo Puntero a la raíz del árbol.
 * @param espacio Espacio de indentación para la visualización.
 */
void abb_mostrarArbol(ABBNodo* nodo, int espacio) {
	int i;
    if (nodo == NULL) return;
    espacio += 5;
    abb_mostrarArbol(nodo->derecho, espacio);
    printf("\n");
    for (i = 5; i < espacio; i++) printf(" ");
    printf("%d\n", nodo->valor);
    abb_mostrarArbol(nodo->izquierdo, espacio);
}

/**
 * @brief Calcula la abb_altura del árbol binario de búsqueda.
 * @param nodo Puntero a la raíz del árbol.
 * @return Altura del árbol (número de niveles).
 */
int abb_altura(ABBNodo* nodo) {
    if (nodo == NULL)
        return 0;
    int altIzq = abb_altura(nodo->izquierdo);
    int altDer = abb_altura(nodo->derecho);
    return (altIzq > altDer ? altIzq : altDer) + 1;
}

/**
 * @brief Cuenta la cantidad de niveles (profundidad) de un árbol binario de búsqueda.
 * @param nodo Puntero a la raíz del árbol.
 * @return Número de niveles del árbol (0 si está vacío).
 */
int abb_contarNiveles(ABBNodo* nodo) {
    if (nodo == NULL)
        return 0;
    int nivelesIzq = abb_contarNiveles(nodo->izquierdo);
    int nivelesDer = abb_contarNiveles(nodo->derecho);
    return (nivelesIzq > nivelesDer ? nivelesIzq : nivelesDer) + 1;
}

