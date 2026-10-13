# Revisión independiente: consumidor Desencolar Prioridad

Dictamen: RECHAZO focal por unicidad de tarjetas vivas no validada. Fecha2026-10-07; proyecto D:\MisProyectos\Web_VisualEstruct; change review-priority-dequeue-legacy-memory-consumer; operación qa.priority-dequeue-legacy-memory-consumer; assignment coordination-priority-dequeue-legacy-memory-independent-qa-low-20261007; task priority-dequeue-legacy-memory-independent-qa.

## Defecto imprescindible

En assert_priority_dequeue_lifetime, heap={id:node for node in memory.heap} elimina duplicados antes de assert len(heap)==4. Duplicar la tarjeta viva del objetivo20 y sincronizar dequeue_memory.heap, heap_objects y heap_transition.after es aceptado. Se reproduce en las tres etapas: objetivoPrev->sgte=objetivo->sgte; *valor=objetivo->valor; *prioridad=objetivo->prioridad. Sigue habiendo cuatro IDs únicos, pero cinco tarjetas para cuatro reservas; los checks existentes no lo detectan. La prueba negativa duplicate_retired sólo cubre tarjetas retiradas, no este caso vivo coordinado.

Reproducción aislada usa el fixture frozen original y helper stdlib, sin aplicación, algoritmos o native C. El fixture sano pasa. Contraejemplos (evidencia local: `openspec/changes/archive/2026-10-13-review-priority-dequeue-legacy-memory-consumer/evidence/independent-review/coordinated-duplicate-counterexample.json`).

Cambio requerido: exigir longitud y unicidad de IDs en la lista original antes de construir el diccionario, y correspondencia exacta de las listas de tarjetas/transición con las cuatro reservas reales hasta free. Añadir negativos coordinados en esas tres etapas manteniendo positivo original y trece casos actuales. No cambiar producto/C ni reabrir implementación cerrada. Éste es un hueco de expectativas, no un defecto demostrado del motor actual.

## Verificación satisfactoria

El C cp_desencolar compara actual->prioridad < objetivo->prioridad: el empate no reemplaza el primer mínimo. El consumidor conserva result20, cinco while/cuatro compares y conteos de items/unlink/free; confirma la desvinculación antes de copiar valor/prioridad, luego free y decremento. El helper exige nodo detached vivo con máscaras/campos válidos y alias activo hasta free; el retirado sólo conserva historical_fields.valor20, sin fields legibles. La sustitución del diccionario legacy temporaries es coherente con el contrato real.

Sólo cambia la función histórica seleccionada y un import, más helper/controles nuevos; los demás cuerpos AST son iguales.38inputs congelados coinciden, C byteidéntico y respuestas completas antes/después idénticas. XML:1FAIL baseline;13únicosPASS después =1ruta+12controles. No se repitieron pruebas ni se suman controles de mi reproducción. Preservación/resultados (evidencia local: `openspec/changes/archive/2026-10-13-review-priority-dequeue-legacy-memory-consumer/evidence/independent-review/preservation-and-results.json`), hashes (evidencia local: `openspec/changes/archive/2026-10-13-review-priority-dequeue-legacy-memory-consumer/evidence/independent-review/hash-check.json`).

Reconfirmados sin discrepancias Sorting9, jerárquico28, Apilar28 y Lista-console29; lotes aceptados e informes anteriores se conservan. Hashes previos (evidencia local: `openspec/changes/archive/2026-10-13-review-priority-dequeue-legacy-memory-consumer/evidence/independent-review/prior-lot-preservation.json`). No se recalcula66FAIL ni se declara cierre global.

Identidad QA propia registrada sin cambiar auditoría/otros bindings. Guardas before/after. Sin producto, publicación, despliegue, commit/push/reintento/ruta alternativa, campañas largas/globales/E2E o nuevos frentes. Pendiente imprescindible únicamente la unicidad viva coordinada descrita arriba.
