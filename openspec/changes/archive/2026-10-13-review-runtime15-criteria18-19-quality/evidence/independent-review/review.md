# QA independiente runtime15 y criterios18/19

**ACEPTAR el cambio documental autorizado a máximo inclusivo15s y el PASS finito del BFS guardado. RETENER18. ACEPTAR19 como entrega parcial conjunta con los artefactos existentes, sin archivo ni aprobación global.** Este dictamen no marca casillas; el cierre de la tarea de entrega requiere entregar efectivamente ese conjunto al usuario.

Proyecto D:\MisProyectos\Web_VisualEstruct; change review-runtime15-criteria18-19-quality; operación audit.runtime15-final-criteria-independent-quality; task runtime15-criteria18-19-independent-review; assignment coordination-runtime15-criteria18-19-independent-qa-low-20261005. Índice/assignment/binding coinciden.18fuentes SHA coinciden antes y al emitir; cero ejecución técnica. Fuentes (evidencia local: `openspec/changes/archive/2026-10-13-review-runtime15-criteria18-19-quality/evidence/independent-review/input-checks.json`), contraste numérico (evidencia local: `openspec/changes/archive/2026-10-13-review-runtime15-criteria18-19-quality/evidence/independent-review/measurement-checks.json`). Guardas before/after propias se guardan en esta carpeta y no aprueban contenido.

## Autorización y alcance

La transcripción vigente dice máximo15/no más de15 y cualquier algoritmo: <=15.0 es correcto; no restringir la regla aBFS ni a17IDs. Graph<=30 y Sorting<=80/int32 conservan dominios; fidelidad/eventos/ownership/cobertura no se relajan. El diff Graph sustituye el antiguo presupuesto5 por15 y preserva100histórico, Graph30/legacy y300reconstrucciones/p95<200ms. El delta application-quality agrega la regla para todos los algoritmos y exige informar timing ausente antes de ejecutar. Segundo prototipoBFS cancelado, sin adopción de aislados. No se necesita otra optimización de BFS por el caso guardado.

La obligación de revisar rendimiento ya existía en validation-plan/criterio18 y en el gate Graph5s. El nuevo acto cambia el umbral y hace explícito cualquier algoritmo y la solicitud completa. Las16 filas son una selección documental de evidencia aún ausente, no16 obligaciones funcionales nuevas, defectos ni una campaña autorizada. La decisión no implica que el usuario hubiera ordenado exactamente esas16entradas. El mínimo focal siguiente se deriva de verificar el alcance explícito por algoritmo, no de reabrir familias11/12/16.

## Contraste aceptado

BFS30/29 no dirigido, peso1, inicio1: request_seconds_plain11.728276199981337<=15,HTTP200/successtrue,11849pasos/29891205bytes. Entrada y protocolo guardados corresponden; bfs_instruction.py conserva SHA3cc2bb8ecf3afaff63e4453b1e7acb92e1d304458537f6a17e3fab61c67a5a65. El PASS nuevo es clasificación documental autorizada de una observación anterior, no nuevo ensayo, estabilidad temporal o certificado del pipeline completo. strict5s_PASS=false permanece en el original.

Los18 registros numéricos instrumentados/parciales remiten a fuentes SHA y filas con valores coincidentes. Prim/Kruskal con tracemalloc>15 no son FAILplain actual; Radixmotor/índice/transporte no se suman para inferir PASSHTTP. No se demostró un incumplimiento actualplain>15 en el material consultado. Ausencia de FAIL no equivale a evidencia de cumplimiento de los demás algoritmos.

## Mínimo focal indispensable antes de aceptar18 en alcance representativo

BFS ya aporta una observación; no repetirlo. Falta una solicitud completa calificante por cada uno de los otros16algoritmos distintos listados en existing-measurements15-contrast.json. Se requiere nueva medición únicamente si coordinación confirma que no hay equivalente plain actual reutilizable. No se exige suitefuncional nueva, nativecampaña, browserporframe, fullcoverage, benchmarksestadísticos ni todos los109controles.

| Familia | Entrada/payload mínimo de referencia | Operación |
|---|---|---|
|DFS|Cadena30v,29arcos(i,i+1,1), no dirigida;start1|POST /graph/graph/operate run_dfs|
|Bellman-Ford/Dijkstra|Misma cadena dirigida;start1,end30|POST /graph/graph/operate run_bellman_ford / run_dijkstra|
|Prim/Kruskal|Misma cadena no dirigida;Prim start1,Kruskal{}|POST /graph/graph/operate run_prim / run_kruskal|
|Intercambio,Selección,Inserción,Burbuja,Shell,Quick,Merge,Heap,Counting,Bin|80enteros80..1;Counting/Bin rango80 admitido|POST /api/ordenamiento/run, algoritmo seleccionado,mode step_by_step|
|Radix|80valores INT_MIN/INT_MAX alternados,40cadauno|POST /api/ordenamiento/run radixsort,mode step_by_step|

