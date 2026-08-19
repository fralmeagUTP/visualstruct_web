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
    Tlista list = NULL; int index = 1;
    while (index < argc) {
        int value;
        if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &value)) { destroy_list(&list); return harness_error("la operacion requiere un entero"); }
        if (strcmp(argv[index], "prepend") == 0) lista_insertar_inicio(&list, value);
        else if (strcmp(argv[index], "append") == 0) lista_insertar_final(&list, value);
        else if (strcmp(argv[index], "remove") == 0) lista_eliminar_elemento(&list, value);
        else { destroy_list(&list); return harness_error("operacion no permitida"); }
        index += 2;
    }
    emit_state(list); destroy_list(&list); return 0;
}
