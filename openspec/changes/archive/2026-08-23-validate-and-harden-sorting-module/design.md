# Diseño de validación

## Oráculos

1. `sorted(input)` como oráculo funcional independiente.
2. Harness C17 de `tad_ordenamiento.c` como oráculo semántico del C mostrado.
3. Estado final del modo rápido contra el último frame del modo paso a paso.
4. Continuidad entre `state_after[i]` y `state_snapshot[i+1]`.
5. Correspondencia exacta entre `line_index`, `line_text` y el fragmento C visible.

## Particiones de entrada

- caso normal desordenado;
- ya ordenado y orden inverso;
- duplicados y todos iguales;
- negativos, cero y positivos;
- un elemento;
- extremos `INT_MIN`/`INT_MAX`;
- tamaño máximo permitido;
- entradas vacías, malformadas, fuera de rango y rangos de conteo excesivos.

Counting Sort y Binsort deben rechazar rangos superiores al límite publicado sin reservar
memoria. Los demás algoritmos deben ordenar extremos de `int`; Radix Sort debe hacerlo sin
negar `INT_MIN` en un `int` con overflow.

## Evidencia

El informe final se publica en `docs/qa/sorting-module-detailed-test-report.md` y una matriz
estructurada en `docs/qa/sorting-module-test-results-v1.json`.
