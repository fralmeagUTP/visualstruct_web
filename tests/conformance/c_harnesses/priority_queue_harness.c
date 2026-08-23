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
    ColaPrioridad queue; int index = 1; cp_inicializar(&queue); harness_qa_begin("priority_queue", argc, argv);
    while (index < argc) {
        if (strcmp(argv[index], "peek") == 0) {
            int values[1], priorities[1];
            HARNESS_QA_OPERATION("peek", "before"); HARNESS_QA_CONDITION(cp_vacia(&queue) ? "queue empty:true" : "queue empty:false");
            if (cp_copiar_items(&queue, values, priorities, 1) != 1) { cp_vaciar(&queue); return harness_error("peek sobre cola vacia"); }
            HARNESS_QA_RETURN_INT("value", values[0]); HARNESS_QA_RETURN_INT("priority", priorities[0]); HARNESS_QA_OPERATION("peek", "after");
            if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after peek"); emit_state(&queue); } index++; continue;
        }
        if (strcmp(argv[index], "empty") == 0) {
            HARNESS_QA_OPERATION("empty", "before"); HARNESS_QA_RETURN_INT("empty", cp_vacia(&queue) ? 1 : 0); HARNESS_QA_OPERATION("empty", "after");
            if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after empty query"); emit_state(&queue); } index++; continue;
        }
        if (strcmp(argv[index], "clear") == 0) {
            HARNESS_QA_OPERATION("clear", "before"); cp_vaciar(&queue); HARNESS_QA_FREE("freed every priority queue node during clear"); HARNESS_QA_POINTER("front and rear set to NULL"); HARNESS_QA_OPERATION("clear", "after");
            if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after clear"); emit_state(&queue); } index++; continue;
        }
        if (strcmp(argv[index], "dequeue") == 0) {
            int value, priority;
            HARNESS_QA_OPERATION("dequeue", "before");
            HARNESS_QA_CONDITION(queue.delante == NULL ? "front == NULL:true" : "front == NULL:false");
            if (!cp_desencolar(&queue, &value, &priority)) { cp_vaciar(&queue); return harness_error("dequeue sobre cola vacia"); }
            HARNESS_QA_RETURN_INT("value", value);
            HARNESS_QA_RETURN_INT("priority", priority);
            HARNESS_QA_FREE("freed dequeued priority queue node");
            HARNESS_QA_POINTER("front advances in priority order");
            if (queue.delante == NULL) { HARNESS_QA_POINTER("rear set to NULL after removing last priority item"); }
            HARNESS_QA_OPERATION("dequeue", "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after dequeue"); emit_state(&queue); } index++; continue;
        }
        int value, priority;
        HARNESS_QA_OPERATION("enqueue", "before");
        if (strcmp(argv[index], "enqueue") != 0 || index + 2 >= argc || !harness_parse_int(argv[index + 1], &value) || !harness_parse_int(argv[index + 2], &priority)) {
            cp_vaciar(&queue); return harness_error("enqueue requiere valor y prioridad");
        }
        if (!cp_encolar(&queue, value, priority)) { cp_vaciar(&queue); return harness_error("fallo al encolar"); }
        HARNESS_QA_ALLOCATION("allocated priority queue node");
        HARNESS_QA_POINTER("node linked at priority position");
        HARNESS_QA_OPERATION("enqueue", "after");
        if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after enqueue"); emit_state(&queue); }
        index += 3;
    }
    emit_state(&queue); cp_vaciar(&queue); HARNESS_QA_FREE("destroyed remaining priority queue nodes"); harness_qa_end(); return 0;
}
