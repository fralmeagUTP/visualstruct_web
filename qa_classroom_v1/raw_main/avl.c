#include <stdio.h>
#include <stddef.h>
#include "tad_avl.h"

/**
 * @brief Calcula el maximo mediante el auxiliar mostrado por la aplicacion.
 * @param raiz Raiz consultada; NULL admitido.
 * @return Alias prestado al maximo o NULL.
 * @note Auxiliar de este programa; no es una exportacion del C/H descargable.
 */
AVL avl_maximo(AVL raiz) {
    AVL aux = raiz;
    while (aux != NULL && aux->der != NULL) {
        aux = aux->der;
    }
    return aux;
}

/**
 * @brief Imprime el recorrido inorden ascendente del historial.
 * @param nodo Raiz consultada; NULL admitido.
 * @note Auxiliar de este programa; no es una exportacion del C/H descargable.
 */
void avl_inorden(AVL nodo) {
    if (nodo != NULL) {
        avl_inorden(nodo->izq);
        printf("%d ", nodo->nro);
        avl_inorden(nodo->der);
    }
}

/**
 * @brief Comprueba equilibrio por alturas en cada subarbol.
 * @param nodo Raiz prestada del subarbol; NULL es valido.
 * @return 1 si todas las diferencias altura(der)-altura(izq) estan entre -1 y 1; 0 en otro caso.
 * @pre Enlaces finitos, aciclicos y nodos vivos.
 * @note No verifica orden ABB, padres ni el FE almacenado; la validacion del backend es distinta.
 * @note No muta, reserva, libera ni imprime; cortocircuita al hallar desequilibrio.
 * @note C no fija el orden de los operandos de la resta de alturas; ambas consultas son puras.
 * @note Recalcula alturas por nodo: coste O(n*h), no certificado lineal.
 */
int avl_validar_fes(AVL nodo) {
    if (nodo == NULL) {
        return 1;
    }
    int fe = avl_altura(nodo->der) - avl_altura(nodo->izq);
    if (fe < -1 || fe > 1) {
        return 0;
    }
    if (!avl_validar_fes(nodo->izq)) {
        return 0;
    }
    if (!avl_validar_fes(nodo->der)) {
        return 0;
    }
    return 1;
}

/**
 * @brief Reproduce las operaciones exitosas del historial AVL y calcula sus consultas.
 * @return 0 al terminar la secuencia.
 * @note Compilar junto a tad_avl.c. Consultas fallidas no se ejecutan. El equilibrio
 * por alturas no certifica el FE almacenado; los auxiliares anteriores pertenecen a este main.
 */
int main(void) {
    // Declaracion de la estructura
    AVL arbol = NULL;
    (void)arbol; // Permite un historial sin operaciones exitosas.

    // Historial de ejecucion del usuario
    avl_insertar(&arbol, 5);
    printf("INSERTAR invocado: %d\n", (int)(5));
    avl_insertar(&arbol, 3);
    printf("INSERTAR invocado: %d\n", (int)(3));
    AVL encontrado_3 = avl_buscar(arbol, 3);
    printf("BUSCAR 3: %s\n", encontrado_3 != NULL ? "encontrado" : "ausente");
    AVL minimo_4 = avl_minimo(arbol);
    printf("MINIMO: %d\n", minimo_4->nro);
    AVL maximo_5 = avl_maximo(arbol);
    printf("MAXIMO: %d\n", maximo_5->nro);
    int altura_6 = avl_altura(arbol);
    printf("ALTURA: %d\n", altura_6);
    printf("INORDEN: ");
    avl_inorden(arbol);
    printf("\n");
    int valido_8 = avl_validar_fes(arbol);
    printf("EQUILIBRIO POR ALTURAS: %s\n", valido_8 ? "correcto" : "incorrecto");
    // Al finalizar el programa:
    avl_liberarAVL(arbol); arbol = NULL;
    return 0;
}