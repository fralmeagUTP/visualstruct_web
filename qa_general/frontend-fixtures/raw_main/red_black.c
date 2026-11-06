#include <stdio.h>
#include "tad_rojo_negro.h"

/**
 * @brief Imprime los enteros en orden ascendente, cada uno seguido de un espacio.
 * @param nodo Raiz prestada; NULL no imprime nada.
 * @note Auxiliar de la aplicacion y del main, no exportado por el C/H. No muta ni libera.
 */
void rbt_inorden(RBT nodo) {
    if (nodo == NULL) return;
    rbt_inorden(nodo->izq);
    printf("%d ", nodo->nro);
    rbt_inorden(nodo->der);
}

/**
 * @brief Calcula la altura en nodos, sin mutar el arbol.
 * @param nodo Raiz prestada; NULL admitido.
 * @return 0 para NULL; uno mas que la mayor altura de los hijos en otro caso.
 * @note Auxiliar de la aplicacion y del main, no exportado por el C/H.
 */
int rbt_altura(RBT nodo) {
    if (nodo == NULL) return 0;
    int altIzq = rbt_altura(nodo->izq);
    int altDer = rbt_altura(nodo->der);
    return (altIzq > altDer ? altIzq : altDer) + 1;
}

/**
 * @brief Reproduce operaciones exitosas y calcula consultas del historial Rojo-Negro.
 * @return 0 al terminar.
 * @note Compilar junto a tad_rojo_negro.c. Auxiliares propios del main.
 * Validar llama al TAD publico: cinco reglas RN, orden estricto y enlaces nativos.
 * Al finalizar, el caller libera las reservas restantes y asigna NULL a su raiz.
 * Esta limpieza no agrega operaciones ni salida al historial del estudiante.
 */
int main(void) {
    // Declaracion de la estructura
    RBT arbol = NULL;
    (void)arbol;

    // Historial de ejecucion del usuario
    rbt_insertar(&arbol, 5);
    rbt_insertar(&arbol, 3);
    RBT encontrado_3 = rbt_buscar(arbol, 3);
    printf("BUSCAR %d: %s\n", (int)(3), encontrado_3 != NULL ? "encontrado" : "ausente");
    int altura_4 = rbt_altura(arbol);
    printf("ALTURA: %d\n", altura_4);
    printf("INORDEN: ");
    rbt_inorden(arbol);
    printf("\n");
    int valido_6 = rbt_validar(arbol);
    printf("VALIDAR RN COMPLETO: %s\n", valido_6 ? "correcto" : "incorrecto");
    // Limpieza final del caller; no es otra operacion del historial.
    rbt_liberar(arbol); arbol = NULL;
    return 0;
}