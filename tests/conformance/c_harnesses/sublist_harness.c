#include "harness_common.h"
#include "tad_sublista.h"
#include <string.h>

static void emit_state(const Nodo *list) {
    const Nodo *parent = list; const char *parent_separator = ""; int count = 0;
    printf("{\"schema\":\"canonical-state/v1\",\"structure_id\":\"sublist\",\"family\":\"sequential\",\"state\":{\"parents\":[");
    while (parent != NULL) {
        const Sublista *child = parent->sub; const char *child_separator = "";
        printf("%s{\"parent\":%d,\"children\":[", parent_separator, parent->nro);
        while (child != NULL) { printf("%s%d", child_separator, child->nro); child_separator = ","; child = child->sgte; }
        printf("]}"); parent_separator = ","; count++; parent = parent->sgte;
    }
    printf("],\"size\":%d},\"invariants\":{\"size_matches\":true}}\n", count);
}

int main(int argc, char **argv) {
    Nodo *list; int index = 1; sublista_inicializar(&list); harness_qa_begin("sublist", argc, argv);
    while (index < argc) {
        int parent_value, child_value; Nodo *parent;
        if (strcmp(argv[index], "clear") == 0) {
            HARNESS_QA_OPERATION("clear", "before"); sublista_destruir(&list); HARNESS_QA_FREE("freed every parent and child node during clear"); HARNESS_QA_POINTER("outer-list head set to NULL"); HARNESS_QA_OPERATION("clear", "after");
            if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after clear"); emit_state(list); } index++; continue;
        }
        if (strcmp(argv[index], "get_children") == 0 || strcmp(argv[index], "remove_parent") == 0) {
            int is_query = strcmp(argv[index], "get_children") == 0;
            HARNESS_QA_OPERATION(is_query ? "get_children" : "remove_parent", "before");
            if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &parent_value)) { sublista_destruir(&list); return harness_error("operacion requiere padre"); }
            parent = sublista_buscar_padre(list, parent_value); HARNESS_QA_CONDITION(parent == NULL ? "parent == NULL:true" : "parent == NULL:false");
            if (is_query) { HARNESS_QA_RETURN_INT("children", sublista_contar_hijos(parent)); }
            else { int removed = sublista_eliminar_padre_primero(&list, parent_value) ? 1 : 0; HARNESS_QA_RETURN_INT("removed_parent", removed); if (removed) HARNESS_QA_FREE("freed parent and its complete child sublist"); }
            HARNESS_QA_OPERATION(is_query ? "get_children" : "remove_parent", "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after parent operation"); emit_state(list); } index += 2; continue;
        }
        if (strcmp(argv[index], "remove_child") == 0) {
            HARNESS_QA_OPERATION("remove_child", "before");
            if (index + 2 >= argc || !harness_parse_int(argv[index + 1], &parent_value) || !harness_parse_int(argv[index + 2], &child_value)) { sublista_destruir(&list); return harness_error("remove_child requiere padre e hijo"); }
            parent = sublista_buscar_padre(list, parent_value); { int removed = parent != NULL && sublista_eliminar_hijo_primero(parent, child_value); HARNESS_QA_RETURN_INT("removed_child", removed); if (removed) HARNESS_QA_FREE("freed selected child node"); }
            HARNESS_QA_OPERATION("remove_child", "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after remove_child"); emit_state(list); } index += 3; continue;
        }
        if (strcmp(argv[index], "add_parent") == 0) {
            HARNESS_QA_OPERATION("add_parent", "before");
            if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &parent_value)) { sublista_destruir(&list); return harness_error("add_parent requiere entero"); }
            if (sublista_insertar_padre_final(&list, parent_value) == NULL) { sublista_destruir(&list); return harness_error("fallo al insertar padre"); }
            HARNESS_QA_ALLOCATION("allocated parent node"); HARNESS_QA_POINTER("parent linked at outer-list tail"); HARNESS_QA_OPERATION("add_parent", "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after add_parent"); emit_state(list); } index += 2; continue;
        }
        if (strcmp(argv[index], "add_child") == 0) {
            HARNESS_QA_OPERATION("add_child", "before");
            if (index + 2 >= argc || !harness_parse_int(argv[index + 1], &parent_value) || !harness_parse_int(argv[index + 2], &child_value)) { sublista_destruir(&list); return harness_error("add_child requiere padre e hijo"); }
            parent = sublista_buscar_padre(list, parent_value);
            HARNESS_QA_CONDITION(parent == NULL ? "parent == NULL:true" : "parent == NULL:false");
            if (parent == NULL || !sublista_insertar_hijo_final(parent, child_value)) { sublista_destruir(&list); return harness_error("padre inexistente o sin memoria"); }
            HARNESS_QA_ALLOCATION("allocated child node"); HARNESS_QA_POINTER("child linked at selected parent sublist tail"); HARNESS_QA_OPERATION("add_child", "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after add_child"); emit_state(list); } index += 3; continue;
        }
        sublista_destruir(&list); return harness_error("operacion no permitida");
    }
    emit_state(list); sublista_destruir(&list); HARNESS_QA_FREE("destroyed parents and child sublists"); harness_qa_end(); return 0;
}
