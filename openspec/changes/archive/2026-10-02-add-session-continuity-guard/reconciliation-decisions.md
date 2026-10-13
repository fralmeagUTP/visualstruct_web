# Diferencias y decisiones
2026-10-02; fuentes leídas, sin certificación funcional. No modificar specs canónicas ni auditoría concurrente.

## RC-HASH-01 — pendiente de consolidación
Archivo2026-08-23-enhance-hash-table-pedagogy/specs/hash-table/spec.md:3-13 pide enteros/capacidad fija; openspec/specs/hash-table/spec.md:26-32 pide texto, :62-70 rehash0.75. Reconciliation activa:32 y43 reconoce divergencia/conserva enteros/capacidad fija sin rediseño.
Diff para revisión: MODIFIED/RENAMED validación texto→enteros; escenarios insert/get y estado; REMOVED Rehash con razón; incorporar requisitos pedagógicos aplicables. Resolver también fields resized/resize_event y compatibilidad.
No aplicar: no se ha demostrado aprobación rastreable de todos los contratos ni conformidad completa. Autorización de arreglar OpenSpec no elige por sí sola semántica.

## RC-ARCHIVE-01 — consolidación incompleta
archive/2026-08-23-establish-comprehensive-app-quality-validation/specs/application-quality-validation/spec.md y archive/2026-08-23-remediate-didactic-c-trace-fidelity/specs/didactic-conformance-remediation/spec.md carecen de capacidad canónica correspondiente. Reconciliation activa:33 reconoce compromisos no incorporados.
Preparar incorporación requisito por requisito con mantener/modificar/retirar y evidencia; reutilizar reconciliation-detailed/JSON existente sin duplicar1653filas. No copiar capacidades completas como verdad implementada por archivo/casillas.

## RC-STATE-01 — mitigación implementada; limpieza pendiente
Proposal/design mezclan borrador/autorización y worklist conserva BFS pendiente histórico. Bootstrap obliga a decisiones/evidencia. No editar archivos de otra tarea mientras es propietaria; coordinar limpieza posterior preservando historia.

## RC-CONTINUITY-01 — cambio propio
Specs nuevas permanecen aquí. Tras verificación/revisión consolidar session-continuity y archivar contexto. No afirmar canonización hecha. Solo pruebas aisladas; suite app prohibida en esta coordinación.

## C1 parcial aplicado2026-10-02
Consolidado solo Traza continua y fuente verificable en openspec/specs/didactic-conformance-remediation/spec.md. Fuente/motor/escenarios/evidencia y11pendientes: openspec/changes/archive/2026-10-02-reconcile-verified-historical-trace-contract/reconciliation.md. No cierra capacidades completas ni auditoría/29casos; no modifica Hash/H1. Evidencia ejecutada es histórica, transferida por identidad relevante, no suite app nueva. Arnés permanece activo pendiente de confirmar adopción con assignment-id.
