"""Transcripcion Python de `tad_monticulo_binario.h`."""

from __future__ import annotations

from dataclasses import dataclass, field

MONTICULO_MIN = 0
MONTICULO_MAX = 1


@dataclass
class MonticuloBinario:
    datos: list[int] = field(default_factory=list)
    cantidad: int = 0
    capacidad: int = 0
    tipo: int = MONTICULO_MIN


def monticulo_inicializar(m: MonticuloBinario, tipo: int, capacidad_inicial: int) -> None:
    m.tipo = tipo
    m.datos = []
    m.cantidad = 0
    m.capacidad = max(0, capacidad_inicial)


def monticulo_insertar(m: MonticuloBinario, valor: int) -> bool:
    if m.cantidad >= m.capacidad:
        m.capacidad = max(1, m.capacidad * 2)
    m.datos.append(valor)
    m.cantidad += 1
    _subir(m, m.cantidad - 1)
    return True


def monticulo_raiz(m: MonticuloBinario, resultado: list[int] | None) -> bool:
    if m.cantidad == 0:
        return False
    _set_out(resultado, m.datos[0])
    return True


def monticulo_extraer_raiz(m: MonticuloBinario, resultado: list[int] | None) -> bool:
    if m.cantidad == 0:
        return False
    raiz = m.datos[0]
    ultimo = m.datos.pop()
    m.cantidad -= 1
    if m.cantidad > 0:
        m.datos[0] = ultimo
        _bajar(m, 0)
    _set_out(resultado, raiz)
    return True


def monticulo_eliminar_valor(m: MonticuloBinario, valor: int) -> bool:
    try:
        idx = m.datos.index(valor)
    except ValueError:
        return False
    ultimo = m.datos.pop()
    m.cantidad -= 1
    if idx < m.cantidad:
        m.datos[idx] = ultimo
        padre = (idx - 1) // 2
        if idx > 0 and _antes(m, m.datos[idx], m.datos[padre]):
            _subir(m, idx)
        else:
            _bajar(m, idx)
    return True


def monticulo_vacio(m: MonticuloBinario) -> bool:
    return m.cantidad == 0


def monticulo_cantidad(m: MonticuloBinario) -> int:
    return m.cantidad


def monticulo_capacidad(m: MonticuloBinario) -> int:
    return m.capacidad


def monticulo_construir(m: MonticuloBinario, valores: list[int], cantidad: int) -> bool:
    m.datos = list(valores[: max(0, cantidad)])
    m.cantidad = len(m.datos)
    m.capacidad = max(m.capacidad, m.cantidad)
    for idx in range((m.cantidad // 2) - 1, -1, -1):
        _bajar(m, idx)
    return True


def monticulo_copiar_valores(m: MonticuloBinario, destino: list[int] | None, capacidad: int) -> int:
    if capacidad <= 0 or destino is None:
        return 0
    copiados = min(m.cantidad, capacidad)
    for i in range(copiados):
        if i < len(destino):
            destino[i] = m.datos[i]
        else:
            destino.append(m.datos[i])
    return copiados


def monticulo_formatear_arreglo(m: MonticuloBinario, destino: list[str] | None, capacidad: int) -> None:
    if capacidad <= 0 or destino is None:
        return
    texto = "[" + ", ".join(str(v) for v in m.datos) + "]"
    texto = texto[: max(0, capacidad - 1)]
    if destino:
        destino[0] = texto
    else:
        destino.append(texto)


def monticulo_formatear_arbol(m: MonticuloBinario, destino: list[str] | None, capacidad: int) -> None:
    if capacidad <= 0 or destino is None:
        return
    niveles: list[str] = []
    nivel = 0
    i = 0
    while i < m.cantidad:
        ancho = 2**nivel
        trozo = m.datos[i : i + ancho]
        niveles.append(" ".join(str(v) for v in trozo))
        i += ancho
        nivel += 1
    texto = "\n".join(niveles) if niveles else "(vacio)"
    texto = texto[: max(0, capacidad - 1)]
    if destino:
        destino[0] = texto
    else:
        destino.append(texto)


def monticulo_destruir(m: MonticuloBinario) -> None:
    m.datos.clear()
    m.cantidad = 0
    m.capacidad = 0


def _antes(m: MonticuloBinario, a: int, b: int) -> bool:
    return a < b if m.tipo == MONTICULO_MIN else a > b


def _subir(m: MonticuloBinario, idx: int) -> None:
    while idx > 0:
        padre = (idx - 1) // 2
        if _antes(m, m.datos[idx], m.datos[padre]):
            m.datos[idx], m.datos[padre] = m.datos[padre], m.datos[idx]
            idx = padre
            continue
        break


def _bajar(m: MonticuloBinario, idx: int) -> None:
    n = m.cantidad
    while True:
        izq = 2 * idx + 1
        der = izq + 1
        mejor = idx
        if izq < n and _antes(m, m.datos[izq], m.datos[mejor]):
            mejor = izq
        if der < n and _antes(m, m.datos[der], m.datos[mejor]):
            mejor = der
        if mejor == idx:
            break
        m.datos[idx], m.datos[mejor] = m.datos[mejor], m.datos[idx]
        idx = mejor


def _set_out(out_ref: list[int] | None, value: int) -> None:
    if out_ref is None:
        return
    if out_ref:
        out_ref[0] = value
    else:
        out_ref.append(value)

