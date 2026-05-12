"""TAD Cola.

Implementación por composición sobre ListaEnlazada.
El frente corresponde a la cabeza y el final a la cola.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Generic, TypeVar

from .lista_enlazada import ListaEnlazada

T = TypeVar("T")


class Cola(Generic[T]):
    """Cola FIFO genérica."""

    def __init__(self, valores: Iterator[T] | None = None) -> None:
        self._lista: ListaEnlazada[T] = ListaEnlazada()

        if valores is not None:
            for valor in valores:
                self.encolar(valor)

    def encolar(self, dato: T) -> None:
        """Inserta un dato al final. Complejidad: O(1)."""
        self._lista.insertar_final(dato)

    enqueue = encolar

    def desencolar(self) -> T:
        """Elimina y retorna el dato del frente. Complejidad: O(1)."""
        return self._lista.eliminar_inicio()

    dequeue = desencolar

    def frente(self) -> T:
        """Retorna el dato del frente sin eliminarlo."""
        return self._lista.primero()

    def final(self) -> T:
        """Retorna el dato del final sin eliminarlo."""
        return self._lista.ultimo()

    def limpiar(self) -> None:
        """Elimina todos los elementos."""
        self._lista.limpiar()

    def vacia(self) -> bool:
        """Indica si la cola está vacía."""
        return self._lista.vacia()

    def tamano(self) -> int:
        """Retorna el número de elementos."""
        return self._lista.tamano()

    def a_lista(self) -> list[T]:
        """Retorna elementos desde el frente hasta el final."""
        return self._lista.a_lista()

    def __len__(self) -> int:
        return self.tamano()

    def __iter__(self) -> Iterator[T]:
        return iter(self._lista)

    def __repr__(self) -> str:
        return f"Cola({self.a_lista()!r})"
