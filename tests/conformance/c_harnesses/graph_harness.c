#include "harness_common.h"
#include "tad_grafo.h"
#include <string.h>

typedef struct { int source; int target; int weight; } Edge;
static int compare_ints(const void *left, const void *right) { int a = *(const int *)left, b = *(const int *)right; return (a > b) - (a < b); }
static int compare_edges(const void *left, const void *right) {
    const Edge *a = left, *b = right;
    if (a->source != b->source) return (a->source > b->source) - (a->source < b->source);
    if (a->target != b->target) return (a->target > b->target) - (a->target < b->target);
    return (a->weight > b->weight) - (a->weight < b->weight);
}
static void destroy_graph(Grafo *graph) {
    while (graph->v != NULL) { ListaVertice next = graph->v->sig; free(graph->v); graph->v = next; }
    while (graph->a != NULL) { ListaArco next = graph->a->sig; free(graph->a); graph->a = next; }
}
static void emit_state(Grafo graph) {
    int vertex_count = grafo_orden(graph), edge_count = grafo_tamano(graph), index = 0;
    int *vertices = vertex_count > 0 ? malloc((size_t)vertex_count * sizeof(*vertices)) : NULL;
    Edge *edges = edge_count > 0 ? malloc((size_t)edge_count * sizeof(*edges)) : NULL;
    ListaVertice vertex = graph.v; ListaArco edge = graph.a;
    while (vertex != NULL) { vertices[index++] = vertex->dato; vertex = vertex->sig; }
    qsort(vertices, (size_t)vertex_count, sizeof(*vertices), compare_ints); index = 0;
    while (edge != NULL) { edges[index].source = edge->origen; edges[index].target = edge->destino; edges[index].weight = edge->costo; index++; edge = edge->sig; }
    qsort(edges, (size_t)edge_count, sizeof(*edges), compare_edges);
    printf("{\"schema\":\"canonical-state/v1\",\"structure_id\":\"graph\",\"family\":\"graph\",\"state\":{\"directed\":true,\"vertices\":[");
    for (index = 0; index < vertex_count; index++) printf("%s\"%d\"", index == 0 ? "" : ",", vertices[index]);
    printf("],\"edges\":[");
    for (index = 0; index < edge_count; index++) printf("%s[\"%d\",\"%d\",%d]", index == 0 ? "" : ",", edges[index].source, edges[index].target, edges[index].weight);
    printf("]},\"invariants\":{\"unique_vertices\":true}}\n"); free(vertices); free(edges);
}
int main(int argc, char **argv) {
    Grafo graph = grafo_crear(); int index = 1;
    while (index < argc) {
        int first, second, weight;
        if (strcmp(argv[index], "add_vertex") == 0) {
            if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &first)) { destroy_graph(&graph); return harness_error("add_vertex requiere entero"); }
            graph = grafo_insertar_vertice(graph, first); index += 2; continue;
        }
        if (strcmp(argv[index], "add_edge") == 0) {
            if (index + 3 >= argc || !harness_parse_int(argv[index + 1], &first) || !harness_parse_int(argv[index + 2], &second) || !harness_parse_int(argv[index + 3], &weight)) { destroy_graph(&graph); return harness_error("add_edge requiere origen destino peso"); }
            graph = grafo_insertar_arco(graph, first, second, weight); index += 4; continue;
        }
        destroy_graph(&graph); return harness_error("operacion no permitida");
    }
    emit_state(graph); destroy_graph(&graph); return 0;
}
