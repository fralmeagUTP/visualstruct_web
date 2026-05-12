"""TAD Union-Find / Disjoint Set.

Usado internamente por Kruskal en el TAD Grafo.
"""

from __future__ import annotations

from typing import Generic, TypeVar

T = TypeVar("T")


class UnionFind(Generic[T]):
    """Estructura de conjuntos disjuntos con compresión de caminos y rango."""

    def __init__(self) -> None:
        self._padre: dict[T, T] = {}
        self._rango: dict[T, int] = {}

    def agregar(self, x: T) -> None:
        if x not in self._padre:
            self._padre[x] = x
            self._rango[x] = 0

    def buscar(self, x: T) -> T:
        self.agregar(x)

        if self._padre[x] != x:
            self._padre[x] = self.buscar(self._padre[x])

        return self._padre[x]

    find = buscar

    def unir(self, a: T, b: T) -> bool:
        """Une dos conjuntos. Retorna False si ya estaban unidos."""
        ra = self.buscar(a)
        rb = self.buscar(b)

        if ra == rb:
            return False

        if self._rango[ra] < self._rango[rb]:
            self._padre[ra] = rb
        elif self._rango[ra] > self._rango[rb]:
            self._padre[rb] = ra
        else:
            self._padre[rb] = ra
            self._rango[ra] += 1

        return True

    union = unir

    def conectados(self, a: T, b: T) -> bool:
        return self.buscar(a) == self.buscar(b)
