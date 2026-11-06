#include <stdio.h>
#include "tad_cola.h"

/** @file main.c @brief Reproduce el historial FIFO y libera los nodos propios. */
/** @brief Ejecuta operaciones registradas; informa fallo de reserva antes de anunciar éxito. @return 0 en éxito, 1 si una reserva falla o un entero no es representable. */
int main(void) {
    struct Cola cola = { .delante = NULL, .atras = NULL };
    // Historial de ejecucion del usuario
    {
        struct NodoCola *anterior = cola.atras;
        cola_encolar(&cola, 10);
        if (cola.atras == anterior) {
            fputs("No se aplico encolar: fallo de reserva.\n", stderr);
            cola_vaciar(&cola);
            return 1;
        }
        puts("Operacion aplicada.");
    }
    {
        struct NodoCola *anterior = cola.atras;
        cola_encolar(&cola, 20);
        if (cola.atras == anterior) {
            fputs("No se aplico encolar: fallo de reserva.\n", stderr);
            cola_vaciar(&cola);
            return 1;
        }
        puts("Operacion aplicada.");
    }
    printf("Extraido: %d\n", cola_desencolar(&cola));
    /* Liberar propiedad del caller al terminar */ cola_vaciar(&cola);
    return 0;
}