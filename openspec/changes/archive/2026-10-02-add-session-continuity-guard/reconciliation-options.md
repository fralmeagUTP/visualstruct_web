# Opciones concretas para reconciliar OpenSpec

Ninguna opción se aplicó a semántica ni specs canónicas. Referencias relativas al proyecto D:.

## Hash
Evidencia: openspec/specs/hash-table/spec.md:26-32 texto; :62-70 rehash0.75. Archivo2026-08-23-enhance-hash-table-pedagogy/specs/hash-table/spec.md:3-13 enteros/capacidad fija. Auditoría activa reconciliation.md:32,43 y current-operation-contract respaldan preservar C, sin rediseño. Esta divergencia no demuestra por sí sola aprobación íntegra del contrato actual.

| Opción | Cambio revisable | Consecuencia |
|---|---|---|
| H1 recomendada | Autorizar que contrato canónico Hash siga C entero/capacidad fija; preparar MODIFIED/RENAMED validación, escenarios insert/get y estado; REMOVED rehash; revisar fields resized/resize_event/compatibilidad | Documentación describe el producto pretendido y fuente didáctica; no introducir nuevo runtime por este cambio. Requiere cotejo técnico del comportamiento real antes de afirmar verdad actual |
| H2 | Mantener texto/rehash como producto objetivo y proponer cambio funcional separado con diseño de compatibilidad/C didáctico | Amplía semántica/alcance y no debe mezclarse con auditoría o arnés |
| H3 provisional | Mantener conflicto explícito y bloquear consolidación semántica Hash hasta decisión | Conserva honestidad, pero no resuelve fuente canónica contradictoria |

Decisión del usuario requerida: confirmar H1 o H2 (H3 permite diferir); especificar si compatibilidad pública de payloads/metadatos antiguos debe mantenerse. No asumir que autorización general de arreglar OpenSpec seleccionó H1. Recomendación H1 porque fuentes de auditoría priorizan C como oráculo y preservar semántica; aprobar intención no sustituye evidencia técnica.

## Capacidades archivadas sin spec canónica
Evidencia: archive/2026-08-23-establish-comprehensive-app-quality-validation/specs/application-quality-validation/spec.md y archive/2026-08-23-remediate-didactic-c-trace-fidelity/specs/didactic-conformance-remediation/spec.md; directorios canónicos ausentes. reconciliation.md:33 reconoce omisión; detailed/JSON clasifica requisitos, escenarios y tareas sin declarar conformidad.

| Opción | Trabajo propuesto | Recomendación |
|---|---|---|
| C1 | Incorporar a specs solo requisitos cuya implementación vigente/evidencia estén verificados; mantener deltas pendientes para los demás, con ID histórico conservado | Recomendada: fuente canónica fiable y pendientes recuperables |
| C2 | Fusionar íntegramente deltas históricos como contrato objetivo, identificándolos como deuda | Mezcla objetivo y verdad actual bajo reglas del repo; no recomendada sin redefinir explícitamente qué significa specs/ |
| C3 | Consolidar capacidades equivalentes existentes mediante MODIFIED/RENAMED/REMOVED con tabla de correspondencia | Útil si elimina duplicación; exige mostrar equivalencia por requisito antes de retirar nombres |

Decisión de producto del usuario: necesaria si se quiere retirar/sustituir compromisos pedagógicos o reducir alcance. No hace falta pedir permiso adicional para inventariar/muestrear/verificar en lectura o preparar C1 dentro de autorización existente; la auditoría dueña aporta signoffs. No inferir ausencia de aprobación porque no sea verificable desde Git.

## Validar Rojo-Negro
Decisión independiente ya registrada en audit-local-quality-and-unified-controls/red-black-validation-limit-decision.md: aceptar validación parcial documentada o autorizar extensión de black-height/parents/cycles. Nunca resolverla por lograr7/7 métodos ni durante Eliminar. No modificar desde este arnés.

## Resultado a revisar
Antes de consolidar mostrar requisito antiguo→decisión→delta completo→código/prueba/evidencia vigente. Conservar archivos históricos. OpenSpec strict es gate estructural; la decisión y conformidad real son gates distintos.

## Refuerzo estático de H1
app/adapters/hash_table_adapter.py:56-66 exige enteros para clave/valor; app/domain/hash/pedagogy.py:171 explica capacidad fija. Es evidencia de lectura, no prueba funcional ni aprobación. La recomendación H1 sigue requiriendo decisión explícita de contrato/compatibilidad y cotejo técnico.

## C1 parcial aplicado2026-10-02
Consolidado solo Traza continua y fuente verificable en openspec/specs/didactic-conformance-remediation/spec.md. Fuente/motor/escenarios/evidencia y11pendientes: openspec/changes/archive/2026-10-02-reconcile-verified-historical-trace-contract/reconciliation.md. No cierra capacidades completas ni auditoría/29casos; no modifica Hash/H1. Evidencia ejecutada es histórica, transferida por identidad relevante, no suite app nueva. Arnés permanece activo pendiente de confirmar adopción con assignment-id.
