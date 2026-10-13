# Ampliar Validar Rojo-Negro completo

## Why
El validador actual omite altura negra e integridad de padres/ciclos; la spec canónica ya exige altura negra. La vista NIL reconstruida puede ocultar errores del modelo. El usuario aprobó validar todas las reglas con fuente C descargable.

## What Changes
Reescribir requisito Invariantes Rojo-Negro con cinco reglas completas e integridad; exportar int rbt_validar(RBT raiz), replicar semántica en backend y mostrar funciones C reales con observación causal, caller y guía coherentes. Mantener consulta booleana sin mutación, política actual sin duplicados y separación entre modelo NULL y vista NIL.

## Impact
Capacidad hierarchical-structures; futura implementación en C/H RN, wrapper/trace/source/main/ayuda/pruebas relacionadas. Sólo contrato documental realizado ahora; implementación por único auditor después de su checkpoint Encolar. Sin cambios Grafos/Dijkstra, otros algoritmos, nuevos botones, diagnóstico estructurado ni punteros arbitrarios.

## Approval
Decisión V3 aprobada por usuario; decision.md conserva citas y excepción C/H acotada. No aprobación ni cierre técnico derivados de OpenSpec syntax.
