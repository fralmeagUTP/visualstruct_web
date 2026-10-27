"""Generate a C17 caller from confirmed mutations and observed queries."""
from __future__ import annotations
from typing import Any


def build_hash_main(history: list[dict[str, Any]]) -> str:
    """Emit checked allocation/results and a single cleanup on every exit."""
    lines = ['/** @file main.c', ' * @brief Caller Hash H1 de mutaciones y consultas C observadas.',
        ' * @details Enteros C y capacidad fija; recrear libera primero la instancia anterior.',
        ' * Un fallo real de reserva se informa y sale por cleanup. No inyecta fallos QA.',
        ' * Consultas ausentes se reproducen; validaciones rechazadas no llaman C.',
        ' */', '#include "tad_tabla_hash.h"', '#include <stdio.h>', '#include <limits.h>', '',
        '/** @brief Ejecuta el historial y libera todos los objetos.',
        ' * @return 0 en exito; 1 ante fallo de reserva o insercion.', ' */',
        'int main(void) {', '    TablaHash tabla = {0};', '    int status = 0;',
        '    th_inicializar(&tabla, 17);', '    if (!tabla.buckets) { status = 1; goto cleanup; }']
    for step in history:
        op, p = step['operation'], step['payload']
        if op == 'create_table':
            cap = int(p['capacity'])
            lines += ['    th_destruir(&tabla);', f'    th_inicializar(&tabla, {cap});',
                '    if (!tabla.buckets) { status = 1; goto cleanup; }',
                '    printf("create:%d\\n", tabla.capacidad);']
        elif op == 'insert':
            key, value = (('INT_MIN' if int(p[name]) == -2147483648 else str(int(p[name]))) for name in ('key', 'value'))
            lines += [f'    {{ bool ok = th_insertar(&tabla, {key}, {value});',
                f'      printf("insert:%d:%d:%d\\n", {key}, {value}, (int)ok);',
                '      if (!ok) { status = 1; goto cleanup; } }']
        elif op == 'get':
            key = 'INT_MIN' if int(p['key']) == -2147483648 else str(int(p['key']))
            lines += [f'    {{ int output = 123456789; bool found = th_buscar(&tabla, {key}, &output);',
                f'      printf("get:%d:%d", {key}, (int)found);',
                '      if (found) printf(":%d", output);', '      printf("\\n"); }']
        elif op == 'contains':
            key = 'INT_MIN' if int(p['key']) == -2147483648 else str(int(p['key']))
            lines += [f'    printf("contains:%d:%d\\n", {key}, (int)th_contiene(&tabla, {key}));']
        elif op == 'stats':
            lines += ['    { THEstadisticas stats = th_estadisticas(&tabla);',
                '      char texto[512];',
                '      th_formatear_estadisticas(&tabla, texto, sizeof(texto));',
                '      printf("stats-C:%d:%d:%d:%d:%.9g\\n", stats.capacidad, stats.cantidad,',
                '             stats.buckets_ocupados, stats.colisiones, (double)stats.factor_carga);',
                '      printf("stats-format:\\n%s", texto);',
                '      printf("stats-API-projection:%d:%d:%.17g\\n", tabla.capacidad, tabla.cantidad,',
                '             tabla.capacidad > 0 ? (double)tabla.cantidad / (double)tabla.capacidad : 0.0); }']
        elif op in {'keys', 'values', 'items'}:
            # Existing formatter text and independent public-field API projection.
            lines += ['    { char buffer[2048];',
                '      th_formatear(&tabla, buffer, sizeof(buffer));',
                f'      printf("format:{op}:\\n%s", buffer);',
                f'      printf("{op}:");',
                '      for (int i = 0; tabla.buckets && i < tabla.capacidad; i++) {',
                '        for (const THNodo *node = tabla.buckets[i]; node; node = node->siguiente) {']
            projection = 'node->clave' if op == 'keys' else 'node->valor'
            lines += ['          printf("%d:%d;", node->clave, node->valor);' if op == 'items'
                else f'          printf("%d;", {projection});']
            lines += ['        }', '      }', '      printf("\\n"); }']
        elif op == 'remove':
            lines += [f'    printf("remove:%d\\n", (int)th_eliminar(&tabla, {int(p["key"])}));']
        elif op in {'clear', 'destroy_table'}:
            lines += ['    th_vaciar(&tabla);' if op == 'clear' else '    th_destruir(&tabla);']
    lines += ['    printf("state:%d:%d\\n", tabla.capacidad, tabla.cantidad);',
        'cleanup:', '    th_destruir(&tabla);', '    return status;', '}']
    return '\n'.join(lines) + '\n'
