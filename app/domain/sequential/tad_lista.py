"""Transcripcion Python de `tad_lista.h`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class NodoLista:
    nro: int
    sgte: NodoLista | None = None


Tlista = NodoLista | None

_INSERTAR_RELATIVO_PROVIDER: Callable[[], int] = lambda: 0


def lista_configurar_insertar_antes_despues_provider(provider: Callable[[], int]) -> None:
    """Configura la estrategia para responder `lista_insertar_antes_despues`."""
    global _INSERTAR_RELATIVO_PROVIDER
    _INSERTAR_RELATIVO_PROVIDER = provider


def lista_insertar_inicio(lista: list[Tlista], valor: int) -> None:
    if lista is None:
        return
    q = NodoLista(nro=valor)
    q.sgte = lista[0]
    lista[0] = q


def lista_insertar_final(lista: list[Tlista], valor: int) -> None:
    if lista is None:
        return

    q = NodoLista(nro=valor)
    if lista[0] is None:
        lista[0] = q
        return

    t = lista[0]
    while t.sgte is not None:
        t = t.sgte
    t.sgte = q


def lista_insertar_antes_despues() -> int:
    respuesta = _INSERTAR_RELATIVO_PROVIDER()
    if respuesta not in {-1, 0}:
        return 0
    return respuesta


def lista_insertar_elemento(lista: list[Tlista], valor: int, pos: int) -> None:
    if lista is None or pos <= 0:
        return

    q = NodoLista(nro=valor)
    if pos == 1:
        q.sgte = lista[0]
        lista[0] = q
        return

    desplazamiento = lista_insertar_antes_despues()
    t = lista[0]
    i = 1
    while t is not None:
        if i == pos + desplazamiento:
            q.sgte = t.sgte
            t.sgte = q
            return
        t = t.sgte
        i += 1

    print("   Error...Posicion no encontrada..!")


def lista_buscar_elemento(lista: Tlista, valor: int) -> None:
    i = 1
    encontrado = False
    q = lista

    while q is not None:
        if q.nro == valor:
            print(f"\n Encontrado en la posicion {i}")
            encontrado = True
        q = q.sgte
        i += 1

    if not encontrado:
        print("\n Numero no encontrado..")


def lista_mostrar(lista: Tlista) -> None:
    i = 1
    aux = lista
    while aux is not None:
        print(f" {i}) {aux.nro}")
        aux = aux.sgte
        i += 1


def lista_eliminar_elemento(lista: list[Tlista], valor: int) -> None:
    if lista is None or lista[0] is None:
        print(" Valor no encontrado o lista vacia.")
        return

    p = lista[0]
    ant: NodoLista | None = None

    while p is not None:
        if p.nro == valor:
            if p is lista[0]:
                lista[0] = p.sgte
            else:
                ant.sgte = p.sgte
            return
        ant = p
        p = p.sgte

    print(" Valor no encontrado o lista vacia.")


def lista_eliminar_repetidos(lista: list[Tlista], valor: int) -> None:
    if lista is None or lista[0] is None:
        print("\n\n Valores eliminados..\n")
        return

    q = lista[0]
    ant: NodoLista | None = None

    while q is not None:
        if q.nro == valor:
            if q is lista[0]:
                lista[0] = q.sgte
                q = lista[0]
            else:
                ant.sgte = q.sgte
                q = ant.sgte
        else:
            ant = q
            q = q.sgte

    print("\n\n Valores eliminados..\n")


def lista_buscar_posiciones(lista: Tlista, valor: int) -> list[int]:
    """Helper para la app: devuelve posiciones base 1."""
    posiciones: list[int] = []
    actual = lista
    pos = 1
    while actual is not None:
        if actual.nro == valor:
            posiciones.append(pos)
        actual = actual.sgte
        pos += 1
    return posiciones