Fuentes/entradas exactas: existing-measurements15-contrast.json, route app/routes/sorting_routes.py /api_run y contratos Graph actuales. Preparar grafo/array/selección fuera del reloj y conservar historial/estado inicial exacto. Medir monotónico desde antes del POST hasta consumo completo del cuerpo HTTP, incluyendo replay,validación,algoritmo,traza,historial/serialización. Privatecliente secuencial, sincoverage/tracemalloc/profiler ni concurrencia; fuentes/entorno/entrada/operation/HTTP/success/result/cantidad de pasos/eventos/bytes y duración registrados. Retener cualquier >15 o timeout; no llamarlo PASS ni truncar contenido. Reutilizar semántica aceptada y comprobar sólo que se ejecutó el algoritmo solicitado y la traza no se omitió. No confundir respuesta paginada conforme al protocolo actual con inline ni omitir preparación requerida; registrar el transporte usado, sin inventar suma de etapas ni espera humana del player.

Una observación poralgoritmo es el piso de la comprobación representativa, no prueba matemática de máximo para todas las densidades/pesos/historias/formas. Estas16no agotan operaciones algorítmicas de otrosTAD ni certifican17como todo el producto. No derivar una campaña adicional de esa limitación general; reportar sólo fallo concreto o cobertura focal relevante que quede explícitamente fuera de la pretensión de aceptación. Las funciones privadas no crean UIpositiva.

La selección debe remitirse a coordinación ANTES de ejecutar. Este dictamen no autoriza ni inició esas16peticiones.18permanece pendiente por evidencia de latencia no demostrada para el alcance representativo; cobertura535, C/sanitizadores no disponibles y11/12/16 se conservan aceptados, sin recomputarlos.

## Oráculos antiguos y entrega19

Predicados5s/resultados antiguos quedan conservados. No modificar logs ni convertirlos aPASS. Un futuro sucesor del test de algoritmo debe usar el umbral autorizado15 y el protocolo completo; no es condición escribirlo ahora para aceptar el cambio documental. tests/test_comprehensive_quality_qa.py:49 mide conjuntamente cincoGET y un apilar pequeño, no el casoBFS30 ni cada uno de los16algoritmos. No sustituir automáticamente su5s independiente por15 ni usarlo como cobertura del gate nuevo. P95300reconstrucciones<200ms tampoco cambia.

19puede satisfacerse por una entrega honesta parcial:18pendiente no prohíbe entregar. El nuevo user-delivery19-runtime15.md es un resumen actualizado y debe acompañarse de la matriz, diffs, hallazgos/evidencia y acceso local ya existentes. No necesita otro paquete ni campaña; para que ese resumen sea entrega completa de la obligación19, coordinación debe incluir estos artefactos/rutas en el mensaje final:

- Matriz: openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-documentary-successors17-applicability-low/matrix11-12-with-approved-successors.json.
- Registro/diffs: evidence/visible-QA-retained-criteria-correction25-low/criterion16-corrected58.json y evidence/visible-documentary-successors17-applicability-low/successors17-diffs-and-acceptances.json dentro del change auditor.
- Evidencia y límites actualizados: evidence/visible-runtime15-authorized-contrast25-low/report.md yexisting-measurements15-contrast.json; QA535/delta306 aceptadas por referencia.
- Acceso local existente http://127.0.0.1:5051; no se comprobó ni reinició preview en esta revisión.

No reenviar como vigente el párrafo anterior5s/segunda variante pendiente de user-partial-delivery.md; está supersedido explícitamente. Con esos componentes, ACEPTO19como entrega parcial de los resultados conocidos y límites. No declarar certificado15s universal,22/22,18cerrado ni archivar.20/22es la fotografía previa a cualquier decisión de checklist; sólo coordinación registra la entrega efectuada. Si se pretende entregar únicamente el resumen nuevo sin matriz/diffs/instrucciones,19no quedaría satisfecho por faltar esos elementos literales.

No se cambiaron producto, tests, C/H, evidenciaautor, bindings/index, tasks, preview ni Git. Fuentes verificadas al terminar coinciden; resultadosprevios conservados. El siguiente paso es decidir la comprobación focal de latencia o entregar el resultado parcial con18abierto, sin reabrir familias funcionales aceptadas.

Emitido UTC 2026-10-05T22:46:56.524768+00:00.
