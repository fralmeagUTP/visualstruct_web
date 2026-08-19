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
    Nodo *list; int index = 1; sublista_inicializar(&list);
    while (index < argc) {
        int parent_value, child_value; Nodo *parent;
        if (strcmp(argv[index], "add_parent") == 0) {
            if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &parent_value)) { sublista_destruir(&list); return harness_error("add_parent requiere entero"); }
            if (sublista_insertar_padre_final(&list, parent_value) == NULL) { sublista_destruir(&list); return harness_error("fallo al insertar padre"); }
            index += 2; continue;
        }
        if (strcmp(argv[index], "add_child") == 0) {
            if (index + 2 >= argc || !harness_parse_int(argv[index + 1], &parent_value) || !harness_parse_int(argv[index + 2], &child_value)) { sublista_destruir(&list); return harness_error("add_child requiere padre e hijo"); }
            parent = sublista_buscar_padre(list, parent_value);
            if (parent == NULL || !sublista_insertar_hijo_final(parent, child_value)) { sublista_destruir(&list); return harness_error("padre inexistente o sin memoria"); }
            index += 3; continue;
        }
        sublista_destruir(&list); return harness_error("operacion no permitida");
    }
    emit_state(list); sublista_destruir(&list); return 0;
}
