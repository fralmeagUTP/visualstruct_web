"""Generate a C17 caller from confirmed mutations and observed queries."""
from __future__ import annotations
from typing import Any
from app.services.hash_caller_program import output_lines


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
                *['    '+line for line in output_lines(op)]]
        elif op == 'insert':
            key, value = (('INT_MIN' if int(p[name]) == -2147483648 else str(int(p[name]))) for name in ('key', 'value'))
            lines += [f'    {{ bool ok = th_insertar(&tabla, {key}, {value});',
                *['      '+line for line in output_lines(op, {'key':key, 'value':value})],
                '      if (!ok) { status = 1; goto cleanup; } }']
        elif op == 'get':
            key = 'INT_MIN' if int(p['key']) == -2147483648 else str(int(p['key']))
            lines += [f'    {{ int output = 123456789; bool found = th_buscar(&tabla, {key}, &output);',
                *['      '+line for line in output_lines(op, {'key':key})], '    }']
        elif op == 'contains':
            key = 'INT_MIN' if int(p['key']) == -2147483648 else str(int(p['key']))
            lines += [f'    {{ bool found = th_contiene(&tabla, {key});',
                      *['      '+line for line in output_lines(op, {'key':key})], '    }']
        elif op == 'stats':
            lines += ['    { THEstadisticas stats = th_estadisticas(&tabla);',
                '      char texto[512];',
                '      th_formatear_estadisticas(&tabla, texto, sizeof(texto));',
                *['      '+line for line in output_lines(op)], '    }']
        elif op in {'keys', 'values', 'items'}:
            # Existing formatter text and independent public-field API projection.
            lines += ['    { char buffer[2048];',
                '      th_formatear(&tabla, buffer, sizeof(buffer));',
                *['      '+line for line in output_lines(op)], '    }']
        elif op == 'remove':
            key = 'INT_MIN' if int(p['key']) == -2147483648 else str(int(p['key']))
            lines += [f'    {{ bool removed = th_eliminar(&tabla, {key});',
                      *['      '+line for line in output_lines(op)], '    }']
        elif op in {'clear', 'destroy_table'}:
            lines += ['    th_vaciar(&tabla);' if op == 'clear' else '    th_destruir(&tabla);']
    lines += [*['    '+line for line in output_lines('epilogue')],
        'cleanup:', '    th_destruir(&tabla);', '    return status;', '}']
    return '\n'.join(lines) + '\n'
