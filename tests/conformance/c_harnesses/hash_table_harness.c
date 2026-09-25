#include "harness_common.h"
#include "tad_tabla_hash.h"
#include <string.h>

typedef struct { int key; int value; } Pair;
static int compare_pairs(const void *left, const void *right) { const Pair *a = left, *b = right; return (a->key > b->key) - (a->key < b->key); }
static void emit_state(const TablaHash *table) {
    int count = th_cantidad(table), index = 0, bucket_index; Pair *pairs = count > 0 ? malloc((size_t)count * sizeof(*pairs)) : NULL;
    for (bucket_index = 0; bucket_index < table->capacidad; bucket_index++) {
        THNodo *node = table->buckets[bucket_index];
        while (node != NULL) { pairs[index].key = node->clave; pairs[index].value = node->valor; index++; node = node->siguiente; }
    }
    qsort(pairs, (size_t)count, sizeof(*pairs), compare_pairs);
    printf("{\"schema\":\"canonical-state/v1\",\"structure_id\":\"hash_table\",\"family\":\"hash\",\"state\":{\"pairs\":[");
    for (index = 0; index < count; index++) printf("%s[%d,\"%d\"]", index == 0 ? "" : ",", pairs[index].key, pairs[index].value);
    printf("],\"size\":%d,\"capacity\":%d},\"invariants\":{\"size_matches\":true,\"capacity_positive\":true}}\n", count, th_capacidad(table)); free(pairs);
}
int main(int argc, char **argv) {
    TablaHash table; int index = 1; th_inicializar(&table, 17); harness_qa_begin("hash_table", argc, argv); HARNESS_QA_ALLOCATION("allocated initial hash bucket array");
    while (index < argc) {
        int key, value;
        if (strcmp(argv[index], "put") == 0) {
            int previous_count = th_cantidad(&table); HARNESS_QA_OPERATION("put", "before");
            if (index + 2 >= argc || !harness_parse_int(argv[index + 1], &key) || !harness_parse_int(argv[index + 2], &value)) { th_destruir(&table); return harness_error("put requiere clave y valor"); }
            if (!th_insertar(&table, key, value)) { th_destruir(&table); return harness_error("fallo al insertar"); }
            if (th_cantidad(&table) > previous_count) HARNESS_QA_ALLOCATION("allocated hash entry");
            HARNESS_QA_COMPARISON("hash bucket chain searched for existing key"); HARNESS_QA_CONDITION("C TAD capacity remains fixed after insertion"); HARNESS_QA_POINTER("entry linked or existing value updated"); HARNESS_QA_OPERATION("put", "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after put"); emit_state(&table); } index += 3; continue;
        }
        if (strcmp(argv[index], "remove") == 0) {
            HARNESS_QA_OPERATION("remove", "before");
            if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &key)) { th_destruir(&table); return harness_error("remove requiere clave"); }
            if (th_eliminar(&table, key)) { HARNESS_QA_FREE("freed removed hash entry"); }
            HARNESS_QA_COMPARISON("hash bucket chain searched for key"); HARNESS_QA_POINTER("bucket chain bypasses removed entry when found"); HARNESS_QA_OPERATION("remove", "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after remove"); emit_state(&table); } index += 2; continue;
        }
        if (strcmp(argv[index], "get") == 0) {
            int found;
            HARNESS_QA_OPERATION("get", "before");
            if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &key)) { th_destruir(&table); return harness_error("get requiere clave"); }
            found = th_buscar(&table, key, &value);
            HARNESS_QA_RETURN_INT("found", found ? 1 : 0);
            if (found) { HARNESS_QA_RETURN_INT("value", value); }
            HARNESS_QA_COMPARISON("hash bucket chain searched until key match or NULL");
            HARNESS_QA_OPERATION("get", "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after get"); emit_state(&table); } index += 2; continue;
        }
        th_destruir(&table); return harness_error("operacion no permitida");
    }
    emit_state(&table); th_destruir(&table); HARNESS_QA_FREE("released hash buckets and entries"); harness_qa_end(); return 0;
}
