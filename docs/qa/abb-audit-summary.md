# Auditoría didáctica de ABB

Se verificaron inserción y duplicados, búsquedas presente/ausente, recorridos,
mínimo/máximo, altura, orden BST y eliminación de hoja, nodo con un hijo y nodo
con dos hijos. La matriz observa `found=1`, `found=0`, `min=3` y `max=8`.

| Área | Resultado |
|---|---|
| Inserción, búsqueda y extremos | Aprobado |
| Recorridos y orden BST | Aprobado |
| Eliminación hoja/un hijo | Aprobado |
| Estado final al eliminar dos hijos | Aprobado |
| Estado temporal de copia del sucesor | Fallido (`ABB-001`, alta) |

La traza salta del árbol anterior al final y omite el instante real donde el
valor sucesor aparece simultáneamente en el nodo sustituido y en su nodo de
origen. La tarea queda auditada con ese defecto abierto.
