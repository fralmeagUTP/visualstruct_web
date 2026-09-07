# Auditoría didáctica de pila

Se verificaron LIFO, apilado, desapilado, cima, vacío, limpieza, liberaciones,
errores por pila vacía y sincronización del estado final. El caso representativo
observa `empty=1`, apila 1 y 2, obtiene `top=2`, desapila `value=2`, limpia y
vuelve a observar pila vacía.

| Área | Resultado |
|---|---|
| Orden LIFO y estado final | Aprobado |
| Retorno de cima y desapilado | Aprobado |
| Limpieza y liberación | Aprobado |
| Código C mostrado para `cima` | Fallido (`STACK-001`, alta) |
| Nodo temporal `aux` y enlaces paso a paso | Fallido (`STACK-002`, alta) |

La tarea se considera auditada, no libre de defectos. Las correcciones sugeridas
están documentadas sin modificar todavía el comportamiento funcional.
