# Entrega vigente: validador completo Rojo-Negro

La aclaración RN-IMPL-01 está aceptada por revisión independiente y la tarea documental `rn-contract-documentation` queda cerrada con guardas. Esta entrega actualiza el estado; la entrega anterior se conserva en `evidence/before-final-close-handoff.md`.

## Contrato y resultado verificado

El contrato aprobado exige las cinco reglas RN (colores legales, raíz negra, NULL conceptual negro, ausencia de rojo-rojo y altura negra uniforme), orden ABB estricto sin duplicados, enlaces padre coherentes y detección de ciclos/nodos compartidos sobre objetos vivos. `int rbt_validar(RBT raiz)` recibe una raíz prestada, acepta vacío y devuelve 1/0 sin modificar estructura, reservar/liberar memoria ni imprimir. Aplicación de invariantes tras operaciones completas desde estado válido, sin exigirlas a primitivas aisladas o estados intermedios.

[Revisión independiente](../2026-10-13-audit-local-quality-and-unified-controls/evidence/independent-review-RN-implementation/review.md) aceptó documentación y funcionalidad finita el 2026-10-03: 53 pruebas propias (52 normativas y una RAW service), 17 fixtures C/Python, cuatro trazas nativas, cinco comprobaciones privadas del registro y un caller de extremos. Las reproducciones/subconjuntos no se suman como nuevos casos globales. La evidencia fue ejecutada por el revisor; este cierre documental no repite pruebas.

[Decisión de cierre funcional del auditor](../2026-10-13-audit-local-quality-and-unified-controls/red-black-full-validator-finite-closure-decision-low.md) delimita el resultado y conserva algoritmos de inserción, eliminación y rotación.

## Historial: RN-IMPL-01 resuelto

Validar preserva valores, colores, enlaces y reservas. Cada consulta explícita completada, incluso resultado False, añade exactamente una entrada al registro cronológico RN existente. GET/rebuild/navegación conservan consultas sin redispatch de las operaciones guardadas ni duplicación. `to_visual_state` puede evaluar el validador readonly para metadata: no se afirma cero llamadas internas. Errores de entrada no se registran como consultas completadas. No se introduce journal ni almacenamiento separado.

[Decisión de aclaración](history-clarification-decision.md), [delta](specs/hierarchical-structures/spec.md), [diseño](design.md) y [aceptación](acceptance-plan.md) conservan el contrato revisado.

## Límites y continuidad

ASan/UBSan no pudieron enlazarse (-lasan/-lubsan); no existe certificación bajo sanitizadores. No se garantiza seguridad para punteros inválidos, profundidad arbitraria, agotamiento de pila, RSS/OOM, todos los inputs ni otros ABI/plataformas. La descripción canónica general de `session-state` sigue pendiente de reconciliación por su dueño; este cierre no la modifica.

Cambio no archivado, C1 y auditoría global abiertos. Las decisiones de Grafos sobre pesos enteros y reglas actuales C de Dijkstra fueron confirmadas por el usuario; su reconciliación corresponde al auditor. Esta entrega no modifica producto, C/H, evidencia/checkpoints ajenos, preview ni Git.
