"""TAD Tabla Hash.

Implementación por encadenamiento separado. Cada bucket reutiliza ListaEnlazada.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from .lista_enlazada import ListaEnlazada

K = TypeVar("K")
V = TypeVar("V")


@dataclass(slots=True)
class _Entrada(Generic[K, V]):
    clave: K
    valor: V


class TablaHash(Generic[K, V]):
    """Tabla hash genérica con buckets basados en ListaEnlazada."""

    def __init__(self, capacidad: int = 17) -> None:
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser positiva.")

        self._capacidad = capacidad
        self._cantidad = 0
        self._buckets: list[ListaEnlazada[_Entrada[K, V]]] = [
            ListaEnlazada() for _ in range(capacidad)
        ]

    def _indice(self, clave: K) -> int:
        return hash(clave) % self._capacidad

    def insertar(self, clave: K, valor: V) -> None:
        """Inserta o actualiza un par clave-valor."""
        bucket = self._buckets[self._indice(clave)]

        for entrada in bucket:
            if entrada.clave == clave:
                entrada.valor = valor
                return

        bucket.insertar_final(_Entrada(clave, valor))
        self._cantidad += 1

        if self.factor_carga() > 0.75:
            self._redimensionar(self._capacidad * 2 + 1)

    def buscar(self, clave: K) -> V | None:
        """Busca una clave y retorna su valor, o None si no existe."""
        bucket = self._buckets[self._indice(clave)]

        for entrada in bucket:
            if entrada.clave == clave:
                return entrada.valor

        return None

    def contiene(self, clave: K) -> bool:
        """Indica si existe una clave."""
        bucket = self._buckets[self._indice(clave)]
        return any(entrada.clave == clave for entrada in bucket)

    def eliminar(self, clave: K) -> bool:
        """Elimina una clave si existe. Retorna True si elimina."""
        bucket = self._buckets[self._indice(clave)]

        for pos, entrada in enumerate(bucket):
            if entrada.clave == clave:
                bucket.eliminar_posicion(pos)
                self._cantidad -= 1
                return True

        return False

    def claves(self) -> list[K]:
        """Retorna todas las claves."""
        return [entrada.clave for bucket in self._buckets for entrada in bucket]

    def valores(self) -> list[V]:
        """Retorna todos los valores."""
        return [entrada.valor for bucket in self._buckets for entrada in bucket]

    def items(self) -> list[tuple[K, V]]:
        """Retorna todos los pares clave-valor."""
        return [
            (entrada.clave, entrada.valor)
            for bucket in self._buckets
            for entrada in bucket
        ]

    def factor_carga(self) -> float:
        """Retorna el factor de carga."""
        return self._cantidad / self._capacidad

    def tamano(self) -> int:
        return self._cantidad

    def capacidad(self) -> int:
        return self._capacidad

    def limpiar(self) -> None:
        self._buckets = [ListaEnlazada() for _ in range(self._capacidad)]
        self._cantidad = 0

    def _redimensionar(self, nueva_capacidad: int) -> None:
        antiguos = self.items()
        self._capacidad = nueva_capacidad
        self._buckets = [ListaEnlazada() for _ in range(nueva_capacidad)]
        self._cantidad = 0

        for clave, valor in antiguos:
            self.insertar(clave, valor)

    def __len__(self) -> int:
        return self._cantidad

    def __repr__(self) -> str:
        return f"TablaHash({self.items()!r})"
