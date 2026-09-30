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
    MonticuloBinario heap; int index = 1; monticulo_inicializar(&heap, MONTICULO_MIN, 4); harness_qa_begin("binary_heap", argc, argv); HARNESS_QA_ALLOCATION("allocated initial heap backing array");
    while (index < argc) {
        if (strcmp(argv[index], "root") == 0) {
            int value;
            HARNESS_QA_OPERATION("root", "before");
            HARNESS_QA_CONDITION(monticulo_cantidad(&heap) == 0 ? "heap empty:true" : "heap empty:false");
            if (!monticulo_raiz(&heap, &value)) { monticulo_destruir(&heap); return harness_error("root sobre monticulo vacio"); }
            HARNESS_QA_RETURN_INT("root", value); HARNESS_QA_OPERATION("root", "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after root query"); emit_state(&heap); } index++; continue;
        }
        if (strcmp(argv[index], "extract") == 0) {
            int value;
            HARNESS_QA_OPERATION("extract", "before");
            HARNESS_QA_CONDITION(monticulo_cantidad(&heap) == 0 ? "heap empty:true" : "heap empty:false");
            if (!monticulo_extraer_raiz(&heap, &value)) { monticulo_destruir(&heap); return harness_error("extract sobre monticulo vacio"); }
            HARNESS_QA_RETURN_INT("value", value); HARNESS_QA_CALL("sift-down", "after"); HARNESS_QA_OPERATION("extract", "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after extract"); emit_state(&heap); } index++; continue;
        }
        int value;
        HARNESS_QA_OPERATION(argv[index], "before");
        if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &value)) { monticulo_destruir(&heap); return harness_error("la operacion requiere entero"); }
        if (strcmp(argv[index], "insert") == 0) { int previous_capacity = monticulo_capacidad(&heap); (void)monticulo_insertar(&heap, value); if (monticulo_capacidad(&heap) != previous_capacity) HARNESS_QA_ALLOCATION("reallocated heap backing array"); HARNESS_QA_CALL("sift-up", "after"); }
        else if (strcmp(argv[index], "remove") == 0) { (void)monticulo_eliminar_valor(&heap, value); HARNESS_QA_CALL("restore heap property", "after"); }
        else { monticulo_destruir(&heap); return harness_error("operacion no permitida"); }
        HARNESS_QA_OPERATION(argv[index], "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after heap operation"); emit_state(&heap); } index += 2;
    }
    emit_state(&heap); monticulo_destruir(&heap); HARNESS_QA_FREE("released heap backing array"); harness_qa_end(); return 0;
}
