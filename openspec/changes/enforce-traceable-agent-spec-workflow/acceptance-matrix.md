# Matriz de aceptación propuesta

Todos los casos son futuros, NO EJECUTADOS. Cada escenario del delta tendrá un test aislado o revisión explícita según su naturaleza; no contar escenarios como tests ya realizados.

| Requisito | Positivo | Negativo / límite | Fase |
|---|---|---|---|
| R1 | Registro autorizado | Propuesta sin autorización técnica; Identidad contradictoria | 2–3 |
| R2 | Cambio cubierto | Ruta sin vínculo; Base desconocida | 2–3 |
| R3 | Documentación pura | Autor revisa su código; Transferencia registrada | 2–3 |
| R4 | Verificación reproducible | Fuente cambió; Check no ejecutado | 2–3 |
| R5 | Archivo funcional válido | Archivo fallido; Propuesta sintácticamente válida | 2–3 |
| R6 | Archivo documental | Requisito sustituido; Retiro sin motivo | 2–3 |
| R7 | Deuda intocada | Piloto aceptado; Bloqueo prematuro | 2–3 |
| R8 | Excepción vigente | Excepción caducada; Excepción inválida | 2–3 |
| R9 | PR conforme en superficie protegida | Check ausente o fallido; Evidencia solo local | 4 |
| R10 | Evaluación sin efectos | Alteración inesperada; Archivo movido | 2–3 |

Criterio adicional: evaluadores sin mutación; outputs legibles; mismos resultados en invocación repetida con mismas fuentes; fuentes legítimamente cambiadas requieren fotografía fresca. Fallo parcial no pierde historial. Activación CI exige ensayo y autorización independiente, no solo tests del evaluador.
