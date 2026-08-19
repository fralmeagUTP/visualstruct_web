"""Direct behavioral coverage for the graph domain transcription."""

from __future__ import annotations

from app.domain.graph.tad_grafo import (
    Conjunto,
    NodoA,
    NodoV,
    grafo_arcos,
    grafo_bellman_ford,
    grafo_bfs,
    grafo_cambiar_arcos,
    grafo_cambiar_vertices,
    grafo_costo_arco,
    grafo_crear,
    grafo_desmarcar,
    grafo_desmarcar_vertice,
    grafo_dfs,
    grafo_dfs_recursivo,
    grafo_dijkstra,
    grafo_eliminar_arco,
    grafo_eliminar_vertice,
    grafo_encontrar_conjunto,
    grafo_existe_arco,
    grafo_existe_vertice,
    grafo_grado_vertice,
    grafo_imprimir_arcos,
    grafo_imprimir_vertices,
    grafo_insertar_arco,
    grafo_insertar_vertice,
    grafo_kruskal,
    grafo_marcado_vertice,
    grafo_marcar_vertice,
    grafo_orden,
    grafo_predecesores,
    grafo_prim,
    grafo_sucesores,
    grafo_tamano,
    grafo_unir_conjuntos,
    grafo_vacio,
    grafo_vertices,
)


def _vertices(head: NodoV | None) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    while head is not None:
        result.append((head.dato, head.marcado))
        head = head.sig
    return result


def _arcs(head: NodoA | None) -> list[tuple[int, int, int]]:
    result: list[tuple[int, int, int]] = []
    while head is not None:
        result.append((head.origen, head.destino, head.costo))
        head = head.sig
    return result


def _weighted_graph():
    graph = grafo_crear()
    for origin, target, cost in [
        (1, 2, 4),
        (1, 3, 1),
        (3, 2, 2),
        (2, 4, 1),
        (3, 4, 8),
    ]:
        grafo_insertar_arco(graph, origin, target, cost)
    return graph


def test_graph_crud_linked_views_marks_and_replacement(capsys) -> None:
    graph = grafo_crear()
    assert grafo_vacio(graph) == 1
    grafo_insertar_vertice(graph, 1)
    grafo_insertar_vertice(graph, 1)  # duplicate is ignored
    grafo_insertar_arco(graph, 1, 2, 5)
    grafo_insertar_arco(graph, 1, 2, 7)  # existing edge is updated
    grafo_insertar_arco(graph, 2, 3, 9)

    assert grafo_vacio(graph) == 0
    assert grafo_orden(graph) == 3
    assert grafo_tamano(graph) == 2
    assert grafo_existe_vertice(graph, 2) == 1
    assert grafo_existe_vertice(graph, 99) == 0
    assert grafo_existe_arco(graph, 1, 2) == 1
    assert grafo_costo_arco(graph, 1, 2) == 7
    assert grafo_costo_arco(graph, 3, 1) == -1
    assert grafo_grado_vertice(graph, 1) == 1
    assert _vertices(grafo_sucesores(graph, 1)) == [(2, 0)]
    assert _vertices(grafo_predecesores(graph, 3)) == [(2, 0)]

    grafo_marcar_vertice(graph, 2)
    grafo_marcar_vertice(graph, 99)
    assert grafo_marcado_vertice(graph, 2) == 1
    assert _vertices(grafo_vertices(graph))[1] == (2, 1)
    grafo_desmarcar_vertice(graph, 2)
    grafo_desmarcar_vertice(graph, 99)
    grafo_marcar_vertice(graph, 1)
    grafo_marcar_vertice(graph, 2)
    grafo_desmarcar(graph)
    assert all(mark == 0 for _, mark in _vertices(grafo_vertices(graph)))

    grafo_imprimir_vertices(graph)
    grafo_imprimir_arcos(graph)
    printed = capsys.readouterr().out.splitlines()
    assert printed == ["1 2 3", "(1,2,7) (2,3,9)"]

    replacement_vertices = NodoV(3, NodoV(3, NodoV(4, marcado=1)))
    grafo_cambiar_vertices(graph, replacement_vertices)
    assert _vertices(grafo_vertices(graph)) == [(3, 0), (4, 1)]
    assert _arcs(grafo_arcos(graph)) == []

    replacement_arcs = NodoA(3, 4, 6, NodoA(3, 4, 6, NodoA(9, 4, 1)))
    grafo_cambiar_arcos(graph, replacement_arcs)
    assert _arcs(grafo_arcos(graph)) == [(3, 4, 6)]
    grafo_eliminar_arco(graph, 3, 4)
    grafo_eliminar_vertice(graph, 4)
    grafo_eliminar_vertice(graph, 99)
    assert _vertices(grafo_vertices(graph)) == [(3, 0)]


def test_graph_traversals_and_shortest_paths_cover_invalid_and_disconnected_cases() -> None:
    graph = _weighted_graph()
    assert _vertices(grafo_bfs(graph, 1)) == [(1, 0), (2, 0), (3, 0), (4, 0)]
    assert _vertices(grafo_dfs(graph, 1)) == [(1, 0), (2, 0), (4, 0), (3, 0)]
    assert grafo_bfs(graph, 99) is None
    assert grafo_dfs(graph, 99) is None

    manual = [None]
    grafo_dfs_recursivo(graph, 99, manual)
    assert manual == [None]

    assert _arcs(grafo_dijkstra(graph, 1, 4)) == [(1, 3, 1), (3, 2, 2), (2, 4, 1)]
    assert _arcs(grafo_bellman_ford(graph, 1, 4)) == [(1, 3, 1), (3, 2, 2), (2, 4, 1)]
    assert grafo_dijkstra(graph, 1, 99) is None
    assert grafo_bellman_ford(graph, 99, 1) is None
    assert grafo_dijkstra(graph, 1, 1) is None

    grafo_insertar_vertice(graph, 8)
    assert grafo_dijkstra(graph, 1, 8) is None
    assert grafo_bellman_ford(graph, 1, 8) is None

    negative_cycle = grafo_crear()
    grafo_insertar_arco(negative_cycle, 1, 2, -2)
    grafo_insertar_arco(negative_cycle, 2, 1, -2)
    assert grafo_bellman_ford(negative_cycle, 1, 2) is None


def test_graph_mst_and_disjoint_sets_cover_cycles_and_disconnected_vertices() -> None:
    graph = grafo_crear()
    for origin, target, cost in [
        (1, 2, 5),
        (2, 1, 3),  # cheaper reverse representation of same undirected edge
        (1, 3, 1),
        (2, 3, 2),
        (3, 4, 4),
    ]:
        grafo_insertar_arco(graph, origin, target, cost)

    assert _arcs(grafo_prim(graph, 1)) == [(1, 3, 1), (2, 3, 2), (3, 4, 4)]
    assert _arcs(grafo_kruskal(graph)) == [(1, 3, 1), (2, 3, 2), (3, 4, 4)]
    assert grafo_prim(graph, 99) is None

    grafo_insertar_vertice(graph, 9)
    assert len(_arcs(grafo_prim(graph, 1))) == 3

    sets = Conjunto(padre=[0, 0, 1, 3], n=4)
    assert grafo_encontrar_conjunto(sets, 2) == 0
    assert sets.padre[2] == 0
    grafo_unir_conjuntos(sets, 2, 3)
    assert grafo_encontrar_conjunto(sets, 3) == 0
    grafo_unir_conjuntos(sets, 0, 3)  # already joined
