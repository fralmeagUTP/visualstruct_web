#include <stdio.h>
#include <stdlib.h>
#include "tad_monticulo_binario.h"

/**
 * @brief Reproduce el historial del monticulo y copia todos sus valores internos.
 * @return 0 al terminar; EXIT_FAILURE si falla la reserva para una copia.
 * @note A lista conserva el orden interno del heap; no ordena sus valores.
 */
int main(void) {
    // Declaracion de la estructura
    MonticuloBinario monticulo;
    monticulo_inicializar(&monticulo, MONTICULO_MIN, 16);

    // Historial de ejecucion del usuario
    bool ok_1 = monticulo_insertar(&monticulo, 5);
    if (!ok_1) { monticulo_destruir(&monticulo); return EXIT_FAILURE; }
    printf("INSERTAR: %d\n", (int)(5));
    bool ok_2 = monticulo_insertar(&monticulo, 3);
    if (!ok_2) { monticulo_destruir(&monticulo); return EXIT_FAILURE; }
    printf("INSERTAR: %d\n", (int)(3));
    int raiz_3; bool ok_3 = monticulo_raiz(&monticulo, &raiz_3);
    if (ok_3) printf("RAIZ: %d\n", raiz_3);
    int cantidad_4 = monticulo_cantidad(&monticulo);
    int *buffer_4 = cantidad_4 > 0 ? malloc((size_t)cantidad_4 * sizeof *buffer_4) : NULL;
    if (cantidad_4 > 0 && buffer_4 == NULL) { monticulo_destruir(&monticulo); return EXIT_FAILURE; }
    int usados_4 = monticulo_copiar_valores(&monticulo, buffer_4, cantidad_4);
    printf("A LISTA: [");
    for (int i_4 = 0; i_4 < usados_4; i_4++) printf("%s%d", i_4 ? ", " : "", buffer_4[i_4]);
    printf("]\n");
    free(buffer_4);
    int extraido_5; bool ok_5 = monticulo_extraer_raiz(&monticulo, &extraido_5);
    if (ok_5) printf("EXTRAIDO: %d\n", extraido_5);
    // Al finalizar el programa:
    monticulo_destruir(&monticulo);
    return 0;
}