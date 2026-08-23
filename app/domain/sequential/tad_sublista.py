"""Transcripcion Python de `tad_sublista.h`."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Sublista:
    nro: int
    sgte: Sublista | None = None


@dataclass
class Nodo:
    nro: int
    sgte: Nodo | None = None
    sub: Sublista | None = None


def sublista_inicializar(lista: list[Nodo | None]) -> None:
    lista[0] = None


def sublista_insertar_padre_final(lista: list[Nodo | None], valor_padre: int) -> Nodo:
    nuevo = Nodo(nro=valor_padre)
    if lista[0] is None:
        lista[0] = nuevo
        return nuevo
    actual = lista[0]
    while actual.sgte is not None:
        actual = actual.sgte
    actual.sgte = nuevo
    return nuevo


def sublista_buscar_padre(lista: Nodo | None, valor_padre: int) -> Nodo | None:
    actual = lista
    while actual is not None:
        if actual.nro == valor_padre:
            return actual
        actual = actual.sgte
    return None


def sublista_eliminar_padre_primero(lista: list[Nodo | None], valor_padre: int) -> bool:
    if lista[0] is None:
        return False
    if lista[0].nro == valor_padre:
        lista[0] = lista[0].sgte
        return True
    previo = lista[0]
    actual = previo.sgte
    while actual is not None:
        if actual.nro == valor_padre:
            previo.sgte = actual.sgte
            return True
        previo = actual
        actual = actual.sgte
    return False


def sublista_contar_padres(lista: Nodo | None) -> int:
    count = 0
    actual = lista
    while actual is not None:
        count += 1
        actual = actual.sgte
    return count


def sublista_insertar_hijo_final(padre: Nodo | None, valor_hijo: int) -> bool:
    if padre is None:
        return False
    nuevo = Sublista(nro=valor_hijo)
    if padre.sub is None:
        padre.sub = nuevo
        return True
    actual = padre.sub
    while actual.sgte is not None:
        actual = actual.sgte
    actual.sgte = nuevo
    return True


def sublista_buscar_hijo(lista_hijos: Sublista | None, valor_hijo: int) -> Sublista | None:
    actual = lista_hijos
    while actual is not None:
        if actual.nro == valor_hijo:
            return actual
        actual = actual.sgte
    return None


def sublista_eliminar_hijo_primero(padre: Nodo | None, valor_hijo: int) -> bool:
    if padre is None or padre.sub is None:
        return False
    if padre.sub.nro == valor_hijo:
        padre.sub = padre.sub.sgte
        return True
    previo = padre.sub
    actual = previo.sgte
    while actual is not None:
        if actual.nro == valor_hijo:
            previo.sgte = actual.sgte
            return True
        previo = actual
        actual = actual.sgte
    return False


def sublista_contar_hijos(padre: Nodo | None) -> int:
    if padre is None:
        return 0
    count = 0
    actual = padre.sub
    while actual is not None:
        count += 1
        actual = actual.sgte
    return count


def sublista_copiar_hijos(padre: Nodo | None, destino: list[int] | None, capacidad: int) -> int:
    if padre is None or destino is None or capacidad <= 0:
        return 0
    copiados = 0
    actual = padre.sub
    while actual is not None and copiados < capacidad:
        if copiados < len(destino):
            destino[copiados] = actual.nro
        else:
            destino.append(actual.nro)
        copiados += 1
        actual = actual.sgte
    return copiados


def sublista_formatear(lista: Nodo | None, destino: list[str] | None, capacidad: int) -> None:
    if capacidad <= 0 or destino is None:
        return
    partes: list[str] = []
    actual = lista
    while actual is not None:
        hijos: list[str] = []
        hijo = actual.sub
        while hijo is not None:
            hijos.append(str(hijo.nro))
            hijo = hijo.sgte
        partes.append(f"{actual.nro}: [{', '.join(hijos)}]")
        actual = actual.sgte
    texto = " | ".join(partes) if partes else "(vacia)"
    texto = texto[: max(0, capacidad - 1)]
    if destino:
        destino[0] = texto
    else:
        destino.append(texto)


def sublista_destruir(lista: list[Nodo | None], eventos: list[dict] | None = None) -> None:
    """Libera lógicamente hijos antes que su padre, igual que el C mostrado."""
    actual = lista[0]
    while actual is not None:
        siguiente = actual.sgte
        hijo = actual.sub
        while hijo is not None:
            hijo_siguiente = hijo.sgte
            if eventos is not None:
                eventos.append({"stage": "free_child", "parent_id": id(actual), "node_id": id(hijo), "value": hijo.nro})
            hijo.sgte = None
            hijo = hijo_siguiente
        actual.sub = None
        if eventos is not None:
            eventos.append({"stage": "free_parent", "node_id": id(actual), "value": actual.nro})
        actual.sgte = None
        actual = siguiente
    lista[0] = None
