"""TAD Sublista.

Estructura tipo lista de padres, donde cada padre posee una lista de hijos.
Reutiliza ListaEnlazada para la lista principal y para cada sublista.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from .exceptions import ElementoNoEncontradoError
from .lista_enlazada import ListaEnlazada

T = TypeVar("T")


@dataclass(slots=True)
class NodoPadre(Generic[T]):
    dato: T
    hijos: ListaEnlazada[T]


class Sublista(Generic[T]):
    """Lista de padres con sublistas de hijos."""

    def __init__(self) -> None:
        self._padres: ListaEnlazada[NodoPadre[T]] = ListaEnlazada()

    def insertar_padre(self, dato: T) -> None:
        self._padres.insertar_final(NodoPadre(dato=dato, hijos=ListaEnlazada()))

    def buscar_padre(self, dato: T) -> NodoPadre[T] | None:
        for padre in self._padres:
            if padre.dato == dato:
                return padre
        return None

    def insertar_hijo(self, padre: T, hijo: T) -> None:
        nodo_padre = self.buscar_padre(padre)
        if nodo_padre is None:
            raise ElementoNoEncontradoError(f"El padre {padre!r} no existe.")
        nodo_padre.hijos.insertar_final(hijo)

    def eliminar_padre(self, dato: T) -> bool:
        for pos, padre in enumerate(self._padres):
            if padre.dato == dato:
                self._padres.eliminar_posicion(pos)
                return True
        return False

    def hijos_de(self, padre: T) -> list[T]:
        nodo_padre = self.buscar_padre(padre)
        if nodo_padre is None:
            raise ElementoNoEncontradoError(f"El padre {padre!r} no existe.")
        return nodo_padre.hijos.a_lista()

    def a_diccionario(self) -> dict[T, list[T]]:
        return {padre.dato: padre.hijos.a_lista() for padre in self._padres}

    def limpiar(self) -> None:
        self._padres.limpiar()

    def __repr__(self) -> str:
        return f"Sublista({self.a_diccionario()!r})"
