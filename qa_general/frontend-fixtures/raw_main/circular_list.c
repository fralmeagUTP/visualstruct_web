#include <stdio.h>
#include "tad_lista_circular.h"

/** @brief Reproduce las llamadas registradas; las consultas se calculan al ejecutar C. */
int main(void) {
    // Declaracion de la estructura
    ListaCircular lc;
    lcir_inicializar(&lc);

    // Historial de ejecucion del usuario
    lcir_insertar_inicio(&lc, 5);
    // Fin de la llamada: insertar_inicio.
    lcir_insertar_final(&lc, 9);
    // Fin de la llamada: insertar_final.
    int posiciones_3[2];
    int cantidad_3 = lcir_buscar_posiciones(&lc, 5, posiciones_3, 2);
    printf("Posiciones:");
    for (int i_3 = 0; i_3 < cantidad_3 && i_3 < 2; ++i_3) printf(" %d", posiciones_3[i_3]);
    printf("\n");
    // Fin de la llamada: buscar_posiciones.
    lcir_eliminar_primero(&lc, 5);
    // Fin de la llamada: eliminar_primero.
    /* Liberar los nodos que aún pertenecen al caller. */ lcir_destruir(&lc);
    return 0;
}