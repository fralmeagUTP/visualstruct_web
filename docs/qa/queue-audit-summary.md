# Auditoría didáctica de cola FIFO

Se verificaron encolado, desencolado, frente, final, vacío, limpieza, enlaces y
liberaciones. El oráculo cubre una cola de un nodo para comprobar que al
desencolarlo `delante` y `atras` quedan en `NULL`, y una cola de varios nodos
para comprobar el orden FIFO.

| Área | Resultado |
|---|---|
| FIFO | Aprobado (`value=1`) |
| Frente y final | Aprobado en C (`front=1/2`, `rear=1/3`) |
| Último nodo | Aprobado; ambos extremos quedan en `NULL` |
| Limpieza y estado vacío | Aprobado |
| Código mostrado para frente/final | Fallido (`QUEUE-001`, alta) |

`QUEUE-001` demuestra que el panel ignora la función C real `cola_frente` y
muestra llamadas a `cola_copiar_valores`, que no existe. La tarea está auditada
con el defecto abierto; no se modificó el comportamiento funcional.
