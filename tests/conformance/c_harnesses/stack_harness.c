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
    harness_qa_begin("stack", argc, argv);
    while (index < argc) {
        if (strcmp(argv[index], "peek") == 0) {
            HARNESS_QA_OPERATION("peek", "before");
            HARNESS_QA_CONDITION(stack == NULL ? "stack == NULL:true" : "stack == NULL:false");
            if (stack == NULL) { pila_destruir(&stack); return harness_error("peek sobre pila vacia"); }
            HARNESS_QA_RETURN_INT("top", stack->nro);
            HARNESS_QA_OPERATION("peek", "after");
            if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after peek"); emit_state(stack); }
            index++;
        } else if (strcmp(argv[index], "empty") == 0) {
            HARNESS_QA_OPERATION("empty", "before"); HARNESS_QA_RETURN_INT("empty", stack == NULL ? 1 : 0); HARNESS_QA_OPERATION("empty", "after");
            if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after empty query"); emit_state(stack); }
            index++;
        } else if (strcmp(argv[index], "clear") == 0) {
            HARNESS_QA_OPERATION("clear", "before"); pila_destruir(&stack); HARNESS_QA_FREE("freed every stack node during clear"); HARNESS_QA_POINTER("top set to NULL"); HARNESS_QA_OPERATION("clear", "after");
            if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after clear"); emit_state(stack); }
            index++;
        } else
        if (strcmp(argv[index], "push") == 0) {
            int value;
            HARNESS_QA_OPERATION("push", "before");
            if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &value)) {
                pila_destruir(&stack);
                return harness_error("push requiere un entero");
            }
            pila_apilar(&stack, value);
            HARNESS_QA_ALLOCATION("allocated stack node");
            HARNESS_QA_POINTER("top points to inserted node");
            HARNESS_QA_OPERATION("push", "after");
            if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after push"); emit_state(stack); }
            index += 2;
        } else if (strcmp(argv[index], "pop") == 0) {
            HARNESS_QA_OPERATION("pop", "before");
            HARNESS_QA_CONDITION(stack == NULL ? "stack == NULL:true" : "stack == NULL:false");
            if (stack == NULL) {
                pila_destruir(&stack);
                return harness_error("pop sobre pila vacia");
            }
            { int removed = pila_desapilar(&stack); HARNESS_QA_RETURN_INT("value", removed); HARNESS_QA_FREE("freed popped stack node"); }
            HARNESS_QA_POINTER("top advances to next node");
            HARNESS_QA_OPERATION("pop", "after");
            if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after pop"); emit_state(stack); }
            index++;
        } else {
            pila_destruir(&stack);
            return harness_error("operacion no permitida");
        }
    }
    emit_state(stack);
    pila_destruir(&stack);
    HARNESS_QA_FREE("destroyed remaining stack nodes");
    harness_qa_end();
    return 0;
}
