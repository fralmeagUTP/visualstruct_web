# Propuesta: una autorización específica, un bloque

Base aceptada: **20159/24423(82.54%)**. Faltan113sentencias distintas para83%. Proponer únicamente **73 IDs exactos**, en **un solo bloque conjunto de máximo120segundos y2GiB por proceso y WindowsJob**. El permiso anterior para8IDs ya se consumió; esta propuesta no está autorizada ni ejecutada.

| Selección | IDs | Potencial distinto sobre base actual | Duración histórica medida |
|---|---:|---:|---:|
| R2-independent-0301: Cima/Pila |65|84|15.906s|
| R2-independent-0215: Counting paging |8|49|44.453s|
| Unión propuesta |73|133|60.359s, suma de dos ejecuciones separadas|

Lista completa y exacta: exact-73-IDs.txt (evidencia local: `openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-proposed-final-current-coverage-selection-low-20261011/exact-73-IDs.txt`) y exact-73-IDs.json (evidencia local: `openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-proposed-final-current-coverage-selection-low-20261011/exact-73-IDs.json`). Los65 IDs de Cima cubren contrato, lectura repetida, guardasNULL, parámetros/punteros, memoria/retorno, rechazoAPI y validación de informes UI/caller ya preservados. Los8 Counting cubren muestras de páginas, navegación, ownership/expiry/reset, lectura concurrente, presupuesto/seek, rango grande y casos dense single/ordered. Los nombres C17/browser de algunos tests validan informes existentes; no compilan ni lanzan navegador.

**133 es potencial, no cobertura aceptada ni garantía.** Si se reproduce ese aporte, resultado proyectado20292/24423(83.09%), margen20sentencias sobre mínimo20272. Al evaluar todos15subconjuntos no vacíos de cuatrogrupos prioritarios completos,73 es el menor número de IDs con potencial suficiente; ver complete-group-minimum-comparison.json. No existe atribución histórica porID para justificar un subconjunto menor; no afirmamos mínimo global ni inventamos cobertura por caso. El grupo de170helpers de prioridad solo añade109potenciales y no alcanza113por sí solo; helper+Counting requeriría178IDs, frente a73propuestos.

Histórico60.359s no mide ni garantiza el tiempo conjunto futuro. El máximo seguirá120s total para colección/tests/reporte, nunca120s por caso. Memoria2GiB por proceso Y agregadoJob, sin extensión. Exactamente un intento; si timeout/memoria: terminar todoJob, conservarparcial/XML/logs/data/hashes que existan y detener, sin retry, bloques adicionales o reserva automática. Si hashes/guarda/selección real difieren, detener antes de tests. Un fallo terminal se reporta, no provoca reintento.

Versiones actuales fijadas:889fuentes en source-freeze.json y14recursos externos exactos en prospective-exact-fixture-resource-freeze.json: report/eventos/recursos/caller/browser preservados de Cima,4main.c, muestrasCounting y2fixturesdense. Verificación actual coincide con hashes antes/después del bloque anterior. Eso NO demuestra los hashes ausentes de los oráculos históricos; solo permite un futuro bloque actual con entradas completas. No nueva certificación nativa/browser/globalC-fidelity.

Ninguno de73 coincide con8yaautorizados ni con230casosGraph/RN agotados/Bellman900/JPEG. Estos dos grupos históricos fueron completosPASS, sin timeout, bajo120s/2GiBproceso+Job; resultados anteriores se conservarán. Reapertura específica requiere una única nueva aprobación para la lista exacta73. Después de aprobar: registrar decisión y scope estrecho, guardar before/after, recursos y actualcollection exactos, retener cada evidencia y combinar solo mismafuenteactual con20159aceptado. Gates global83/component85 y4exclusiones intactos; QA evalúa, sin cierre global automático.

Texto concreto para solicitar permiso: «¿Autorizas reabrir y ejecutar una sola vez los73 IDs de exact-73-IDs.txt, en un único bloque conjunto de máximo120segundos y2GiB por proceso y Job? Si vence el límite, terminar elJob y conservar lo parcial, sin reintentar, ampliar recursos ni ejecutar reservas.»

No se modificaron autorización/index/scope ni se ejecutó/recolectó ninguna prueba durante esta preparación. La aprobación anterior sigue consumida; el silencio no concede este nuevo permiso.
