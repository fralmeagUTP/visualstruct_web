# C1: reconciliación de once obligaciones restantes

Fotografía documental 2026-10-02T17:56:27.199042+00:00, proyecto canónico D:. **0 nuevos requisitos admitidos; C1 permanece 1/12 admitido y 11 pendientes.** Se revisaron los veinte escenarios originales; C1-REM-06 no reabierto. Ningún delta/cambio canónico procede con esta evidencia.

Hash H1 aprobado y reconciliado documentalmente; pruebas funcionales pendientes. Counting parcial n<=4/k<=4, ampliación en curso sin cierre acreditado. Decisiones RN/Grafos pendientes. Los resultados antiguos preservados no son estado vivo ni se suman para certificar exhaustividad.

La matriz JSON conserva textos completos, escenarios, rutas/líneas originales, SHA y fuentes actuales. source-snapshot.json registra hashes de lectura. No pruebas app/motor nuevas.

## C1-QA-01 — Inventario exhaustivo y verificable

Estado: **NOT_DEMONSTRATED**, no admitido. Canonical: `None`; requisito original presente: False.
Origen: `openspec/changes/archive/2026-08-23-establish-comprehensive-app-quality-validation/specs/application-quality-validation/spec.md:9`; SHA `552929ebaa2f1276b1d831252982c865f8e2fcc693edf7fd5d82fe3eb76168d5`.

IDs/oráculos autoasignados y controles omitidos no prueban vínculos ejecutables.

Decisión: Implementación del gate de cobertura pendiente; no consolidar por cadenas no vacías.

- Escenario **nueva operación publicada**: Prueba existente con fixture/esperado, enlace verificable y fallo al añadir operación no cubierta.

- Escenario **control visible sin cobertura E2E**: Todos los controles visibles: prueba E2E vinculada o fila explícita faltante, incluidos sin identificador.

Evidencia leída:
- `scripts/build_app_quality_inventory.py:32-51`
- `scripts/build_app_quality_inventory.py:150-169`
- `scripts/build_app_quality_inventory.py:202-219`

## C1-QA-02 — Cobertura funcional de todos los módulos

Estado: **PARTIAL**, no admitido. Canonical: `None`; requisito original presente: False.
Origen: `openspec/changes/archive/2026-08-23-establish-comprehensive-app-quality-validation/specs/application-quality-validation/spec.md:25`; SHA `552929ebaa2f1276b1d831252982c865f8e2fcc693edf7fd5d82fe3eb76168d5`.

Campaña de riesgo y cierres registrados reales; no matriz completa final de todas las opciones/clases.

Decisión: Mantener pendiente cierre final y cobertura por opción; no sumar muestras históricas como exhaustividad.

- Escenario **algoritmo de ordenamiento registrado**: Once algoritmos: vacío/un elemento/repetidos/ordenado/inverso/negativo/límite y comparación rápido/replay cuando aplican. Binsort/Radix pendientes; Counting parcial.

- Escenario **operación de grafo por fase**: Todas las operaciones por fase con precondiciones/API/vista/traza en una revisión coherente. BFS/DFS finitos no prueban Dijkstra/Bellman-Ford/Prim/Kruskal/construcción.

Evidencia leída:
- `openspec/changes/audit-local-quality-and-unified-controls/tasks.md:12-21`
- `openspec/changes/audit-local-quality-and-unified-controls/validation-plan.md:20-25`
- `openspec/changes/audit-local-quality-and-unified-controls/sorting-counting-scope-correction-decision.md:5-31`
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-counting-expanded-fidelity/README.md:1-3`
- `openspec/changes/audit-local-quality-and-unified-controls/graph-dijkstra-numeric-contract-decision.md:9-38`
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-graph-dijkstra-history-caller-low/README.md:7-13`
- `openspec/specs/graph-structures/spec.md:48-54`

## C1-QA-03 — Fidelidad C, estado y traza

Estado: **PARTIAL**, no admitido. Canonical: `None`; requisito original presente: False.
Origen: `openspec/changes/archive/2026-08-23-establish-comprehensive-app-quality-validation/specs/application-quality-validation/spec.md:43`; SHA `552929ebaa2f1276b1d831252982c865f8e2fcc693edf7fd5d82fe3eb76168d5`.

Fidelidad causal y restauración comprobadas en métodos registrados; faltan familias y entradas admitidas.

Decisión: Los avances RN posteriores superan el antiguo motivo de baseline solamente; el requisito global sigue pendiente por cobertura restante.

- Escenario **reproducción de una operación mutante**: Restauración, consola, historial, rápido y ambas vistas de cada operación evaluada sobre fuentes coherentes; Counting fuera del corte carece instruction_event.

