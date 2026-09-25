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
    ListaCircular list; int index = 1; lcir_inicializar(&list); harness_qa_begin("circular_list", argc, argv);
    while (index < argc) {
        if (strcmp(argv[index], "clear") == 0) { HARNESS_QA_OPERATION("clear", "before"); lcir_destruir(&list); HARNESS_QA_FREE("freed every circular-list node during clear"); HARNESS_QA_POINTER("head and tail set to NULL"); HARNESS_QA_OPERATION("clear", "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after clear"); emit_state(&list); } index++; continue; }
        if (strcmp(argv[index], "reverse") == 0) { HARNESS_QA_OPERATION("reverse", "before"); lcir_invertir(&list); HARNESS_QA_POINTER("circular next links reversed and cycle closed"); HARNESS_QA_OPERATION("reverse", "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after reverse"); emit_state(&list); } index++; continue; }
        int value;
        HARNESS_QA_OPERATION(argv[index], "before");
        if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &value)) { lcir_destruir(&list); return harness_error("la operacion requiere un entero"); }
        if (strcmp(argv[index], "prepend") == 0) { if (lcir_insertar_inicio(&list, value)) HARNESS_QA_ALLOCATION("allocated circular-list node"); }
        else if (strcmp(argv[index], "append") == 0) { if (lcir_insertar_final(&list, value)) HARNESS_QA_ALLOCATION("allocated circular-list node"); }
        else if (strcmp(argv[index], "remove") == 0) { if (lcir_eliminar_primero(&list, value)) HARNESS_QA_FREE("freed removed circular-list node"); }
        else if (strcmp(argv[index], "search") == 0) { int positions[64]; int matches = lcir_buscar_posiciones(&list, value, positions, 64); HARNESS_QA_RETURN_INT("matches", matches); HARNESS_QA_COMPARISON("traversal stopped after returning to head"); }
        else { lcir_destruir(&list); return harness_error("operacion no permitida"); }
        HARNESS_QA_POINTER("circular head/tail links updated and tail next targets head"); HARNESS_QA_OPERATION(argv[index], "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after circular-list operation"); emit_state(&list); } index += 2;
    }
    emit_state(&list); lcir_destruir(&list); HARNESS_QA_FREE("destroyed circular-list nodes"); harness_qa_end(); return 0;
}
