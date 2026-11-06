#include <stdio.h>
#include "tad_lista.h"

/** @brief Reproduce las llamadas registradas; las consultas se calculan al ejecutar C. */
int main(void) {
    // Declaracion de la estructura
    Tlista lista = NULL;

    // Historial de ejecucion del usuario
    lista_insertar_inicio(&lista, 5);
    // Fin de la llamada: insertar_inicio.
    lista_insertar_final(&lista, 9);
    // Fin de la llamada: insertar_final.
    lista_buscar_elemento(lista, 5);
    // Fin de la llamada: buscar_elemento.
    lista_eliminar_elemento(&lista, 5);
    // Fin de la llamada: eliminar_elemento.
    /* Liberar los nodos que aún pertenecen al caller. */ lista_limpiar(&lista);
    return 0;
}