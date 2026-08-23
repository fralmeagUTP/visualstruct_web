# Auditoría didáctica de sublistas

Se verificaron inserciones de padres e hijos, duplicados, búsqueda, consulta de
hijos, eliminación presente/ausente, eliminación de padre con su sublista,
limpieza y enlaces de ambos niveles.

| Área | Resultado |
|---|---|
| Inserción, consulta y eliminación C | Aprobado |
| Liberación padre con hijos | Aprobado en oráculo C |
| Identidad lógica padre/hijo | Corregida para snapshots canónicos |
| Padres duplicados en frontend | Fallido (`SUBLIST-001`, alta) |
| Limpieza backend frente a C | Fallido (`SUBLIST-002`, alta) |

El wrapper colapsa padres duplicados al convertirlos en diccionario y su método
`limpiar` descarta la referencia sin ejecutar `sublista_destruir`. La tarea está
auditada con ambos defectos abiertos.
