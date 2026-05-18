"""Transcripcion Python de `tad_lista_circular.h`."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LCirNodo:
    valor: int
    sgte: LCirNodo | None = None


@dataclass
class ListaCircular:
    cabeza: LCirNodo | None = None
    cola: LCirNodo | None = None
    cantidad: int = 0


def lcir_inicializar(lista: ListaCircular) -> None:
    lista.cabeza = None
    lista.cola = None
    lista.cantidad = 0


def lcir_insertar_inicio(lista: ListaCircular, valor: int) -> bool:
    nuevo = LCirNodo(valor=valor)
    if lista.cabeza is None:
        nuevo.sgte = nuevo
        lista.cabeza = nuevo
        lista.cola = nuevo
    else:
        nuevo.sgte = lista.cabeza
        lista.cola.sgte = nuevo
        lista.cabeza = nuevo
    lista.cantidad += 1
    return True


def lcir_insertar_final(lista: ListaCircular, valor: int) -> bool:
    nuevo = LCirNodo(valor=valor)
    if lista.cabeza is None:
        nuevo.sgte = nuevo
        lista.cabeza = nuevo
        lista.cola = nuevo
    else:
        nuevo.sgte = lista.cabeza
        lista.cola.sgte = nuevo
        lista.cola = nuevo
    lista.cantidad += 1
    return True


def lcir_buscar_posiciones(
    lista: ListaCircular, valor: int, destino: list[int] | None, capacidad: int
) -> int:
    if lista.cabeza is None or capacidad <= 0:
        return 0
    copiados = 0
    actual = lista.cabeza
    for pos in range(lista.cantidad):
        if actual.valor == valor and destino is not None and copiados < capacidad:
            if copiados < len(destino):
                destino[copiados] = pos
            else:
                destino.append(pos)
            copiados += 1
        actual = actual.sgte
    return copiados


def lcir_eliminar_primero(lista: ListaCircular, valor: int) -> bool:
    if lista.cabeza is None:
        return False
    actual = lista.cabeza
    previo = lista.cola
    for _ in range(lista.cantidad):
        if actual.valor == valor:
            if lista.cantidad == 1:
                lista.cabeza = None
                lista.cola = None
            else:
                previo.sgte = actual.sgte
                if actual is lista.cabeza:
                    lista.cabeza = actual.sgte
                if actual is lista.cola:
                    lista.cola = previo
            lista.cantidad -= 1
            return True
        previo = actual
        actual = actual.sgte
    return False


def lcir_invertir(lista: ListaCircular) -> None:
    if lista.cantidad <= 1:
        return
    previo = lista.cola
    actual = lista.cabeza
    for _ in range(lista.cantidad):
        siguiente = actual.sgte
        actual.sgte = previo
        previo = actual
        actual = siguiente
    lista.cabeza, lista.cola = lista.cola, lista.cabeza


def lcir_vacia(lista: ListaCircular) -> bool:
    return lista.cantidad == 0


def lcir_contar(lista: ListaCircular) -> int:
    return lista.cantidad


def lcir_copiar_valores(lista: ListaCircular, destino: list[int] | None, capacidad: int) -> int:
    if lista.cabeza is None or capacidad <= 0 or destino is None:
        return 0
    copiados = 0
    actual = lista.cabeza
    for _ in range(min(lista.cantidad, capacidad)):
        if copiados < len(destino):
            destino[copiados] = actual.valor
        else:
            destino.append(actual.valor)
        copiados += 1
        actual = actual.sgte
    return copiados


def lcir_formatear(lista: ListaCircular, destino: list[str] | None, capacidad: int) -> None:
    if capacidad <= 0:
        return
    valores: list[str] = []
    if lista.cabeza is not None:
        actual = lista.cabeza
        for pos in range(lista.cantidad):
            valores.append(f"[{pos}]={actual.valor}")
            actual = actual.sgte
    texto = "HEAD -> " + (" -> ".join(valores) if valores else "(vacia)")
    if valores:
        texto += " -> (vuelve a HEAD)"
    texto = texto[: max(0, capacidad - 1)]
    if destino is not None:
        if destino:
            destino[0] = texto
        else:
            destino.append(texto)


def lcir_destruir(lista: ListaCircular) -> None:
    lcir_inicializar(lista)

