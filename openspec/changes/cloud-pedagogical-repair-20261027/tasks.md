# Tareas — estado verificable 2026-10-27 09:39 UTC

- [x] pedagogical-repair: alcance finito completado, revisión independiente y paquete reversible verificados; decisiones de convergencia libro/IA siguen pendientes fuera de este cierre.

## Alcance y continuidad
- [x] Inventario finito de operaciones y algoritmos (`qa/inventory.json`); baseline reversible preservado.
- [x] Separar servidor/cookie/cache de reparación del original.
- [x] Registrar requisitos y contratos de cinco roles; no interpretar cierres históricos como pruebas actuales.

## Reparaciones y criterios reproducibles
- [x] Ordenamiento inexistente responde400 sin mutar historia, no500 (`qa/test_sorting_regressions.py`).
- [x] Validación enteros C32 y entrada inválida no ejecuta/simula cuerpo C; conserva históricos previos (`qa/test_history_validation.py`, revisión independiente `qa_trazas`).
- [x] Reproductor atómico, cancelación de carga/avance y cierre/reinicio coherentes (`qa/test_trace_player*.js`).
- [x] Ocultar comentarios no oculta escrituras por punteros (`qa/test_c_code_navigation.js` + UI002).
- [x] Comprender conciso contextual y referencia opcional, sin paneles vacíos iniciales (`qa/test_contextual_help.js`); recorrido UI global aún pendiente.
- [x] Vista sorting código/imagen/memoria estable, ajuste de línea sin recorte; UI003/UI008 revalidados con clics nativos.
- [x] Memoria compacta Shell/Radix describe valores y reserva/liberación, sin objectObject; UI004/UI005 revalidados.
- [x] Reset sorting sincroniza algoritmo/código/datos; cancelación conserva estado; UI006 revalidado.
- [x] JPG usa descarga Blob y errores/timeout observables; UI007 descarga y píxeles reales revalidados.
- [x] Main C exportado compila y ejecuta resultado real:9mains+70operaciones,9balances memoria; revisión independiente.
- [x] Límite de capacidad pedagógica hash: servidor/UI, rechazo sin mutación, histórico preservado: backend, revisión independiente y suspensión/exportación/reset UI PASS.

## Cobertura UI en orden solicitado
- [x] Ordenamiento:11algoritmos normales y todas sus trazas en casos definidos;6operaciones, variantes negativas/cero/duplicados, validaciones, controles, teclado y descargas. Evidencia `qa_ui`.
- [x] Secuenciales:29operaciones visibles/6TAD normales y paso a paso, variantes y controles expuestos;6JPG abiertos,12C/H descargados y6mainDOM exactos compilados/ejecutados. Cierre definido UI07:33.
- [x] Jerárquicas:33operaciones normales/paso/reversa,4resets,4mainsDOM literales C17,8C/H y4JPG reales; predicción/4comparaciones y memoria revisadas. Cierre definido UI08:25.
- [x] Grafos: operaciones/fases, reservas/enlaces, controles y descargables. 16acciones normal/paso completas, JPG panel/global completos y C/main compilables; guía15 y retornoNULL revalidados.
- [x] Hash:11operaciones normal/paso/reversa, colisiones/memoria/capacidades, controles, guías y exports.

## Cierre
- [x] Matriz backend independiente423invocaciones/103operaciones, sin errores detectados en el conjunto definido (antes parche grafo separado).
- [x] Descarga26C/H y13TAD compilación/ejecución/sanitizadores (antes parche grafo separado); sin atribuir reparación al C que ya funcionaba.
- [x] Regresiones agregadas:43métodos Python y27scripts Node PASS; revisión independiente actual423invocaciones, C descargado y guard grafo incluidos.
- [x] Revisiones independientes calidad/visual/documentación y cinco gates de roles aprobados.
- [x] Paquete reversible, manifiesto y límites; primera extracción fresca43Python/27Node y rollback byte-exacto PASS. Coordinador separado. Verificación final versionada en deliverables/verification.json.

Parche mínimo de invariante grafo tiene alcance y evidencias propios en `cloud-graph-invariant-20261027`. Igualación canónica completa libro/web NO resuelta:11firmas y29cuerpos grafo divergentes preexistentes, decisión pendiente. No marcar aplicación completa por el cierre de una familia.
