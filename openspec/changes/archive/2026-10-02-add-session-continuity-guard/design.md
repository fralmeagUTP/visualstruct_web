# Diseño mínimo
Python estándar sin Flask; índice con proyecto/sources/bindings operación→fuente/marcador/evidencia. Sin estados/contadores duplicados. Guarda imprime JSON y nunca escribe. Protege agentes que ejecutan bootstrap; no sandbox ni verificador semántico.

Cierres por marcadores exactos revisados en evidencia. Sin marcador no inferir signoff; IDs desconocidos fallan. Evidencia se exige existente y contenida en raíz; hash no es prueba verde. Registrar alcance finito. Nuevos títulos/cierres requieren reconciliar binding.

Checkpoint incluye UTC/SHA/bytes/mtime. Stat y segunda lectura detectan cambios durante lectura; comparar fotografía exige identidad/conjunto/bytes iguales. Cambios posteriores siguen posibles; repetir antes de actuar. No claim de commit completo ni todas las fuentes productivas.

Reapertura exige ID/razón exactos persistidos en decisión de openspec/changes; no valida quién aprobó ni suficiencia de razón. Agente confirma autorización aplicable. Última cabecera es pista, nunca siguiente tarea automática.

Pruebas usan TemporaryDirectory/unittest fuera de tests/conftest.py; -B evita bytecode. Validación OpenSpec solo del propio cambio. No suite app por prohibición explícita.

Reconciliación: preparar diferencias sin fusionar contratos Hash/capacidades cuya aprobación/consolidación completa sea ambigua. Archivo del propio arnés pendiente de revisión y decisión; mantener change activo.

## Adopción
Guarda exige directorio change activo; archivado no sigue trabajando mediante binding antiguo. context_sources enlaza plan/decisiones/diagnósticos existentes; task_prefix deriva pendiente/completado de una casilla única sin duplicar estado ni reemplazar cierre por operación. before exige decisión para repetir cerrado; after solo reporta cierre, jamás autoriza nueva implementación. Log adicional fuera de fuentes no invalida foto; append/fuente nueva registrada requiere releer/foto fresca. Permite ciclos legítimos protegiendo contra contexto antiguo.

## Incidente de asignación
Guardas de cierres no comprobaban identidad de instrucción; coordinación reportó selección histórica Lista/Circular pese a asignación explícita MEDIUM EliminarRN. No inferir causa interna. assignment_source apunta a registro persistido de instrucción; ID explícito obligatorio, operación coincide antes de gate de reapertura. No duplicar estado de auditoría: registro es instrucción/procedencia, no pending/completed. Preservar registros antiguos y actualizar puntero al cambiar solicitud. No autentica prompt fuera del proceso; bootstrap exige cotejo humano/agente con mensaje nuevo.

## Cierre y runtime estable
Mover referencias operativas a openspec/continuity/index.json, README.md, reconciliation-status.md y assignments/. Conservar originales como snapshots en archivo. Script CONFIG y AGENTS apuntan solo a runtime estable. Índice operativo solo registra changes activos tras archivo; el change cerrado no sigue siendo trabajo seleccionable. Consolidar session-continuity y verificar requisito literal/enlaces/runtime. Adopción confirmada mediante README/checkpoint/continuity-after técnicos con ID; no editar esos archivos ni fabricar cierreLOW/global. Hash y11pendientesC1 siguen abiertos.
