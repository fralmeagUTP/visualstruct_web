/** @file main.c @brief Reproduce el historial de Pila con el TAD C real. */
#include <limits.h>
#include <stddef.h>
#include <stdio.h>
#include "tad_pila.h"
/** @brief Ejecuta el historial y libera la pila al terminar. @return 0 en éxito, 1 si malloc falla. */
int main(void) {
    ptrPila pila = NULL;
    printf("state:[");
    for (ptrPila nodo = pila; nodo != NULL; nodo = nodo->sgte) {
        printf("%s%d", nodo == pila ? "" : ",", nodo->nro);
    }
    puts("]");
    pila_destruir(&pila);
    return 0;
}
