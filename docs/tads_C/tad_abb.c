/**
 * @file tad_abb.c
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
    int valor; /**< Dato almacenado. */
    struct ABBNodo* izquierdo; /**< Hijo izquierdo; NULL si no existe. */
    struct ABBNodo* derecho; /**< Hijo derecho; NULL si no existe. */
} ABBNodo; /**< Alias del nodo del árbol binario. */

/**
 * @brief Inserta un valor en el árbol binario de búsqueda.
 * @param nodo Puntero a la raíz del árbol.
 * @param valor Valor entero.
 * @return Raíz actualizada; NULL si el árbol estaba vacío y malloc falla.
 * @note Si falla la reserva en un subárbol, se conserva la raíz existente sin insertar el valor.
  * @note El arbol debe ser un ABB valido y aciclico. Un duplicado conserva la misma raiz sin reservar otro nodo. Asigne el retorno a la raiz del llamador; los enlaces internos se modifican. El nuevo nodo se inicializa antes de enlazarlo.
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
 * @param valor Valor entero.
 * @return Puntero al nodo encontrado o NULL si no existe.
  * @note Consulta sin mutacion. El retorno es un alias prestado de un nodo existente, no una copia ni una reserva nueva. NULL tambien representa un arbol vacio.
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
 * @return Puntero al nodo con el valor mínimo, o NULL si el árbol está vacío.
  * @note Consulta sin mutacion: sigue enlaces izquierdos y retorna un alias prestado, no una reserva nueva. NULL representa el arbol vacio.
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
 * @return Puntero al nodo con el valor máximo, o NULL si el árbol está vacío.
  * @note Consulta sin mutacion: sigue enlaces derechos y retorna un alias prestado, no una reserva nueva. NULL representa el arbol vacio.
 */
ABBNodo* abb_encontrarMaximo(ABBNodo* nodo) {
    while (nodo != NULL && nodo->derecho != NULL)
        nodo = nodo->derecho;
    return nodo;
}

/**
 * @brief Elimina un valor del árbol binario de búsqueda.
 * @param nodo Puntero a la raíz del árbol.
 * @param valor Valor entero.
 * @return Puntero a la raíz actualizada.
  * @note Un valor ausente conserva la raiz. Asigne el retorno a la raiz del llamador. Con cero o un hijo se libera el nodo encontrado y se retorna el reemplazo. Con dos hijos se copia el valor del sucesor, se conserva la reserva del nodo encontrado y se elimina el sucesor. Los alias al nodo liberado dejan de ser validos.
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
 * @brief Realiza un recorrido preorden del árbol.
 * @param nodo Puntero a la raíz del árbol.
  * @note Imprime raiz, izquierdo y derecho en stdout con formato "%d " por nodo, incluido el espacio final y sin agregar salto de linea. NULL no imprime nada. No modifica enlaces ni reserva memoria.
 */
void abb_preorden(ABBNodo* nodo) {
    if (nodo != NULL) {
        printf("%d ", nodo->valor);
        abb_preorden(nodo->izquierdo);
        abb_preorden(nodo->derecho);
    }
}

/**
 * @brief Realiza un recorrido inorden del árbol.
 * @param nodo Puntero a la raíz del árbol.
  * @note Imprime izquierdo, raiz y derecho en stdout con formato "%d " por nodo, incluido el espacio final y sin agregar salto de linea. NULL no imprime nada. No modifica enlaces ni reserva memoria.
 */
void abb_inorden(ABBNodo* nodo) {
    if (nodo != NULL) {
        abb_inorden(nodo->izquierdo);
        printf("%d ", nodo->valor);
        abb_inorden(nodo->derecho);
    }
}

/**
 * @brief Realiza un recorrido postorden del árbol.
 * @param nodo Puntero a la raíz del árbol.
  * @note Imprime izquierdo, derecho y raiz en stdout con formato "%d " por nodo, incluido el espacio final y sin agregar salto de linea. NULL no imprime nada. No modifica enlaces ni reserva memoria.
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
  * @note Libera cada nodo en orden izquierdo, derecho y raiz; NULL no hace nada. El parametro se recibe por valor: no pone a NULL la raiz del llamador. Despues de la llamada, asigne NULL a esa raiz y no use los alias a las reservas liberadas.
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
  * @note Imprime primero el subarbol derecho, luego el valor y luego el izquierdo. En cada nivel aumenta espacio en cinco y emite saltos de linea; NULL no imprime. No modifica el arbol. Para la presentacion habitual use espacio igual a cero.
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
  * @note Cuenta niveles: NULL retorna cero y una hoja retorna uno. No cuenta aristas, no modifica el arbol y recorre ambos subarboles.
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
  * @note Retorna el mismo numero de niveles que abb_altura: cero para NULL y uno para una hoja. No modifica el arbol.
 */
int abb_contarNiveles(ABBNodo* nodo) {
    if (nodo == NULL)
        return 0;
    int nivelesIzq = abb_contarNiveles(nodo->izquierdo);
    int nivelesDer = abb_contarNiveles(nodo->derecho);
    return (nivelesIzq > nivelesDer ? nivelesIzq : nivelesDer) + 1;
}

