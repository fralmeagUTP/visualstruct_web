"""Transcripcion Python de `tad_grafo.h`."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import inf


@dataclass
class NodoV:
    dato: int
    sig: NodoV | None = None
    marcado: int = 0


ListaVertice = NodoV | None


@dataclass
class NodoA:
    origen: int
    destino: int
    costo: int
    sig: NodoA | None = None


ListaArco = NodoA | None


@dataclass
class Grafo:
    v: ListaVertice = None
    a: ListaArco = None
    _vertices: list[int] = field(default_factory=list)
    _arcos: list[tuple[int, int, int]] = field(default_factory=list)
    _marcas: dict[int, int] = field(default_factory=dict)


@dataclass
class Conjunto:
    padre: list[int]
    n: int


def grafo_crear() -> Grafo:
    return Grafo()


def grafo_insertar_vertice(g: Grafo, x: int) -> Grafo:
    if x not in g._vertices:
        g._vertices.append(x)
        g._marcas[x] = 0
        _sync_graph_lists(g)
    return g


def grafo_insertar_arco(g: Grafo, x: int, y: int, z: int) -> Grafo:
    if x not in g._vertices:
        grafo_insertar_vertice(g, x)
    if y not in g._vertices:
        grafo_insertar_vertice(g, y)
    for i, (ox, oy, _) in enumerate(g._arcos):
        if ox == x and oy == y:
            g._arcos[i] = (x, y, z)
            _sync_graph_lists(g)
            return g
    g._arcos.append((x, y, z))
    _sync_graph_lists(g)
    return g


def grafo_imprimir_vertices(g: Grafo) -> None:
    print(" ".join(str(v) for v in g._vertices))


def grafo_imprimir_arcos(g: Grafo) -> None:
    print(" ".join(f"({o},{d},{c})" for o, d, c in g._arcos))


def grafo_vertices(g: Grafo) -> ListaVertice:
    return _build_vertices_list(g._vertices, g._marcas)


def grafo_arcos(g: Grafo) -> ListaArco:
    return _build_arcs_list(g._arcos)


def grafo_cambiar_vertices(g: Grafo, k: ListaVertice) -> Grafo:
    nuevos: list[int] = []
    marcas: dict[int, int] = {}
    actual = k
    while actual is not None:
        if actual.dato not in nuevos:
            nuevos.append(actual.dato)
            marcas[actual.dato] = 1 if actual.marcado else 0
        actual = actual.sig
    g._vertices = nuevos
    g._marcas = {v: marcas.get(v, 0) for v in nuevos}
    g._arcos = [(o, d, c) for (o, d, c) in g._arcos if o in g._vertices and d in g._vertices]
    _sync_graph_lists(g)
    return g


def grafo_cambiar_arcos(g: Grafo, k: ListaArco) -> Grafo:
    nuevos: list[tuple[int, int, int]] = []
    actual = k
    while actual is not None:
        if actual.origen in g._vertices and actual.destino in g._vertices:
            tripleta = (actual.origen, actual.destino, actual.costo)
            if (actual.origen, actual.destino, actual.costo) not in nuevos:
                nuevos.append(tripleta)
        actual = actual.sig
    g._arcos = nuevos
    _sync_graph_lists(g)
    return g


def grafo_vacio(g: Grafo) -> int:
    return 1 if not g._vertices else 0


def grafo_existe_vertice(g: Grafo, x: int) -> int:
    return 1 if x in g._vertices else 0


def grafo_existe_arco(g: Grafo, x: int, y: int) -> int:
    return 1 if any(o == x and d == y for o, d, _ in g._arcos) else 0


def grafo_eliminar_vertice(g: Grafo, x: int) -> Grafo:
    if x in g._vertices:
        g._vertices.remove(x)
        g._marcas.pop(x, None)
        g._arcos = [(o, d, c) for (o, d, c) in g._arcos if o != x and d != x]
        _sync_graph_lists(g)
    return g


def grafo_eliminar_arco(g: Grafo, x: int, y: int) -> Grafo:
    g._arcos = [(o, d, c) for (o, d, c) in g._arcos if not (o == x and d == y)]
    _sync_graph_lists(g)
    return g


def grafo_costo_arco(g: Grafo, x: int, y: int) -> int:
    for o, d, c in g._arcos:
        if o == x and d == y:
            return c
    return -1


def grafo_orden(g: Grafo) -> int:
    return len(g._vertices)


def grafo_tamano(g: Grafo) -> int:
    return len(g._arcos)


def grafo_grado_vertice(g: Grafo, x: int) -> int:
    return sum(1 for o, _, _ in g._arcos if o == x)


def grafo_desmarcar_vertice(g: Grafo, x: int) -> Grafo:
    if x in g._marcas:
        g._marcas[x] = 0
        _sync_graph_lists(g)
    return g


def grafo_desmarcar(g: Grafo) -> Grafo:
    for v in g._vertices:
        g._marcas[v] = 0
    _sync_graph_lists(g)
    return g


def grafo_marcar_vertice(g: Grafo, x: int) -> Grafo:
    if x in g._marcas:
        g._marcas[x] = 1
        _sync_graph_lists(g)
    return g


def grafo_marcado_vertice(g: Grafo, x: int) -> int:
    return 1 if g._marcas.get(x, 0) else 0


def grafo_sucesores(g: Grafo, x: int) -> ListaVertice:
    suces = [d for o, d, _ in g._arcos if o == x]
    return _build_vertices_list(suces, g._marcas)


def grafo_predecesores(g: Grafo, x: int) -> ListaVertice:
    pred = [o for o, d, _ in g._arcos if d == x]
    return _build_vertices_list(pred, g._marcas)


def grafo_bfs(g: Grafo, inicio: int) -> ListaVertice:
    """Normal-allocation C parity: reset shared marks, mark on enqueue.

    The returned list owns new unmarked nodes, independently of graph marks.
    Negative vertex identifiers, including -1, remain valid data.
    """
    grafo_desmarcar(g)
    if inicio not in g._vertices:
        return None
    cola: list[int] = [inicio]
    grafo_marcar_vertice(g, inicio)
    orden: list[int] = []
    while cola:
        actual = cola.pop(0)
        orden.append(actual)
        for vecino in _vecinos(g, actual):
            if not grafo_marcado_vertice(g, vecino):
                cola.append(vecino)
                grafo_marcar_vertice(g, vecino)
    return _build_vertices_list(orden, {})


def grafo_dfs_recursivo(g: Grafo, actual: int, recorrido: list[ListaVertice]) -> None:
    """Follow normal-allocation C recursion, sharing graph marks and output head.

    The public wrapper validates the start; recursive successors belong to g.
    Returned nodes are new, unmarked and independent from graph vertex nodes.
    """
    if recorrido is None:
        return
    grafo_marcar_vertice(g, actual)
    _append_vertice_nodo(recorrido, NodoV(dato=actual, marcado=0))
    for vecino in _vecinos(g, actual):
        if not grafo_marcado_vertice(g, vecino):
            grafo_dfs_recursivo(g, vecino, recorrido)


def grafo_dfs(g: Grafo, inicio: int) -> ListaVertice:
    """Validate before resetting marks, as the actual C wrapper does."""
    if inicio not in g._vertices:
        return None
    grafo_desmarcar(g)
    recorrido_ref: list[ListaVertice] = [None]
    grafo_dfs_recursivo(g, inicio, recorrido_ref)
    return recorrido_ref[0]


def grafo_dijkstra(g: Grafo, inicio: int, llegada: int) -> ListaArco:
    from .integer_algorithms import dijkstra
    if inicio not in g._vertices or llegada not in g._vertices or any(w < 0 for _, _, w in g._arcos):
        return None
    _, prev = dijkstra(g, inicio)
    return _ruta_arcos(g, prev, inicio, llegada)


def grafo_bellman_ford(g: Grafo, inicio: int, llegada: int) -> ListaArco:
    from .integer_algorithms import bellman_ford
    if inicio not in g._vertices or llegada not in g._vertices:
        return None
    _, prev, negative_cycle = bellman_ford(g, inicio)
    if negative_cycle:
        return None
    return _ruta_arcos(g, prev, inicio, llegada)


def grafo_prim(g: Grafo, inicio: int) -> ListaArco:
    from .integer_algorithms import prim
    if inicio not in g._vertices:
        return None
    arcs, _ = prim(g, inicio)
    return _build_arcs_list(arcs)


def grafo_encontrar_conjunto(c: Conjunto, x: int) -> int:
    if c.padre[x] != x:
        c.padre[x] = grafo_encontrar_conjunto(c, c.padre[x])
    return c.padre[x]


def grafo_unir_conjuntos(c: Conjunto, x: int, y: int) -> None:
    rx = grafo_encontrar_conjunto(c, x)
    ry = grafo_encontrar_conjunto(c, y)
    if rx != ry:
        c.padre[ry] = rx


def grafo_kruskal(g: Grafo) -> ListaArco:
    from .integer_algorithms import kruskal
    arcs, _ = kruskal(g)
    return _build_arcs_list(arcs)


def _sync_graph_lists(g: Grafo) -> None:
    g.v = grafo_vertices(g)
    g.a = grafo_arcos(g)


def _build_vertices_list(vertices: list[int], marcas: dict[int, int]) -> ListaVertice:
    head: ListaVertice = None
    tail: ListaVertice = None
    for vertice in vertices:
        nodo = NodoV(dato=vertice, marcado=1 if marcas.get(vertice, 0) else 0)
        if head is None:
            head = nodo
            tail = nodo
        else:
            tail.sig = nodo
            tail = nodo
    return head


def _build_arcs_list(arcos: list[tuple[int, int, int]]) -> ListaArco:
    head: ListaArco = None
    tail: ListaArco = None
    for o, d, c in arcos:
        nodo = NodoA(origen=o, destino=d, costo=c)
        if head is None:
            head = nodo
            tail = nodo
        else:
            tail.sig = nodo
            tail = nodo
    return head


def _append_vertice_nodo(recorrido: list[ListaVertice], nodo: NodoV) -> None:
    if recorrido[0] is None:
        recorrido[0] = nodo
        return
    actual = recorrido[0]
    while actual.sig is not None:
        actual = actual.sig
    actual.sig = nodo


def _vecinos(g: Grafo, vertice: int) -> list[int]:
    return [d for o, d, _ in g._arcos if o == vertice]


def _vecinos_con_peso(g: Grafo, vertice: int) -> list[tuple[int, int]]:
    return [(d, c) for o, d, c in g._arcos if o == vertice]


def _ruta_arcos(g: Grafo, prev: dict[int, int | None], inicio: int, llegada: int) -> ListaArco:
    if inicio == llegada:
        return None
    camino_vertices: list[int] = []
    actual: int | None = llegada
    while actual is not None:
        camino_vertices.append(actual)
        if actual == inicio:
            break
        actual = prev.get(actual)
    if not camino_vertices or camino_vertices[-1] != inicio:
        return None
    camino_vertices.reverse()
    arcos: list[tuple[int, int, int]] = []
    for i in range(len(camino_vertices) - 1):
        o = camino_vertices[i]
        d = camino_vertices[i + 1]
        arcos.append((o, d, grafo_costo_arco(g, o, d)))
    return _build_arcs_list(arcos)


def _aristas_no_dirigidas(g: Grafo) -> list[tuple[int, int, int]]:
    mejores: dict[tuple[int, int], int] = {}
    for o, d, c in g._arcos:
        a, b = (o, d) if o <= d else (d, o)
        key = (a, b)
        if key not in mejores or c < mejores[key]:
            mejores[key] = c
    return [(a, b, c) for (a, b), c in mejores.items()]

