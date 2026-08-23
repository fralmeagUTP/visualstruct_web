# Auditoría didáctica de lista enlazada

Se verificaron inserciones al inicio, final y posición, búsqueda con múltiples
coincidencias, eliminación de cabeza/medio/cola, valor ausente, eliminación de
repetidos, enlaces y liberaciones. El harness registra `matches=2` y
`removed=2` y conserva las salidas reales de `printf` separadas del estado.

| Área | Resultado |
|---|---|
| Inicio/final/posición | Aprobado según contrato C actual |
| Búsqueda y `printf` | Aprobado |
| Primera ocurrencia y repetidos | Aprobado |
| Enlaces y liberaciones | Aprobado en estado final |
| Inversión, primero, último y eliminar posición | Fallido (`LINKED-001`, alta) |

`LINKED-001` documenta que esas operaciones se ejecutan únicamente mediante
código Python del wrapper y carecen de función C para interpretar o resaltar.
La tarea queda auditada con el defecto abierto.
