#include "harness_common.h"
#include "tad_ordenamiento.h"

#include <string.h>

typedef void (*sort_fn)(int[], size_t);
typedef int (*sort_status_fn)(int[], size_t);

static sort_fn select_algorithm(const char *name) {
    if (strcmp(name, "exchange") == 0) return ordenar_intercambio;
    if (strcmp(name, "selection") == 0) return ordenar_seleccion;
    if (strcmp(name, "insertion") == 0) return ordenar_insercion;
    if (strcmp(name, "bubble") == 0) return ordenar_burbuja;
    if (strcmp(name, "shell") == 0) return ordenar_shell;
    if (strcmp(name, "quick") == 0) return ordenar_quicksort;
    if (strcmp(name, "heap") == 0) return ordenar_heapsort;
    return NULL;
}

static sort_status_fn select_status_algorithm(const char *name) {
    if (strcmp(name, "merge") == 0) return ordenar_mergesort;
    if (strcmp(name, "counting") == 0) return ordenar_counting_sort;
    if (strcmp(name, "bin") == 0) return ordenar_binsort;
    if (strcmp(name, "radix") == 0) return ordenar_radixsort;
    return NULL;
}

int main(int argc, char **argv) {
    int *values;
    int index;
    sort_fn algorithm;
    sort_status_fn status_algorithm;
    harness_qa_begin("sorting", argc, argv);
    if (argc < 2) return harness_error("falta algoritmo");
    if (argc < 3) return harness_error("el arreglo no puede estar vacio");
    algorithm = select_algorithm(argv[1]);
    status_algorithm = select_status_algorithm(argv[1]);
    HARNESS_QA_BRANCH(algorithm == NULL && status_algorithm == NULL ? "algorithm recognized:false" : "algorithm recognized:true");
    if (algorithm == NULL && status_algorithm == NULL) return harness_error("algoritmo no permitido");
    values = argc > 2 ? malloc((size_t)(argc - 2) * sizeof(*values)) : NULL;
    HARNESS_QA_ALLOCATION("allocate sorting working array");
    if (argc > 2 && values == NULL) return harness_error("sin memoria");
    for (index = 2; index < argc; index++) {
        if (!harness_parse_int(argv[index], &values[index - 2])) {
            free(values);
            return harness_error("valor no entero");
        }
    }
    HARNESS_QA_OPERATION(argv[1], "before"); HARNESS_QA_CALL("selected C sorting function", "before");
    if (algorithm != NULL) algorithm(values, (size_t)(argc - 2));
    else HARNESS_QA_RETURN_INT("status", status_algorithm(values, (size_t)(argc - 2)));
    HARNESS_QA_CALL("selected C sorting function", "after"); HARNESS_QA_OPERATION(argv[1], "after");
    HARNESS_QA_SNAPSHOT("state after sorting algorithm");
    printf("{\"schema\":\"canonical-state/v1\",\"structure_id\":\"sorting\","
           "\"family\":\"sorting\",\"state\":{\"values\":[");
    for (index = 2; index < argc; index++) {
        printf("%s%d", index == 2 ? "" : ",", values[index - 2]);
    }
    printf("],\"size\":%d},\"invariants\":{\"size_matches\":true}}\n", argc - 2);
    free(values);
    HARNESS_QA_FREE("released sorting working array"); harness_qa_end();
    return 0;
}
