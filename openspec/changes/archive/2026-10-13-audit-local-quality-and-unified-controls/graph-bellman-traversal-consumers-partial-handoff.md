# Resultado parcial: consumidores Bellman / BFS-DFS

Asignación coordination-graph-bellman-traversal-consumers-low-20261008; operación audit.graph-bellman-traversal-consumers. Se detiene por instrucción expresa de coordinación de entregar los parciales ahora, sin nuevas ejecuciones.

Última ejecución completada: graphbt-compact-before, 2 FAILED en 111.81 s; supervisor 112.5 s, exit 1, límite 120 s y Job 2 GiB. Bellman original falla al buscar la guarda antigua dist[u] != INT_MAX; BFS pasa sus comprobaciones anteriores y DFS falla por esperar recursive_stack frente a recursión C. El ciclo negativo original de tres vértices no fue alcanzado por el primer fallo Bellman. No se corrigieron todavía los dos tests originales.

La primera ejecución graphbt-before agotó 120 s durante el volcado de evidencia tras retornar el servicio Bellman. Su JSON parcial se conserva como incompleto; no demuestra fallo funcional ni tiempo aislado del algoritmo.

Los siete archivos bajo snapshot permanecen idénticos, incluidos ambos tests originales, C/H y servicios. Se conserva tests/_graph_bellman_traversal_consumer_oracle.py como borrador NO VALIDADO: falta definir project_graphbt, referenciado por assert_graphbt_consumer; no se ha integrado ni probado. No usarlo como evidencia de conformidad.

No hay procesos de prueba graphbt/Bellman activos al entregar. Preview5051 no se tocó. No se ejecutó QA, publicación, campaña visual ni cambios de semántica. El balance previo sigue 27 aceptados / 33 corregidos pendientes QA independiente / 6 pendientes; estos dos IDs no se suman como corregidos.

Próximo paso, si coordinación mantiene el bloque: completar y validar primero el oráculo con capturas guardadas; corregir únicamente los dos consumidores y verificar por separado dentro de los límites. Ningún cierre funcional nuevo.
