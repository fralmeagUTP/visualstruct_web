"""TAD Pila.

Implementación por composición sobre ListaEnlazada.
El tope corresponde a la cabeza de la lista para lograr push y pop O(1).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Generic, TypeVar

from .lista_enlazada import ListaEnlazada

T = TypeVar("T")


class Pila(Generic[T]):
    """Pila LIFO genérica."""

    def __init__(self, valores: Iterator[T] | None = None) -> None:
        self._lista: ListaEnlazada[T] = ListaEnlazada()

        if valores is not None:
            for valor in valores:
                self.apilar(valor)

    def apilar(self, dato: T) -> None:
        """Inserta un dato en el tope. Complejidad: O(1)."""
        self._lista.insertar_inicio(dato)

    push = apilar

    def desapilar(self) -> T:
        """Elimina y retorna el tope. Complejidad: O(1)."""
        return self._lista.eliminar_inicio()

    pop = desapilar

    def cima(self) -> T:
        """Retorna el tope sin eliminarlo. Complejidad: O(1)."""
        return self._lista.primero()

    peek = cima

    def limpiar(self) -> None:
        """Elimina todos los elementos."""
        self._lista.limpiar()

    def vacia(self) -> bool:
        """Indica si la pila está vacía."""
        return self._lista.vacia()

    def tamano(self) -> int:
        """Retorna el número de elementos."""
        return self._lista.tamano()

    def a_lista(self) -> list[T]:
        """Retorna elementos desde el tope hasta el fondo."""
        return self._lista.a_lista()

    def __len__(self) -> int:
        return self.tamano()

    def __iter__(self) -> Iterator[T]:
        return iter(self._lista)

    def __repr__(self) -> str:
        return f"Pila({self.a_lista()!r})"
