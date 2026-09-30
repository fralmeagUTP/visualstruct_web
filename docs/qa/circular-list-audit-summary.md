# Auditoría didáctica de lista circular

Se probaron lista vacía, un nodo, varios nodos, duplicados, inserción en ambos
extremos, búsqueda acotada por retorno a cabeza, eliminación de cabeza/cola/nodo
único, inversión y limpieza. Las búsquedas produjeron `matches=1` y `matches=2`.

| Área | Resultado |
|---|---|
| Operaciones e invariante circular C | Aprobado |
| Búsqueda sin ciclo infinito | Aprobado |
| Eliminación e inversión | Aprobado |
| Cierre visual con varios nodos | Aprobado por renderer SVG |
| Autoenlace visual con un nodo | Fallido (`CIRCULAR-001`, alta) |

El renderer retorna cuando encuentra menos de dos nodos, aunque en C un único
nodo apunta a sí mismo. La tarea queda auditada con este defecto abierto.
