# Opciones compartidas Dijkstra / Bellman-Ford, sin decisión implementada

| Tema | Alternativas | Recomendación y compatibilidad |
|---|---|---|
| Tipo/rango de pesos | A: int32 representable y finito, integral; B: diseñar decimales en C/H, API, trazas y exportación | A conserva C docente actual y rechazo de fracciones; debe rechazarse limpiamente fuera de rango/Infinity. Requiere reconciliar spec decimal; decisión de usuario aún pendiente. B es cambio transversal y no permite truncamiento silencioso. |
| Infinito/overflow de distancias | A: reproducir int/INT_MAX y guardas; B: distancias amplias con infinito separado y suma comprobada | Para fidelidad inmediata A documenta el C, pero INT_MAX válido queda ambiguo y Bellman puede omitir ciclos. Recomiendo B como reparación explícita posterior de distancias, manteniendo pesos int si se aprueba A de la primera fila. A no resuelve el defecto matemático. No retirar guardas ni ejecutar overflow. |
| Empates | A: backend/traza reproducen lista de índices/arcos y mejora estricta del C; B: cambiar desempate C | A mantiene lo que aprende el estudiante. Mismo costo no prueba mismo camino/aristas. |
| Ciclo negativo alcanzable | A: conservar comprobación C acotada y defecto abierto; B: detección con distancias suficientemente amplias/suma segura | B resuelve caso de dos arcos INT_MIN y requiere oráculo de límites. Ciclo desconectado no invalida otro origen. Dijkstra conserva rechazo de todo arco negativo; Bellman admite pesos negativos. |
| Estatus de ciclo | A: success=true+bandera y reconciliar spec; B: error conforme a spec | Recomiendo B después de asegurar detección fiable. Definir HTTP, consola de advertencia y exclusión del historial exitoso; la traza debe explicar la llamada real, no inventar rechazo previo. |
| Compatibilidad | Mantener firmas externas de pesos int, ampliar distancias internas/resultado con contrato explícito; o rediseñar también pesos | Tipo int externo limita ruptura, pero C NULL no distingue ciclo, vacío o error de memoria; cualquier resultado enriquecido necesita diseño acordado. Pruebas de generación/historial no resuelven esta decisión. |

Prioridad: coordinación resuelve primero enteros/decimales; después representación de distancias, ciclos y estatus. No se repite la pregunta al usuario ni se cambia semántica. Las recomendaciones son propuestas, no aprobación. Prim también tiene divergencias de negativos/INT_MAX/empate; no extender automáticamente decisiones de camino mínimo a MST. Prim C opera arcos sin bandera dirigida, API exige no dirigido; esa compatibilidad permanece documentada.

Fuentes locales: graph-dijkstra-numeric-contract-decision.md, graph-bellman-ford-numeric-cycle-options.md y evidencia visible-graph-prim-baseline-low. No conversiones C inseguras ejecutadas.


## Confirmación nueva 2026-10-03: enteros y reglas actuales C de Dijkstra

Usuario confirmó pesos enteros representables y reglas C actuales de Dijkstra. Esta instrucción sustituye las filas históricas que aún pedían decisión de enteros/decimales y de empate/INT_MAX/guarda Dijkstra. Ver graph-approved-integer-dijkstra-contract-decision-low.md y specs/graph-structures/spec.md. No implementación/paridad técnica cerrada; representación/ciclos Bellman-Ford y dominio Prim siguen pendientes por su propia decisión. No volver a preguntar pesos/Dijkstra ni ampliar automáticamente su restricción no negativa a otros algoritmos.
