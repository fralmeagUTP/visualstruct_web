#include <stdio.h>
#include "tad_cola_prioridad.h"

/** @file main.c @brief Reproduce el historial de Prioridad y libera su propiedad. */
/** @brief Ejecuta el historial y comprueba cada reserva antes de anunciar éxito. @return 0 en éxito, 1 ante reserva fallida o entero fuera de int C. */
int main(void) {
    ColaPrioridad cp;
    cp_inicializar(&cp);
    // Historial de ejecucion del usuario
    if (!cp_encolar(&cp, 5, 2)) {
        fputs("No se aplico encolar: fallo de reserva.\n", stderr);
        cp_vaciar(&cp);
        return 1;
    }
    puts("Operacion aplicada.");
    if (!cp_encolar(&cp, 9, 1)) {
        fputs("No se aplico encolar: fallo de reserva.\n", stderr);
        cp_vaciar(&cp);
        return 1;
    }
    puts("Operacion aplicada.");
    {
        int valor = 0;
        int prioridad = 0;
        if (cp_frente(&cp, &valor, &prioridad)) {
            printf("Frente: %d prioridad: %d\n", valor, prioridad);
        } else {
            fputs("No se pudo consultar frente.\n", stderr);
            cp_vaciar(&cp);
            return 1;
        }
    }
    {
        int valor = 0;
        int prioridad = 0;
        if (cp_desencolar(&cp, &valor, &prioridad)) {
            printf("Extraido: %d prioridad: %d\n", valor, prioridad);
        } else {
            fputs("No se pudo desencolar.\n", stderr);
            cp_vaciar(&cp);
            return 1;
        }
    }
    /* Liberar propiedad del caller al terminar */ cp_vaciar(&cp);
    return 0;
}