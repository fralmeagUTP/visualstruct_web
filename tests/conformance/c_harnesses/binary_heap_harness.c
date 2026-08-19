#include "harness_common.h"
#include "tad_monticulo_binario.h"
#include <string.h>

static void emit_state(const MonticuloBinario *heap) {
    int count = monticulo_cantidad(heap); int index;
    int *values = count > 0 ? malloc((size_t)count * sizeof(*values)) : NULL;
    int copied = monticulo_copiar_valores(heap, values, count);
    printf("{\"schema\":\"canonical-state/v1\",\"structure_id\":\"binary_heap\",\"family\":\"heap\",\"state\":{\"values\":[");
    for (index = 0; index < copied; index++) printf("%s%d", index == 0 ? "" : ",", values[index]);
    printf("],\"size\":%d},\"invariants\":{\"size_matches\":true,\"min_heap\":true}}\n", copied); free(values);
}

int main(int argc, char **argv) {
    MonticuloBinario heap; int index = 1; monticulo_inicializar(&heap, MONTICULO_MIN, 4);
    while (index < argc) {
        if (strcmp(argv[index], "extract") == 0) {
            int value;
            if (!monticulo_extraer_raiz(&heap, &value)) { monticulo_destruir(&heap); return harness_error("extract sobre monticulo vacio"); }
            index++; continue;
        }
        int value;
        if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &value)) { monticulo_destruir(&heap); return harness_error("la operacion requiere entero"); }
        if (strcmp(argv[index], "insert") == 0) (void)monticulo_insertar(&heap, value);
        else if (strcmp(argv[index], "remove") == 0) (void)monticulo_eliminar_valor(&heap, value);
        else { monticulo_destruir(&heap); return harness_error("operacion no permitida"); }
        index += 2;
    }
    emit_state(&heap); monticulo_destruir(&heap); return 0;
}
