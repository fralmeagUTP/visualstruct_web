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
    for (index = 0; index < count; index++) printf("%s[\"%d\",\"%d\"]", index == 0 ? "" : ",", pairs[index].key, pairs[index].value);
    printf("],\"size\":%d,\"capacity\":%d},\"invariants\":{\"size_matches\":true,\"capacity_positive\":true}}\n", count, th_capacidad(table)); free(pairs);
}
int main(int argc, char **argv) {
    TablaHash table; int index = 1; th_inicializar(&table, 17);
    while (index < argc) {
        int key, value;
        if (strcmp(argv[index], "put") == 0) {
            if (index + 2 >= argc || !harness_parse_int(argv[index + 1], &key) || !harness_parse_int(argv[index + 2], &value)) { th_destruir(&table); return harness_error("put requiere clave y valor"); }
            if (!th_insertar(&table, key, value)) { th_destruir(&table); return harness_error("fallo al insertar"); }
            index += 3; continue;
        }
        if (strcmp(argv[index], "remove") == 0) {
            if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &key)) { th_destruir(&table); return harness_error("remove requiere clave"); }
            (void)th_eliminar(&table, key); index += 2; continue;
        }
        th_destruir(&table); return harness_error("operacion no permitida");
    }
    emit_state(&table); th_destruir(&table); return 0;
}
