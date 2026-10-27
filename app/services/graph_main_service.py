"""Generate a real C caller for the book contract; never precompute query results."""
from __future__ import annotations
from typing import Any
from app.adapters.base_adapter import BaseAdapter

_ALGORITHMS = {
    'run_bfs': ('grafo_bfs', 'BFS'), 'run_dfs': ('grafo_dfs', 'DFS'),
    'run_dijkstra': ('grafo_dijkstra', 'Dijkstra'),
    'run_bellman_ford': ('grafo_bellman_ford', 'Bellman-Ford'),
    'run_prim': ('grafo_prim', 'Prim'), 'run_kruskal': ('grafo_kruskal', 'Kruskal'),
}


def _integer(payload: dict[str, Any], name: str) -> str:
    value = BaseAdapter._require_int(payload, name, name)
    if not -2147483648 <= value <= 2147483647:
        raise ValueError('El main C requiere vértices y pesos int32.')
    return '(-2147483647 - 1)' if value == -2147483648 else str(value)


def _weight(payload: dict[str, Any]) -> str:
    # Reuse only the existing pure input validator, never an algorithm engine.
    from app.domain.graph.integer_algorithms import integer_weight
    raw = payload.get('weight', 1)
    value = 1 if raw is None or str(raw).strip() == '' else integer_weight(raw)
    return _integer({'weight': value}, 'weight')


def _directed(value: Any) -> bool:
    if isinstance(value, bool): return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {'1', 'true', 'si', 'yes'}: return True
        if normalized in {'0', 'false', 'no'}: return False
    if isinstance(value, (int, float)): return bool(value)
    raise ValueError('El valor de dirigido es inválido.')


def _vertices_call(function: str, args: str, index: str, label: str) -> list[str]:
    return [f'GrafoEstado estado_{index};',
            f'ListaVertice lista_{index} = {function}({args}, &estado_{index});',
            f'printf("{label}: estado=%d", (int)estado_{index});',
            f'if (estado_{index} == GRAFO_OK) {{',
            f'    for (ListaVertice it = lista_{index}; it != NULL; it = it->sig) printf(" %d", it->dato);',
            f'    if (lista_{index} == NULL) printf(" (lista vacia valida)");', '}',
            'printf("\\n");', f'grafo_liberar_vertices(&lista_{index});']


def _arcs_call(function: str, args: str, index: str, label: str) -> list[str]:
    return [f'GrafoEstado estado_{index};',
            f'ListaArco lista_{index} = {function}({args}, &estado_{index});',
            f'printf("{label}: estado=%d", (int)estado_{index});',
            f'if (estado_{index} == GRAFO_OK) {{', '    long long total = 0;',
            f'    for (ListaArco it = lista_{index}; it != NULL; it = it->sig) {{',
            '        printf(" %d->%d(%d)", it->origen, it->destino, it->costo);',
            '        total += (long long)it->costo;', '    }',
            f'    if (lista_{index} == NULL) printf(" (sin arcos; resultado valido)");',
            '    printf(" | costo=%lld", total);', '}', 'printf("\\n");',
            f'grafo_liberar_arcos(&lista_{index});']


def _insert_call(operation: str, payload: dict[str, Any], index: str, directed: bool) -> list[str]:
    if operation == 'insert_vertex':
        return [f'GrafoEstado estado_{index};',
                f'g = grafo_insertar_vertice(g, {_integer(payload,"vertex")}, &estado_{index});',
                f'printf("insert_vertex: estado=%d\\n", (int)estado_{index});']
    a, b, cost = _integer(payload,'origin'), _integer(payload,'target'), _weight(payload)
    block = [f'GrafoEstado estado_{index};', f'g = grafo_insertar_arco(g, {a}, {b}, {cost}, &estado_{index});',
             f'printf("insert_edge: estado=%d\\n", (int)estado_{index});']
    if not directed and a != b:
        block += [f'if (estado_{index} == GRAFO_OK) {{',
                  f'    g = grafo_insertar_arco(g, {b}, {a}, {cost}, &estado_{index});',
                  f'    printf("insert_edge inverso: estado=%d\\n", (int)estado_{index});', '}']
    return block


