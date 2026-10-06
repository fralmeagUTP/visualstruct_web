"""Actual session caller for the stack TAD; results are computed by C."""
from __future__ import annotations
from typing import Any
from app.adapters.base_adapter import BaseAdapter


def build_stack_main(history: list[dict[str, Any]]) -> str:
    """Reproduce successful mutations and release all caller-owned nodes."""
    code = ['/** @file main.c @brief Reproduce el historial de Pila con el TAD C real. */',
        '#include <limits.h>', '#include <stddef.h>', '#include <stdio.h>', '#include "tad_pila.h"',
        '/** @brief Ejecuta el historial y libera la pila al terminar. @return 0 en éxito, 1 si malloc falla. */',
        'int main(void) {', '    ptrPila pila = NULL;']
    for step in history:
        operation = step.get('operation')
        if operation == 'apilar':
            value = BaseAdapter._require_int(step.get('payload', {}), 'value', 'valor')
            if not -2147483648 <= value <= 2147483647:
                raise ValueError('El historial contiene un entero fuera del rango int del TAD C.')
            literal = 'INT_MIN' if value == -2147483648 else 'INT_MAX' if value == 2147483647 else str(value)
            code += ['    {', '        ptrPila anterior = pila;', f'        pila_apilar(&pila, {literal});',
                '        if (pila == anterior) { pila_destruir(&pila); return 1; }',
                '        printf("push:%d\\n", pila_cima(pila));', '    }']
        elif operation == 'desapilar':
            code.append('    printf("pop:%d\\n", pila_desapilar(&pila));')
        elif operation == 'limpiar':
            code += ['    pila_destruir(&pila);', '    puts("clear");']
    code += ['    printf("state:[");', '    for (ptrPila nodo = pila; nodo != NULL; nodo = nodo->sgte) {',
        '        printf("%s%d", nodo == pila ? "" : ",", nodo->nro);', '    }', '    puts("]");',
        '    pila_destruir(&pila);', '    return 0;', '}']
    return '\n'.join(code) + '\n'
