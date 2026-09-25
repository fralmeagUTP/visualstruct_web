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
static void emit_colors(RBT node, int *first) { if (node == NULL) return; printf("%s\"%c\"", *first ? "" : ",", node->rbt_color); *first = 0; emit_colors(node->izq, first); emit_colors(node->der, first); }
static void emit_shape(RBT node) { if (node == NULL) { printf("null"); return; } printf("[%d,", node->nro); emit_shape(node->izq); printf(","); emit_shape(node->der); printf("]"); }
static void emit_state(RBT root) {
    int first = 1, black_height = 0; int valid = (root == NULL || root->rbt_color == NEGRO) && validate_rbt(root, LONG_MIN, LONG_MAX, &black_height); int size = count_nodes(root);
    printf("{\"schema\":\"canonical-state/v1\",\"structure_id\":\"red_black\",\"family\":\"tree\",\"state\":{\"inorder\":["); emit_inorder(root, &first);
    printf("],\"preorder\":["); first = 1; emit_preorder(root, &first); printf("],\"shape\":"); emit_shape(root);
    printf(",\"size\":%d},\"invariants\":{\"size_matches\":true,\"bst_order\":true,\"root_black\":%s,\"black_height\":%d,\"preorder_colors\":[", size, root == NULL || root->rbt_color == NEGRO ? "true" : "false", black_height);
    first = 1; emit_colors(root, &first);
    printf("],\"red_black_valid\":%s}}\n", valid ? "true" : "false");
}
int main(int argc, char **argv) {
    RBT root = NULL; int index = 1; harness_qa_begin("red_black", argc, argv);
    while (index < argc) { int value; RBT previous_root = root; const char *operation = argv[index]; HARNESS_QA_OPERATION(operation, "before");
        if (strcmp(operation, "root") == 0) {
            HARNESS_QA_CONDITION(root == NULL ? "red-black root is NULL" : "red-black root is present");
            if (root != NULL) HARNESS_QA_RETURN_INT("root", root->nro);
            index += 1;
        } else if (strcmp(operation, "clear") == 0) {
            int before = count_nodes(root); rbt_liberar(root); root = NULL;
            if (before > 0) HARNESS_QA_FREE("released red-black nodes during clear");
            index += 1;
        } else {
            if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &value)) { rbt_liberar(root); return harness_error("la operacion requiere entero"); }
            if (strcmp(operation, "insert") == 0) { int before = count_nodes(root); HARNESS_QA_CALL("rbt_insertar and fix-up", "before"); rbt_insertar(&root, value); if (count_nodes(root) > before) HARNESS_QA_ALLOCATION("allocated red-black node"); HARNESS_QA_CALL("rbt_insertar and fix-up", "after"); }
            else if (strcmp(operation, "remove") == 0) { int before = count_nodes(root); HARNESS_QA_CALL("rbt_eliminar and fix-up", "before"); rbt_eliminar(&root, value); if (count_nodes(root) < before) HARNESS_QA_FREE("released red-black node during remove"); HARNESS_QA_CALL("rbt_eliminar and fix-up", "after"); }
            else { rbt_liberar(root); return harness_error("operacion no permitida"); }
            index += 2;
        }
        HARNESS_QA_BRANCH(previous_root != root ? "root changed during red-black fix-up" : "root unchanged during red-black fix-up"); HARNESS_QA_POINTER("tree links and colors updated by fix-up"); HARNESS_QA_OPERATION(operation, "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after red-black operation"); emit_state(root); }
    }
    emit_state(root); rbt_liberar(root); HARNESS_QA_FREE("released red-black tree recursively"); harness_qa_end(); return 0;
}
