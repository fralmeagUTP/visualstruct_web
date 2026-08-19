#include "harness_common.h"
#include "tad_cola_prioridad.h"
#include <string.h>

static void emit_state(const ColaPrioridad *queue) {
    int count = cp_contar(queue);
    int *values = count > 0 ? malloc((size_t)count * sizeof(*values)) : NULL;
    int *priorities = count > 0 ? malloc((size_t)count * sizeof(*priorities)) : NULL;
    int copied = cp_copiar_items(queue, values, priorities, count); int index;
    printf("{\"schema\":\"canonical-state/v1\",\"structure_id\":\"priority_queue\",\"family\":\"sequential\",\"state\":{\"items\":[");
    for (index = 0; index < copied; index++) printf("%s{\"value\":%d,\"priority\":%d}", index == 0 ? "" : ",", values[index], priorities[index]);
    printf("],\"size\":%d},\"invariants\":{\"size_matches\":true}}\n", copied);
    free(values); free(priorities);
}

int main(int argc, char **argv) {
    ColaPrioridad queue; int index = 1; cp_inicializar(&queue);
    while (index < argc) {
        if (strcmp(argv[index], "dequeue") == 0) {
            int value, priority;
            if (!cp_desencolar(&queue, &value, &priority)) { cp_vaciar(&queue); return harness_error("dequeue sobre cola vacia"); }
            index++; continue;
        }
        int value, priority;
        if (strcmp(argv[index], "enqueue") != 0 || index + 2 >= argc || !harness_parse_int(argv[index + 1], &value) || !harness_parse_int(argv[index + 2], &priority)) {
            cp_vaciar(&queue); return harness_error("enqueue requiere valor y prioridad");
        }
        if (!cp_encolar(&queue, value, priority)) { cp_vaciar(&queue); return harness_error("fallo al encolar"); }
        index += 3;
    }
    emit_state(&queue); cp_vaciar(&queue); return 0;
}
