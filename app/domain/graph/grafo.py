"""TAD Grafo.

Implementación con diccionario de adyacencia.
Reutiliza:
- Cola para BFS
- Pila para DFS iterativo
- ColaPrioridad para Dijkstra y Prim
- UnionFind para Kruskal
"""

from __future__ import annotations

from math import inf
from typing import Generic, Hashable, TypeVar

from .cola import Cola
from .cola_prioridad import ColaPrioridad
from .exceptions import PesoNegativoError, VerticeNoEncontradoError
from .pila import Pila
from .union_find import UnionFind

V = TypeVar("V", bound=Hashable)


class Grafo(Generic[V]):
    """Grafo dirigido o no dirigido, ponderado o no ponderado."""

    def __init__(self, dirigido: bool = False) -> None:
        self.dirigido = dirigido
        self._ady: dict[V, dict[V, float]] = {}

    def insertar_vertice(self, vertice: V) -> None:
        self._ady.setdefault(vertice, {})

    def eliminar_vertice(self, vertice: V) -> None:
        if vertice not in self._ady:
            raise VerticeNoEncontradoError(f"El vértice {vertice!r} no existe.")

        del self._ady[vertice]

        for vecinos in self._ady.values():
            vecinos.pop(vertice, None)

    def insertar_arista(self, origen: V, destino: V, peso: float = 1) -> None:
        self.insertar_vertice(origen)
        self.insertar_vertice(destino)

        self._ady[origen][destino] = peso

        if not self.dirigido:
            self._ady[destino][origen] = peso

    def eliminar_arista(self, origen: V, destino: V) -> None:
        if origen not in self._ady or destino not in self._ady[origen]:
            return

        del self._ady[origen][destino]

        if not self.dirigido and destino in self._ady:
            self._ady[destino].pop(origen, None)

    def existe_vertice(self, vertice: V) -> bool:
        return vertice in self._ady

    def existe_arista(self, origen: V, destino: V) -> bool:
        return origen in self._ady and destino in self._ady[origen]

    def vertices(self) -> list[V]:
        return list(self._ady.keys())

    def vecinos(self, vertice: V) -> list[V]:
        self._validar_vertice(vertice)
        return list(self._ady[vertice].keys())

    def peso(self, origen: V, destino: V) -> float:
        self._validar_vertice(origen)
        return self._ady[origen][destino]

    def bfs(self, inicio: V) -> list[V]:
        """Recorrido en anchura reutilizando Cola."""
        self._validar_vertice(inicio)

        visitados = {inicio}
        orden: list[V] = []
        cola: Cola[V] = Cola()
        cola.encolar(inicio)

        while not cola.vacia():
            actual = cola.desencolar()
            orden.append(actual)

            for vecino in self._ady[actual]:
                if vecino not in visitados:
                    visitados.add(vecino)
                    cola.encolar(vecino)

        return orden

    def dfs(self, inicio: V) -> list[V]:
        """Recorrido en profundidad iterativo reutilizando Pila."""
        self._validar_vertice(inicio)

        visitados: set[V] = set()
        orden: list[V] = []
        pila: Pila[V] = Pila()
        pila.apilar(inicio)

        while not pila.vacia():
            actual = pila.desapilar()

            if actual in visitados:
                continue

            visitados.add(actual)
            orden.append(actual)

            for vecino in reversed(list(self._ady[actual].keys())):
                if vecino not in visitados:
                    pila.apilar(vecino)

        return orden

    def dijkstra(self, inicio: V) -> tuple[dict[V, float], dict[V, V | None]]:
        """Caminos mínimos con pesos no negativos, reutilizando ColaPrioridad."""
        self._validar_vertice(inicio)
        self._validar_pesos_no_negativos()

        dist = {v: inf for v in self._ady}
        previo: dict[V, V | None] = {v: None for v in self._ady}
        dist[inicio] = 0

        cola: ColaPrioridad[V] = ColaPrioridad()
        cola.encolar(inicio, 0)

        while not cola.vacia():
            actual = cola.desencolar()

            for vecino, peso in self._ady[actual].items():
                nueva = dist[actual] + peso

                if nueva < dist[vecino]:
                    dist[vecino] = nueva
                    previo[vecino] = actual
                    cola.encolar(vecino, int(nueva))

        return dist, previo

    def bellman_ford(self, inicio: V) -> tuple[dict[V, float], dict[V, V | None], bool]:
        """Caminos mínimos con posible peso negativo. Retorna si hay ciclo negativo."""
        self._validar_vertice(inicio)

        dist = {v: inf for v in self._ady}
        previo: dict[V, V | None] = {v: None for v in self._ady}
        dist[inicio] = 0
        aristas = self.aristas()

        for _ in range(len(self._ady) - 1):
            cambio = False

            for origen, destino, peso in aristas:
                if dist[origen] != inf and dist[origen] + peso < dist[destino]:
                    dist[destino] = dist[origen] + peso
                    previo[destino] = origen
                    cambio = True

            if not cambio:
                break

        ciclo_negativo = any(
            dist[origen] != inf and dist[origen] + peso < dist[destino]
            for origen, destino, peso in aristas
        )

        return dist, previo, ciclo_negativo

    def prim(self, inicio: V | None = None) -> tuple[list[tuple[V, V, float]], float]:
        """Árbol de expansión mínima con Prim, reutilizando ColaPrioridad."""
        if self.dirigido:
            raise ValueError("Prim requiere un grafo no dirigido.")

        if not self._ady:
            return [], 0

        if inicio is None:
            inicio = next(iter(self._ady))

        self._validar_vertice(inicio)

        visitados = {inicio}
        mst: list[tuple[V, V, float]] = []
        total = 0.0
        cola: ColaPrioridad[tuple[V, V, float]] = ColaPrioridad()

        for destino, peso in self._ady[inicio].items():
            cola.encolar((inicio, destino, peso), int(peso))

        while not cola.vacia() and len(visitados) < len(self._ady):
            origen, destino, peso = cola.desencolar()

            if destino in visitados:
                continue

            visitados.add(destino)
            mst.append((origen, destino, peso))
            total += peso

            for vecino, peso_vecino in self._ady[destino].items():
                if vecino not in visitados:
                    cola.encolar((destino, vecino, peso_vecino), int(peso_vecino))

        return mst, total

    def kruskal(self) -> tuple[list[tuple[V, V, float]], float]:
        """Árbol de expansión mínima con Kruskal, reutilizando UnionFind."""
        if self.dirigido:
            raise ValueError("Kruskal requiere un grafo no dirigido.")

        uf: UnionFind[V] = UnionFind()
        mst: list[tuple[V, V, float]] = []
        total = 0.0

        for vertice in self._ady:
            uf.agregar(vertice)

        for origen, destino, peso in sorted(self.aristas(), key=lambda item: item[2]):
            if uf.unir(origen, destino):
                mst.append((origen, destino, peso))
                total += peso

        return mst, total

    def aristas(self) -> list[tuple[V, V, float]]:
        """Retorna aristas. En no dirigido evita duplicados."""
        resultado: list[tuple[V, V, float]] = []
        vistas: set[frozenset[V]] = set()

        for origen, vecinos in self._ady.items():
            for destino, peso in vecinos.items():
                if not self.dirigido:
                    clave = frozenset((origen, destino))
                    if clave in vistas:
                        continue
                    vistas.add(clave)

                resultado.append((origen, destino, peso))

        return resultado

    def cantidad_vertices(self) -> int:
        return len(self._ady)

    def cantidad_aristas(self) -> int:
        return len(self.aristas())

    def _validar_vertice(self, vertice: V) -> None:
        if vertice not in self._ady:
            raise VerticeNoEncontradoError(f"El vértice {vertice!r} no existe.")

    def _validar_pesos_no_negativos(self) -> None:
        for origen, destino, peso in self.aristas():
            if peso < 0:
                raise PesoNegativoError(
                    f"Dijkstra no admite peso negativo: {origen!r}->{destino!r} = {peso}."
                )

    def __len__(self) -> int:
        return self.cantidad_vertices()

    def __repr__(self) -> str:
        return f"Grafo(dirigido={self.dirigido}, aristas={self.aristas()!r})"
