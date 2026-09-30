# Auditoría didáctica de montículo binario

## Cobertura ejecutada

Se verificaron min-heap y max-heap a nivel de dominio, inserciones, duplicados,
consulta y extracción de raíz, eliminación presente/ausente, construcción,
crecimiento de capacidad, vacío, copia y formatos de arreglo/árbol. El harness
C representativo inserta once valores para forzar el `realloc`, consulta la raíz
y después la extrae.

| Operación | Caso | Resultado |
|---|---|---|
| Insertar / sift-up | once valores descendentes | Estado final e invariante aprobados |
| Crecimiento | inserción 11 sobre capacidad efectiva 10 | `realloc` observado |
| Raíz | min-heap con raíz 1 | retorno exacto `root=1` aprobado |
| Extraer / sift-down | extraer 1 | retorno y estado final aprobados |
| Arreglo/árbol | árbol derivado por índices `2i+1`, `2i+2` | Estado final aprobado |
| Paso a paso | insertar 1 sobre `[2,5,3]` | Fallido (`HEAP-001`) |

## Hallazgo abierto

`HEAP-001` (alta): el frontend omite el append y los swaps reales de sift-up.
El modo rápido alcanza el estado correcto, pero el paso a paso no interpreta
los estados intermedios ejecutados por C.
