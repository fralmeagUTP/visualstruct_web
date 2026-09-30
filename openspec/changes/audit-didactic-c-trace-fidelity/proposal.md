# Propuesta: auditar la fidelidad didáctica del intérprete C

## Why

VisualEstruct presenta como ejecución didáctica una cadena de artefactos distintos: código C,
implementación Python, estado del adapter, traza técnica, consola y representación visual. Aunque
existen pruebas de conformidad del estado final, una aplicación educativa también debe demostrar
que cada paso mostrado corresponde a una instrucción realmente ejecutada, que no inventa ramas ni
omite mutaciones relevantes y que los controles de reproducción conservan el mismo resultado.

Una divergencia intermedia puede enseñar una semántica falsa aun cuando el estado final coincida.
Se requiere por ello una auditoría exhaustiva, reproducible y basada en evidencia para todas las
estructuras y operaciones disponibles.

## What Changes

- Se define una matriz QA que cubre estructuras secuenciales, árboles, montículo, grafos, tabla
  hash y los once algoritmos de ordenamiento.
- Se establece el código C de `docs/tads_C/` como oráculo primario, ejecutado mediante harnesses
  instrumentados que permitan observar estados y eventos relevantes.
- Se comparan, paso por paso, el oráculo C, el backend, la traza, el historial técnico, la consola
  y el frontend, además de verificar la equivalencia entre modo rápido y paso a paso.
- Se exige que la representación visual de cada TAD sea dirigida por la instrucción C que se está
  interpretando: cada cambio visible debe ocurrir en el mismo paso causal que la mutación C y no
  puede anticipar, retrasar ni inventar estados a partir del resultado final.
- Se incorporan casos normales, límites, entradas inválidas, memoria dinámica, punteros,
  recursión y todas las construcciones de control presentes en el código.
- Se normaliza un informe de hallazgos con severidad, causa probable, localización, prueba de
  regresión recomendada y corrección sugerida.
- La auditoría no modifica código productivo; cualquier corrección requerirá autorización y un
  cambio posterior.

## Scope

Incluye los 13 TAD (`stack`, `queue`, `priority_queue`, `linked_list`, `circular_list`, `sublist`,
`abb`, `avl`, `red_black`, `binary_heap`, `graph`, `hash_table`, `sorting`) y todas las operaciones
expuestas por sus adapters/rutas. Para ordenamiento incluye `intercambio`, `seleccion`, `insercion`,
`burbuja`, `shell`, `quicksort`, `mergesort`, `heapsort`, `counting_sort`, `binsort` y `radixsort`.

## Out of Scope

- Corregir automáticamente los defectos encontrados.
- Rediseñar la interfaz o cambiar los contratos públicos.
- Aceptar diferencias didácticas sin documentar su justificación y evidencia.

## Success Criteria

La auditoría estará completa cuando cada operación registrada tenga casos normales, límite e
inválidos ejecutados; cada resultado tenga evidencia C/backend/traza/UI; todos los fallos tengan
severidad y prueba de regresión propuesta; y no quede ninguna divergencia crítica o alta sin
documentar y priorizar.
