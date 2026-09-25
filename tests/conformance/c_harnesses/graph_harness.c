#include "harness_common.h"
#include "tad_grafo.h"
#include <string.h>

static int vertex_count(Grafo graph) { int count = 0; ListaVertice item = grafo_vertices(graph); while (item != NULL) { count++; item = item->sig; } return count; }
static int edge_count(Grafo graph) { int count = 0; ListaArco item = grafo_arcos(graph); while (item != NULL) { count++; item = item->sig; } return count; }
static int has_vertex(Grafo graph, int value) { ListaVertice item = graph.v; while (item != NULL) { if (item->dato == value) return 1; item = item->sig; } return 0; }

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
static void emit_vertex_result(const char *label, ListaVertice list) {
    char detail[512]; size_t used = (size_t)snprintf(detail, sizeof(detail), "%s=", label);
    ListaVertice item = list; int first = 1;
    while (item != NULL && used < sizeof(detail)) { int written = snprintf(detail + used, sizeof(detail) - used, "%s%d", first ? "" : ",", item->dato); if (written < 0) break; used += (size_t)written; first = 0; item = item->sig; }
    HARNESS_QA_RETURN(detail);
}
static void free_vertex_result(ListaVertice list) { while (list != NULL) { ListaVertice next = list->sig; free(list); list = next; } }
static void emit_edge_result(const char *label, ListaArco list) {
    int count = 0, cost = 0; char detail[128]; ListaArco item = list;
    while (item != NULL) { count++; cost += item->costo; item = item->sig; }
    (void)snprintf(detail, sizeof(detail), "%s_edges=%d,cost=%d", label, count, cost); HARNESS_QA_RETURN(detail);
}
static void free_edge_result(ListaArco list) { while (list != NULL) { ListaArco next = list->sig; free(list); list = next; } }
static void emit_state(Grafo graph) {
    int vertex_count = grafo_orden(graph), edge_count = grafo_tamano(graph), index = 0, unique = 1, endpoints_exist = 1;
    int *vertices = vertex_count > 0 ? malloc((size_t)vertex_count * sizeof(*vertices)) : NULL;
    Edge *edges = edge_count > 0 ? malloc((size_t)edge_count * sizeof(*edges)) : NULL;
    ListaVertice vertex = graph.v; ListaArco edge = graph.a;
    while (vertex != NULL) { vertices[index++] = vertex->dato; vertex = vertex->sig; }
    if (vertex_count > 1) qsort(vertices, (size_t)vertex_count, sizeof(*vertices), compare_ints);
    for (index = 1; index < vertex_count; index++) if (vertices[index - 1] == vertices[index]) unique = 0;
    index = 0;
    while (edge != NULL) { edges[index].source = edge->origen; edges[index].target = edge->destino; edges[index].weight = edge->costo; if (!has_vertex(graph, edge->origen) || !has_vertex(graph, edge->destino)) endpoints_exist = 0; index++; edge = edge->sig; }
    if (edge_count > 1) qsort(edges, (size_t)edge_count, sizeof(*edges), compare_edges);
    printf("{\"schema\":\"canonical-state/v1\",\"structure_id\":\"graph\",\"family\":\"graph\",\"state\":{\"directed\":true,\"vertices\":[");
    for (index = 0; index < vertex_count; index++) printf("%s\"%d\"", index == 0 ? "" : ",", vertices[index]);
    printf("],\"edges\":[");
    for (index = 0; index < edge_count; index++) printf("%s[\"%d\",\"%d\",%d]", index == 0 ? "" : ",", edges[index].source, edges[index].target, edges[index].weight);
    printf("]},\"invariants\":{\"unique_vertices\":%s,\"edge_endpoints_exist\":%s}}\n", unique ? "true" : "false", endpoints_exist ? "true" : "false"); free(vertices); free(edges);
}
int main(int argc, char **argv) {
    Grafo graph = grafo_crear(); int index = 1; harness_qa_begin("graph", argc, argv);
    while (index < argc) {
        int first, second, weight;
        if (strcmp(argv[index], "add_vertex") == 0) {
            HARNESS_QA_OPERATION("add_vertex", "before");
            if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &first)) { destroy_graph(&graph); return harness_error("add_vertex requiere entero"); }
            { int before = vertex_count(graph); graph = grafo_insertar_vertice(graph, first); if (vertex_count(graph) > before) HARNESS_QA_ALLOCATION("allocated graph vertex"); } HARNESS_QA_COMPARISON("vertex list searched for duplicate"); HARNESS_QA_POINTER("vertex linked into graph vertex list"); HARNESS_QA_OPERATION("add_vertex", "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after add_vertex"); emit_state(graph); } index += 2; continue;
        }
        if (strcmp(argv[index], "add_edge") == 0) {
            HARNESS_QA_OPERATION("add_edge", "before");
            if (index + 3 >= argc || !harness_parse_int(argv[index + 1], &first) || !harness_parse_int(argv[index + 2], &second) || !harness_parse_int(argv[index + 3], &weight)) { destroy_graph(&graph); return harness_error("add_edge requiere origen destino peso"); }
            { int before = edge_count(graph); graph = grafo_insertar_arco(graph, first, second, weight); if (edge_count(graph) > before) HARNESS_QA_ALLOCATION("allocated graph edge"); } HARNESS_QA_CONDITION("C insertion does not validate endpoints or duplicates"); HARNESS_QA_POINTER("edge linked into graph edge list"); HARNESS_QA_OPERATION("add_edge", "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after add_edge"); emit_state(graph); } index += 4; continue;
        }
        if (strcmp(argv[index], "remove_vertex") == 0 || strcmp(argv[index], "exists_vertex") == 0) {
            const char *operation = argv[index]; HARNESS_QA_OPERATION(operation, "before");
            if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &first)) { destroy_graph(&graph); return harness_error("operacion de vertice requiere entero"); }
            if (strcmp(operation, "exists_vertex") == 0) HARNESS_QA_RETURN_INT("exists_vertex", grafo_existe_vertice(graph, first));
            else { int before = vertex_count(graph); graph = grafo_eliminar_vertice(graph, first); if (vertex_count(graph) < before) HARNESS_QA_FREE("released graph vertex during remove"); }
            HARNESS_QA_OPERATION(operation, "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after vertex operation"); emit_state(graph); } index += 2; continue;
        }
        if (strcmp(argv[index], "remove_edge") == 0 || strcmp(argv[index], "exists_edge") == 0 || strcmp(argv[index], "weight") == 0) {
            const char *operation = argv[index]; HARNESS_QA_OPERATION(operation, "before");
            if (index + 2 >= argc || !harness_parse_int(argv[index + 1], &first) || !harness_parse_int(argv[index + 2], &second)) { destroy_graph(&graph); return harness_error("operacion de arco requiere origen y destino"); }
            if (strcmp(operation, "exists_edge") == 0) HARNESS_QA_RETURN_INT("exists_edge", grafo_existe_arco(graph, first, second));
            else if (strcmp(operation, "weight") == 0) HARNESS_QA_RETURN_INT("weight", grafo_costo_arco(graph, first, second));
            else { int before = edge_count(graph); graph = grafo_eliminar_arco(graph, first, second); if (edge_count(graph) < before) HARNESS_QA_FREE("released graph edge during remove"); }
            HARNESS_QA_OPERATION(operation, "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after edge operation"); emit_state(graph); } index += 3; continue;
        }
        if (strcmp(argv[index], "empty") == 0 || strcmp(argv[index], "order") == 0 || strcmp(argv[index], "size") == 0 || strcmp(argv[index], "clear") == 0) {
            const char *operation = argv[index]; HARNESS_QA_OPERATION(operation, "before");
            if (strcmp(operation, "empty") == 0) HARNESS_QA_RETURN_INT("empty", grafo_vacio(graph));
            else if (strcmp(operation, "order") == 0) HARNESS_QA_RETURN_INT("order", grafo_orden(graph));
            else if (strcmp(operation, "size") == 0) HARNESS_QA_RETURN_INT("size", grafo_tamano(graph));
            else { destroy_graph(&graph); HARNESS_QA_FREE("released graph during clear"); }
            HARNESS_QA_OPERATION(operation, "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state after graph query or clear"); emit_state(graph); } index += 1; continue;
        }
        if (strcmp(argv[index], "bfs") == 0 || strcmp(argv[index], "dfs") == 0 || strcmp(argv[index], "prim") == 0) {
            const char *operation = argv[index]; HARNESS_QA_OPERATION(operation, "before");
            if (index + 1 >= argc || !harness_parse_int(argv[index + 1], &first)) { destroy_graph(&graph); return harness_error("algoritmo requiere vertice inicial"); }
            if (strcmp(operation, "bfs") == 0 || strcmp(operation, "dfs") == 0) { ListaVertice result = strcmp(operation, "bfs") == 0 ? grafo_bfs(graph, first) : grafo_dfs(graph, first); emit_vertex_result(operation, result); free_vertex_result(result); HARNESS_QA_FREE("released traversal result"); }
            else { ListaArco result = grafo_prim(graph, first); emit_edge_result(operation, result); free_edge_result(result); HARNESS_QA_FREE("released Prim result"); }
            HARNESS_QA_OPERATION(operation, "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state unchanged after graph algorithm"); emit_state(graph); } index += 2; continue;
        }
        if (strcmp(argv[index], "dijkstra") == 0 || strcmp(argv[index], "bellman") == 0) {
            const char *operation = argv[index]; HARNESS_QA_OPERATION(operation, "before");
            if (index + 2 >= argc || !harness_parse_int(argv[index + 1], &first) || !harness_parse_int(argv[index + 2], &second)) { destroy_graph(&graph); return harness_error("camino requiere inicio y llegada"); }
            { ListaArco result = strcmp(operation, "dijkstra") == 0 ? grafo_dijkstra(graph, first, second) : grafo_bellman_ford(graph, first, second); emit_edge_result(operation, result); free_edge_result(result); HARNESS_QA_FREE("released shortest-path result"); }
            HARNESS_QA_OPERATION(operation, "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state unchanged after shortest path"); emit_state(graph); } index += 3; continue;
        }
        if (strcmp(argv[index], "kruskal") == 0) {
            ListaArco result; HARNESS_QA_OPERATION("kruskal", "before"); result = grafo_kruskal(graph); emit_edge_result("kruskal", result); free_edge_result(result); HARNESS_QA_FREE("released Kruskal result"); HARNESS_QA_OPERATION("kruskal", "after"); if (harness_qa_enabled()) { HARNESS_QA_SNAPSHOT("state unchanged after Kruskal"); emit_state(graph); } index += 1; continue;
        }
        destroy_graph(&graph); return harness_error("operacion no permitida");
    }
    emit_state(graph); destroy_graph(&graph); HARNESS_QA_FREE("released graph vertices and edges"); harness_qa_end(); return 0;
}
