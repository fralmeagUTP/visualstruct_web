#include <stdio.h>
#include "tad_sublista.h"

/** @brief Reproduce las llamadas registradas; las consultas se calculan al ejecutar C. */
int main(void) {
    // Declaracion de la estructura
    Nodo *sublista = NULL;
    sublista_inicializar(&sublista);

    // Historial de ejecucion del usuario
    sublista_insertar_padre_final(&sublista, 1);
    // Fin de la llamada: insertar_padre.
    sublista_insertar_hijo(sublista, 1, 2);
    // Fin de la llamada: insertar_hijo.
    int hijos_3[1];
    int cantidad_hijos_3 = sublista_obtener_hijos(sublista, 1, hijos_3, 1);
    printf("Hijos:");
    for (int i_3 = 0; i_3 < cantidad_hijos_3; i_3++) printf(" %d", hijos_3[i_3]);
    printf("\n");
    // Fin de la llamada: hijos_de.
    /* Liberar los nodos que aún pertenecen al caller. */ sublista_destruir(&sublista);
    return 0;
}