- Escenario **llamada auxiliar del código C**: Llamada/cuerpo/retorno real de helpers en familias restantes; Dijkstra sigue sin modelo C fiel por instrucción.

Evidencia leída:
- `openspec/changes/audit-local-quality-and-unified-controls/tasks.md:12-21`
- `openspec/changes/audit-local-quality-and-unified-controls/validation-plan.md:20-25`
- `openspec/changes/audit-local-quality-and-unified-controls/sorting-counting-scope-correction-decision.md:5-31`
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-counting-expanded-fidelity/README.md:1-3`
- `openspec/changes/audit-local-quality-and-unified-controls/graph-dijkstra-numeric-contract-decision.md:9-38`
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-graph-dijkstra-history-caller-low/README.md:7-13`
- `openspec/specs/graph-structures/spec.md:48-54`

## C1-QA-04 — Calidad no funcional y reporte

Estado: **PARTIAL**, no admitido. Canonical: `None`; requisito original presente: False.
Origen: `openspec/changes/archive/2026-08-23-establish-comprehensive-app-quality-validation/specs/application-quality-validation/spec.md:60`; SHA `552929ebaa2f1276b1d831252982c865f8e2fcc693edf7fd5d82fe3eb76168d5`.

Existen resultados históricos y separación infraestructura/producto; falta campaña no funcional actual completa y reportes íntegros.

Decisión: No transferir automáticamente resultados 2026-08-23 a revisión actual; CI declarada no es ejecución demostrada.

- Escenario **navegador E2E no instalado**: Registro reproducible del entorno sin browser con comando de resolución y clasificación infraestructura. Firefox ausente histórico no prueba por sí solo todo el escenario.

- Escenario **informe de hallazgo**: Informe por fallo con operación/entrada/esperado/observado/severidad/causa/ubicación/prueba recomendada; trazabilidad de accesibilidad, seguridad, rendimiento y compatibilidad finales.

Evidencia leída:
- `docs/qa/comprehensive-app-quality-results-v1.json:8-16`
- `docs/qa/remediation-gates.md:7-17`
- `openspec/changes/audit-local-quality-and-unified-controls/tasks.md:17-20`
- `openspec/changes/audit-local-quality-and-unified-controls/tasks.md:12-21`
- `openspec/changes/audit-local-quality-and-unified-controls/validation-plan.md:20-25`

## C1-REM-01 — Un único contrato ejecutable por operación

Estado: **PARTIAL_WITH_DIVERGENCES**, no admitido. Canonical: `openspec/specs/didactic-conformance-remediation/spec.md`; requisito original presente: False.
Origen: `openspec/changes/archive/2026-08-23-remediate-didactic-c-trace-fidelity/specs/didactic-conformance-remediation/spec.md:5`; SHA `a5fc25baad2f949a356418c71001656391262a9374ea5899ae7c067974f0dd20`.

Hash H1 ya resuelto documentalmente; Grafos conserva divergencias de algoritmo/tipos/errores y casos sin fidelidad completa.

Decisión: No modificar Hash ni Grafos automáticamente; H1 aprobado no cierra funcionalidad. Decisión numérica Grafos pendiente.

- Escenario **implementaciones con igual resultado y algoritmo distinto**: Reconciliar empate/infinito/suma Dijkstra y verificar cada capa según decisión; resultado igual no valida algoritmo distinto.

- Escenario **operación sin implementación C**: Inventario actual de composiciones C compilables por operación pública y decisión expresa para fallbacks no C.

Evidencia leída:
- `openspec/changes/audit-local-quality-and-unified-controls/graph-dijkstra-numeric-contract-decision.md:9-38`
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-graph-dijkstra-history-caller-low/README.md:7-13`
- `openspec/specs/graph-structures/spec.md:48-54`
- `openspec/changes/archive/2026-10-02-reconcile-hash-integer-fixed-capacity/decision.md:3-7`
- `openspec/specs/hash-table/spec.md:71-93`
- `openspec/continuity/reconciliation-status.md:10-16`
- `openspec/changes/audit-local-quality-and-unified-controls/tasks.md:12-21`
- `openspec/changes/audit-local-quality-and-unified-controls/validation-plan.md:20-25`
- `openspec/changes/audit-local-quality-and-unified-controls/sorting-counting-scope-correction-decision.md:5-31`
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-counting-expanded-fidelity/README.md:1-3`

## C1-REM-02 — Aritmética y memoria definidas en los límites

Estado: **NOT_DEMONSTRATED**, no admitido. Canonical: `openspec/specs/didactic-conformance-remediation/spec.md`; requisito original presente: False.
Origen: `openspec/changes/archive/2026-08-23-remediate-didactic-c-trace-fidelity/specs/didactic-conformance-remediation/spec.md:21`; SHA `a5fc25baad2f949a356418c71001656391262a9374ea5899ae7c067974f0dd20`.

