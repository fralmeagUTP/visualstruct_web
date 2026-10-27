# Mapa de pendientes tras Radix, antes de iniciar otro bloque

Radix undécimodeonceSorting consolidado por sorting-radix-consolidated-closure-decision.md. Global13/22 y documentación121/208(87pendientes) no cambian. Este mapa no ejecuta otrobloque ni crea asignaciónHash.

## Siguiente no bloqueado recomendado: Hash H1

H1 está aprobado y reconciliado, no pedir nuevamente decisión enteros/texto: openspec/changes/archive/2026-10-02-reconcile-hash-integer-fixed-capacity/decision.md conserva propuesta/respuesta del usuario; openspec/specs/hash-table/spec.md exige claves/valoresint representablesC y capacidadfija; recrear explícitamente puede elegirotra. Encadenamiento permitefactor>1, noresize/rehash nuevo. La aprobación documental no cierra semántica, fidelidad,legacy ni demás requisitos.

Documentos históricos hash-baseline-decision-gate-low.md y docs/qa/hash-table-audit-summary.md contienen conflicto/texto/rehash antiguo; H1supera la espera, y hallazgos históricos no son fallosactuales sin verificación. Bindinghash.instructions se actualiza documentalmente al contratoaprobado, preservando referencias históricas. No adopta resultados antiguos como baseline fresco.

Primera etapa propuesta LOW: crear asignación nueva con operación fina hash.create-insert-baseline-low y taskbaseline de create_table/insert antes de la guarda. La familia hash.instructions no basta para elegir operaciones automáticamente. Leer C/H descargados, proposal/deltas/design/tasks, H1 e inventario de11operaciones visibles get_supported_operations.

Matriz inicial concreta: capacidad3/17; tabla vacía; insert1/4/7/10 para colisiones y carga>1sinresize; actualizarvalor de4sincrecertamaño; clavesnegativas yINT_MIN/INT_MAX contra móduloC real; campos inválidos/cap0o negativa sinmutación. Registrar reserva/alias/pila/locales/condiciones/mallocNULLsimulado en observer independiente y comparar API. No reservar capacidadenorme ni ejecutarOOMreal. Baseline endpoint no certifica fidelidad porinstrucción; conservar cualquier rojo y proponer MEDIUM sólo con causa delimitada.

Gates de esa etapa: bytesHTTP C/H/hash; callerreal calculadoC17/Doxygen/ownership; historial/main/GET/repeticiones; tabla/buckets/nodos/máscaras/alias; ceroPOSTextra de navegación; captura errores yestadoaceptado. No retirar checkboxQA ni rediseñar contrato sin instrucción específica. Revisar rutas de descargas y contratoJSON real antes de fixturehelpers.

Después, bloques finos separados: get/contains presenteausente; remove cabeza/interior/final de cadena; keys/values/items/stats y sus helpers; clear conserva capacidad frente destroy_table liberaestructura; replay ysesioneslegacy sin inventar compatibilidad. Sólo cierres registrados por método/camino, no familiaHash por seis casos históricos.

## Otros pendientes y dependencias

- Pila/Cola/ColaPrioridad: completar cobertura real desde docs/qa/app-coverage-manifest-v1.json, fuentes depublicidad y evidence, distinguiendo inventario concase_id de testejecutado. No repetir Lista/Circular/Sublista cerradas; aprobar bloque fino antes de verificar/reparar.
- GrafosDijkstra/BellmanFord/Prim/Kruskal: instrucción pendiente aun con baselines/historial/callers registrados. Decisiones numéricas/ciclos/semánticas abiertas se consultan en sus últimas fuentes; no cambiar por silenciosa normalización. BFS/DFS cerrados no se repiten.
- ValidarRN: C-RBT-VALIDAR-LIMIT-01 sigue decisión de producto (altura negra/padres/ciclos);7métodos registrados no certifican validador completo. Noextender sinaprobación.
- Documentación:121/208contratos revisados,87pendientes según documentation-symbol-signoff-ledger.md/JSON. Doxygen0solo no suma firmas.
- C1remaining:1/12reconciliado,11pendientes según openspec/continuity/reconciliation-status.md. No archivar auditoríaglobal ni afirmarcasos29/29como cierre actual.
- Agregadofinal: después de frentes/decisiones yautorización, suite/cobertura/descargas/QAglobal. No ejecutarlo en esta consolidación deRadix.

PreviewD5051 mantiene proceso21196/19092,actual;noHash/otros procesos de pruebas activos. No push/merge/deploy. Próxima acción del coordinador: comunicar cierreRadix y asignar baselineHashfino si se elige esta prioridad.
