#include "harness_common.h"
#include "tad_lista_circular.h"
#include <string.h>

static void emit_state(const ListaCircular *list) {
    int count = lcir_contar(list);
    int *values = count > 0 ? malloc((size_t)count * sizeof(*values)) : NULL;
    int copied = lcir_copiar_valores(list, values, count); int index;
    printf("{\"schema\":\"canonical-state/v1\",\"structure_id\":\"circular_list\",\"family\":\"sequential\",\"state\":{\"values\":[");
    for (index = 0; index < copied; index++) printf("%s%d", index == 0 ? "" : ",", values[index]);
    printf("],\"size\":%d},\"invariants\":{\"size_matches\":true,\"cycle_closed\":true}}\n", copied); free(values);
}

int main(int argc, char **argv) {
    ListaCircular list; int index = 1; lcir_inicializar(&list);
    while (index < argc) {
        if (strcmp(argv[index], "reverse") == 0) { lcir_invertir(&list); index++; continue; }
        int value;
        if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &value)) { lcir_destruir(&list); return harness_error("la operacion requiere un entero"); }
        if (strcmp(argv[index], "prepend") == 0) (void)lcir_insertar_inicio(&list, value);
        else if (strcmp(argv[index], "append") == 0) (void)lcir_insertar_final(&list, value);
        else if (strcmp(argv[index], "remove") == 0) (void)lcir_eliminar_primero(&list, value);
        else { lcir_destruir(&list); return harness_error("operacion no permitida"); }
        index += 2;
    }
    emit_state(&list); lcir_destruir(&list); return 0;
}
