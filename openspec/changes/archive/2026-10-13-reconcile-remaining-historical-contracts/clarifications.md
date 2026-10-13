# Aclaraciones operativas vigentes — C1 y PNG

## Hash
H1 está APROBADO: claves/valores enteros y capacidad fija. `openspec/specs/hash-table/spec.md:71-93` y `openspec/changes/archive/2026-10-02-reconcile-hash-integer-fixed-capacity/decision.md:3-7`. La contradicción texto/rehash del catálogo anterior es histórica y quedó reconciliada documentalmente; no usarla como decisión pendiente. Funcionalidad, índice entre procesos, fidelidad por instrucción y sesiones legacy siguen sin cierre inferido. Catálogo anterior y fuentes archivadas conservados íntegros; esta matriz actualiza interpretación, no reescribe historia.

## PNG: cobertura ejecutada frente a automatización pendiente
Las cuatro capturas PNG del piloto sí fueron verificadas. QA independiente ejecutó el checker y cotejó cuatro SHA256 (exit0); repitió en copia temporal y corrompió una captura de esa copia: rechazo exit1. También inspeccionó capturas visualmente. Fuente exacta: `openspec/changes/archive/2026-10-02-adopt-local-role-documentation-example/evidence/independent-review/report.md:17-18`.

Antes del cierre el autor volvió a ejecutar el suplemento; `evidence/closure-final/png-integrity-before-close.log` registra OK para las cuatro capturas. `evidence/closure-final/verification.md` conserva la secuencia de cierre. No faltó ese paso ni se requiere repetirlo por esta aclaración.

Lo pendiente es automatización nativa: la guarda actual lee UTF-8 y no detecta automáticamente un cambio aislado del PNG si el manifiesto textual permanece igual. Integridad binaria depende del checker suplementario explícito y de mantener vinculados manifiesto/bytes. No se añadió funcionalidad, no se volvió a ejecutar checker/browser ni se modificó evidencia cerrada. `openspec/continuity/USAGE.md:32-33` ya describe ese límite y confirma suplemento ejecutado; la frase anterior de entrega «requiere suplemento» significaba dependencia operativa, no verificación omitida.

## Cierre de esta revisión
C1 sigue 1/12 admitido y11pendientes. No nuevo delta: ninguno de los once requisitos completos está demostrado con la evidencia leída. Tres tareas documentales pueden completarse; QA independiente y decisión final quedan pendientes. No se archiva ni se proclama baseline completa.
