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


def _capacidad_para_objetivo(actual: int, objetivo: int) -> int:
    """Mirror the actual C reserve metadata: default10, double, INT_MAX guard."""
    nueva = actual if actual > 0 else 10
    while nueva < objetivo:
        if nueva > 2147483647 // 2:
            return objetivo
        nueva *= 2
    return nueva


def monticulo_inicializar(m: MonticuloBinario, tipo: int, capacidad_inicial: int) -> None:
    m.tipo = tipo
    m.datos = []
    m.cantidad = 0
    m.capacidad = _capacidad_para_objetivo(0, capacidad_inicial if capacidad_inicial > 0 else 10)


def monticulo_insertar(m: MonticuloBinario | None, valor: int) -> bool:
    if m is None:
        return False
    if m.cantidad >= m.capacidad:
        m.capacidad = _capacidad_para_objetivo(m.capacidad, m.cantidad + 1)
    m.datos.append(valor)
    _subir(m, m.cantidad)
    m.cantidad += 1
    return True


def monticulo_raiz(m: MonticuloBinario | None, resultado: list[int] | None) -> bool:
    if m is None or m.cantidad == 0 or resultado is None:
        return False
    _set_out(resultado, m.datos[0])
    return True


def monticulo_extraer_raiz(m: MonticuloBinario | None, resultado: list[int] | None) -> bool:
    if m is None or m.cantidad == 0 or resultado is None:
        return False
    raiz = m.datos[0]
    _set_out(resultado, raiz)
    ultimo = m.datos.pop()
    m.cantidad -= 1
    if m.cantidad > 0:
        m.datos[0] = ultimo
        _bajar(m, 0)
    return True


def monticulo_eliminar_valor(m: MonticuloBinario | None, valor: int) -> bool:
    if m is None or m.cantidad == 0:
        return False
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


def monticulo_vacio(m: MonticuloBinario | None) -> bool:
    return m is None or m.cantidad == 0


def monticulo_cantidad(m: MonticuloBinario | None) -> int:
    return m.cantidad if m is not None else 0


def monticulo_capacidad(m: MonticuloBinario | None) -> int:
    return m.capacidad if m is not None else 0


def monticulo_construir(m: MonticuloBinario | None, valores: list[int] | None, cantidad: int) -> bool:
    """Mirror C guards and replacement ownership for valid readable input arrays."""
    if m is None or valores is None or cantidad <= 0:
        return False
    # C destroys the old reserve before attempting the fresh reserve; tipo survives.
    monticulo_destruir(m)
    try:
        datos = list(valores[:cantidad])
    except MemoryError:
        return False
    m.datos = datos
    m.cantidad = len(datos)
    m.capacidad = _capacidad_para_objetivo(0, m.cantidad)
    for idx in range((m.cantidad // 2) - 1, -1, -1):
        _bajar(m, idx)
    return True


def monticulo_copiar_valores(m: MonticuloBinario | None, destino: list[int] | None, capacidad: int) -> int:
    if m is None or destino is None or capacidad <= 0:
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

