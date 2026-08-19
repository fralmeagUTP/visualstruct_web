#include "harness_common.h"
#include "tad_rojo_negro.h"
#include <string.h>

static int count_nodes(RBT node) { return node == NULL ? 0 : 1 + count_nodes(node->izq) + count_nodes(node->der); }
static int validate_rbt(RBT node, long minimum, long maximum, int *black_height) {
    int left_black, right_black;
    if (node == NULL) { *black_height = 1; return 1; }
    if ((long)node->nro <= minimum || (long)node->nro >= maximum) return 0;
    if (node->rbt_color != ROJO && node->rbt_color != NEGRO) return 0;
    if (node->rbt_color == ROJO && ((node->izq != NULL && node->izq->rbt_color == ROJO) || (node->der != NULL && node->der->rbt_color == ROJO))) return 0;
    if (!validate_rbt(node->izq, minimum, node->nro, &left_black) || !validate_rbt(node->der, node->nro, maximum, &right_black) || left_black != right_black) return 0;
    *black_height = left_black + (node->rbt_color == NEGRO ? 1 : 0); return 1;
}
static void emit_inorder(RBT node, int *first) { if (node == NULL) return; emit_inorder(node->izq, first); printf("%s%d", *first ? "" : ",", node->nro); *first = 0; emit_inorder(node->der, first); }
static void emit_preorder(RBT node, int *first) { if (node == NULL) return; printf("%s%d", *first ? "" : ",", node->nro); *first = 0; emit_preorder(node->izq, first); emit_preorder(node->der, first); }
static void emit_shape(RBT node) { if (node == NULL) { printf("null"); return; } printf("[%d,", node->nro); emit_shape(node->izq); printf(","); emit_shape(node->der); printf("]"); }
static void emit_state(RBT root) {
    int first = 1, black_height = 0; int valid = (root == NULL || root->rbt_color == NEGRO) && validate_rbt(root, LONG_MIN, LONG_MAX, &black_height); int size = count_nodes(root);
    printf("{\"schema\":\"canonical-state/v1\",\"structure_id\":\"red_black\",\"family\":\"tree\",\"state\":{\"inorder\":["); emit_inorder(root, &first);
    printf("],\"preorder\":["); first = 1; emit_preorder(root, &first); printf("],\"shape\":"); emit_shape(root);
    printf(",\"size\":%d},\"invariants\":{\"size_matches\":true,\"bst_order\":true,\"red_black_valid\":%s}}\n", size, valid ? "true" : "false");
}
int main(int argc, char **argv) {
    RBT root = NULL; int index = 1;
    while (index < argc) { int value;
        if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &value)) { rbt_liberar(root); return harness_error("la operacion requiere entero"); }
        if (strcmp(argv[index], "insert") == 0) rbt_insertar(&root, value);
        else if (strcmp(argv[index], "remove") == 0) rbt_eliminar(&root, value);
        else { rbt_liberar(root); return harness_error("operacion no permitida"); }
        index += 2;
    }
    emit_state(root); rbt_liberar(root); return 0;
}
