# Auditoría de construcción y consultas de grafos

Se verificaron grafo vacío, vértices aislados, componentes desconectados,
orientación, inserción repetida, extremos inexistentes, pesos y consultas de
existencia, costo, orden y tamaño.

| Área | Resultado |
|---|---|
| Consultas C de vacío, existencia, costo, orden y tamaño | Aprobado |
| Grafo dirigido y vértices desconectados | Aprobado en el oráculo C |
| Unicidad y validación de extremos | Divergencia (`GRAPH-001`, alta) |
| Actualización frente a duplicación de aristas | Divergencia (`GRAPH-001`, alta) |
| Grafo no dirigido frente al C interpretado | Divergencia (`GRAPH-002`, alta) |
| Pesos decimales y sincronización de consola/estado | Fallido (`GRAPH-002`, alta) |

El oráculo dejó de declarar invariantes no comprobadas y ahora expone cuándo el
C contiene vértices duplicados o aristas con extremos inexistentes. La tarea
queda auditada sin modificar la lógica productiva.