C17 y checks de ownership finitos no prueban ausencia de UB global ni escenarios sanitizados.

Decisión: Mantener pendiente; no ejecutar C inseguro. Counting n<=4/k<=4 no satisface dominio admitido ni prueba sanitizada.

- Escenario **Radix Sort contiene INT_MIN**: Log ejecutado UBSan para Radix INT_MIN, multiconjunto/orden y equivalencia de transcripción actual.

- Escenario **rango de conteo excesivo**: Counting y Bin: rechazo excesivo antes de reserva en C/backend y mismo error tipado consola/traza; límites size_t32/fullspan no verificados.

Evidencia leída:
- `docs/qa/comprehensive-app-quality-results-v1.json:8-16`
- `docs/qa/remediation-gates.md:7-17`
- `openspec/changes/audit-local-quality-and-unified-controls/tasks.md:17-20`
- `openspec/changes/audit-local-quality-and-unified-controls/sorting-counting-scope-correction-decision.md:5-31`
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-counting-expanded-fidelity/README.md:1-3`
- `openspec/changes/audit-local-quality-and-unified-controls/graph-dijkstra-numeric-contract-decision.md:9-38`
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-graph-dijkstra-history-caller-low/README.md:7-13`
- `openspec/specs/graph-structures/spec.md:48-54`

## C1-REM-03 — Contrato coherente para grafos

Estado: **CONTRADICTORY_PENDING_DECISION**, no admitido. Canonical: `openspec/specs/didactic-conformance-remediation/spec.md`; requisito original presente: False.
Origen: `openspec/changes/archive/2026-08-23-remediate-didactic-c-trace-fidelity/specs/didactic-conformance-remediation/spec.md:38`; SHA `a5fc25baad2f949a356418c71001656391262a9374ea5899ae7c067974f0dd20`.

Spec decimal vs C entero/API rechazo; fuera de rango aceptado y Infinity500. Contrato único no resuelto.

Decisión: Decidir tipos y política coherentes antes de consolidar; no asumir ausencia de aprobación histórica.

- Escenario **arista con atributos no representables**: Rechazo sin mutación de dirección/peso no representable o contrato C extendido exacto, rango/finitud y mismas representaciones.

- Escenario **grafo desconectado para MST**: Prim/Kruskal desconectados: bosque mínimo, componentes explícitos, API/traza/DOM y no etiqueta árbol completo. Baselines no cierran obligación.

