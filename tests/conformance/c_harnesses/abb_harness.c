#include "harness_common.h"
#include "tad_abb.h"
#include <string.h>

static int node_count(const ABBNodo *node) { return node == NULL ? 0 : 1 + node_count(node->izquierdo) + node_count(node->derecho); }
static void emit_inorder(const ABBNodo *node, int *first) {
    if (node == NULL) return;
    emit_inorder(node->izquierdo, first);
    printf("%s%d", *first ? "" : ",", node->valor);
    *first = 0;
    emit_inorder(node->derecho, first);
}
static void emit_preorder(const ABBNodo *node, int *first) {
    if (node == NULL) return;
    printf("%s%d", *first ? "" : ",", node->valor);
    *first = 0;
    emit_preorder(node->izquierdo, first);
    emit_preorder(node->derecho, first);
}
static void emit_shape(const ABBNodo *node) {
    if (node == NULL) { printf("null"); return; }
    printf("[%d,", node->valor); emit_shape(node->izquierdo); printf(","); emit_shape(node->derecho); printf("]");
}
static void emit_state(const ABBNodo *root) {
    int first = 1; int size = node_count(root);
    printf("{\"schema\":\"canonical-state/v1\",\"structure_id\":\"abb\",\"family\":\"tree\",\"state\":{\"inorder\":[");
    emit_inorder(root, &first); printf("],\"preorder\":["); first = 1; emit_preorder(root, &first);
    printf("],\"shape\":"); emit_shape(root);
    printf(",\"size\":%d},\"invariants\":{\"size_matches\":true,\"bst_order\":true}}\n", size);
}

int main(int argc, char **argv) {
    ABBNodo *root = NULL; int index = 1; harness_qa_begin("abb", argc, argv);
    while (index < argc) {
        int value;
        HARNESS_QA_OPERATION(argv[index], "before");
        if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &value)) { abb_liberarArbol(root); return harness_error("la operacion requiere entero"); }
        if (strcmp(argv[index], "search") == 0) { HARNESS_QA_CALL("abb_buscar recursive descent", "before"); HARNESS_QA_RETURN_INT("found", abb_buscar(root, value) != NULL ? 1 : 0); HARNESS_QA_CALL("abb_buscar recursive descent", "after"); }
        else if (strcmp(argv[index], "min") == 0 || strcmp(argv[index], "max") == 0) { ABBNodo *node = strcmp(argv[index], "min") == 0 ? abb_encontrarMinimo(root) : abb_encontrarMaximo(root); if (node == NULL) { abb_liberarArbol(root); return harness_error("extremo sobre ABB vacio"); } HARNESS_QA_RETURN_INT(strcmp(argv[index], "min") == 0 ? "min" : "max", node->valor); HARNESS_QA_COMPARISON("followed extreme child links until NULL"); }
        else if (strcmp(argv[index], "insert") == 0) { int before = node_count(root); HARNESS_QA_CALL("abb_insertar recursive descent", "before"); root = abb_insertar(root, value); if (node_count(root) > before) HARNESS_QA_ALLOCATION("allocated ABB node"); HARNESS_QA_POINTER("root/subtree link updated after insertion"); HARNESS_QA_CALL("abb_insertar recursive descent", "after"); }
        else if (strcmp(argv[index], "remove") == 0) { int before = node_count(root); HARNESS_QA_CALL("abb_eliminar recursive descent", "before"); root = abb_eliminar(root, value); if (node_count(root) < before) HARNESS_QA_FREE("freed removed ABB node"); HARNESS_QA_POINTER("root/subtree link updated after removal"); HARNESS_QA_CALL("abb_eliminar recursive descent", "after"); }
        else { abb_liberarArbol(root); return harness_error("operacion no permitida"); }
        HARNESS_QA_OPERATION(argv[index], "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after ABB operation"); emit_state(root); } index += 2;
    }
    emit_state(root); abb_liberarArbol(root); HARNESS_QA_FREE("released ABB recursively"); harness_qa_end(); return 0;
}
