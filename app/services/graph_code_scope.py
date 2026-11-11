"""Canonical source ranges for the graph operation readers."""
from __future__ import annotations

from functools import lru_cache
from app.domain.graph.book_c_subset import Program
from app.domain.graph.book_source import canonical_source


@lru_cache(maxsize=1)
def graph_algorithm_code_scopes() -> dict[str, dict]:
    """Resolve transitive C calls without changing the interpreter's line IDs.

    Result cleanup belongs to the caller of an owned result and is included
    explicitly, just as it is in the recorded execution.
    """
    source = canonical_source()
    program = Program(source)
    ranges = {}
    calls = {}
    for name, function in program.functions.items():
        start, end = function['token'].pos, function['body'].end
        ranges[name] = [function['token'].line, source.count('\n', 0, end)]
        tokens = [token for token in program.tokens if start <= token.pos < end]
        calls[name] = {token.text for token, following in zip(tokens, tokens[1:])
                       if following.text == '(' and token.text in program.functions}
    scopes = {}
    entries = {**{'run_' + name: 'grafo_' + name for name in
                  ('bfs', 'dfs', 'dijkstra', 'bellman_ford', 'prim', 'kruskal')},
               'insert_vertex': 'grafo_insertar_vertice', 'remove_vertex': 'grafo_eliminar_vertice',
               'insert_edge': 'grafo_insertar_arco', 'remove_edge': 'grafo_eliminar_arco'}
    for operation, entry in entries.items():
        pending, selected = [entry], set()
        if operation.startswith('run_'):
            pending.append('grafo_liberar_vertices' if operation in ('run_bfs', 'run_dfs') else 'grafo_liberar_arcos')
        while pending:
            name = pending.pop()
            if name not in selected:
                selected.add(name)
                pending.extend(calls[name] - selected)
        ordered = sorted(selected, key=lambda name: ranges[name][0])
        scopes[operation] = {'functions': ordered, 'ranges': [ranges[name] for name in ordered]}
    return scopes
