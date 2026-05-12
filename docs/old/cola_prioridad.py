"""TAD Cola de Prioridad.

Implementada por composición sobre MonticuloBinario.
Permite conservar estabilidad en empates mediante un contador de llegada.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from .exceptions import EstructuraVaciaError
from .monticulo_binario import MonticuloBinario

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class _ItemPrioridad(Generic[T]):
    prioridad: int
    orden: int
    dato: T


class ColaPrioridad(Generic[T]):
    """Cola de prioridad estable. Menor prioridad numérica se atiende primero."""

    def __init__(self) -> None:
        self._orden = 0
        self._heap: MonticuloBinario[_ItemPrioridad[T]] = MonticuloBinario(
            prioridad=lambda item: (item.prioridad, item.orden),
            min_heap=True,
        )

    def encolar(self, dato: T, prioridad: int) -> None:
        """Inserta un dato con prioridad. Complejidad: O(log n)."""
        item = _ItemPrioridad(prioridad=prioridad, orden=self._orden, dato=dato)
        self._orden += 1
        self._heap.insertar(item)

    def desencolar(self) -> T:
        """Extrae el dato de mayor prioridad efectiva. Complejidad: O(log n)."""
        if self._heap.vacio():
            raise EstructuraVaciaError("La cola de prioridad está vacía.")
        return self._heap.extraer_raiz().dato

    def frente(self) -> T:
        """Retorna el dato de mayor prioridad sin extraerlo."""
        if self._heap.vacio():
            raise EstructuraVaciaError("La cola de prioridad está vacía.")
        return self._heap.raiz().dato

    def vacia(self) -> bool:
        return self._heap.vacio()

    def tamano(self) -> int:
        return self._heap.tamano()

    def limpiar(self) -> None:
        self._heap.limpiar()

    def a_lista(self) -> list[tuple[T, int]]:
        """Retorna pares (dato, prioridad) en el orden interno del heap."""
        return [(item.dato, item.prioridad) for item in self._heap.a_lista()]

    def __len__(self) -> int:
        return self.tamano()

    def __repr__(self) -> str:
        return f"ColaPrioridad({self.a_lista()!r})"
