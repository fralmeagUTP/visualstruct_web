"""One session-history C caller for Graph DOM and HTTP, never replaying queries."""
from __future__ import annotations
from string import Template
from typing import Any
from app.adapters.base_adapter import BaseAdapter
from app.adapters.graph_adapter import GraphAdapter
from app.domain.graph.integer_algorithms import integer_weight
from app.domain.graph.incident_caller import incident_caller_lines

_CALLS = {'run_bfs': 'ListaVertice rec_$index = grafo_bfs(g, $start); printf("BFS:"); for (ListaVertice it_$index = rec_$index; it_$index != NULL; it_$index = it_$index->sig) printf(" %d", it_$index->dato); printf("\\n"); while (rec_$index != NULL) { ListaVertice next_$index = rec_$index->sig; free(rec_$index); rec_$index = next_$index; }', 'run_dfs': 'ListaVertice rec_$index = grafo_dfs(g, $start); printf("DFS:"); for (ListaVertice it_$index = rec_$index; it_$index != NULL; it_$index = it_$index->sig) printf(" %d", it_$index->dato); printf("\\n"); while (rec_$index != NULL) { ListaVertice next_$index = rec_$index->sig; free(rec_$index); rec_$index = next_$index; }', 'run_dijkstra': 'ListaArco camino_$index = grafo_dijkstra(g, $start, $end); printf("Dijkstra:"); if (camino_$index != NULL) { long long costo_$index = 0; printf(" %d", camino_$index->origen); for (ListaArco it_$index = camino_$index; it_$index != NULL; it_$index = it_$index->sig) { printf(" -> %d", it_$index->destino); costo_$index += (long long)it_$index->costo; } printf(" | costo=%lld\\n", costo_$index); } else printf(" NULL (sin arcos, sin ruta o error de entrada/memoria)\\n"); while (camino_$index != NULL) { ListaArco next_$index = camino_$index->sig; free(camino_$index); camino_$index = next_$index; }', 'run_bellman_ford': 'ListaArco camino_$index = grafo_bellman_ford(g, $start, $end); printf("Bellman-Ford:"); if (camino_$index != NULL) { long long costo_$index = 0; printf(" %d", camino_$index->origen); for (ListaArco it_$index = camino_$index; it_$index != NULL; it_$index = it_$index->sig) { printf(" -> %d", it_$index->destino); costo_$index += (long long)it_$index->costo; } printf(" | costo=%lld\\n", costo_$index); } else printf(" NULL (sin arcos, sin ruta, ciclo negativo o error de entrada/memoria)\\n"); while (camino_$index != NULL) { ListaArco next_$index = camino_$index->sig; free(camino_$index); camino_$index = next_$index; }', 'run_prim': 'ListaArco mst_$index = grafo_prim(g, $start); printf("Prim:"); long long total_$index = 0; for (ListaArco it_$index = mst_$index; it_$index != NULL; it_$index = it_$index->sig) { printf(" %d-%d(%d)", it_$index->origen, it_$index->destino, it_$index->costo); total_$index += (long long)it_$index->costo; } printf(" | costo=%lld\\n", total_$index); while (mst_$index != NULL) { ListaArco next_$index = mst_$index->sig; free(mst_$index); mst_$index = next_$index; }', 'run_kruskal': 'ListaArco mst_$index = grafo_kruskal(g); printf("Kruskal:"); long long total_$index = 0; for (ListaArco it_$index = mst_$index; it_$index != NULL; it_$index = it_$index->sig) { printf(" %d-%d(%d)", it_$index->origen, it_$index->destino, it_$index->costo); total_$index += (long long)it_$index->costo; } printf(" | costo=%lld\\n", total_$index); while (mst_$index != NULL) { ListaArco next_$index = mst_$index->sig; free(mst_$index); mst_$index = next_$index; }'}

_CLEANUP = "while (g.a != NULL) { ListaArco next = g.a->sig; free(g.a); g.a = next; } while (g.v != NULL) { ListaVertice next = g.v->sig; free(g.v); g.v = next; }"

def _integer(payload: dict[str, Any], name: str) -> str:
    value = BaseAdapter._require_int(payload, name, name)
    if not -2147483648 <= value <= 2147483647:
        raise ValueError("El main C requiere vértices y argumentos int32.")
    return "(-2147483647 - 1)" if value == -2147483648 else str(value)


def build_graph_main(history: list[dict[str, Any]]) -> str:
    """Emit chronological accepted calls, printing and freeing actual C results.

    Duplicate successful queries remain distinct. Mutation replay is used only
    to materialize a recorded seeded random graph; algorithms are never called.
    C has no directed flag, so undirected insertion/removal emits both arcs.
    """
    lines = ['/** @file main.c @brief Historial de sesión Graph; resultados calculados en C y listas propias liberadas. */', '#include "tad_grafo.h"', '#include <stdio.h>', '#include <stdlib.h>', '/** @brief Ejecuta las llamadas cronológicas. @return 0 tras liberar el grafo. */', 'int main(void) {', '    Grafo g = grafo_crear();', '']
    directed = False
    random_adapter = None
    if any(step.get('operation') == 'generate_random_graph' for step in history):
        random_adapter = GraphAdapter()
        # Materialize legitimate historical seeded graphs without truncation.
        random_adapter._enforce_educational_limit = False
    for index, step in enumerate(history, 1):
        operation = step['operation']; payload = step.get('payload', {})
        if random_adapter is not None and operation not in _CALLS:
            random_adapter.execute(operation, dict(payload))
        if operation in {'create_graph', 'clear_graph', 'generate_random_graph'}:
            if operation == 'create_graph':
                directed = GraphAdapter._parse_bool(payload.get('directed', False))
            lines.append('    ' + _CLEANUP)
            lines.append('    g = grafo_crear();')
            if operation == 'generate_random_graph':
                graph = random_adapter.graph._g
                for vertex in graph._vertices:
                    lines.append('    g = grafo_insertar_vertice(g, ' + _integer({'vertex': vertex}, 'vertex') + ');')
                for origin, target, weight in graph._arcos:
                    lines.append(f'    g = grafo_insertar_arco(g, {origin}, {target}, {weight});')
        elif operation in {'insert_vertex', 'remove_vertex'}:
            function = 'grafo_insertar_vertice' if operation == 'insert_vertex' else 'grafo_eliminar_vertice'
            lines.append(f'    g = {function}(g, {_integer(payload, "vertex")});')
            if operation == "remove_vertex":
                lines.extend(incident_caller_lines(BaseAdapter._require_int(payload, "vertex", "vertex")))
        elif operation in {'insert_edge', 'remove_edge'}:
            origin = _integer(payload, 'origin'); target = _integer(payload, 'target')
            function = 'grafo_insertar_arco' if operation == 'insert_edge' else 'grafo_eliminar_arco'
            weight = ', ' + str(integer_weight(payload.get('weight', 1))) if operation == 'insert_edge' else ''
            lines.append(f'    g = {function}(g, {origin}, {target}{weight});')
            if not directed and origin != target:
                lines.append(f'    g = {function}(g, {target}, {origin}{weight});')
        elif operation in _CALLS:
            arguments = {'index': str(index)}
            if operation != 'run_kruskal': arguments['start'] = _integer(payload, 'start')
            if operation in {'run_dijkstra', 'run_bellman_ford'}: arguments['end'] = _integer(payload, 'end')
            lines.append('    ' + Template(_CALLS[operation]).substitute(arguments))
        else:
            raise ValueError('Operación sin caller C Graph: ' + operation)
    lines.extend(['    ' + _CLEANUP, '    return 0;', '}'])
    return '\n'.join(lines)
