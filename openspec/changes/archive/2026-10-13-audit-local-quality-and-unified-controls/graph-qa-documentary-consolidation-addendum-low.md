# Graph: consolidación LOW tras QA independiente

FechaUTC 2026-10-04T06:29:42.435379+00:00. Asignación coordination-graph-qa-documentary-consolidation-low-20261004, misma operación Graph abierta graph.bellman-prim-integer-cycle-approved-medium. Fuente de autorización instrucción vigente (evidencia local: `openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/graph-qa-documentary-consolidation-instruction-low.json`). Dictamen real [QA](evidence/independent-review-graph-three-approved-adjustments/review.md), checks (evidencia local: `openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/independent-review-graph-three-approved-adjustments/checks-report.json`), guardas verificadas (evidencia local: `openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/independent-review-graph-three-approved-adjustments/verify.json`).

## GRAPH-QA-DOC-01 corregido: métrica del autor

Esta corrección prevalece sobre el término CPU en los checkpoints2/3 y publicaciones/resources-comparison del autor; esos originales permanecen intactos como historia. Su script usa perf_counter: son tiempos transcurridos de generación+serialización con tracemalloc, no mediciones de CPU de proceso. Antes=frozenFreeze1 verificado en C temporal, después=D actual del bloque2, mismas entradas3vértices/hashC/eventos/pasos; dos procesos lanzados concurrentemente, una observación por versión/algoritmo, sin benchmark estadístico. El main del bloque3 se añadió después de esa medición.

| Algoritmo | Tiempo transcurrido antes→después | Aumento | JSON menor | Pico Python menor |
|---|---|---|---|---|
| Bellman-Ford |9.713→12.672s|30.47%|87.72%|73.33%|
| Prim |16.867→21.093s|25.05%|89.54%|78.09%|
| Dijkstra |7.069→8.810s|24.62%|86.56%|71.38%|
| Kruskal |14.311→17.827s|24.57%|88.30%|76.83%|

Datos del autor originales (evidencia local: `openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-graph-three-approved-adjustments-medium/block2-exact-snapshot-pool/resources-comparison.json`). La medición independiente QA (evidencia local: `openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/independent-review-graph-three-approved-adjustments/resource-comparison.json`) es otra observación secuencial, sóloPrim3vértices/815eventos/816pasos: JSON22,858,901→2,391,321bytes(-89.54%); picoPython189,589,805→41,724,822bytes(-77.99%); perf_counter17.225→21.435s(+24.44%); process_time17.219→21.438s(+24.50%). CPU QA no se atribuye al autor. No se midió RSS/heap del navegador ni máximos200/latencia distribuida.

## GRAPH-QA-DOC-02 corregido: inmutabilidad exacta y evidencia nueva

El bloqueo técnico standalone del autor (evidencia local: `openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-graph-three-approved-adjustments-medium/block2-exact-snapshot-pool/browser-immutability-blocker.md`) continúa como evidencia histórica: driver no inició Chromium, sin rechazo de permisos, intentos interrumpidos; no se inventa un resultado verde del autor. Después QA sí inicióChromium y 30148mutaciones rechazadas (evidencia local: `openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/independent-review-graph-three-approved-adjustments/mutation-results.json`) sobre cincofixtures conservaron igualdad completa de todos los campos antes/después. Counts6518/4732/7205/5290/6403 pertenecen respectivamenteBF/BFciclo/Prim/Dijkstra/Kruskal; son objetos/intentospool, no grafos ni pasos.

Object.freeze cubre en navegador los records de cada paso y todos los subárboles compartidos del pool. La raíz de traza, metadata, ledger C_instruction_events y arraysconsole ordinarios NO están congelados. Python intern comparte almacenamiento, no crea contenedores Python congelados. El player observado conserva estados/scopes/variables/highlights/stdout/mensajes adelante/atrás/seek sin remutación/redispatch; no certifica todas las respuestas JSON como inmutables.

## Aceptación técnica finita y residuales

Las dos correcciones requeridas están incorporadas en docs/USER_GUIDE.md y docs/qa/graph-teacher-guide.md y este addendum, sin reescribir checkpoints/freezes/informes originales del autor/revisor. QA ejecutó46IDs(42contratos+4E2E), seisfixtures nativos críticos aparte y cincofixtures de mutación; before/verify/after0, fuentes800coincidentes en su foto fechada. No se suman cohortes solapadas. Los tres ajustes quedan aceptados técnicamente para los casos ejecutados: fallo atómico Prim/Dijkstra, expansión exacta/pool congelado y main únicoDOM/HTTP/session sin consultas porGET.

[Criterios por algoritmo y nueve casillas](graph-finite-acceptance-criteria-low.md). Los seisalgoritmos tienen criterios finitos registrados aceptados; sus números de método no cierran las tareas globales de oráculo/UI/documentación. Ledger histórico121/208,87pendientes,38metadataGraphstale y helper privado nuevo fuera del inventario antiguo; sin signoffs nuevos, sin hashrefresh silencioso. Otros67pendientes noGraph conservan hashes actuales y lecturaSDD reutilizada como preparación, no aprobación documental.

[Plan documental preparado](documentary-stable-sources-after-graph-qa-plan-low.md). No cambios C/H/runtime/frontend/tests/preview/sesiones, no reruns de algoritmos/Doxygen/suites. Sólo dosguías y seguimiento propio append; nuevos registros de continuidad preservan asignación anterior. Tras corregir las guías, sólo esos bytes documentales cambian legítimamente respecto a freeze3; su800hashmatch sigue siendo foto anterior, no prueba eterna. Auditoría global abierta, sin archivar/Git/despliegue.
