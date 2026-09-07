#include "harness_common.h"
#include "tad_avl.h"
#include <string.h>

static int count_nodes(AVL node) { return node == NULL ? 0 : 1 + count_nodes(node->izq) + count_nodes(node->der); }
static int validate_avl(AVL node, long minimum, long maximum, int *height) {
    int left_height, right_height;
    if (node == NULL) { *height = 0; return 1; }
    if ((long)node->nro <= minimum || (long)node->nro >= maximum) return 0;
    if (!validate_avl(node->izq, minimum, node->nro, &left_height) || !validate_avl(node->der, node->nro, maximum, &right_height)) return 0;
    if (left_height - right_height > 1 || right_height - left_height > 1) return 0;
    if ((node->izq != NULL && node->izq->padre != node) || (node->der != NULL && node->der->padre != node)) return 0;
    *height = (left_height > right_height ? left_height : right_height) + 1; return 1;
}
static void emit_inorder(AVL node, int *first) { if (node == NULL) return; emit_inorder(node->izq, first); printf("%s%d", *first ? "" : ",", node->nro); *first = 0; emit_inorder(node->der, first); }
static void emit_preorder(AVL node, int *first) { if (node == NULL) return; printf("%s%d", *first ? "" : ",", node->nro); *first = 0; emit_preorder(node->izq, first); emit_preorder(node->der, first); }
static void emit_shape(AVL node) { if (node == NULL) { printf("null"); return; } printf("[%d,", node->nro); emit_shape(node->izq); printf(","); emit_shape(node->der); printf("]"); }
static void emit_state(AVL root) {
    int first = 1, height = 0; int valid = validate_avl(root, LONG_MIN, LONG_MAX, &height); int size = count_nodes(root);
    printf("{\"schema\":\"canonical-state/v1\",\"structure_id\":\"avl\",\"family\":\"tree\",\"state\":{\"inorder\":["); emit_inorder(root, &first);
    printf("],\"preorder\":["); first = 1; emit_preorder(root, &first); printf("],\"shape\":"); emit_shape(root);
    printf(",\"size\":%d},\"invariants\":{\"size_matches\":true,\"bst_order\":true,\"avl_valid\":%s}}\n", size, valid ? "true" : "false");
}
int main(int argc, char **argv) {
    AVL root = NULL; int index = 1; harness_qa_begin("avl", argc, argv);
    while (index < argc) { int value; AVL previous_root = root; const char *operation = argv[index]; HARNESS_QA_OPERATION(operation, "before");
        if (strcmp(operation, "root") == 0) {
            HARNESS_QA_CONDITION(root == NULL ? "AVL root is NULL" : "AVL root is present");
            if (root != NULL) HARNESS_QA_RETURN_INT("root", root->nro);
            index += 1;
        } else if (strcmp(operation, "clear") == 0) {
            int before = count_nodes(root);
            avl_liberarAVL(root); root = NULL;
            if (before > 0) HARNESS_QA_FREE("released AVL nodes during clear");
            index += 1;
        } else {
            if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &value)) { avl_liberarAVL(root); return harness_error("la operacion requiere entero"); }
            if (strcmp(operation, "insert") == 0) { int before = count_nodes(root); HARNESS_QA_CALL("avl_insertar recursive descent and rebalance", "before"); avl_insertar(&root, value); if (count_nodes(root) > before) HARNESS_QA_ALLOCATION("allocated AVL node"); HARNESS_QA_CALL("avl_insertar recursive descent and rebalance", "after"); }
            else if (strcmp(operation, "remove") == 0) { int before = count_nodes(root); HARNESS_QA_CALL("avl_eliminar recursive descent and rebalance", "before"); avl_eliminar(&root, value); if (count_nodes(root) < before) HARNESS_QA_FREE("released AVL node during remove"); HARNESS_QA_CALL("avl_eliminar recursive descent and rebalance", "after"); }
            else { avl_liberarAVL(root); return harness_error("operacion no permitida"); }
            index += 2;
        }
        HARNESS_QA_BRANCH(previous_root != root ? "root changed during AVL rebalance" : "root unchanged during AVL rebalance"); HARNESS_QA_POINTER("parent and child links validated after AVL operation"); HARNESS_QA_OPERATION(operation, "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after AVL operation"); emit_state(root); }
    }
    emit_state(root); avl_liberarAVL(root); HARNESS_QA_FREE("released AVL recursively"); harness_qa_end(); return 0;
}
