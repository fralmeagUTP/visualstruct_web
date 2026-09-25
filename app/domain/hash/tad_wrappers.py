"""Wrappers de alto nivel sobre `tad_tabla_hash`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from .tad_tabla_hash import THNodo, TablaHash as TablaHashTAD, th_buscar, th_capacidad, th_cantidad, th_contiene, th_destruir, th_eliminar, th_inicializar, th_insertar, th_vaciar

K = TypeVar("K")
V = TypeVar("V")


@dataclass(slots=True)
class _Entrada(Generic[K, V]):
    clave: K
    valor: V


class TablaHash(Generic[K, V]):
    """Tabla hash compatible con la app, respaldada por el TAD nuevo."""

    def __init__(self, capacidad: int = 17) -> None:
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser positiva.")
        self._tabla = TablaHashTAD()
        th_inicializar(self._tabla, capacidad)
        self._buckets: list[list[_Entrada[K, V]]] = []
        self._sync_buckets_cache()

    def _indice(self, clave: K) -> int:
        if isinstance(clave, bool) or not isinstance(clave, int):
            raise ValueError("La clave debe ser un entero representable por el TAD C.")
        return clave % self.capacidad()

    def insertar(self, clave: K, valor: V) -> None:
        if isinstance(clave, bool) or not isinstance(clave, int) or isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("La clave y el valor deben ser enteros representables por el TAD C.")
        if not th_insertar(self._tabla, clave, valor):
            raise ValueError("La tabla no está inicializada; crea una tabla antes de insertar.")
        self._sync_buckets_cache()

    def buscar(self, clave: K) -> V | None:
        out: list[int] = []
        if not th_buscar(self._tabla, clave, out):
            return None
        return out[0] if out else None  # type: ignore[return-value]

    def contiene(self, clave: K) -> bool:
        return bool(th_contiene(self._tabla, clave))

    def eliminar(self, clave: K) -> bool:
        ok = th_eliminar(self._tabla, clave)
        self._sync_buckets_cache()
        return ok

    def claves(self) -> list[K]:
        return [entrada.clave for bucket in self._buckets for entrada in bucket]

    def valores(self) -> list[V]:
        return [entrada.valor for bucket in self._buckets for entrada in bucket]

    def items(self) -> list[tuple[K, V]]:
        return [(entrada.clave, entrada.valor) for bucket in self._buckets for entrada in bucket]

    def factor_carga(self) -> float:
        cap = self.capacidad()
        return (self.tamano() / cap) if cap > 0 else 0.0

    def tamano(self) -> int:
        return th_cantidad(self._tabla)

    def capacidad(self) -> int:
        return th_capacidad(self._tabla)

    def limpiar(self) -> None:
        th_vaciar(self._tabla)
        self._sync_buckets_cache()

    def destruir(self) -> None:
        th_destruir(self._tabla)
        self._sync_buckets_cache()

    def _sync_buckets_cache(self) -> None:
        buckets: list[list[_Entrada[K, V]]] = [[] for _ in range(self.capacidad())]
        for idx, head in enumerate(self._tabla.buckets):
            actual: THNodo | None = head
            while actual is not None:
                buckets[idx].append(_Entrada(clave=actual.clave, valor=actual.valor))  # type: ignore[arg-type]
                actual = actual.siguiente
        self._buckets = buckets

    def __len__(self) -> int:
        return self.tamano()

    def __repr__(self) -> str:
        return f"TablaHash({self.items()!r})"
