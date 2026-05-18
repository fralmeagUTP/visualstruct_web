"""Wrappers de alto nivel sobre el nuevo `tad_grafo`.

Este modulo reemplaza al wrapper legacy `grafo.py` para que el dominio
de grafos use solo el TAD nuevo.
"""

from __future__ import annotations

from math import inf
from typing import Generic, Hashable, TypeVar

from .exceptions import PesoNegativoError, VerticeNoEncontradoError
from .tad_grafo import Grafo as GrafoTAD
from .tad_grafo import grafo_bfs, grafo_crear, grafo_dfs, grafo_eliminar_arco, grafo_eliminar_vertice, grafo_existe_arco, grafo_existe_vertice, grafo_insertar_arco, grafo_insertar_vertice
from .union_find import UnionFind

V = TypeVar("V", bound=Hashable)


class Grafo(Generic[V]):
    """Grafo dirigido o no dirigido, ponderado o no ponderado."""

    def __init__(self, dirigido: bool = False) -> None:
        self.dirigido = dirigido
        self._g: GrafoTAD = grafo_crear()

    def insertar_vertice(self, vertice: V) -> None:
        grafo_insertar_vertice(self._g, int(vertice))

    def eliminar_vertice(self, vertice: V) -> None:
        value = int(vertice)
        if not grafo_existe_vertice(self._g, value):
            raise VerticeNoEncontradoError(f"El vertice {vertice!r} no existe.")
        grafo_eliminar_vertice(self._g, value)

    def insertar_arista(self, origen: V, destino: V, peso: float = 1) -> None:
        o = int(origen)
        d = int(destino)
        w = float(peso)
        grafo_insertar_arco(self._g, o, d, int(w))
        if not self.dirigido and o != d:
            grafo_insertar_arco(self._g, d, o, int(w))

    def eliminar_arista(self, origen: V, destino: V) -> None:
        o = int(origen)
        d = int(destino)
        grafo_eliminar_arco(self._g, o, d)
        if not self.dirigido and o != d:
            grafo_eliminar_arco(self._g, d, o)

    def existe_vertice(self, vertice: V) -> bool:
        return bool(grafo_existe_vertice(self._g, int(vertice)))

    def existe_arista(self, origen: V, destino: V) -> bool:
        return bool(grafo_existe_arco(self._g, int(origen), int(destino)))

    def vertices(self) -> list[V]:
        return list(self._g._vertices)  # type: ignore[return-value]

    def vecinos(self, vertice: V) -> list[V]:
        self._validar_vertice(vertice)
        v = int(vertice)
        return [destino for (origen, destino, _) in self._g._arcos if origen == v]  # type: ignore[return-value]

    def peso(self, origen: V, destino: V) -> float:
        self._validar_vertice(origen)
        o = int(origen)
        d = int(destino)
        for ao, ad, aw in self._g._arcos:
            if ao == o and ad == d:
                return float(aw)
        raise KeyError(f"La arista {origen!r}->{destino!r} no existe.")

    def bfs(self, inicio: V) -> list[V]:
        self._validar_vertice(inicio)
        lista = grafo_bfs(self._g, int(inicio))
        return self._vertices_from_lista(lista)  # type: ignore[return-value]

    def dfs(self, inicio: V) -> list[V]:
        self._validar_vertice(inicio)
        lista = grafo_dfs(self._g, int(inicio))
        return self._vertices_from_lista(lista)  # type: ignore[return-value]

    def dijkstra(self, inicio: V) -> tuple[dict[V, float], dict[V, V | None]]:
        self._validar_vertice(inicio)
        self._validar_pesos_no_negativos()
        start = int(inicio)

        dist: dict[int, float] = {v: inf for v in self._g._vertices}
        previo: dict[int, int | None] = {v: None for v in self._g._vertices}
        dist[start] = 0.0
        pendientes: set[int] = set(self._g._vertices)

        while pendientes:
            actual = min(pendientes, key=lambda x: dist[x])
            pendientes.remove(actual)
            if dist[actual] == inf:
                break
            for vecino, peso in self._vecinos_con_peso(actual):
                nueva = dist[actual] + peso
                if nueva < dist[vecino]:
                    dist[vecino] = nueva
                    previo[vecino] = actual

        return dist, previo  # type: ignore[return-value]

    def bellman_ford(self, inicio: V) -> tuple[dict[V, float], dict[V, V | None], bool]:
        self._validar_vertice(inicio)
        start = int(inicio)

        dist: dict[int, float] = {v: inf for v in self._g._vertices}
        previo: dict[int, int | None] = {v: None for v in self._g._vertices}
        dist[start] = 0.0
        # Bellman-Ford debe relajar aristas dirigidas; para grafo no dirigido
        # el TAD mantiene ambos sentidos en `_g._arcos`.
        aristas = [(int(o), int(d), float(c)) for o, d, c in self._g._arcos]

        for _ in range(len(self._g._vertices) - 1):
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
        return dist, previo, ciclo_negativo  # type: ignore[return-value]

    def prim(self, inicio: V | None = None) -> tuple[list[tuple[V, V, float]], float]:
        if self.dirigido:
            raise ValueError("Prim requiere un grafo no dirigido.")
        if not self._g._vertices:
            return [], 0.0

        start = int(inicio) if inicio is not None else self._g._vertices[0]
        self._validar_vertice(start)

        visitados = {start}
        mst: list[tuple[int, int, float]] = []
        total = 0.0
        aristas = self._aristas_no_dirigidas()

        while len(visitados) < len(self._g._vertices):
            candidato: tuple[int, int, float] | None = None
            for o, d, c in aristas:
                cruza = (o in visitados and d not in visitados) or (d in visitados and o not in visitados)
                if not cruza:
                    continue
                if candidato is None or c < candidato[2]:
                    candidato = (o, d, c)
            if candidato is None:
                break
            o, d, c = candidato
            mst.append(candidato)
            total += c
            visitados.add(o)
            visitados.add(d)

        return mst, total  # type: ignore[return-value]

    def kruskal(self) -> tuple[list[tuple[V, V, float]], float]:
        if self.dirigido:
            raise ValueError("Kruskal requiere un grafo no dirigido.")

        uf: UnionFind[int] = UnionFind()
        mst: list[tuple[int, int, float]] = []
        total = 0.0

        for vertice in self._g._vertices:
            uf.agregar(vertice)

        for origen, destino, peso in sorted(self._aristas_no_dirigidas(), key=lambda item: item[2]):
            if uf.unir(origen, destino):
                mst.append((origen, destino, peso))
                total += peso

        return mst, total  # type: ignore[return-value]

    def aristas(self) -> list[tuple[V, V, float]]:
        if self.dirigido:
            return [(o, d, float(c)) for o, d, c in self._g._arcos]  # type: ignore[return-value]
        vistas: set[frozenset[int]] = set()
        resultado: list[tuple[int, int, float]] = []
        for o, d, c in self._g._arcos:
            clave = frozenset((o, d))
            if clave in vistas:
                continue
            vistas.add(clave)
            resultado.append((o, d, float(c)))
        return resultado  # type: ignore[return-value]

    def cantidad_vertices(self) -> int:
        return len(self._g._vertices)

    def cantidad_aristas(self) -> int:
        return len(self.aristas())

    def _validar_vertice(self, vertice: V) -> None:
        value = int(vertice)
        if not grafo_existe_vertice(self._g, value):
            raise VerticeNoEncontradoError(f"El vertice {vertice!r} no existe.")

    def _validar_pesos_no_negativos(self) -> None:
        for origen, destino, peso in self._g._arcos:
            if peso < 0:
                raise PesoNegativoError(
                    f"Dijkstra no admite peso negativo: {origen!r}->{destino!r} = {peso}."
                )

    @staticmethod
    def _vertices_from_lista(lista: object) -> list[int]:
        out: list[int] = []
        actual = lista
        while actual is not None:
            out.append(int(actual.dato))
            actual = actual.sig
        return out

    def _vecinos_con_peso(self, origen: int) -> list[tuple[int, float]]:
        return [(destino, float(peso)) for o, destino, peso in self._g._arcos if o == origen]

    def _aristas_no_dirigidas(self) -> list[tuple[int, int, float]]:
        return [(int(o), int(d), float(c)) for o, d, c in self.aristas()]

    def __len__(self) -> int:
        return self.cantidad_vertices()

    def __repr__(self) -> str:
        return f"Grafo(dirigido={self.dirigido}, aristas={self.aristas()!r})"
