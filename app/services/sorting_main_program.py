"""Generate a C17 caller from validated sorting history, without computed output literals."""
from __future__ import annotations
from typing import Any
from app.domain.sorting import SORTING_ALGORITHMS

_C_FUNCTIONS = {item['id']: item['c_function'] for item in SORTING_ALGORITHMS}
_C_INT_RETURNS = {'mergesort', 'counting_sort', 'binsort', 'radixsort'}


def _values(values: Any) -> list[int]:
    """Require the normalized, materialized int32 values accepted by the server."""
    if not isinstance(values, list) or not 1 <= len(values) <= 80:
        raise ValueError('El main requiere valores materializados de 1 a 80 elementos.')
    if any(type(value) is not int or not -(2**31) <= value <= 2**31 - 1 for value in values):
        raise ValueError('El main requiere enteros int32 validados.')
    return list(values)


def _literal(value: int) -> str:
    return 'INT_MIN' if value == -(2**31) else 'INT_MAX' if value == 2**31 - 1 else str(value)


def build_sorting_main(history: list[dict[str, Any]]) -> str:
    """Replay accepted creations/runs chronologically with actual C signatures."""
    lines = [
        '/** @file main.c',
        ' * @brief Reproduce el historial aceptado de Ordenamientos.',
        ' * @details Compilar: gcc -std=c17 -Wall -Wextra -pedantic main.c tad_ordenamiento.c -o ordenamiento',
        ' * Datos aleatorios materializados; no usa rand ni resultados precalculados.',
        ' * Arreglo automatico de 80 enteros. El TAD libera sus auxiliares internos.',
        ' */',
        '#include <stdio.h>', '#include <stddef.h>', '#include <limits.h>',
        '#include "tad_ordenamiento.h"',
        '#if INT_MAX != 2147483647 || INT_MIN != (-2147483647 - 1)',
        '#error "Este ejemplo reproduce el contrato int32 de la aplicacion."',
        '#endif',
        '/** @brief Ejecuta en orden creaciones y ordenamientos aceptados.',
        ' * @return 0 si termina; 1 si un metodo int reporta un fallo nativo, incluida memoria.',
        ' */',
        'int main(void) {', '    int arreglo[80] = {0};', '    size_t n = 0;',
    ]
    current: list[int] | None = None
    selected = 'burbuja'
    run_number = 0
    for entry in history:
        operation, payload = entry['operation'], entry['payload']
        if operation in {'create_array', 'generate_random_array'}:
            current = _values(payload['values'] if operation == 'create_array' else entry['materialized_values'])
            lines.append('    /* Nueva creacion: reemplaza los datos corrientes. */')
            lines.append(f'    n = {len(current)};')
            lines.extend(f'    arreglo[{index}] = {_literal(value)};' for index, value in enumerate(current))
            lines.append('    imprimir_arreglo(arreglo, n);')
        elif operation == 'select_algorithm':
            selected = payload['algorithm_id']
            if selected not in _C_FUNCTIONS:
                raise ValueError('Metodo del main no reconocido.')
            lines.append(f'    /* Metodo preparado: {_C_FUNCTIONS[selected]}; seleccion no ejecuta el TAD. */')
        elif operation == 'run':
            selected = payload['algorithm_id']
            effect = entry['array_effect']
            if selected not in _C_FUNCTIONS or current is None or effect['input'] != current or effect['output'] != sorted(current):
                raise ValueError('Historial no cronologico para generar el main.')
            run_number += 1
            function = _C_FUNCTIONS[selected]
            lines.append(f'    printf("Run {run_number}: {function}\\n");')
            if selected in _C_INT_RETURNS:
                status = f'estado_{run_number}'
                lines.extend([
                    f'    int {status} = {function}(arreglo, n);',
                    f'    printf("Estado: %d\\n", {status});',
                    f'    if ({status} != ORDENAMIENTO_OK) {{',
                    '        fprintf(stderr, "El TAD reporto un fallo; no se imprime un resultado exitoso.\\n");',
                    '        return 1;', '    }',
                ])
            else:
                lines.append(f'    {function}(arreglo, n);')
            lines.append('    imprimir_arreglo(arreglo, n);')
            # This effect validates the next caller input; it is never emitted as C output.
            current = list(effect['output'])
    if current is None:
        lines.append('    imprimir_arreglo(arreglo, n);')
    lines.extend(['    return 0;', '}'])
    return '\n'.join(lines) + '\n'
