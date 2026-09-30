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
    harness_qa_begin("queue", argc, argv);
    while (index < argc) {
        if (strcmp(argv[index], "front") == 0 || strcmp(argv[index], "rear") == 0) {
            int is_front = strcmp(argv[index], "front") == 0;
            HARNESS_QA_OPERATION(is_front ? "front" : "rear", "before");
            HARNESS_QA_CONDITION(queue.delante == NULL ? "front == NULL:true" : "front == NULL:false");
            if (queue.delante == NULL) { cola_vaciar(&queue); return harness_error("consulta sobre cola vacia"); }
            HARNESS_QA_RETURN_INT(is_front ? "front" : "rear", is_front ? cola_frente(queue) : queue.atras->nro);
            HARNESS_QA_OPERATION(is_front ? "front" : "rear", "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after endpoint query"); emit_state(&queue); } index++;
        } else if (strcmp(argv[index], "empty") == 0) {
            HARNESS_QA_OPERATION("empty", "before"); HARNESS_QA_RETURN_INT("empty", queue.delante == NULL ? 1 : 0); HARNESS_QA_OPERATION("empty", "after");
            if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after empty query"); emit_state(&queue); } index++;
        } else if (strcmp(argv[index], "clear") == 0) {
            HARNESS_QA_OPERATION("clear", "before"); cola_vaciar(&queue); HARNESS_QA_FREE("freed every queue node during clear"); HARNESS_QA_POINTER("front and rear set to NULL"); HARNESS_QA_OPERATION("clear", "after");
            if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after clear"); emit_state(&queue); } index++;
        } else
        if (strcmp(argv[index], "enqueue") == 0) {
            int value;
            HARNESS_QA_OPERATION("enqueue", "before");
            if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &value)) {
                cola_vaciar(&queue);
                return harness_error("enqueue requiere un entero");
            }
            cola_encolar(&queue, value);
            HARNESS_QA_ALLOCATION("allocated queue node");
            HARNESS_QA_POINTER("rear points to inserted node");
            HARNESS_QA_OPERATION("enqueue", "after");
            if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after enqueue"); emit_state(&queue); }
            index += 2;
        } else if (strcmp(argv[index], "dequeue") == 0) {
            HARNESS_QA_OPERATION("dequeue", "before");
            HARNESS_QA_CONDITION(queue.delante == NULL ? "front == NULL:true" : "front == NULL:false");
            if (queue.delante == NULL) {
                cola_vaciar(&queue);
                return harness_error("dequeue sobre cola vacia");
            }
            { int removed = cola_desencolar(&queue); HARNESS_QA_RETURN_INT("value", removed); HARNESS_QA_FREE("freed dequeued queue node"); }
            HARNESS_QA_POINTER("front advances to next node");
            if (queue.delante == NULL) { HARNESS_QA_POINTER("rear set to NULL after removing last node"); }
            HARNESS_QA_OPERATION("dequeue", "after");
            if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after dequeue"); emit_state(&queue); }
            index++;
        } else {
            cola_vaciar(&queue);
            return harness_error("operacion no permitida");
        }
    }
    emit_state(&queue);
    cola_vaciar(&queue);
    HARNESS_QA_FREE("destroyed remaining queue nodes");
    harness_qa_end();
    return 0;
}
