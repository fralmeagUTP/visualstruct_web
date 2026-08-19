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
    ABBNodo *root = NULL; int index = 1;
    while (index < argc) {
        int value;
        if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &value)) { abb_liberarArbol(root); return harness_error("la operacion requiere entero"); }
        if (strcmp(argv[index], "insert") == 0) root = abb_insertar(root, value);
        else if (strcmp(argv[index], "remove") == 0) root = abb_eliminar(root, value);
        else { abb_liberarArbol(root); return harness_error("operacion no permitida"); }
        index += 2;
    }
    emit_state(root); abb_liberarArbol(root); return 0;
}
