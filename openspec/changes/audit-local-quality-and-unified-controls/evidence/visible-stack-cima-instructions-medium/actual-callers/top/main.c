/** @file main.c @brief Reproduce el historial de Pila con el TAD C real. */
#include <limits.h>
#include <stddef.h>
#include <stdio.h>
#include "tad_pila.h"
/** @brief Ejecuta el historial y libera la pila al terminar. @return 0 en éxito, 1 si malloc falla. */
int main(void) {
    ptrPila pila = NULL;
    {
        ptrPila anterior = pila;
        pila_apilar(&pila, 3);
        if (pila == anterior) { pila_destruir(&pila); return 1; }
        printf("push:%d\n", pila_cima(pila));
    }
    {
        ptrPila anterior = pila;
        pila_apilar(&pila, 17);
        if (pila == anterior) { pila_destruir(&pila); return 1; }
        printf("push:%d\n", pila_cima(pila));
    }
    {
        ptrPila anterior = pila;
        pila_apilar(&pila, 9);
        if (pila == anterior) { pila_destruir(&pila); return 1; }
        printf("push:%d\n", pila_cima(pila));
    }
    printf("state:[");
    for (ptrPila nodo = pila; nodo != NULL; nodo = nodo->sgte) {
        printf("%s%d", nodo == pila ? "" : ",", nodo->nro);
    }
    puts("]");
    pila_destruir(&pila);
    return 0;
}
