#include "harness_common.h"
#include "tad_lista.h"
#include <string.h>

static void destroy_list(Tlista *list) {
    while (*list != NULL) { Tlista next = (*list)->sgte; free(*list); *list = next; }
}

static void emit_state(Tlista list) {
    Tlista current = list; const char *separator = ""; size_t size = 0;
    printf("{\"schema\":\"canonical-state/v1\",\"structure_id\":\"linked_list\",\"family\":\"sequential\",\"state\":{\"values\":[");
    while (current != NULL) { printf("%s%d", separator, current->nro); separator = ","; size++; current = current->sgte; }
    printf("],\"size\":%zu},\"invariants\":{\"size_matches\":true}}\n", size);
}

int main(int argc, char **argv) {
    Tlista list = NULL; int index = 1; harness_qa_begin("linked_list", argc, argv);
    while (index < argc) {
        int value;
        if (strcmp(argv[index], "insert_at") == 0) {
            int position; size_t before = 0; Tlista cursor = list;
            HARNESS_QA_OPERATION("insert_at", "before");
            if (index + 2 >= argc || !harness_parse_int(argv[index + 1], &value) || !harness_parse_int(argv[index + 2], &position)) { destroy_list(&list); return harness_error("insert_at requiere valor y posicion"); }
            while (cursor != NULL) { before++; cursor = cursor->sgte; }
            lista_insertar_elemento(&list, value, position); cursor = list; { size_t after = 0; while (cursor != NULL) { after++; cursor = cursor->sgte; } if (after > before) HARNESS_QA_ALLOCATION("allocated positional linked-list node"); }
            HARNESS_QA_POINTER("positional predecessor linked to new node"); HARNESS_QA_OPERATION("insert_at", "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after positional insert"); emit_state(list); } index += 3; continue;
        }
        HARNESS_QA_OPERATION(argv[index], "before");
        if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &value)) { destroy_list(&list); return harness_error("la operacion requiere un entero"); }
        if (strcmp(argv[index], "prepend") == 0) { lista_insertar_inicio(&list, value); HARNESS_QA_ALLOCATION("allocated linked-list node"); HARNESS_QA_POINTER("head points to inserted node"); }
        else if (strcmp(argv[index], "append") == 0) { lista_insertar_final(&list, value); HARNESS_QA_ALLOCATION("allocated linked-list node"); HARNESS_QA_POINTER("tail next points to inserted node"); }
        else if (strcmp(argv[index], "remove") == 0) { Tlista cursor = list; int existed = 0; while (cursor != NULL) { if (cursor->nro == value) { existed = 1; break; } cursor = cursor->sgte; } HARNESS_QA_CONDITION(list == NULL ? "head == NULL:true" : "head == NULL:false"); lista_eliminar_elemento(&list, value); if (existed) HARNESS_QA_FREE("freed removed linked-list node"); HARNESS_QA_POINTER("predecessor bypasses removed node"); }
        else if (strcmp(argv[index], "remove_all") == 0) { Tlista cursor = list; int removed = 0; while (cursor != NULL) { if (cursor->nro == value) removed++; cursor = cursor->sgte; } lista_eliminar_repetidos(&list, value); HARNESS_QA_RETURN_INT("removed", removed); if (removed > 0) HARNESS_QA_FREE("freed all matching linked-list nodes"); HARNESS_QA_POINTER("links bypass every removed occurrence"); }
        else if (strcmp(argv[index], "search") == 0) { Tlista cursor = list; int matches = 0; while (cursor != NULL) { if (cursor->nro == value) matches++; cursor = cursor->sgte; } lista_buscar_elemento(list, value); HARNESS_QA_RETURN_INT("matches", matches); HARNESS_QA_COMPARISON("visited every linked-list node during search"); }
        else { destroy_list(&list); return harness_error("operacion no permitida"); }
        HARNESS_QA_OPERATION(argv[index], "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after linked-list operation"); emit_state(list); } index += 2;
    }
    emit_state(list); destroy_list(&list); HARNESS_QA_FREE("destroyed remaining linked-list nodes"); harness_qa_end(); return 0;
}
