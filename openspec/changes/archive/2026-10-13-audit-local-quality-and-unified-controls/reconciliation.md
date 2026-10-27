# Reconciliación documental previa

BORRADOR. 18 propuestas previas y 16 specs actuales inventariadas. Cumplimiento funcional NO verificado. El catálogo detallado se conserva en `commitment-inventory.md`; no representa aprobación funcional ni revisión semántica concluida de cada escenario.

## Decisiones por cambio
Los primeros 16 cambios están en `openspec/changes/archive/`; los dos últimos siguen abiertos. No se reabre automáticamente lo archivado ni se impone cuatro botones a todos los TAD.

| Cambio | Tratamiento propuesto |
|---|---|
| 2026-08-19-harden-trace-conformance-and-state | Mantener trazas, oráculo C, checkpoints, presupuesto de replay y métricas; verificar evidencia actual. Proxy/despliegue solo revisión local. |
| 2026-08-23-enhance-graph-structures-pedagogy | Mantener frames, auxiliares, algoritmos, invariantes, comparaciones y ayudas; simplificar controles por fase/estado. |
| 2026-08-23-enhance-hash-table-pedagogy | Mantener contrato C de tipos/capacidad, encadenamiento, memoria y costo; contrastar spec actual. |
| 2026-08-23-enhance-hierarchical-structures-pedagogy | Mantener recursión, rotaciones, recoloreos, heap, invariantes, ayuda y comparación. |
| 2026-08-23-enhance-sequential-structures-pedagogy | Mantener causalidad, punteros, memoria, ciclos, prioridades y aprendizaje; revisar accesibilidad. |
| 2026-08-23-enhance-sorting-pedagogy | Mantener estrategias, signos, variables, recursión, invariantes y comparación; adaptar controles. |
| 2026-08-23-establish-comprehensive-app-quality-validation | Mantener inventario, cobertura funcional, fidelidad C y reporte; actualizar evidencia. |
| 2026-08-23-remediate-didactic-c-trace-fidelity | Verificar regresiones y cierre real; no reabrir defectos sin evidencia. |
| 2026-08-23-validate-and-harden-sorting-module | Verificar creación, algoritmos, cursor y trazas de los once algoritmos. |
| 2026-09-25-extend-sequential-structural-visualizations | Mantener modos, enlaces, animación, carriles de Sublista, resultados plegables y C correlacionado. |
| 2026-09-25-organize-help-and-download-tad-sources | Mantener fuentes/dependencias/allowlist; ampliar a bytes HTTP, compilación, Doxygen y manual. |
| 2026-09-25-reorganize-graph-learning-workspace | Mantener fases, frame fiel, C y resultados; documentar controles propios por fase. |
| 2026-09-25-reorganize-hash-learning-workspace | Mantener flujo y encadenamiento; distinguir scroll de bucket del menú indebido. |
| 2026-09-25-reorganize-hierarchical-learning-workspace | Mantener visualización específica, C y resultados; simplificar por árbol/heap/estado. |
| 2026-09-25-reorganize-sorting-learning-workspace | Mantener representación, comparación y servicios; no eliminar capacidades por conteo. |
| 2026-09-25-separate-sequential-execution-and-playback | Mantener ejecución exactamente una vez y navegación no mutante; adaptar disposición. |
| audit-didactic-c-trace-fidelity | Mantener contraste por evento/capa; revisar pendientes de harness/memoria/consola/sanitizadores. |
| redesign-stack-learning-workspace | Mantener compactación y estado/C; verificar piloto antes de extensión y corregir scroll. |

## Conflictos y pendientes explícitos
- Modo rápido: spec actual deshabilita navegación; la petición nueva exige ocultarla. Delta incluido.
- Disposición Reproducir/Reiniciar y Anterior/Siguiente: sustituir por controles contextuales, preservando ejecución/navegación sin doble mutación.
- Hash vigente: H1 entero/capacidad fija aprobado y consolidado en `openspec/specs/hash-table/spec.md`; decisión `openspec/changes/archive/2026-10-02-reconcile-hash-integer-fixed-capacity/decision.md`. Verificación funcional, fidelidad por instrucción y sesiones legacy pendientes.
  - Fotografía histórica sustituida por H1 (nota 2026-10-02T18:12:42.165328+00:00): Hash: spec actual enumera texto/rehash; delta pedagógico archivado pide tipos fieles/capacidad fija. Contrastar C, adapters, descargas y guía; consultar cambios semánticos mayores.
- Specs actuales no incorporan todos los compromisos pedagógicos archivados. Revisar por escenario, sin dar por cumplido lo archivado.
- Auditoría C abierta: pendientes instrumentación por instrucción, identidad/enlaces/reservas/liberaciones, captura printf/retornos/errores y C17/ASan/UBSan.
- Pila abierta: pendientes medición y responsive, límites de scroll/foco/contraste, operaciones repetidas, sincronización C, teclado/movimiento reducido, capturas, aprobación antes de extensión y conservación de traza al plegar.

## Specs actuales incluidas
application-shell; c-code-interpreter; graph-learning-workspace; graph-structures; hash-learning-workspace; hash-table; help-system; hierarchical-learning-workspace; hierarchical-structures; sequential-structural-visualization; sequential-structures; sequential-workspace-consistency; session-state; sorting-learning-workspace; sorting-visualizer; visual-playback-ui.

Cada requisito se registra como mantener/verificar, sustituir por delta aprobado o fuera de alcance justificado. Clasificación final por escenario y evidencia después de aprobación; generar un inventario no concluye esa revisión.


## Reconciliación individual publicada
Revisión documental individual en reconciliation-detailed.md y evidence/prior-commitment-reconciliation.json: 315 requisitos, 424 escenarios, 679 tareas y 235 secciones proposal/design. Sus textos, rutas, líneas y SHA se conservan; clasificación no infiere aprobación funcional. Se conserva lo aplicable, se sustituye solo disposición/visibilidad aprobada y se registra conflicto Hash texto/rehash vs C entero/capacidad fija sin rediseñar runtime. Los seis algoritmos de Grafos requeridos están presentes; sus obligaciones nativas intermedias y las de ABB/AVL/Rojo-Negro/heap siguen retenidas. Ninguna propuesta anterior se reabre ni se altera su estado.


Nota de precedencia H1 (2026-10-02T18:12:42.165328+00:00): el conflicto texto/rehash descrito en el registro individual anterior es histórico. Rige entero/capacidad fija según decisión H1 citada; inventario, hashes y observaciones originales se conservan. Esta corrección documental no acredita cobertura funcional de Hash ni C1; C1 continúa1/12, cero cierres nuevos.
