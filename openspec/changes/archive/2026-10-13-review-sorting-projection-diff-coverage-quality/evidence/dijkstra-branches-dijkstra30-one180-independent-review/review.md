# QA Dijkstra30 privado180s: MemoryError e incidencia de continuidad

Dictamen: **ACEPTAR los artefactos como evidencia diagnóstica de un fallo real e incompleto; RECHAZAR cumplimiento de guarda previa y cierre operativo/fidelidad Dijkstra30.** Sin adopción, repetición ni nuevas pruebas.853 hashes vinculados coinciden;250 fuentes canónicas y3 fuentes privadas aceptadas permanecen iguales. Guarda de esta revisión before aprobada con coordination-dijkstra-branches-dijkstra30-one180-qa-low-20261006 / audit.dijkstra-branches-dijkstra30-one180-independent-quality. Proyecto canónico D:\MisProyectos\Web_VisualEstruct; sólo evidencia/tracker propios.

## Secuencia y autorización

- 07:42:39.950177Z: assignment de coordinación autoriza UNA petición180s/2GiB misma variante; operación sucesora audit.dijkstra-branches-dijkstra30-one180-observed. Decision/scope conservan ensayo60s cerrado y especifican alcance nuevo, sin optimización/retry.
- Antes del lanzamiento según incidencia preservada: guarda inicial rechazada literalmente: `Continuity guard: Reopen arguments apply only to a recorded closed operation before work`. Archivo de rechazo no tiene timestamp propio: no es posible asignar UTC exacto independiente a esa llamada. La evidencia disponible no incluye transcripción íntegra de shell/assert, por lo que el mecanismo shell-continuó-tras-assert es declaración preservada del autor, consistente con los arranques registrados.
- 07:42:41.478407Z: controller5056 inicia campaña1. Worker real8992 inicia07:42:41.570048Z; prueba selfJob/límite antes imports; wrapper6880 distinto, sin inferir genealogía.
- 07:42:59.772857Z: comienza la única petición tras60POSTs preparatorios fuera del reloj.
- 07:44:18.926033Z: registro de incidencia reconoce fallo inicial y petición activa.
- 07:44:21.370067Z: timestamp interno de checkpoint corregido before;81.597210s DESPUÉS de empezar petición. Incidencia registra final captura07:44:21.428823Z. before0 es TARDÍO; no subsana precondición incumplida.
- 07:45:02.649571Z: campaña registra workerexit1/operational_stop null;07:45:02.653567Z controllerexit0 sólo significa campaña guardada, no petición exitosa. after0 posterior informa continuidad actual.

El rechazo es documental de la guarda por flags de reapertura usados sobre una operación sucesora, no una denegación del sandbox/auto-review ni rechazo de la autorización sustantiva ONE180. Tampoco es mero detalle inocuo: continuar sin guarda válida incumple AGENTS y pierde verificación de precondiciones al instante anterior al trabajo. La instrucción ya emitida autoriza el ensayo; la validación tardía no permite afirmar cumplimiento previo ni reconstruir retrospectivamente igualdad de todos los inputs en ese instante.

## Evidencia válida y límites

Se recalcularon853SHA,250canon,107muestras, límites y stacks desde archivos originales. Worker8992 selfJob específico con2147483648bytes/flags8448 antes de imports. Tres overlays efectivos coinciden con variante aceptada. Preparación contiene60operaciones. No complete-response ni plain-result.

Primer conteo22430 a110.2650265s ocurre en normalize_steps/validate_graph_logical_trace: etiqueta heuristic generation_pedagogy no describe fase real. Primera muestra pack111.4029639s y última118.261228s aún dentro finish_graph_trace/build_graph_numeric_trace: builder_returned=true no demuestra retorno en ese momento. Traceback graph_routes.py272 -> jsonify -> json.dumps -> encoder.iterencode/_iterencode -> MemoryError demuestra retorno eventual builder/pack/validadores normales y _json_safe, seguido de fallo JSON. No timeout180: workerexit1. No tiempo completo request perf_counter;119.7159398 es última muestra,141.156 incluye preparación/error/save.

MaxPrivateUsage2104016896(2006.546875MiB); máximo PeakPagefileUsage observado2147143680(2047.675781MiB),339968bytes debajo del límite. Es highwater commit histórico del worker observado, no RSS/sistema/pico final de todos los procesos. Junto con MemoryError en encoder respalda agotamiento de memoria durante JSON. No atribuye exclusividad a DAG/copy/chunks/ciclos ni prueba defecto semántico C. Muestras no estiman porcentajes CPU ni duraciones exclusivas.

22430 es conteo generado observado,161877 registros es metadata previa de builder, no tabla final wire verificada. Sin traza completa/HTTPstatus/rawhash no hay oráculo de todos estados, refs, orden, frees/returns/callerownership ni UI reutilizable; verify_complete_saved sólo preparado. La evidencia técnica finita anterior sigue válida bajo sus casos, no se amplía a30. Prueba autor del cache propio indica60operaciones persistidas y ninguna query; no demuestra sesión en RAM tras fallo ni éxito61. Cache excluido del binding; no se deserializó aquí ni se presenta como reproducción independiente. Native histórico no reejecutado.

## Remediación necesaria antes del siguiente ensayo

1. Conservar rechazo, checkpoint tardío y cronología sin renombrarlo como previa ni retroeditar logs. Registrar incumplimiento material de continuidad y su resolución procesal en seguimiento propio del autor; esta QA no certifica limpieza before.
2. Hacer el lanzamiento futuro dependiente explícito de exit0 de la guarda exacta Y validación de IDs. PowerShell no debe continuar a la llamada siguiente tras fallo de proceso/assert: comprobar $LASTEXITCODE y abortar antes de crear worker/job. Para sucesor nuevo, no pasar flags de reapertura incompatibles; para operación realmente cerrada, aplicar decisión/ID exactos. La corrección de orquestación debe ser concreta y revisable antes de otra ejecución, dentro de nueva asignación; no requiere repetir el ensayo fallido.
3. Mantener pausa de ensayos. Siguiente trabajo propuesto es inventario readonly de lifetimes pool/source/table/normalización/JSON y retenciones para identificar una reducción específica que conserve contrato. Ni aumentar límite ni implementar/repetir/adoptar queda autorizado por esta revisión.

Se acepta diagnóstico con limitación procedimental explícita, no éxito funcional ni cierre global20/22. Evidencia propia checks.json; guardas de QA before/after sólo de esta revisión. Sin imports app/tests/HTTP/native/benchmark/escenarios/producto/Git/preview/retry.