def build_graph_main(history: list[dict[str, Any]]) -> str:
    """Emit chronological recorded calls using exact book signatures.

    Numeric statuses are GrafoEstado from the canonical header. A NULL list is
    interpreted only together with that status. Borrowed lists are not freed.
    The undirected policy is two real calls, not a new transactional C routine.
    """
    lines = ['/* main.c: llamador de la app; tad_grafo.c/h son los originales del libro. */',
             '#include "tad_grafo.h"', '#include <stdio.h>', '',
             '/* GrafoEstado: 0 OK, 1 MEMORIA, 2 NO_EXISTE, 3 PESO_NEGATIVO,',
             '   4 CICLO_NEGATIVO, 5 DESCONECTADO, 6 ARGUMENTO, 7 RANGO. */',
             'int main(void) {', '    Grafo g = grafo_crear();']
    directed = False
    for number, step in enumerate(history, 1):
        op = step['operation']; payload = step.get('payload', {}); index = str(number)
        block: list[str] = []
        if op in {'create_graph', 'clear_graph', 'generate_random_graph'}:
            if op == 'create_graph':
                directed = _directed(payload.get('directed', False))
            block = ['grafo_destruir(&g);', 'g = grafo_crear();']
            if op == 'generate_random_graph':
                from app.domain.graph.graph_commands import materialize_random_commands
                seed, commands = materialize_random_commands(payload, directed, require_seed=True)
                block.append(f'/* Preparación aleatoria de la app, semilla registrada: {seed}. */')
                for subindex, command in enumerate(commands, 1):
                    block += _insert_call(command['operation'], command['payload'], f'{index}_{subindex}', directed)
        elif op == 'insert_vertex':
            block = _insert_call(op, payload, index, directed)
        elif op == 'remove_vertex':
            block = [f'g = grafo_eliminar_vertice(g, {_integer(payload,"vertex")});']
        elif op in {'insert_edge', 'remove_edge'}:
            a, b = _integer(payload,'origin'), _integer(payload,'target')
            if op == 'insert_edge':
                block = _insert_call(op, payload, index, directed)
            else:
                block = [f'g = grafo_eliminar_arco(g, {a}, {b});']
                if not directed and a != b: block += [f'g = grafo_eliminar_arco(g, {b}, {a});']
        elif op in _ALGORITHMS:
            function, label = _ALGORITHMS[op]
            args = 'g'
            if op != 'run_kruskal': args += ', ' + _integer(payload,'start')
            if op in {'run_dijkstra','run_bellman_ford'}: args += ', ' + _integer(payload,'end')
            block = (_vertices_call if op in {'run_bfs','run_dfs'} else _arcs_call)(function,args,index,label)
        elif op == 'neighbors':
            block = _vertices_call('grafo_sucesores','g, '+_integer(payload,'vertex'),index,'Vecinos')
        elif op == 'edge_weight':
            block = [f'int costo_{index} = 0;',
                     f'int existe_{index} = grafo_costo_arco(g, {_integer(payload,"origin")}, {_integer(payload,"target")}, &costo_{index});',
                     f'if (existe_{index}) printf("Peso: %d\\n", costo_{index});',
                     'else printf("Peso: no encontrado; salida no escrita\\n");']
        elif op in {'exists_vertex','exists_edge'}:
            args = _integer(payload,'vertex') if op == 'exists_vertex' else _integer(payload,'origin')+', '+_integer(payload,'target')
            fn = 'grafo_existe_vertice' if op == 'exists_vertex' else 'grafo_existe_arco'
            block = [f'printf("{op}: %d\\n", {fn}(g, {args}));']
        elif op == 'list_vertices':
            block = ['printf("Vertices:");', 'for (ListaVertice it = grafo_vertices(g); it != NULL; it = it->sig) printf(" %d", it->dato);', 'printf("\\n");']
        elif op == 'list_edges':
            block = ['printf("Arcos:");', 'for (ListaArco it = grafo_arcos(g); it != NULL; it = it->sig) printf(" %d->%d(%d)", it->origen, it->destino, it->costo);', 'printf("\\n");']
        else:
            raise ValueError('Operación sin caller C del libro: '+op)
        lines += ['', f'    /* Llamada {number}: {op}. */'] + ['    '+line for line in block]
    lines += ['', '    grafo_destruir(&g);', '    return 0;', '}']
    return '\n'.join(lines)
