# Propuesta: corregir divergencias de fidelidad didáctica C

## Why

La auditoría `audit-didactic-c-trace-fidelity` encontró 29 discrepancias reproducibles entre el
código C, el backend, la traza, la consola y la visualización: una crítica y 28 altas. Estas
divergencias pueden ejecutar una semántica distinta de la mostrada, presentar estados visuales
falsos o enseñar pasos que el algoritmo C nunca ejecutó.

El informe y los casos mínimos ya están publicados en `docs/qa/`. Este cambio autoriza convertir
esa evidencia en correcciones funcionales, manteniendo el código C y la visualización bajo un
único contrato verificable.

## What Changes

- Corrige primero el comportamiento indefinido de Radix Sort con `INT_MIN` y limita el consumo de
  memoria de Counting/Bin Sort.
- Unifica los contratos C/Python/UI de grafos, tabla hash, pila, cola, cola de prioridad y lista
  enlazada, eliminando snippets inexistentes y algoritmos equivalentes sólo en estado final.
- Hace que cada frame visual derive del evento C causal, incluyendo temporales, enlaces,
  rotaciones, recoloreos, sift, relajaciones y estructuras auxiliares.
- Endurece el contrato de traza: continuidad `after→before`, línea fuente válida y consola
  procedente de eventos reales, no de inferencias sobre el texto C.
- Añade una prueba de regresión por cada caso `SORT/GRAPH/HASH/.../TRACE` publicado y gates C17,
  ASan/UBSan, backend y frontend.
- Migra de forma explícita cualquier estado de sesión afectado por cambios de contrato.

## Scope

Incluye los 29 casos de `docs/qa/findings/`, clasificados como P0, P1 y P2 en
`docs/qa/correction-backlog.md`, y las capas C, dominio Python, adapters, planificadores de traza,
servicio de código C, renderers JavaScript y pruebas relacionadas.

## Out of Scope

- Añadir TAD o algoritmos nuevos que no sean necesarios para cerrar una operación ya expuesta.
- Rediseñar la apariencia general de la aplicación.
- Cambiar la semántica pública sin documentar compatibilidad, migración y decisión arquitectónica.
- Cerrar la auditoría original antes de completar su matriz Linux ASan/UBSan pendiente.

## Success Criteria

- Los 29 casos mínimos pasan como regresiones y dejan de producir su divergencia documentada.
- Los 120 resultados del inventario conservan evidencia y no aparece una operación sin contrato C
  explícito o exclusión justificada.
- Modo rápido y todas las rutas paso a paso terminan en el mismo estado canónico.
- Cada frame, resaltado y salida de consola corresponde al evento C que lo causa.
- Compilación C17 estricta, sanitizers, pruebas backend y pruebas UI terminan sin fallos nuevos.

