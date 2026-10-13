# Criterios Graph aceptados y tareas globales — alcance finito

Esta matriz declara criterios satisfechos en casos registrados, no una certificación de cualquier entrada/camino/tamaño. Consolidación documental autorizada, sin nueva ejecución. La aceptación del revisor real corresponde a los tres ajustes y los casos independientes, no a repetir todas las cohortes históricas.

| Algoritmo | Criterios registrados aceptados | Evidencia estable |
|---|---|---|
| BFS | ColaFIFO/marcaalencolar, helpersC/punteros/scopes/reserva-liberación, orden/marcas/caller reales, ambasvistas/replay/noPOST/historial de consultas; cierre anterior preservado | BFSLOW (evidencia local: `openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-graph-bfs-low-closure/README.md`) |
| DFS | Recursión/frames/helpers/alias/memoria/retornos/orden/marcas, historial con efectos cronológicos validados sin queryredispatch, ambosDOM/replay/C17/ownership; cierre anterior preservado | DFSLOW (evidencia local: `openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-graph-dfs-history-context-low/README.md`) |
| Bellman-Ford | Pesosint32 aprobados, distancias internasamplias/reachability separada/suma comprobada, ordenarcos/mejorastricta; ciclo extremo alcanzable detectado con ejecuciónC definida y API400/successfalse/diagnóstico causal/no llamadaexitosa; arrays/helpers/scopes/heap/eventos/ownership y callerC17 | [Funcional](graph-integer-cycle-functional-milestone-checkpoint-medium.md), [instrucción](graph-four-instruction-traces-checkpoint-medium.md), [QAajustes](evidence/independent-review-graph-three-approved-adjustments/review.md) |
| Dijkstra | Rechazo global de negativos incluso desconectados; INT_MAXinfinito, guardas antes de suma, orden índiceslistaC/empatesestrictos, entradaint32 finita/integral; sucesores privados atómicos/errorNULL/cleanup; arrays/helpers/tipos/scopes/estados sourceC y callerC17 | Mismos checkpoints funcional/instrucción y QA: mínimos/fallos críticos independientes,22faultIDs autor compartidos conPrim no sumadoscomo nuevos |
| Prim | Negativos/INT_MIN/INT_MAX con presencia candidata separada, primeríndiceC en empate, bosque por reinicio decomponentes/API no dirigido, sucesoresatómicos/errorNULL/cleanup sin mínimo parcial; helpers/arrays/scopes/eventos/callerC17 | Funcional17fixturesnormales, instrucción registrada y QA críticaPrim malloc6/8+normal; no nuevo conteo global |
| Kruskal | Orden estable de arcosC/bubble y Union-Find real/índices/padres/scopes, lazos/arcos inversos descartados porunión, bosque/API no dirigido; resultado propio/cleanup; callerC17 | Funcional17fixturesnormales, instrucción y QAplayer/main; operandosUF observados conGCC, no promesa de orden universal de evaluación C |

Los cuatro numéricos: igualdad normalC/backend y eventos del modelo/oráculo en sus cohortes; memoria inicial sin futuro, typedarrays/frames/lifetime/printf/condiciones/linehighlight; cincoexpansiones completas precodec, poolsharedfrozen con alcance preciso;4playerE2E y4mains HTTP idénticos DOM con dosconsultas,recarga/GET/replay0redispatch/cicloexcluido/sesiones/ownership. Native normalfixtures20BF/17Prim/16Dijkstra/17Kruskal son entradas de sus cohortes existentes; no se suman a46QA como casos independientes únicos. RestriccionesNULL, normal/faultseleccionados y fuenteGCC/ABI probada se mantienen.

## Criterios globales aún abiertos

La fuente canónica tasks.md contiene22casillas,13marcadas y9abiertas; la revisión de sus criterios no autoriza ninguna casilla nueva. Se deriva de la fuente, no de contar6algoritmos/67lecturas/46pruebas.

| Fila derivada tasks.md | Motivo concreto para conservar abierta |
|---|---|
|11 Oráculo nativo completo|Aceptación porcasos/familias no consolida todaslasoperaciones/caminos/invariantes/memoria del inventario global; matriz agregada y límites faltan|
|12 Sección2 todasoperaciones/TAD|Fidelidad finita registrada no es cobertura agregada de todasopciones; integración/criterios noaplicables y estados de matriz global requieren cierre propio|
|13 C/HHTTP+Doxygen+exactitud porsímbolo|Ledger87pendientes,38Graphhashstale y entidadprivada nueva; Doxygen0/local compilation no son signoff global|
|14 Manual/ayudas|Sólo correccionesGraph acotadas; permanecen revisión porsímbolo, coherencia de ayudas/controles/formatos/límites del resto|
|16 Implementación aprobada yregresiones|Falta concluir documentación aprobada y cerrar matriz de requisitos/diff/regresiones final; no marca porsubsetGraph|
|17 Consultas/decisiones semánticas|Las decisionesnuméricasGraph/H1/RNyaaprobadas no se vuelven apedir; sigue reconciliación global de compromisos, incluidoC1parcial, no verificación del criterio total desdeGraph|
|18 Gatefinal/pruebas/cobertura/C/sanitizers|Sin suite/cobertura final actual ni gateagregado; ASan/UBSan no disponibles permanecen límite documentado|
|19 Entrega final|Matriz/hallazgos/diff/instrucciones/globalclosing no entregados; auditoría permanece sinarchivar|
|22 Raíces de uso/depuración|Revisión global deUI/APIoculta/internals/legacy/raíces sigue sin cerrar; no depuración nueva desdeQA Graph|

Ledger121revisados/87pendientes sobre208históricos permanece sin modificación;38Graph incluyen18con estados revisados históricos y20pendientes, todosdeclSHAstale. Los67noGraph pendientes mantienendeclSHA; cincoauxPriority y20exportaciones Pila/Colas,Hash11/Sorting11/RNprevios no son nuevos signoffsdoc. Escala200/RSS/navegador/sanitizers/otroscompiladores/antiguashistorias sin mark_effect/canonicalspechistorical siguen límites respectivos; no quedan decisionesnuméricasGraph pendientes ni se inventa necesidad de reaprobarlas.
