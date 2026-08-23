# Propuesta: Mejorar la pedagogía del módulo de tablas hash

## Why

El módulo representa buckets y cadenas de colisión, pero todavía no explica de manera causal cómo el código C calcula el índice, recorre enlaces, actualiza una clave o elimina un nodo. Además existen divergencias didácticas críticas: la ayuda anuncia redimensionamiento automático aunque el TAD tiene capacidad fija; la interfaz acepta valores de texto mientras el C almacena enteros; y el wrapper sustituye claves visibles por identificadores internos sin explicarlo.

Estas diferencias pueden producir una interpretación falsa del programa C y dificultan enseñar función hash, colisiones, complejidad y memoria dinámica.

## What Changes

- Adoptar como contrato inicial una tabla de capacidad fija con claves y valores enteros, fiel al TAD C actual.
- Eliminar afirmaciones y estados de rehash/redimensionamiento inexistentes; un rehash real requerirá otro cambio explícito.
- Eliminar la sustitución oculta de claves o, durante la migración, exponerla como una capa no equivalente al C y bloquear la presentación de ejecución directa.
- Garantizar que las llamadas y el `main` generados sean C17 compilable y usen los valores realmente ejecutados.
- Emitir frames hash canónicos con índice, expresión módulo, normalización de negativos, cadena, comparaciones, punteros, memoria e invariante.
- Reorganizar la pantalla en Preparar, Predecir, Ejecutar, Comprender, Relacionar con C, Comparar y Reflexionar.
- Visualizar inserción sin colisión, colisión, actualización, búsqueda exitosa/fallida y los casos de eliminación.
- Diferenciar `th_vaciar` de `th_destruir` y enseñar propiedad/liberación de memoria.
- Añadir niveles, ejemplos guiados, predicciones, pistas, práctica, navegación completa y progreso conceptual de sesión.
- Comparar capacidades sobre copias aisladas de una entrada inmutable y mostrar distribución, colisiones y costo observado.
- Ampliar ayuda, glosario, guía docente, accesibilidad y exportación.
- Cerrar con contratos, golden traces, propiedades, equivalencia rápido/paso a paso, Playwright, cobertura, C17, ASan y UBSan.

## Out of Scope

- Implementar direccionamiento abierto, sondeo lineal/cuadrático o doble hashing.
- Añadir redimensionamiento automático sin una implementación C, backend, traza y UI completa.
- Aceptar valores de texto mientras el contrato público se presente como ejecución directa del TAD C `int`/`int`.
- Ejecutar código C arbitrario suministrado por el usuario.
- Persistir calificaciones o datos personales fuera de la sesión.

## Dependencies

- Reutiliza el motor común de trazas, reproducción, consola y exportación.
- Requiere alinear `tad_tabla_hash.c`, wrapper, adaptador, historial técnico y visualización.
- Conserva el encadenamiento separado y la normalización de claves negativas del TAD.

## Impact

- Dominio C/wrapper: claves reales, valores enteros y ciclo de vida verificable.
- Backend: contrato de frames, invariantes, ejemplos y comparaciones aisladas.
- Frontend: arquitectura pedagógica, punteros, cadenas activas, práctica y métricas.
- Ayuda: política de capacidad fija, complejidad, memoria y errores frecuentes.
- QA: conformidad C/backend/traza/consola/historial/UI y pruebas de accesibilidad.
