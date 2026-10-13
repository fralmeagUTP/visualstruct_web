# Revisión independiente: oráculo de frames jerárquicos

Dictamen: RECHAZO focal; un defecto material pendiente. Fecha2026-10-07, proyecto canónico D:\MisProyectos\Web_VisualEstruct. Change review-hierarchical-frame-oracle-fidelity; operación qa.hierarchical-frame-oracle-fidelity; assignment coordination-hierarchical-frame-oracle-fidelity-independent-qa-low-20261007; task hierarchical-frame-oracle-fidelity-independent-qa.

## Defecto indispensable para aceptación

El oráculo acepta tarjetas de memoria liberada inventadas. En assert_hierarchical_case se filtran objetos con freed=True antes de comprobar contenido, número e identidades de objects_before/objects_after. La lista freed_objects se verifica por separado; no autentica las tarjetas excluidas de aquellas listas.

Reproducción independiente: partir del fixture RN sano escrito a mano de test_hierarchical_frame_oracle.py; añadir a objects_before o a objects_after del primer frame una tarjeta {id:N_INVENTADO,address:N_INVENTADO,value:999,freed:True,allocated:True}. Ambas corrupciones son aceptadas. El fixture no contiene esa reserva ni evento de liberación. Esto permite mostrar identidad y contenido ficticios mientras todos los checks vivos y finales pasan. La reproducción sólo ejecuta el helper y fixture stdlib, sin importar producto, ejecutar algoritmos, C nativo o suites. Véase contraejemplo (evidencia local: `openspec/changes/archive/2026-10-13-review-hierarchical-frame-oracle-fidelity/evidence/independent-review/fabricated-freed-card-counterexample.json`).

Cambio requerido: validar también procedencia, unicidad, identidad, contenido y estado de tarjetas históricas/liberadas contra la evidencia causal de reservas y liberaciones; rechazar tarjetas que no pertenecen a esa historia. Conservar la presentación histórica legítima y no eliminar todas las tarjetas freed como solución. Añadir los dos negativos reproducidos y controles positivos de historia liberada real. Evitar comparación por conjuntos que admita tarjetas duplicadas en listas de eventos. Este arreglo es continuación del mismo defecto de oráculo; no requiere cambiar C, algoritmos, RN V3, los nueve preparados ni abrir otro frente.

## Verificación del resto del lote

Los124inputs del manifest final coinciden con SHA-256. En el test histórico sólo cambia test_every_hierarchical_operation_has_valid_state_and_trace y su import. El subconjunto se limita explícitamente a once combinaciones structure/operation, seeds y payloads; el else mantiene el assert original. None se exige como fidelidad del metadata de esos productores y nunca prueba validez de los estados transitorios. Fuera de ese subconjunto no hay exención global.

Las invariantes finales se calculan independientemente: orden BST estricto; altura real/FE/balance AVL; minheap y array/tree/count; colores, raíz negra, rojo-rojo y altura negra RN; identidades vivas, padres, ciclos, objetos compartidos y reservas separadas. Se revisaron predicados sobre operandos previos y cortocircuito, escrituras físicas/RHS, proyección y continuidad, y negativos contra alteraciones coordinadas. Esas comprobaciones no dependen del flag validation del motor como verdad. El alcance declarado de locales recursivos y fixtures simples permanece finito; no se certifica un intérprete C completo.

Las dos modificaciones RN son exactamente un literal explicativo en cada archivo: la consulta Validar completa sobre estado estable reemplaza el texto antiguo de consulta limitada. Restaurar sólo esos literales recupera el AST original completo en ambos módulos; las diferencias de líneas vacías no alteran comportamiento. La decisión V3 y su cierre finito respaldan el texto nuevo. No se reabre ni reimplementa Validar.

XML verificados: baseline once IDs11FAIL; intermediarios40 y44PASS; hierarchy-verified.xml contiene48únicosPASS0FAIL (once rutas y37controles). No se suman ejecuciones superpuestas. El XML verified registra5.256s de pytest y el result del supervisor6.594s; el5.91s del resumen no coincide con esos dos relojes y debe etiquetarse con su fuente si se conserva. Este detalle no cambia el denominador ni sustituye el defecto de memoria. Job efectivo2GiB antes de imports y supervisor120s registrados; no se repitieron pruebas. Véase AST/resultados (evidencia local: `openspec/changes/archive/2026-10-13-review-hierarchical-frame-oracle-fidelity/evidence/independent-review/structural-results-check.json`), hashes (evidencia local: `openspec/changes/archive/2026-10-13-review-hierarchical-frame-oracle-fidelity/evidence/independent-review/hash-check.json`).

## Continuidad y límites

El handoff autorizaba registrar identidad propia, aún ausente. Se añadieron únicamente fuentes/asignación/binding de esta revisión; la comparación semántica confirma que todos los changes/bindings anteriores permanecen iguales. Guarda before0; after guardada separadamente. Originales técnicos y evidencia histórica intactos. No commit/push/reintento/ruta alternativa, publicación, instalación, red, preview, campañas largas ni nuevos frentes.

La aceptación focal está bloqueada exclusivamente por la admisión de tarjetas de memoria ficticias descrita arriba. No implica defecto del TAD o cambios requeridos en C/algoritmos. Resolver y presentar negativos/positivos causales del mismo lote basta para nueva revisión; no hay recomendación de ampliar auditoría ni afirmación de cierre global.
