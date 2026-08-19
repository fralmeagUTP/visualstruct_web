#include "harness_common.h"
#include "tad_ordenamiento.h"

#include <string.h>

typedef void (*sort_fn)(int[], size_t);

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

int main(int argc, char **argv) {
    int *values;
    int index;
    sort_fn algorithm;
    if (argc < 2) return harness_error("falta algoritmo");
    if (argc < 3) return harness_error("el arreglo no puede estar vacio");
    algorithm = select_algorithm(argv[1]);
    if (algorithm == NULL) return harness_error("algoritmo no permitido");
    values = argc > 2 ? malloc((size_t)(argc - 2) * sizeof(*values)) : NULL;
    if (argc > 2 && values == NULL) return harness_error("sin memoria");
    for (index = 2; index < argc; index++) {
        if (!harness_parse_int(argv[index], &values[index - 2])) {
            free(values);
            return harness_error("valor no entero");
        }
    }
    algorithm(values, (size_t)(argc - 2));
    printf("{\"schema\":\"canonical-state/v1\",\"structure_id\":\"sorting\","
           "\"family\":\"sorting\",\"state\":{\"values\":[");
    for (index = 2; index < argc; index++) {
        printf("%s%d", index == 2 ? "" : ",", values[index - 2]);
    }
    printf("],\"size\":%d},\"invariants\":{\"size_matches\":true}}\n", argc - 2);
    free(values);
    return 0;
}
