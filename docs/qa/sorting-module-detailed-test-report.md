# Informe detallado de pruebas del módulo de ordenamiento

Fecha: 2026-08-23  
Resultado final: **APROBADO después de correcciones**

## Alcance y método

Se probaron directamente los once algoritmos disponibles: Intercambio, Selección, Inserción,
Burbuja, Shell, QuickSort, MergeSort, HeapSort, Counting Sort, Binsort y Radix Sort. Para cada
uno se ingresaron arreglos normales, ya ordenados, inversos, con duplicados, con números
negativos/cero/positivos y unitarios. También se probaron extremos de `int` C, tamaño máximo,
errores de formato, rangos de conteo excesivos y todas las opciones de API y reproducción.

El oráculo funcional fue el orden ascendente independiente más la conservación del
multiconjunto. La fidelidad didáctica se comprobó contra `tad_ordenamiento.c`, verificando cada
`line_index`, su `line_text`, continuidad de frames, estado visual final y equivalencia entre
modo rápido y paso a paso.

## Resultado por algoritmo

| Método | Normal | Ordenado | Inverso | Duplicados | Con signos | Unitario | Resultado |
|---|---:|---:|---:|---:|---:|---:|---|
| Intercambio | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Aprobado |
| Selección | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Aprobado |
| Inserción | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Aprobado |
| Burbuja | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Aprobado |
| Shell | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Aprobado |
| QuickSort | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Aprobado |
| MergeSort | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Aprobado |
| HeapSort | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Aprobado |
| Counting Sort | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Aprobado |
| Binsort | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Aprobado |
| Radix Sort | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Aprobado |

Counting Sort y Binsort rechazaron correctamente `[-2147483648, 2147483647]` porque el rango
supera `ORDENAMIENTO_RANGO_MAX`; la entrada se conservó intacta. Los otros nueve métodos
ordenaron los extremos. Radix Sort ordenó `INT_MIN` bajo ASan/UBSan sin overflow.

## Opciones y operaciones

| Operación/opción | Caso ejecutado | Resultado |
|---|---|---|
| Crear manual | `5,-1,3,3,0` | Aprobado |
| Generar aleatorio | tamaño 80, rango -10..10, semilla 20260823 | Reproducible, aprobado |
| Seleccionar algoritmo | los 11 identificadores | Aprobado |
| Modo rápido | los 11 métodos | Aprobado |
| Paso a paso | los 11 métodos | Aprobado |
| Siguiente/anterior | `next`, `previous` y `prev` | Aprobado |
| Estado | consulta tras generación y selección | Aprobado |
| Reiniciar | estado e historial del módulo | Aprobado |
| UI real | ingreso manual y ejecución de los 11 métodos en Chromium | Aprobado |

## Problemas encontrados y arreglos

### SORT-QA-001 — Código C del algoritmo equivocado (alta)

- Observado: si la selección persistida era Burbuja y `run` solicitaba QuickSort, se ejecutaba
  QuickSort pero se construía la traza con el fragmento de Burbuja.
- Corrección: el servicio ahora resuelve el código usando el algoritmo efectivo solicitado.
- Regresión: `test_run_algorithm_override_uses_matching_c_source`.

### SORT-QA-002 — Pasos sin línea C (alta)

- Observado: 55 frames de Selección, Inserción, Shell, QuickSort y HeapSort tenían
  `line_index=None`, principalmente porque no se mostraban auxiliares transitivos.
- Corrección: se agregaron patrones faltantes y se incluyeron `quicksort_recursivo` y `heapify`
  en el código visible; HeapSort distingue comparación izquierda y derecha.
- Resultado: cero pasos sin línea en los once métodos.

### SORT-QA-003 — Valores fuera de `int` C (alta)

- Observado: Python aceptaba `2147483648` y `-2147483649`, aunque el C mostrado usa `int`.
- Corrección: validación central de `INT_MIN..INT_MAX` para creación manual y aleatoria.
- La validación fallida no modifica el arreglo previo.

### SORT-QA-004 — Incompatibilidad `prev`/`previous` (media)

- Observado: la especificación y cliente podían enviar `prev`, pero el adaptador lo rechazaba.
- Corrección: `prev` se normaliza a `previous`, conservando ambos contratos.

### SORT-QA-005 — CSV incompleto aceptado (media)

- Observado: `1,,2`, `,1,2` y `1,2,` omitían silenciosamente posiciones vacías.
- Corrección: se rechaza cualquier posición vacía o no entera con mensaje didáctico y sin mutación.

### SORT-QA-006 — Consola `printf` falsa (alta)

- Observado: notas internas y el mensaje HTTP se mostraban con prefijo `[printf]`, aunque los
  algoritmos C no ejecutan `printf`.
- Corrección: la consola sólo consume `console_events` reales; para estas rutas muestra que no
  hubo salida, sin inventarla.

### SORT-QA-007 — Funciones comunes ausentes del seguimiento (alta)

- Observado: el algoritmo llamaba realmente `arreglo_valido` y, según el método,
  `intercambiar`, pero el panel sólo mostraba la función pública.
- Corrección: cada fragmento incluye ahora sus dependencias transitivas y la traza entra en
  ellas. Los once métodos recorren `arreglo_valido`; Intercambio, Selección, Burbuja, QuickSort
  y HeapSort recorren la guarda, `temporal`, `*a = *b` y `*b = temporal` de `intercambiar`.
  La visualización muestra la variable `temporal` y los estados transitorios de las asignaciones.

### SORT-QA-008 — El arreglo aleatorio cambiaba al reproducir (alta)

- Observado: al generar sin semilla explícita se guardaba una semilla vacía. La reconstrucción
  previa a seleccionar o reproducir invocaba de nuevo el generador y producía otros valores.
- Corrección: el generador materializa una semilla efectiva, la devuelve y el servicio la
  persiste en el historial. Todo replay reconstruye exactamente el arreglo mostrado originalmente.

## Evidencia de cierre

- 150 pruebas específicas del módulo aprobadas.
- 66 combinaciones algoritmo/partición aprobadas.
- 11 equivalencias rápido/paso a paso aprobadas.
- 11 verificaciones completas de línea C aprobadas.
- Prueba Playwright de los 11 algoritmos y controles aprobada.
- Harness C17 aprobado.
- ASan y UBSan en Linux aprobados.
- Suite general: **800 pruebas aprobadas**.
- OpenSpec validado en modo estricto.

La matriz legible por herramientas está en `docs/qa/sorting-module-test-results-v1.json`.
