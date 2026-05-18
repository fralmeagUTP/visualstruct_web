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
    if inicio not in g._vertices:
        return None
    visitados: set[int] = set()
    cola: list[int] = [inicio]
    orden: list[int] = []
    while cola:
        actual = cola.pop(0)
        if actual in visitados:
            continue
        visitados.add(actual)
        orden.append(actual)
        for vecino in _vecinos(g, actual):
            if vecino not in visitados:
                cola.append(vecino)
    return _build_vertices_list(orden, g._marcas)


def grafo_dfs_recursivo(g: Grafo, actual: int, recorrido: list[ListaVertice]) -> None:
    if "_dfs_visitados" not in g.__dict__:
        g.__dict__["_dfs_visitados"] = set()
    visitados: set[int] = g.__dict__["_dfs_visitados"]
    if actual in visitados or actual not in g._vertices:
        return
    visitados.add(actual)
    _append_vertice_nodo(recorrido, NodoV(dato=actual, marcado=g._marcas.get(actual, 0)))
    for vecino in _vecinos(g, actual):
        grafo_dfs_recursivo(g, vecino, recorrido)


def grafo_dfs(g: Grafo, inicio: int) -> ListaVertice:
    if inicio not in g._vertices:
        return None
    g.__dict__["_dfs_visitados"] = set()
    recorrido_ref: list[ListaVertice] = [None]
    grafo_dfs_recursivo(g, inicio, recorrido_ref)
    g.__dict__.pop("_dfs_visitados", None)
    return recorrido_ref[0]


def grafo_dijkstra(g: Grafo, inicio: int, llegada: int) -> ListaArco:
    if inicio not in g._vertices or llegada not in g._vertices:
        return None
    dist: dict[int, float] = {v: inf for v in g._vertices}
    prev: dict[int, int | None] = {v: None for v in g._vertices}
    dist[inicio] = 0.0
    pendientes = set(g._vertices)
    while pendientes:
        u = min(pendientes, key=lambda v: dist[v])
        pendientes.remove(u)
        if dist[u] == inf:
            break
        if u == llegada:
            break
        for v, costo in _vecinos_con_peso(g, u):
            alt = dist[u] + costo
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
    return _ruta_arcos(g, prev, inicio, llegada)


def grafo_bellman_ford(g: Grafo, inicio: int, llegada: int) -> ListaArco:
    if inicio not in g._vertices or llegada not in g._vertices:
        return None
    dist: dict[int, float] = {v: inf for v in g._vertices}
    prev: dict[int, int | None] = {v: None for v in g._vertices}
    dist[inicio] = 0.0
    for _ in range(max(0, len(g._vertices) - 1)):
        hubo_cambio = False
        for o, d, c in g._arcos:
            if dist[o] != inf and dist[o] + c < dist[d]:
                dist[d] = dist[o] + c
                prev[d] = o
                hubo_cambio = True
        if not hubo_cambio:
            break
    for o, d, c in g._arcos:
        if dist[o] != inf and dist[o] + c < dist[d]:
            return None
    return _ruta_arcos(g, prev, inicio, llegada)


def grafo_prim(g: Grafo, inicio: int) -> ListaArco:
    if inicio not in g._vertices:
        return None
    visitados = {inicio}
    mst: list[tuple[int, int, int]] = []
    aristas = _aristas_no_dirigidas(g)
    while len(visitados) < len(g._vertices):
        candidato: tuple[int, int, int] | None = None
        for o, d, c in aristas:
            cruza = (o in visitados and d not in visitados) or (d in visitados and o not in visitados)
            if not cruza:
                continue
            if candidato is None or c < candidato[2]:
                candidato = (o, d, c)
        if candidato is None:
            break
        o, d, c = candidato
        mst.append((o, d, c))
        visitados.add(o)
        visitados.add(d)
    return _build_arcs_list(mst)


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
    vertices = list(g._vertices)
    indice = {v: i for i, v in enumerate(vertices)}
    conjunto = Conjunto(padre=list(range(len(vertices))), n=len(vertices))
    mst: list[tuple[int, int, int]] = []
    for o, d, c in sorted(_aristas_no_dirigidas(g), key=lambda e: e[2]):
        ro = grafo_encontrar_conjunto(conjunto, indice[o])
        rd = grafo_encontrar_conjunto(conjunto, indice[d])
        if ro != rd:
            mst.append((o, d, c))
            grafo_unir_conjuntos(conjunto, ro, rd)
    return _build_arcs_list(mst)


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

