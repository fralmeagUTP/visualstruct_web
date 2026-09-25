# Auditoría didáctica de tabla hash

## Cobertura ejecutada

El harness C usa capacidad 17 y ejecuta, en orden: inserción `(1,10)`, inserción
colisionante `(18,20)`, actualización `(1,11)`, búsqueda de `1`, búsqueda de
`99` y eliminación de `18`. Cada operación genera límites `before/after`, estado
canónico y eventos de comparación, retorno, enlace, reserva o liberación cuando
corresponde.

| Operación | Entrada | Estado o retorno C esperado | Resultado |
|---|---|---|---|
| Insertar | `(1,10)` | par nuevo, tamaño 1 | Aprobado |
| Colisión | `(18,20)` | mismo bucket que 1, tamaño 2 | Aprobado |
| Actualizar | `(1,11)` | tamaño 2, valor 11 | Aprobado |
| Buscar | `1` | `found=1`, `value=11`, sin mutación | Aprobado |
| Buscar ausente | `99` | `found=0`, sin valor ni mutación | Aprobado |
| Eliminar | `18` | nodo liberado, tamaño 1 | Aprobado |
| Rehash | tercera inserción con capacidad 3 | C conserva 3; backend cambia a 7 | Fallido (`HASH-001`) |
| Función hash textual | clave `"A"` | misma función e índice que C | Fallido (`HASH-002`) |

## Hallazgos abiertos

- `HASH-001` (alta): el backend implementa rehash automático que no existe en el TAD C.
- `HASH-002` (alta): el backend usa claves de texto y el `hash()` no reproducible de Python; el C usa enteros y `clave % capacidad`.

Las correcciones propuestas están en `docs/qa/findings/` y no se ha modificado
el comportamiento funcional de la aplicación durante la auditoría.
