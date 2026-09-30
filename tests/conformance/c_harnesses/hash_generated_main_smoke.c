/* Representative C17 main emitted by the hash technical-history generator. */
#include "tad_tabla_hash.h"
#include <stdio.h>

int main(void) {
    TablaHash tabla = {0};
    int valor_3 = 0;
    bool ok_1;
    bool ok_2;
    bool ok_3;
    bool eliminado_4;

    th_inicializar(&tabla, 3);
    ok_1 = th_insertar(&tabla, 1, 10);
    ok_2 = th_insertar(&tabla, 4, 40);
    ok_3 = th_buscar(&tabla, 1, &valor_3);
    eliminado_4 = th_eliminar(&tabla, 4);
    printf("%d %d %d %d %d\n", ok_1, ok_2, ok_3, eliminado_4, valor_3);
    th_vaciar(&tabla);
    th_destruir(&tabla);
    return 0;
}
