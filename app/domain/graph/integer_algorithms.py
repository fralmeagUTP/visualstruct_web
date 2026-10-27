"""Integer algorithms in the stored-list order of the downloaded C graph.

Python topology stays in insertion order for existing UI/BFS/DFS contracts.
These four algorithms explicitly reverse vertices/arcs to reproduce C heads.
"""
from decimal import Decimal, InvalidOperation
from math import inf

INT_MIN = -2147483648
INT_MAX = 2147483647
LLONG_MIN = -(1 << 63)
LLONG_MAX = (1 << 63) - 1


def integer_weight(value):
    try:
        if isinstance(value, bool):
            raise ValueError
        number = Decimal(str(value))
        if not number.is_finite() or number != number.to_integral_value():
            raise ValueError
        if not INT_MIN <= number <= INT_MAX:
            raise ValueError
        return int(number)
    except (InvalidOperation, ValueError, TypeError) as error:
        raise ValueError("El peso debe ser un entero representable por el TAD C (INT_MIN..INT_MAX).") from error


def dijkstra(g, start):
    if any(w < 0 for _, _, w in g._arcos):
        raise ValueError("Dijkstra requiere pesos no negativos, incluidos los arcos desconectados.")
    vertices = list(reversed(g._vertices))
    dist = {v: inf for v in vertices}
    prev = {v: None for v in vertices}
    dist[start] = 0
    visited = set()
    for _ in vertices:
        u = None
        minimum = INT_MAX
        for v in vertices:
            if v not in visited and dist[v] < minimum:
                minimum, u = dist[v], v
        if u is None:
            break
        visited.add(u)
        for origin, v, weight in g._arcos:
            if origin == u and v not in visited and weight >= 0 and dist[u] <= INT_MAX - weight:
                candidate = dist[u] + weight
                if candidate < INT_MAX and candidate < dist[v]:
                    dist[v], prev[v] = candidate, u
    return dist, prev


def bellman_ford(g, start):
    vertices = list(reversed(g._vertices))
    arcs = list(reversed(g._arcos))
    dist = {v: inf for v in vertices}
    prev = {v: None for v in vertices}
    dist[start] = 0
    lower = (len(vertices) - 1) * INT_MIN
    for _ in range(max(0, len(vertices) - 1)):
        for u, v, weight in arcs:
            if dist[u] == inf:
                continue
            candidate = dist[u] + weight
            if not LLONG_MIN <= candidate <= LLONG_MAX:
                raise ValueError("Distancia fuera del rango interno.")
            if candidate < lower:
                return dist, prev, True
            if candidate < dist[v]:
                dist[v], prev[v] = candidate, u
    for u, v, weight in arcs:
        if dist[u] == inf:
            continue
        candidate = dist[u] + weight
        if not LLONG_MIN <= candidate <= LLONG_MAX:
            raise ValueError("Distancia fuera del rango interno.")
        if candidate < lower or candidate < dist[v]:
            return dist, prev, True
    return dist, prev, False


def prim(g, start):
    vertices = list(reversed(g._vertices))
    costs = {start: 0}
    parents = {v: None for v in vertices}
    visited = set()
    for _ in vertices:
        u = None
        for v in vertices:
            if v not in visited and v in costs and (u is None or costs[v] < costs[u]):
                u = v
        if u is None:
            u = next(v for v in vertices if v not in visited)
            costs[u] = 0
        visited.add(u)
        for origin, v, weight in g._arcos:
            if origin == u and v not in visited and (v not in costs or weight < costs[v]):
                costs[v], parents[v] = weight, u
    result = []
    for v in vertices:
        if parents[v] is not None:
            result.insert(0, (parents[v], v, costs[v]))
    return result, sum(weight for _, _, weight in result)


def kruskal(g):
    vertices = list(reversed(g._vertices))
    parents = {v: v for v in vertices}
    def root(v):
        while parents[v] != v:
            v = parents[v]
        return v
    result = []
    # Stable ordering preserves every raw arc, including mirror orientations.
    for u, v, weight in sorted(reversed(g._arcos), key=lambda arc: arc[2]):
        ru, rv = root(u), root(v)
        if ru != rv:
            parents[rv] = ru
            result.insert(0, (u, v, weight))
    return result, sum(weight for _, _, weight in result)
