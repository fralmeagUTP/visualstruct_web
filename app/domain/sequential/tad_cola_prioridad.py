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


def cp_inicializar(cola: ColaPrioridad) -> None:
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


def cp_desencolar(cola: ColaPrioridad, valor: list[int] | None, prioridad: list[int] | None) -> bool:
    if cola.delante is None:
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
    if cola.delante is None:
        cola.atras = None
    cola.cantidad -= 1
    _set_out(valor, nodo.valor)
    _set_out(prioridad, nodo.prioridad)
    return True


def cp_frente(cola: ColaPrioridad, valor: list[int] | None, prioridad: list[int] | None) -> bool:
    """Return the same stable candidate as dequeue without unlinking it."""
    if cola.delante is None:
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


def cp_vacia(cola: ColaPrioridad) -> bool:
    return cola.cantidad == 0


def cp_contar(cola: ColaPrioridad) -> int:
    return cola.cantidad


def cp_copiar_items(
    cola: ColaPrioridad, valores: list[int] | None, prioridades: list[int] | None, capacidad: int
) -> int:
    if capacidad <= 0:
        return 0
    copiados = 0
    actual = cola.delante
    while actual is not None and copiados < capacidad:
        _set_index(valores, copiados, actual.valor)
        _set_index(prioridades, copiados, actual.prioridad)
        copiados += 1
        actual = actual.sgte
    return copiados


def cp_formatear(cola: ColaPrioridad, destino: list[str] | None, capacidad: int) -> None:
    if capacidad <= 0:
        return
    partes: list[str] = []
    actual = cola.delante
    pos = 0
    while actual is not None:
        partes.append(f"[{pos}]={actual.valor}(p={actual.prioridad})")
        pos += 1
        actual = actual.sgte
    texto = " <- ".join(partes) if partes else "(vacia)"
    texto = texto[: max(0, capacidad - 1)]
    if destino is not None:
        if destino:
            destino[0] = texto
        else:
            destino.append(texto)


def cp_vaciar(cola: ColaPrioridad) -> None:
    cp_inicializar(cola)


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
