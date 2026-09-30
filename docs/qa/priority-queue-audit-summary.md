# Auditoría didáctica de cola de prioridad

Se probaron prioridades iguales, estabilidad por llegada, `INT_MIN`, `INT_MAX`,
consulta, cuatro extracciones consecutivas, vacío, último nodo y limpieza.

El C conserva enlaces en orden de llegada y busca el mínimo durante
`cp_desencolar` en O(n). La transcripción Python inserta ordenado y elimina el
frente en O(1). Ambos producen `200,100,300,400` para el caso extremo, pero los
pasos, comparaciones y enlaces internos no son equivalentes.

| Área | Resultado |
|---|---|
| Prioridad y extremos | Estado final aprobado |
| Empates FIFO | Aprobado |
| Liberación y último nodo | Aprobado |
| Estrategia C frente a backend | Fallido (`PRIORITY-001`, alta) |
| Semántica de `frente` | Fallido (`PRIORITY-002`, alta) |

La tarea queda auditada con dos defectos abiertos y sin modificar el código
funcional de la aplicación.
