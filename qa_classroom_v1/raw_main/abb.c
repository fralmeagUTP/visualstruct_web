#include <stdio.h>
#include "tad_abb.h"

int main(void) {
    // Declaracion de la estructura
    ABBNodo *arbol = NULL;

    // Historial de ejecucion del usuario
    arbol = abb_insertar(arbol, 5);
    // Llamada registrada: insertar; no se imprime un resultado precalculado.
    arbol = abb_insertar(arbol, 3);
    // Llamada registrada: insertar; no se imprime un resultado precalculado.
    ABBNodo *encontrado_3 = abb_buscar(arbol, 3);
    printf("BUSCAR: %s\n", encontrado_3 != NULL ? "encontrado" : "ausente");
    ABBNodo *minimo_4 = abb_encontrarMinimo(arbol);
    if (minimo_4 != NULL) printf("MINIMO: %d\n", minimo_4->valor);
    else puts("Arbol vacio.");
    ABBNodo *maximo_5 = abb_encontrarMaximo(arbol);
    if (maximo_5 != NULL) printf("MAXIMO: %d\n", maximo_5->valor);
    else puts("Arbol vacio.");
    int altura_6 = abb_altura(arbol);
    printf("ALTURA: %d\n", altura_6);
    abb_inorden(arbol);
    printf("\n");
    abb_preorden(arbol);
    printf("\n");
    abb_postorden(arbol);
    printf("\n");
    // Al finalizar el programa:
    abb_liberarArbol(arbol); arbol = NULL;
    return 0;
}