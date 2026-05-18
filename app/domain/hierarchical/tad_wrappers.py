"""Wrappers jerarquicos de alto nivel sobre los nuevos `tad_*`.

Este modulo reemplaza a los wrappers legacy por archivo separado
(`abb.py`, `avl.py`, `rojo_negro.py`, `monticulo_binario.py`) para que
la app use solo los TAD nuevos.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

from .exceptions import ElementoDuplicadoError, ElementoNoEncontradoError, EstructuraVaciaError
from .tad_abb import ABBNodo, abb_altura, abb_buscar, abb_eliminar, abb_encontrarMaximo, abb_encontrarMinimo, abb_insertar, abb_liberarArbol
from .tad_avl import AVL as AVLNode
from .tad_avl import avl_altura, avl_buscar, avl_eliminar, avl_insertar, avl_liberarAVL, avl_minimo, nodoAVL
from .tad_monticulo_binario import (
    MONTICULO_MAX,
    MONTICULO_MIN,
    MonticuloBinario as MonticuloTAD,
    monticulo_cantidad,
    monticulo_destruir,
    monticulo_extraer_raiz,
    monticulo_inicializar,
    monticulo_insertar,
    monticulo_raiz,
    monticulo_vacio,
)
from .tad_rojo_negro import NEGRO, ROJO, RBT, nodoRBT, rbt_buscar, rbt_eliminar, rbt_insertar

T = TypeVar("T")


def _patch_abb_node_aliases() -> None:
    if not isinstance(getattr(ABBNodo, "dato", None), property):
        ABBNodo.dato = property(
            lambda self: self.valor,
            lambda self, value: setattr(self, "valor", int(value)),
        )


def _patch_avl_node_aliases() -> None:
    if not isinstance(getattr(nodoAVL, "dato", None), property):
        nodoAVL.dato = property(
            lambda self: self.nro,
            lambda self, value: setattr(self, "nro", int(value)),
        )
    if not isinstance(getattr(nodoAVL, "izquierdo", None), property):
        nodoAVL.izquierdo = property(
            lambda self: self.izq,
            lambda self, value: setattr(self, "izq", value),
        )
    if not isinstance(getattr(nodoAVL, "derecho", None), property):
        nodoAVL.derecho = property(
            lambda self: self.der,
            lambda self, value: setattr(self, "der", value),
        )
    if not isinstance(getattr(nodoAVL, "altura", None), property):
        nodoAVL.altura = property(lambda self: 1 + max(avl_altura(self.izq), avl_altura(self.der)))


_patch_abb_node_aliases()
_patch_avl_node_aliases()


class ABB(Generic[T]):
    """Arbol binario de busqueda sin duplicados."""

    def __init__(self, valores: Iterator[T] | None = None) -> None:
        self._raiz: ABBNodo | None = None
        self._tamano = 0
        if valores is not None:
            for valor in valores:
                self.insertar(valor)

    def insertar(self, dato: T) -> None:
        value = int(dato)
        if self.buscar(value):
            raise ElementoDuplicadoError(f"El dato {value!r} ya existe.")
        self._raiz = abb_insertar(self._raiz, value)
        self._tamano = self._count_nodes(self._raiz)

    def eliminar(self, dato: T) -> None:
        value = int(dato)
        if not self.buscar(value):
            raise ElementoNoEncontradoError(f"El dato {value!r} no existe.")
        self._raiz = abb_eliminar(self._raiz, value)
        self._tamano = self._count_nodes(self._raiz)

    def buscar(self, dato: T) -> bool:
        return abb_buscar(self._raiz, int(dato)) is not None

    def minimo(self) -> T:
        nodo = abb_encontrarMinimo(self._raiz)
        if nodo is None:
            raise ElementoNoEncontradoError("El arbol esta vacio.")
        return nodo.valor  # type: ignore[return-value]

    def maximo(self) -> T:
        nodo = abb_encontrarMaximo(self._raiz)
        if nodo is None:
            raise ElementoNoEncontradoError("El arbol esta vacio.")
        return nodo.valor  # type: ignore[return-value]

    def altura(self) -> int:
        return abb_altura(self._raiz)

    def contar_hojas(self) -> int:
        return self._contar_hojas_rec(self._raiz)

    def inorden(self) -> list[T]:
        out: list[int] = []
        self._inorden_rec(self._raiz, out)
        return out  # type: ignore[return-value]

    def preorden(self) -> list[T]:
        out: list[int] = []
        self._preorden_rec(self._raiz, out)
        return out  # type: ignore[return-value]

    def postorden(self) -> list[T]:
        out: list[int] = []
        self._postorden_rec(self._raiz, out)
        return out  # type: ignore[return-value]

    def validar(self) -> bool:
        return self._validar_rango(self._raiz, None, None)

    def limpiar(self) -> None:
        abb_liberarArbol(self._raiz)
        self._raiz = None
        self._tamano = 0

    def vacio(self) -> bool:
        return self._tamano == 0

    def tamano(self) -> int:
        return self._tamano

    def _count_nodes(self, nodo: ABBNodo | None) -> int:
        if nodo is None:
            return 0
        return 1 + self._count_nodes(nodo.izquierdo) + self._count_nodes(nodo.derecho)

    def _contar_hojas_rec(self, nodo: ABBNodo | None) -> int:
        if nodo is None:
            return 0
        if nodo.izquierdo is None and nodo.derecho is None:
            return 1
        return self._contar_hojas_rec(nodo.izquierdo) + self._contar_hojas_rec(nodo.derecho)

    def _inorden_rec(self, nodo: ABBNodo | None, out: list[int]) -> None:
        if nodo is None:
            return
        self._inorden_rec(nodo.izquierdo, out)
        out.append(nodo.valor)
        self._inorden_rec(nodo.derecho, out)

    def _preorden_rec(self, nodo: ABBNodo | None, out: list[int]) -> None:
        if nodo is None:
            return
        out.append(nodo.valor)
        self._preorden_rec(nodo.izquierdo, out)
        self._preorden_rec(nodo.derecho, out)

    def _postorden_rec(self, nodo: ABBNodo | None, out: list[int]) -> None:
        if nodo is None:
            return
        self._postorden_rec(nodo.izquierdo, out)
        self._postorden_rec(nodo.derecho, out)
        out.append(nodo.valor)

    def _validar_rango(self, nodo: ABBNodo | None, minimo: int | None, maximo: int | None) -> bool:
        if nodo is None:
            return True
        if minimo is not None and nodo.valor <= minimo:
            return False
        if maximo is not None and nodo.valor >= maximo:
            return False
        return self._validar_rango(nodo.izquierdo, minimo, nodo.valor) and self._validar_rango(nodo.derecho, nodo.valor, maximo)

    def __len__(self) -> int:
        return self._tamano

    def __contains__(self, dato: object) -> bool:
        try:
            return self.buscar(int(dato))
        except (TypeError, ValueError):
            return False

    def __iter__(self) -> Iterator[T]:
        return iter(self.inorden())

    def __repr__(self) -> str:
        return f"ABB({self.inorden()!r})"


class AVL(Generic[T]):
    """Arbol AVL sin duplicados."""

    def __init__(self, valores: Iterator[T] | None = None) -> None:
        self._raiz_ref: list[AVLNode] = [None]
        self._raiz: AVLNode = None
        self._tamano = 0
        if valores is not None:
            for valor in valores:
                self.insertar(valor)

    def insertar(self, dato: T) -> None:
        value = int(dato)
        if self.buscar(value):
            raise ElementoDuplicadoError(f"El dato {value!r} ya existe.")
        avl_insertar(self._raiz_ref, value)
        self._raiz = self._raiz_ref[0]
        self._tamano = self._count_nodes(self._raiz)

    def eliminar(self, dato: T) -> None:
        value = int(dato)
        if not self.buscar(value):
            raise ElementoNoEncontradoError(f"El dato {value!r} no existe.")
        avl_eliminar(self._raiz_ref, value)
        self._raiz = self._raiz_ref[0]
        self._tamano = self._count_nodes(self._raiz)

    def buscar(self, dato: T) -> bool:
        return avl_buscar(self._raiz, int(dato)) is not None

    def minimo(self) -> T:
        nodo = avl_minimo(self._raiz)
        if nodo is None:
            raise ElementoNoEncontradoError("El arbol esta vacio.")
        return nodo.nro  # type: ignore[return-value]

    def maximo(self) -> T:
        if self._raiz is None:
            raise ElementoNoEncontradoError("El arbol esta vacio.")
        actual = self._raiz
        while actual.der is not None:
            actual = actual.der
        return actual.nro  # type: ignore[return-value]

    def altura(self) -> int:
        return avl_altura(self._raiz)

    def inorden(self) -> list[T]:
        out: list[int] = []
        self._inorden_rec(self._raiz, out)
        return out  # type: ignore[return-value]

    def validar(self) -> bool:
        ok, _, _ = self._validar_rec(self._raiz, None, None)
        return ok

    def limpiar(self) -> None:
        avl_liberarAVL(self._raiz)
        self._raiz_ref[0] = None
        self._raiz = None
        self._tamano = 0

    def vacio(self) -> bool:
        return self._tamano == 0

    def tamano(self) -> int:
        return self._tamano

    def _count_nodes(self, nodo: AVLNode) -> int:
        if nodo is None:
            return 0
        return 1 + self._count_nodes(nodo.izq) + self._count_nodes(nodo.der)

    def _inorden_rec(self, nodo: AVLNode, out: list[int]) -> None:
        if nodo is None:
            return
        self._inorden_rec(nodo.izq, out)
        out.append(nodo.nro)
        self._inorden_rec(nodo.der, out)

    def _validar_rec(self, nodo: AVLNode, minimo: int | None, maximo: int | None) -> tuple[bool, int, int]:
        if nodo is None:
            return True, 0, 0
        if minimo is not None and nodo.nro <= minimo:
            return False, 0, 0
        if maximo is not None and nodo.nro >= maximo:
            return False, 0, 0

        ok_izq, h_izq, c_izq = self._validar_rec(nodo.izq, minimo, nodo.nro)
        ok_der, h_der, c_der = self._validar_rec(nodo.der, nodo.nro, maximo)
        fe = h_der - h_izq
        return ok_izq and ok_der and -1 <= fe <= 1, 1 + max(h_izq, h_der), c_izq + c_der + 1

    def __len__(self) -> int:
        return self._tamano

    def __contains__(self, dato: object) -> bool:
        try:
            return self.buscar(int(dato))
        except (TypeError, ValueError):
            return False

    def __iter__(self) -> Iterator[T]:
        return iter(self.inorden())

    def __repr__(self) -> str:
        return f"AVL({self.inorden()!r})"


class ColorRN(Enum):
    ROJO = 0
    NEGRO = 1


@dataclass(slots=True)
class _NilNode:
    dato: int | None = None
    color: ColorRN = ColorRN.NEGRO
    padre: _NilNode | _NodoRNView | None = None
    izquierdo: _NilNode | _NodoRNView | None = None
    derecho: _NilNode | _NodoRNView | None = None


@dataclass(slots=True)
class _NodoRNView:
    dato: int
    color: ColorRN
    padre: _NilNode | _NodoRNView
    izquierdo: _NilNode | _NodoRNView
    derecho: _NilNode | _NodoRNView


class RojoNegro(Generic[T]):
    """Arbol rojo-negro sin duplicados, con vista compatible para adapters."""

    def __init__(self, valores: Iterator[T] | None = None) -> None:
        self._root_ref: list[RBT] = [None]
        self._nil = _NilNode()
        self._nil.padre = self._nil
        self._nil.izquierdo = self._nil
        self._nil.derecho = self._nil
        self._raiz: _NilNode | _NodoRNView = self._nil
        self._tamano = 0
        if valores is not None:
            for valor in valores:
                self.insertar(valor)

    def insertar(self, dato: T) -> None:
        value = int(dato)
        if self.buscar(value):
            raise ElementoDuplicadoError(f"El dato {value!r} ya existe.")
        rbt_insertar(self._root_ref, value)
        self._tamano = self._count_nodes(self._root_ref[0])
        self._sync_view()

    def eliminar(self, dato: T) -> None:
        value = int(dato)
        if not self.buscar(value):
            raise ElementoNoEncontradoError(f"El dato {value!r} no existe.")
        rbt_eliminar(self._root_ref, value)
        self._tamano = self._count_nodes(self._root_ref[0])
        self._sync_view()

    def buscar(self, dato: T) -> bool:
        return rbt_buscar(self._root_ref[0], int(dato)) is not None

    def inorden(self) -> list[T]:
        out: list[int] = []
        self._inorden_rec(self._root_ref[0], out)
        return out  # type: ignore[return-value]

    def altura(self) -> int:
        return self._altura_rec(self._root_ref[0])

    def validar(self) -> bool:
        raiz = self._root_ref[0]
        if raiz is None:
            return True
        if raiz.rbt_color != NEGRO:
            return False
        ok = self._validar_rec(raiz, None, None)
        return ok

    def limpiar(self) -> None:
        self._root_ref[0] = None
        self._tamano = 0
        self._sync_view()

    def vacio(self) -> bool:
        return self._tamano == 0

    def tamano(self) -> int:
        return self._tamano

    def _sync_view(self) -> None:
        raiz = self._build_view(self._root_ref[0], self._nil)
        self._raiz = raiz
        if isinstance(raiz, _NodoRNView):
            raiz.padre = self._nil

    def _build_view(self, nodo: RBT, padre: _NilNode | _NodoRNView) -> _NilNode | _NodoRNView:
        if nodo is None:
            return self._nil
        color = ColorRN.ROJO if nodo.rbt_color == ROJO else ColorRN.NEGRO
        view = _NodoRNView(
            dato=nodo.nro,
            color=color,
            padre=padre,
            izquierdo=self._nil,
            derecho=self._nil,
        )
        view.izquierdo = self._build_view(nodo.izq, view)
        view.derecho = self._build_view(nodo.der, view)
        return view

    def _count_nodes(self, nodo: RBT) -> int:
        if nodo is None:
            return 0
        return 1 + self._count_nodes(nodo.izq) + self._count_nodes(nodo.der)

    def _inorden_rec(self, nodo: RBT, out: list[int]) -> None:
        if nodo is None:
            return
        self._inorden_rec(nodo.izq, out)
        out.append(nodo.nro)
        self._inorden_rec(nodo.der, out)

    def _altura_rec(self, nodo: RBT) -> int:
        if nodo is None:
            return 0
        return 1 + max(self._altura_rec(nodo.izq), self._altura_rec(nodo.der))

    def _validar_rec(self, nodo: RBT, minimo: int | None, maximo: int | None) -> bool:
        if nodo is None:
            return True
        if minimo is not None and nodo.nro <= minimo:
            return False
        if maximo is not None and nodo.nro >= maximo:
            return False
        if nodo.rbt_color == ROJO:
            if (nodo.izq is not None and nodo.izq.rbt_color == ROJO) or (nodo.der is not None and nodo.der.rbt_color == ROJO):
                return False

        return self._validar_rec(nodo.izq, minimo, nodo.nro) and self._validar_rec(nodo.der, nodo.nro, maximo)

    def __len__(self) -> int:
        return self._tamano

    def __contains__(self, dato: object) -> bool:
        try:
            return self.buscar(int(dato))
        except (TypeError, ValueError):
            return False

    def __iter__(self) -> Iterator[T]:
        return iter(self.inorden())

    def __repr__(self) -> str:
        return f"RojoNegro({self.inorden()!r})"


class MonticuloBinario(Generic[T]):
    """API de monticulo usada por el adapter jerarquico."""

    def __init__(
        self,
        valores: Iterator[T] | None = None,
        *,
        prioridad: Callable[[T], object] | None = None,
        min_heap: bool = True,
    ) -> None:
        self._prioridad = prioridad if prioridad is not None else (lambda x: x)
        self._min_heap = min_heap
        self._use_tad = prioridad is None
        self._py_datos: list[T] = []
        self._m = MonticuloTAD()
        monticulo_inicializar(self._m, MONTICULO_MIN if min_heap else MONTICULO_MAX, 16)
        if valores is not None:
            for valor in valores:
                self.insertar(valor)

    def insertar(self, dato: T) -> None:
        if self._use_tad:
            monticulo_insertar(self._m, int(dato))
            return
        self._py_datos.append(dato)
        self._subir_py(len(self._py_datos) - 1)

    def extraer_raiz(self) -> T:
        if self._use_tad:
            out: list[int] = []
            ok = monticulo_extraer_raiz(self._m, out)
            if not ok:
                raise EstructuraVaciaError("El monticulo esta vacio.")
            return out[0]  # type: ignore[return-value]
        if not self._py_datos:
            raise EstructuraVaciaError("El monticulo esta vacio.")
        raiz = self._py_datos[0]
        ultimo = self._py_datos.pop()
        if self._py_datos:
            self._py_datos[0] = ultimo
            self._bajar_py(0)
        return raiz

    def raiz(self) -> T:
        if self._use_tad:
            out: list[int] = []
            ok = monticulo_raiz(self._m, out)
            if not ok:
                raise EstructuraVaciaError("El monticulo esta vacio.")
            return out[0]  # type: ignore[return-value]
        if not self._py_datos:
            raise EstructuraVaciaError("El monticulo esta vacio.")
        return self._py_datos[0]

    def vacio(self) -> bool:
        return monticulo_vacio(self._m) if self._use_tad else not self._py_datos

    def tamano(self) -> int:
        return monticulo_cantidad(self._m) if self._use_tad else len(self._py_datos)

    def limpiar(self) -> None:
        if self._use_tad:
            tipo = self._m.tipo
            monticulo_destruir(self._m)
            monticulo_inicializar(self._m, tipo, 16)
            return
        self._py_datos.clear()

    def a_lista(self) -> list[T]:
        return list(self._m.datos) if self._use_tad else list(self._py_datos)  # type: ignore[return-value]

    def __len__(self) -> int:
        return self.tamano()

    def __iter__(self):
        return iter(self.a_lista())

    def __repr__(self) -> str:
        return f"MonticuloBinario({self.a_lista()!r})"

    def _antes_py(self, a: T, b: T) -> bool:
        pa = self._prioridad(a)
        pb = self._prioridad(b)
        return pa < pb if self._min_heap else pa > pb

    def _subir_py(self, idx: int) -> None:
        while idx > 0:
            padre = (idx - 1) // 2
            if not self._antes_py(self._py_datos[idx], self._py_datos[padre]):
                break
            self._py_datos[idx], self._py_datos[padre] = self._py_datos[padre], self._py_datos[idx]
            idx = padre

    def _bajar_py(self, idx: int) -> None:
        n = len(self._py_datos)
        while True:
            izq = 2 * idx + 1
            der = 2 * idx + 2
            mejor = idx
            if izq < n and self._antes_py(self._py_datos[izq], self._py_datos[mejor]):
                mejor = izq
            if der < n and self._antes_py(self._py_datos[der], self._py_datos[mejor]):
                mejor = der
            if mejor == idx:
                break
            self._py_datos[idx], self._py_datos[mejor] = self._py_datos[mejor], self._py_datos[idx]
            idx = mejor
