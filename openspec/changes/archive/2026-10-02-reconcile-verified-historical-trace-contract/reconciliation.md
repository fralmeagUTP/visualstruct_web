# Resultado C1 conservador

Se admite1/12requisitos íntegros;11quedan pendientes, con texto/escenarios/ruta/línea/SHA preservados en evidence/requirement-decisions.json. No son11incumplimientos funcionales nuevos ni11casos reabiertos automáticamente.

## Admitido
Traza continua y fuente verificable (histórico:84): invariantes del motor, no fidelidad C de toda aplicación. Evidencia ejecutada histórica, identidad actual de partes relevantes y llamadas al gate cotejadas. No se ejecutó aplicación ni suite nueva. Aprobación C1 de coordinación y alcance de auditoría registrado; aprobación histórica original no autenticable desde Git.

## Pendientes

### C1-QA-01 — Inventario exhaustivo y verificable
El generador asigna case_id/layer/oracle automáticamente y el gate verifica cadenas/frescura; no demuestra prueba existente con datos/esperado para operación nueva. Controles sin identificador se omiten. Falta trazabilidad ejecutable por opción, no basta357IDs históricos.
Referencias: scripts/build_app_quality_inventory.py:35-55, validate_inventory/main; tests/test_app_quality_inventory.py; origen openspec/changes/archive/2026-08-23-establish-comprehensive-app-quality-validation/specs/application-quality-validation/spec.md:9

### C1-QA-02 — Cobertura funcional de todos los módulos
Matriz funcional de riesgo no demuestra todas las opciones/variantes/casos/vistas sobre revisión final coherente. Familias Grafos/Hash/Ordenamiento y gate final siguen pendientes en fuentes consultadas.
Referencias: audit-local-quality-and-unified-controls/tasks.md:12-21; validation-plan.md; origen openspec/changes/archive/2026-08-23-establish-comprehensive-app-quality-validation/specs/application-quality-validation/spec.md:25

### C1-QA-03 — Fidelidad C, estado y traza
El baseline RN demuestra endpoints/eventos pero no cierre por instrucción/UI; faltan familias restantes. Dos escenarios de invariantes del motor no prueban fidelidad causal global.
Referencias: audit-local-quality-and-unified-controls/evidence/visible-red-black-delete-baseline-low/README.md; red-black-delete-instruction-review-plan.md; origen openspec/changes/archive/2026-08-23-establish-comprehensive-app-quality-validation/specs/application-quality-validation/spec.md:43

### C1-QA-04 — Calidad no funcional y reporte
Reporte histórico/CI configurada no prueban campaña vigente de seguridad/rendimiento/accesibilidad/compatibilidad ni sus gates completos. Mantener bloqueos infraestructura explícitos; no certificar por suite histórica.
Referencias: docs/qa/comprehensive-app-quality-results-v1.json; audit-local-quality-and-unified-controls/validation-plan.md; origen openspec/changes/archive/2026-08-23-establish-comprehensive-app-quality-validation/specs/application-quality-validation/spec.md:60

### C1-REM-01 — Un único contrato ejecutable por operación
Contrato Hash contradice spec canónica, APIs ocultas requieren decisión y varias familias no tienen equivalencia C por instrucción demostrada. No transferir13TAD completos desde cierres finitos.
Referencias: audit-local-quality-and-unified-controls/reconciliation.md:32-35; current-operation-contract.md; origen openspec/changes/archive/2026-08-23-remediate-didactic-c-trace-fidelity/specs/didactic-conformance-remediation/spec.md:5

### C1-REM-02 — Aritmética y memoria definidas en los límites
UBSan/ASan históricos no son ejecución sobre actuales bytes/casos; disponibilidad local limitada. Falta vincular escenarios Radix INT_MIN y rango excesivo a revisión vigente y demostrar errores equivalentes en capas.
Referencias: docs/qa/remediation-gates.md; audit-local-quality-and-unified-controls/progress.md; origen openspec/changes/archive/2026-08-23-remediate-didactic-c-trace-fidelity/specs/didactic-conformance-remediation/spec.md:21

### C1-REM-03 — Contrato coherente para grafos
Verificación vigente completa de dirección/pesos/duplicados/extremos/recorridos/MST-bosque no establecida; contraste nativo intermedio pendiente. No afirmar fallo funcional solo por falta de prueba actual.
Referencias: docs/qa/graph-mst-audit-summary.md; audit-local-quality-and-unified-controls/reconciliation-detailed.md:12; specs/graph-structures/spec.md; origen openspec/changes/archive/2026-08-23-remediate-didactic-c-trace-fidelity/specs/didactic-conformance-remediation/spec.md:38

### C1-REM-04 — Contrato coherente para hash y secuenciales
Decisión H1 pendiente; no consolidar dominio/capacidad Hash ni reducir obligación combinada a secuenciales muestreados. Respetar APIs ocultas y consultas públicas compilables.
Referencias: openspec/specs/hash-table/spec.md:26-70; archive/2026-08-23-enhance-hash-table-pedagogy/specs/hash-table/spec.md:3-13; origen openspec/changes/archive/2026-08-23-remediate-didactic-c-trace-fidelity/specs/didactic-conformance-remediation/spec.md:54

### C1-REM-05 — Estado visual causado por eventos C
Cierres ABB/AVL/Heap/RN son casos registrados, no garantía de cada frame/evento de todas las familias. Mantener revisión futura sin convertir baseline/finalstate en causalidad.
Referencias: audit-local-quality-and-unified-controls/native-instruction-worklist.md; red-black-delete-instruction-review-plan.md; origen openspec/changes/archive/2026-08-23-remediate-didactic-c-trace-fidelity/specs/didactic-conformance-remediation/spec.md:68

### C1-REM-07 — Consola derivada de ejecución
Existe transporte console y verificación parcial; hay generación de literal printf desde texto y múltiples rutas. Falta demostrar exclusividad de eventos C alcanzados y reproducción exacta para todo contrato; no extrapolar una prueba positiva.
Referencias: app/services/execution_trace_service.py:68-74,1469; tests/test_phase7_trace_contract_remediation.py:58; origen openspec/changes/archive/2026-08-23-remediate-didactic-c-trace-fidelity/specs/didactic-conformance-remediation/spec.md:98

### C1-REM-08 — Cierre verificable de los hallazgos QA
Reporte29closed contrasta con29fixed_pending_gate preservados en matriz/prueba. No significa ausencia de corrección histórica; impide inferir cierre global vigente sin reconciliar gates/oráculos/revisión/evidencia antes-después.
Referencias: docs/qa/remediation-closure-report-v1.json; docs/qa/remediation-regression-matrix-v1.json; tests/test_remediation_plan_contract.py:15-25; origen openspec/changes/archive/2026-08-23-remediate-didactic-c-trace-fidelity/specs/didactic-conformance-remediation/spec.md:108

## Historia y cierre
Matriz histórica29fixed_pending_gate y reporte29closed permanecen intactos. Archivar este cambio solo consolida un contrato íntegro verificado; no cierra las dos capacidades completas, el arnés, la auditoría ni H1. Obtener evidencia/decisión faltante permite otro cambio posterior. No repartir requisitos amplios para fingir cumplimiento.

## Verificación
Pruebas documentales aisladas comparan requisito literal/scenarios,12decisiones,AST/identidad relevantes y JUnit; OpenSpec strict revisa estructura. No importan Flask ni motor app. Sanitizadores/aplicación no se vuelven a ejecutar por instrucción vigente.
