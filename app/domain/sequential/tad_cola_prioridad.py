"""Transcripcion Python de `tad_cola_prioridad.h`."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CPNodo:
    valor: int
    prioridad: int
    sgte: CPNodo | None = None


@dataclass
class ColaPrioridad:
    delante: CPNodo | None = None
    atras: CPNodo | None = None
    cantidad: int = 0


def cp_inicializar(cola: ColaPrioridad | None) -> None:
    if cola is None:
        return
    cola.delante = None
    cola.atras = None
    cola.cantidad = 0


def cp_encolar(cola: ColaPrioridad, valor: int, prioridad: int) -> bool:
    nuevo = CPNodo(valor=valor, prioridad=prioridad)
    if cola.delante is None:
        cola.delante = nuevo
        cola.atras = nuevo
        cola.cantidad = 1
        return True

    cola.atras.sgte = nuevo
    cola.atras = nuevo
    cola.cantidad += 1
    return True


def cp_desencolar(cola: ColaPrioridad | None, valor: list[int] | None, prioridad: list[int] | None) -> bool:
    if cola is None or cola.delante is None or valor is None or prioridad is None:
        return False
    nodo = cola.delante
    anterior: CPNodo | None = None
    actual = cola.delante
    anterior_actual: CPNodo | None = None
    while actual is not None:
        if actual.prioridad < nodo.prioridad:
            nodo = actual
            anterior = anterior_actual
        anterior_actual = actual
        actual = actual.sgte
    if anterior is None:
        cola.delante = nodo.sgte
    else:
        anterior.sgte = nodo.sgte
    if cola.atras is nodo:
        cola.atras = anterior
    if cola is None or cola.delante is None or valor is None or prioridad is None:
        cola.atras = None
    _set_out(valor, nodo.valor)
    _set_out(prioridad, nodo.prioridad)
    if cola.cantidad > 0:
        cola.cantidad -= 1
    return True


def cp_frente(cola: ColaPrioridad | None, valor: list[int] | None, prioridad: list[int] | None) -> bool:
    """Return the same stable candidate as dequeue without unlinking it."""
    if cola is None or cola.delante is None or valor is None or prioridad is None:
        return False
    candidato = cola.delante
    actual = cola.delante.sgte
    while actual is not None:
        if actual.prioridad < candidato.prioridad:
            candidato = actual
        actual = actual.sgte
    _set_out(valor, candidato.valor)
    _set_out(prioridad, candidato.prioridad)
    return True


def cp_vacia(cola: ColaPrioridad | None) -> bool:
    return cola is None or cola.delante is None or cola.cantidad == 0


def cp_contar(cola: ColaPrioridad | None) -> int:
    if cola is None:
        return 0
    return cola.cantidad


def cp_copiar_items(
    cola: ColaPrioridad | None, valores: list[int] | None, prioridades: list[int] | None, capacidad: int
) -> int:
    if cola is None or valores is None or prioridades is None or capacidad <= 0:
        return 0
    usados = 0
    aux = cola.delante
    while aux is not None and usados < capacidad:
        _set_index(valores, usados, aux.valor)
        _set_index(prioridades, usados, aux.prioridad)
        usados += 1
        aux = aux.sgte
    return usados


def cp_formatear(cola: ColaPrioridad | None, destino: list[str] | None, capacidad: int) -> None:
    """Write bounded C text; saturation stops traversal exactly as in C."""
    if destino is None or capacidad <= 0:
        return
    texto = ""
    usado = 0

    def append_text(fragmento: str) -> None:
        nonlocal texto, usado
        if usado >= capacidad:
            return
        disponibles = capacidad - usado
        texto += fragmento[: disponibles - 1]
        usado = capacidad if len(fragmento) >= disponibles else usado + len(fragmento)

    if cola is None or cola.delante is None:
        texto = "Cola de prioridad vacia"[: capacidad - 1]
    else:
        append_text("frente -> ")
        aux = cola.delante
        while aux is not None and usado < capacidad:
            append_text(f"{aux.valor}(p={aux.prioridad})")
            aux = aux.sgte
            if aux is not None and usado < capacidad:
                append_text(" | ")
    if destino:
        destino[0] = texto
    else:
        destino.append(texto)


def cp_vaciar(cola: ColaPrioridad) -> None:
    actual = cola.delante
    while actual is not None:
        siguiente = actual.sgte
        cola.delante = siguiente
        if cola.atras is actual:
            cola.atras = None
        actual.sgte = None
        if cola.cantidad > 0:
            cola.cantidad -= 1
        actual = siguiente
    cola.delante = None
    cola.atras = None
    cola.cantidad = 0


def _set_out(out_ref: list[int] | None, value: int) -> None:
    if out_ref is None:
        return
    if out_ref:
        out_ref[0] = value
    else:
        out_ref.append(value)


def _set_index(target: list[int] | None, index: int, value: int) -> None:
    if target is None:
        return
    if index < len(target):
        target[index] = value
    else:
        target.append(value)
