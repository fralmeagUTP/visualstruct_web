#include "harness_common.h"
#include "tad_pila.h"

#include <string.h>

static void emit_state(ptrPila stack) {
    ptrPila current = stack;
    size_t size = 0;
    const char *separator = "";
    printf("{\"schema\":\"canonical-state/v1\",\"structure_id\":\"stack\","
           "\"family\":\"sequential\",\"state\":{\"values\":[");
    while (current != NULL) {
        printf("%s%d", separator, current->nro);
        separator = ",";
        size++;
        current = current->sgte;
    }
    printf("],\"size\":%zu},\"invariants\":{\"size_matches\":true}}\n", size);
}

int main(int argc, char **argv) {
    ptrPila stack = NULL;
    int index = 1;
    while (index < argc) {
        if (strcmp(argv[index], "push") == 0) {
            int value;
            if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &value)) {
                pila_destruir(&stack);
                return harness_error("push requiere un entero");
            }
            pila_apilar(&stack, value);
            index += 2;
        } else if (strcmp(argv[index], "pop") == 0) {
            if (stack == NULL) {
                pila_destruir(&stack);
                return harness_error("pop sobre pila vacia");
            }
            (void)pila_desapilar(&stack);
            index++;
        } else {
            pila_destruir(&stack);
            return harness_error("operacion no permitida");
        }
    }
    emit_state(stack);
    pila_destruir(&stack);
    return 0;
}
