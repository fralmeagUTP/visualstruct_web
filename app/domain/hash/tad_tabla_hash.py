"""Transcripcion Python de `tad_tabla_hash.h`."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class THNodo:
    clave: int
    valor: int
    siguiente: THNodo | None = None


@dataclass
class TablaHash:
    buckets: list[THNodo | None] = field(default_factory=list)
    capacidad: int = 0
    cantidad: int = 0


@dataclass
class THEstadisticas:
    capacidad: int
    cantidad: int
    buckets_ocupados: int
    colisiones: int
    factor_carga: float


def th_indice(tabla: TablaHash, clave: int) -> int:
    if tabla.capacidad <= 0:
        return 0
    return clave % tabla.capacidad


def th_inicializar(tabla: TablaHash, capacidad: int) -> None:
    cap = max(1, capacidad)
    tabla.capacidad = cap
    tabla.cantidad = 0
    tabla.buckets = [None] * cap


def th_insertar(tabla: TablaHash, clave: int, valor: int) -> bool:
    if tabla.capacidad <= 0:
        th_inicializar(tabla, 17)
    idx = th_indice(tabla, clave)
    actual = tabla.buckets[idx]
    while actual is not None:
        if actual.clave == clave:
            actual.valor = valor
            return True
        actual = actual.siguiente
    tabla.buckets[idx] = THNodo(clave=clave, valor=valor, siguiente=tabla.buckets[idx])
    tabla.cantidad += 1
    return True


def th_buscar(tabla: TablaHash, clave: int, valor: list[int] | None) -> bool:
    if tabla.capacidad <= 0:
        return False
    idx = th_indice(tabla, clave)
    actual = tabla.buckets[idx]
    while actual is not None:
        if actual.clave == clave:
            if valor is not None:
                if valor:
                    valor[0] = actual.valor
                else:
                    valor.append(actual.valor)
            return True
        actual = actual.siguiente
    return False


def th_contiene(tabla: TablaHash, clave: int) -> bool:
    return th_buscar(tabla, clave, None)


def th_eliminar(tabla: TablaHash, clave: int) -> bool:
    if tabla.capacidad <= 0:
        return False
    idx = th_indice(tabla, clave)
    actual = tabla.buckets[idx]
    previo: THNodo | None = None
    while actual is not None:
        if actual.clave == clave:
            if previo is None:
                tabla.buckets[idx] = actual.siguiente
            else:
                previo.siguiente = actual.siguiente
            tabla.cantidad -= 1
            return True
        previo = actual
        actual = actual.siguiente
    return False


def th_vaciar(tabla: TablaHash) -> None:
    if tabla.capacidad <= 0:
        return
    tabla.buckets = [None] * tabla.capacidad
    tabla.cantidad = 0


def th_destruir(tabla: TablaHash) -> None:
    tabla.buckets = []
    tabla.capacidad = 0
    tabla.cantidad = 0


def th_vacia(tabla: TablaHash) -> bool:
    return tabla.cantidad == 0


def th_cantidad(tabla: TablaHash) -> int:
    return tabla.cantidad


def th_capacidad(tabla: TablaHash) -> int:
    return tabla.capacidad


def th_estadisticas(tabla: TablaHash) -> THEstadisticas:
    ocupados = 0
    colisiones = 0
    for bucket in tabla.buckets:
        if bucket is None:
            continue
        ocupados += 1
        longitud = 0
        actual = bucket
        while actual is not None:
            longitud += 1
            actual = actual.siguiente
        if longitud > 1:
            colisiones += longitud - 1
    factor = (tabla.cantidad / tabla.capacidad) if tabla.capacidad > 0 else 0.0
    return THEstadisticas(
        capacidad=tabla.capacidad,
        cantidad=tabla.cantidad,
        buckets_ocupados=ocupados,
        colisiones=colisiones,
        factor_carga=factor,
    )


def th_formatear(tabla: TablaHash, destino: list[str] | None, capacidad: int) -> None:
    if capacidad <= 0 or destino is None:
        return
    partes: list[str] = []
    for i, bucket in enumerate(tabla.buckets):
        valores: list[str] = []
        actual = bucket
        while actual is not None:
            valores.append(f"({actual.clave}:{actual.valor})")
            actual = actual.siguiente
        partes.append(f"{i}: " + (" -> ".join(valores) if valores else "[]"))
    texto = " | ".join(partes) if partes else "(sin inicializar)"
    texto = texto[: max(0, capacidad - 1)]
    if destino:
        destino[0] = texto
    else:
        destino.append(texto)


def th_formatear_estadisticas(tabla: TablaHash, destino: list[str] | None, capacidad: int) -> None:
    if capacidad <= 0 or destino is None:
        return
    stats = th_estadisticas(tabla)
    texto = (
        f"capacidad={stats.capacidad}, cantidad={stats.cantidad}, "
        f"buckets_ocupados={stats.buckets_ocupados}, colisiones={stats.colisiones}, "
        f"factor_carga={stats.factor_carga:.3f}"
    )
    texto = texto[: max(0, capacidad - 1)]
    if destino:
        destino[0] = texto
    else:
        destino.append(texto)