Evidencia leída:
- `openspec/changes/audit-local-quality-and-unified-controls/graph-dijkstra-numeric-contract-decision.md:9-38`
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-graph-dijkstra-history-caller-low/README.md:7-13`
- `openspec/specs/graph-structures/spec.md:48-54`
- `openspec/changes/audit-local-quality-and-unified-controls/tasks.md:12-21`
- `openspec/changes/audit-local-quality-and-unified-controls/validation-plan.md:20-25`

## C1-REM-04 — Contrato coherente para hash y secuenciales

Estado: **PARTIAL**, no admitido. Canonical: `openspec/specs/didactic-conformance-remediation/spec.md`; requisito original presente: False.
Origen: `openspec/changes/archive/2026-08-23-remediate-didactic-c-trace-fidelity/specs/didactic-conformance-remediation/spec.md:54`; SHA `a5fc25baad2f949a356418c71001656391262a9374ea5899ae7c067974f0dd20`.

H1 fija enteros/capacidad; sigue faltando prueba combinada íntegra Hash+secuenciales.

Decisión: Conservar avances de snippets secuenciales sin inferir todos ni índice Hash reproducible; decisión H1 ya aprobada, no pendiente.

- Escenario **índice hash reproducible**: Comparación C/backend en procesos distintos para mismas claves/capacidad/colisiones con hashes/versiones actuales.

- Escenario **snippet de consulta**: Snippet DOM real cima/frente/final compilado con header publicado, ejecución y comparación UI para consultas aplicables.

Evidencia leída:
- `openspec/changes/archive/2026-10-02-reconcile-hash-integer-fixed-capacity/decision.md:3-7`
- `openspec/specs/hash-table/spec.md:71-93`
- `openspec/continuity/reconciliation-status.md:10-16`
- `openspec/changes/audit-local-quality-and-unified-controls/tasks.md:12-21`
- `openspec/changes/audit-local-quality-and-unified-controls/validation-plan.md:20-25`

## C1-REM-05 — Estado visual causado por eventos C

Estado: **PARTIAL**, no admitido. Canonical: `openspec/specs/didactic-conformance-remediation/spec.md`; requisito original presente: False.
Origen: `openspec/changes/archive/2026-08-23-remediate-didactic-c-trace-fidelity/specs/didactic-conformance-remediation/spec.md:68`; SHA `a5fc25baad2f949a356418c71001656391262a9374ea5899ae7c067974f0dd20`.

Cierres causales finitos de listas/árboles/heap/BFS/DFS no certifican cada frame de toda aplicación.

Decisión: No reabrir cierres finitos; pedir trazabilidad directa del escenario circular y cerrar familias restantes con autorización.

- Escenario **operación compuesta**: Mutaciones/intermedios/identidades/alias/retornos por cada operación compuesta; Counting fuera del corte y Dijkstra siguen pendientes.

- Escenario **nodo único circular**: Prueba nativa y DOM actual del circular único con autoenlace y HEAD/COLA mismo ID, referenciada directamente al escenario. Cierre de familia sin mapping exacto insuficiente.

Evidencia leída:
- `openspec/changes/audit-local-quality-and-unified-controls/tasks.md:12-21`
- `openspec/changes/audit-local-quality-and-unified-controls/validation-plan.md:20-25`
- `openspec/changes/audit-local-quality-and-unified-controls/sorting-counting-scope-correction-decision.md:5-31`
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-counting-expanded-fidelity/README.md:1-3`
- `openspec/changes/audit-local-quality-and-unified-controls/graph-dijkstra-numeric-contract-decision.md:9-38`
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-graph-dijkstra-history-caller-low/README.md:7-13`
- `openspec/specs/graph-structures/spec.md:48-54`

## C1-REM-07 — Consola derivada de ejecución

Estado: **PARTIAL**, no admitido. Canonical: `openspec/specs/didactic-conformance-remediation/spec.md`; requisito original presente: False.
Origen: `openspec/changes/archive/2026-08-23-remediate-didactic-c-trace-fidelity/specs/didactic-conformance-remediation/spec.md:98`; SHA `a5fc25baad2f949a356418c71001656391262a9374ea5899ae7c067974f0dd20`.

Transporte step.console demostrado; generic builder aún deduce printf literal por línea y entrega console_events en último paso. Inspección no demuestra procedencia C alcanzada de todos los emisores.

Decisión: No declarar defecto por simple existencia del fallback; falta demostrar procedencia causal global y determinismo, no sólo transporte frontend.

- Escenario **mensaje técnico sin printf**: Prueba negativa descriptivo-sin-printf para todos los paths emisores, captura de salidas C alcanzadas y prefijos exactos avanzar/retroceder/reiniciar.

Evidencia leída:
- `app/services/execution_trace_service.py:1469-1484`
- `tests/test_phase7_trace_contract_remediation.py:58-65`
- `openspec/changes/audit-local-quality-and-unified-controls/sorting-counting-scope-correction-decision.md:5-31`
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-counting-expanded-fidelity/README.md:1-3`
- `openspec/changes/audit-local-quality-and-unified-controls/graph-dijkstra-numeric-contract-decision.md:9-38`
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-graph-dijkstra-history-caller-low/README.md:7-13`
- `openspec/specs/graph-structures/spec.md:48-54`
- `openspec/changes/audit-local-quality-and-unified-controls/tasks.md:12-21`
- `openspec/changes/audit-local-quality-and-unified-controls/validation-plan.md:20-25`

## C1-REM-08 — Cierre verificable de los hallazgos QA

Estado: **NOT_DEMONSTRATED**, no admitido. Canonical: `openspec/specs/didactic-conformance-remediation/spec.md`; requisito original presente: False.
Origen: `openspec/changes/archive/2026-08-23-remediate-didactic-c-trace-fidelity/specs/didactic-conformance-remediation/spec.md:108`; SHA `a5fc25baad2f949a356418c71001656391262a9374ea5899ae7c067974f0dd20`.

Informe29closed y matriz fixed_pending_gate no determinan cierre actual único; gate sanitario obligatorio no acreditado completo.

Decisión: No reabrir29casos automáticamente ni usar GRAPH-004 negativo como defecto actual: Dijkstra sí rechaza negativos según evidencia posterior.

- Escenario **cierre de un hallazgo**: Mapping29IDs a fixture/prueba/oráculo antes/después y resultados capa+integración+C17/sanitizers/UI en versión pertinente; resolver estados históricos sin borrar evidencias.

Evidencia leída:
- `docs/qa/remediation-closure-report-v1.json:5-9`
- `docs/qa/remediation-regression-matrix-v1.json:7-26`
- `docs/qa/remediation-gates.md:7-17`
- `openspec/changes/audit-local-quality-and-unified-controls/tasks.md:12-21`
- `openspec/changes/audit-local-quality-and-unified-controls/validation-plan.md:20-25`
- `docs/qa/comprehensive-app-quality-results-v1.json:8-16`
- `docs/qa/remediation-gates.md:7-17`
- `openspec/changes/audit-local-quality-and-unified-controls/tasks.md:17-20`
