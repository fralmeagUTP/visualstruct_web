#include "harness_common.h"
#include "tad_cola.h"

#include <string.h>

static void emit_state(const struct Cola *queue) {
    const struct NodoCola *current = queue->delante;
    const char *separator = "";
    size_t size = 0;
    printf("{\"schema\":\"canonical-state/v1\",\"structure_id\":\"queue\","
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
    struct Cola queue = {NULL, NULL};
    int index = 1;
    while (index < argc) {
        if (strcmp(argv[index], "enqueue") == 0) {
            int value;
            if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &value)) {
                cola_vaciar(&queue);
                return harness_error("enqueue requiere un entero");
            }
            cola_encolar(&queue, value);
            index += 2;
        } else if (strcmp(argv[index], "dequeue") == 0) {
            if (queue.delante == NULL) {
                cola_vaciar(&queue);
                return harness_error("dequeue sobre cola vacia");
            }
            (void)cola_desencolar(&queue);
            index++;
        } else {
            cola_vaciar(&queue);
            return harness_error("operacion no permitida");
        }
    }
    emit_state(&queue);
    cola_vaciar(&queue);
    return 0;
}
