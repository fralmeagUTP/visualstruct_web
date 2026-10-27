# Paquete documental para el único auditor — 2026-10-03

Destinatario del trabajo técnico: dueño 01a0fc18-c146-7460-b83f-47a215e630cf. No se ejecutó este paquete ni se asignó siguiente operación. Reutilizar logs, fixtures y cierres existentes antes de proponer ejecuciones nuevas. Matriz: matrix-20261003.json/md. La QA del 02oct valida la entrega anterior, no esta actualización.

## Avance que debe conservarse
Once Sorting cerrados por dominio UI 1..80/int32 y entorno observado. Counting superó el cutoff n4/k4 y tiene rechazo de rango y reserva NULL modelados; Bin delega en Counting; Radix usa magnitud uint32 y rama INT_MIN. No repetir los once métodos ni tratarlos como pendientes generales. Radix excluye sanitizers y otras plataformas: C17 no prueba UBSan.

Hash ya tiene cierre LOW de create_table, insert, get, contains: 106 IDs únicos, 98 previos y ocho nuevos. El checkpoint MEDIUM que decía consolidación pendiente es histórico y queda superado por hash-query-finite-closure-decision-low.md. Restan remove, keys, values, items, stats, clear, destroy_table. Callers con cleanup no cierran automáticamente esos métodos. Retención arbitraria de consultas, truncamiento de historial y capacidad enorme no están certificados. No sumar 98+106 como cobertura nueva.

## Decisiones para el usuario, sin elección por esta revisión

| Decisión | Opciones existentes | Consecuencias |
|---|---|---|
| Validar RN | V1 conservar alcance parcial; V2 ampliar backend y auxiliares del main; V3 exportar validación completa también en C/H | V1 acepta explícitamente limitación: OK no certifica altura negra/padres/ciclos. V2 modifica semántica sin ofrecer función descargable. V3 modifica C/H, fuente mostrada, main, trazas y guía; evita duplicar helpers y exige negativos de invariantes. La recomendación V3 pertenece a la propuesta técnica, no es aprobación. |
| Grafos entero fiel | Conservar int C, orden de empate, INT_MAX como infinito y guarda de suma; validar rango/finitud y reconciliar escenario decimal | Contrato C docente consistente; modifica expectativas canónicas sobre decimales con decisión expresa. Preservar regresiones numéricas y no truncar fracciones silenciosamente. |
| Grafos ampliado | Diseñar pesos decimales o tipos/distancias más amplios con política explícita | Impacta C/H, API, algoritmos, parser, exportación/main, errores, trazas y manual; requiere cambio separado y evidencia nueva. No inferir aprobación por aceptar H1 Hash. |

Fuentes: [opciones RN](../2026-10-13-audit-local-quality-and-unified-controls/red-black-validation-extension-proposal.md), [limitación RN](../2026-10-13-audit-local-quality-and-unified-controls/red-black-validation-limit-decision.md), [decisión Grafos](../2026-10-13-audit-local-quality-and-unified-controls/graph-dijkstra-numeric-contract-decision.md). Resolver esas decisiones no cierra automáticamente fidelidad global. No ejecutar pesos no representables en C para producir un oráculo.

## Evidencia concreta que falta — buscar primero lo ya ejecutado

| Obligación C1 | Entrega requerida del auditor | Criterio conservador |
|---|---|---|
| QA-01 inventario | Mapa opción/control→ruta de test→ID/fixture→datos/esperado→log/revisión; controles sin ID como filas faltantes | Un ID generado o una cadena oracle no prueba enlace ejecutable; nueva opción sin prueba debe producir fallo verificable. No suite general para comprobar cadenas. |
| QA-02/03, REM-01/05 | Tabla por escenario/clase/vista que enlace cierres Sorting11, Hash4 y demás familias; justificar vacío rechazado y no aplicables; dejar Hash7/Grafos pendientes | No repetir cierre para generar mapa. Cada cobertura remite a prueba/eventos/UI realmente existentes y fuentes pertinentes. |
| REM-02 Radix INT_MIN | Ubicación y salida de UBSan realmente ejecutado con ese fixture, compilador/flags/ABI y SHA de fuentes. Si no existe, documentar bloqueo y proponer corrida acotada al dueño, según entorno/autorización | Resultado/multiconjunto/orden correctos y sin UB; no atribuir ASan/UBSan a C17 o a CI configurada. Count/Bin rango/error ya apoyados: enlazar esos casos antes de ensayar otra vez. |
| REM-04 Hash/secuenciales | Mapping del índice determinista C/backend entre procesos, claves/capacidad/cadenas y logs; snippets DOM cima/frente/final con header y comparación UI | Hashquery caller no reemplaza el escenario secuencial. Nativos C son otro proceso, pero registrar claramente ambos ejecutores y repetibilidad antes de afirmar el escenario entero. |
| REM-03 Grafos | Después de decisión: casos no representables sin mutación; Prim/Kruskal desconectados con bosque/componentes API/traza/DOM | No cerrar con presencia de seis algoritmos ni con solo estado final. Mantener los negativos Dijkstra que ya pasan; no revivir GRAPH-004 como defecto actual. |
| REM-07 consola | Mapa de todos los emisores y pruebas ya existentes de mensaje técnico sin printf, salida C alcanzada y prefijos adelante/atrás/reinicio | Sorting sinprintf y Hash4 constituyen evidencia local nueva; transporte step.console no demuestra procedencia en toda app. |
| QA-04 y REM-08 | Resultados finales no funcionales e índice 29 caseIDs con antes/después, fixture/oráculo/capa/integración/C17/sanitizers/UI; explicar precedencia closed/fixed_pending_gate | No convertir 106 Hash en 29 remediaciones. Infraestructura ausente es bloqueo; cierre de informe antiguo no es cierre actual por inferencia. |

## Forma de respuesta suficiente
Por cada fila, devolver evidencia existente con ruta/ID exacto, datos/esperado, resultado real, fecha/plataforma y hashes pertinentes, o gap explícito. Si requiere ejecución nueva, indicar fixture/objetivo acotado, comando propuesto y criterio de seguridad antes de ejecutarlo en el flujo técnico propio. Este autor no crea pruebas ni corre comandos de aplicación.

C1 sigue 1/12 admitido y once requisitos íntegros pendientes. El corte antiguo Counting ya no es motivo vivo; el avance parcial sí debe reconocerse. 13/22 sigue contando tareas transversales, no tiempo, porcentaje funcional ni suma de métodos. La decisión de consolidar un requisito completo exige su evidencia íntegra y revisión; esta actualización no archiva ni reescribe specs.

## Límite temporal de esta entrega

Véase [snapshot e impacto](snapshot-impact-20261003.md). Cierres históricos yfuentes fechadas; no se certifica repo vivo totalmente fresco. El auditor trabaja Hashremove: nueva implementación provisional hasta sucheckpoint/cierre. No detenerlo ni repetir ensayos para estabilizar nuestros hashes. Re-QA sólo del snapshot congelado ycorrección documental.
