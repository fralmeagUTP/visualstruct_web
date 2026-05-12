"""TAD Montículo Binario.

Montículo genérico basado en arreglo.
Se usa como componente interno de ColaPrioridad y algoritmos de grafos.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Generic, TypeVar

from .exceptions import EstructuraVaciaError

T = TypeVar("T")


class MonticuloBinario(Generic[T]):
    """Montículo binario configurable mediante una función de prioridad."""

    def __init__(
        self,
        valores: Iterator[T] | None = None,
        *,
        prioridad: Callable[[T], object] | None = None,
        min_heap: bool = True,
    ) -> None:
        self._datos: list[T] = []
        self._prioridad = prioridad if prioridad is not None else lambda x: x
        self._min_heap = min_heap

        if valores is not None:
            for valor in valores:
                self.insertar(valor)

    def _antes(self, a: T, b: T) -> bool:
        pa = self._prioridad(a)
        pb = self._prioridad(b)
        return pa < pb if self._min_heap else pa > pb

    def insertar(self, dato: T) -> None:
        """Inserta un dato. Complejidad: O(log n)."""
        self._datos.append(dato)
        self._subir(len(self._datos) - 1)

    def extraer_raiz(self) -> T:
        """Extrae la raíz del montículo. Complejidad: O(log n)."""
        if not self._datos:
            raise EstructuraVaciaError("El montículo está vacío.")

        raiz = self._datos[0]
        ultimo = self._datos.pop()

        if self._datos:
            self._datos[0] = ultimo
            self._bajar(0)

        return raiz

    def raiz(self) -> T:
        """Retorna la raíz sin eliminarla. Complejidad: O(1)."""
        if not self._datos:
            raise EstructuraVaciaError("El montículo está vacío.")
        return self._datos[0]

    def _subir(self, indice: int) -> None:
        while indice > 0:
            padre = (indice - 1) // 2

            if not self._antes(self._datos[indice], self._datos[padre]):
                break

            self._datos[indice], self._datos[padre] = self._datos[padre], self._datos[indice]
            indice = padre

    def _bajar(self, indice: int) -> None:
        n = len(self._datos)

        while True:
            izquierdo = 2 * indice + 1
            derecho = 2 * indice + 2
            seleccionado = indice

            if izquierdo < n and self._antes(self._datos[izquierdo], self._datos[seleccionado]):
                seleccionado = izquierdo

            if derecho < n and self._antes(self._datos[derecho], self._datos[seleccionado]):
                seleccionado = derecho

            if seleccionado == indice:
                break

            self._datos[indice], self._datos[seleccionado] = (
                self._datos[seleccionado],
                self._datos[indice],
            )
            indice = seleccionado

    def vacio(self) -> bool:
        return len(self._datos) == 0

    def tamano(self) -> int:
        return len(self._datos)

    def limpiar(self) -> None:
        self._datos.clear()

    def a_lista(self) -> list[T]:
        """Retorna la representación interna del arreglo."""
        return list(self._datos)

    def __len__(self) -> int:
        return len(self._datos)

    def __iter__(self) -> Iterator[T]:
        return iter(self._datos)

    def __repr__(self) -> str:
        tipo = "min" if self._min_heap else "max"
        return f"MonticuloBinario({self._datos!r}, tipo={tipo!r})"
