# Diagnóstico inicial

Base c51226864929e6b77d217e86b339cbefda8eeb5c. graph_layout.js seleccionaba largeComponentLayout para componentes de más de 15 vértices, con círculo para componentes no árboles. templates/help/graph_structure.html contiene el acordeón explícito de fuente completa mostrado por Francisco. No se ha demostrado fallo funcional del player. Pruebas del candidato pendientes; no es entrega aprobada.

## Reproducción acotada del panel activo

Desktop: tres diagnósticos PASS en 12.10 s; wall 12.812 s; pico 407154688 bytes; Job Object sin procesos remanentes. Grafos insertar22 sobre grafo pequeño: HTTP200, 53 pasos; 619 filas DOM, 22 visibles y sólo `fijar_estado`/grafo_existe_vertice/grafo_insertar_vertice; avanzar/retroceder observado. Sin errores JS/HTTP. Pila y ABB comparativos también avanzan/retroceden. No reproduce fallo funcional ni código ajeno visible en el panel activo. La captura de Francisco muestra la referencia completa explícita de la ayuda, superficie distinta. Estos tres casos no validan todos los algoritmos ni el grafo particular del usuario.

## Controles de geometría

Versión inicial seis controles Node PASS en 0.91 s; wall 1.313 s, pico 58245120 bytes. Resultado intermedio, no entrega.
Versión2 siete controles Node PASS en 0.90 s; wall 1.297 s, pico 59260928 bytes, cero procesos remanentes. SHA256 layout a6963ae5f4b413c54823bf20bafc6bf6fa6d487a6f6a2638f0c2ec077202f855; test c63289fc8c6427bb740f0f340333a3848990a3d93627ab9f0274bbc3b2d40f14. Incluye crecimiento a 22, paso 15→16, ajuste local de arista, metadata/reciprocidad, carga 30 sin anillo ni solapamiento de nodos, reinicio vacío y nueva edición frente a topología antigua con replay. No sustituye QA visual navegador, aún pendiente. Todos los bloques usan límite 120 s y 2 GiB agregado por Job Object.

## Navegador y fuente canónica, plantilla inicial

Desktop: dos casos navegador y uno de integridad PASS en 60.68 s, wall 61.187 s, pico 506290176 bytes, Job Object sin procesos remanentes. Runtime exacto del candidato (graph/layout/C/manifest); plantilla todavía anterior al cache-bust. Crecimiento: componente inicial 15 y nuevas inserciones aisladas 16–22, sin solapamientos ni anillo, posiciones anteriores conservadas. Segundo caso arista válida/replay/rechazo inválido. Integridad acepta nueva fuente exacta y rechaza byte agregado tanto en memoria como archivo. No equivale a prueba de todos los algoritmos.

Inspección visual: no todos los 22 nodos caben simultáneamente en el panel a zoom 78%; parte inferior fuera del área visible. No se afirma visibilidad total ni corrección de un problema de overflow. Pendiente comprobar desplazamiento local y final 16conectados con plantilla organic1. El dibujo no promete encoger todos los nodos para caber a la vez.

## Plantilla final y revisión posterior

V2: smoke componente conectado 15→16 con plantilla organic1 y cuatro comprobaciones de assets PASS en 38.95 s; wall 39.734 s; pico 416075776 bytes; cero procesos remanentes. Sin métricas DOM de scroll en ese bloque; screenshot no demuestra reachability de nodos inferiores.

Revisión independiente identificó que el vacío de reproducción borraba snapshots. V2 no se publicó. V3 conserva snapshots para replay vacío y añade regresión con renderer real y singleton de posición heredada distinta de 70,70. Los siete controles previos y QA visual V2 son evidencia intermedia, no prueba del nuevo runtime V3. Verificación final V3 pendiente al momento de este registro.

## V3: regresión de vacío

Ocho controles Node PASS en 0.98 s; wall 1.656 s; pico 70467584 bytes; cero procesos remanentes. Layout SHA256 11fb195815359bd445420d7cca6d8833139bac8a50c4281178885d199994b691; graph.js e92b4471be0d9dbf87fc6db7bc2ddd67b4be11c0e3841cdaddbd2c5679b926c6; test e20ef6ad93d3738e72e8fa9d549fc6273d10352cabe4145e7b324085af201252. Octavo control ejecuta renderer real para vacío y comprueba restauración de posición heredada al retroceder, y reinicio tras vaciado real. Browser de cierre V3 pendiente.

## Cierre V3 navegador no aprobado

Único caso de cierre FAIL en 12.87 s; wall 13.547 s; pico 387276800 bytes; cero procesos remanentes. Después de eliminar último vértice y buscar el último paso cuyo state_snapshot contiene el nodo 2, seek a ese paso no produjo SVG (timeout 7 s). La parte de viewport de 22 no se ejecutó. No se publica el candidato ni se considera cierre verde.

Diagnóstico de lectura: interpreter_runtime.js seek(i>=0) pinta state_after; sólo seek(-1) usa snapshot inicial. BookTraceCollector conserva state_snapshot como estado previo y state_after como posterior, enlazando el siguiente snapshot con el after anterior. La selección del último snapshot previo no vacío puede elegir justamente la instrucción que elimina el último nodo; en ese caso el dibujo vacío después de seek es correcto. Pendiente confirmar selección literal del arnés/artefacto; no cambiar el runtime para resucitar nodos ni normalizar el oráculo. Sin nueva ejecución autorizada al registrar esta evidencia.

### Clasificación del fallo del arnés

Confirmado por lectura del test: seleccionaba findLastIndex sobre state_snapshot.nodes, mientras seek renderiza state_after. El body del primer fallo no fue persistido (reporte vacío); no se inventa el evento concreto. Se autorizó una única repetición corrigiendo selección a state_after y guardando índice, before/after y evento antes de navegar; mantiene la igualdad exacta de coordenadas y el caso vacío. Runtime V3 no cambió.

### Límite de caché no cubierto por estos casos

La caché mantiene 64 topologías. Navegaciones de borrado masivo que sobrepasen esa cantidad podrían requerir recomputar snapshots expulsados. No se ha probado conservación de coordenadas para todos los posibles 4000 eventos de una traza. Se informa como límite de la evidencia, no como resultado PASS ni relajación de validadores.

## Resultado del cierre corregido y clasificación viewport

El cierre corregido FAIL en 6.08 s; wall 6.782 s; pico 391528448 bytes; cero procesos remanentes. El subcaso de replay vacío SÍ alcanzó igualdad exacta: nodo 2 original y restaurado [210,70], frame 29, event_type=line, line_index 122, stage=write, con evidencia anterior/posterior persistida. Falló después al exigir propietario de overflow vertical; no se atribuye automáticamente al runtime.

Lectura del arnés revela selector de fixture incorrecto: renderGraphState recibió document.querySelector("#visual-state"), mientras Grafos utiliza #graph-visual-state. La función retorna ante container nulo, por lo que no había evidencia de haber renderizado los 22 nodos (no se contó DOM). Además sólo buscó scrollHeight/overflowY, no scrollWidth/overflowX. Se autorizó una inspección independiente final del viewport de 22 con selector correcto, conteo 22 y evidencia de ambos ejes previa a las aserciones. No hay nueva modificación de runtime.

### Preparación corregida del último caso de accesibilidad

Una inspección posterior repitió por descoordinación el selector inválido antes de recibir la corrección y falló esperando 22 nodos (10.61 s); no cambió runtime ni aporta evidencia de defecto del producto. Se detuvo. La inspección definitiva fue revisada literalmente antes de iniciar: contenedor #graph-visual-state no nulo, conteo 22 círculos acotado al contenedor, medidas X/Y y screenshot antes de aserciones, y visita a los 22 nodos con desplazamiento nativo. Arnés SHA256 c0b19dedc8b3b6d1acb31c51af39942d8a31bf3fc0f4b77cb762af86fd079cb0. No comprueba invariancia de coordenadas del panel de código; su alcance es accesibilidad de los 22 nodos. Resultado pendiente.

## Cierre de accesibilidad V3 aprobado en alcance finito

Único caso corregido y revisado PASS en 4.49 s; wall 5.172 s; pico 372822016 bytes; cero procesos remanentes.22 nodos DOM comprobados y22 alcanzables dentro de classroom-stage mediante desplazamiento local. Contenedor: client 831×560, scroll 2232×560, overflowX/overflowY auto; scrollLeft de 0 a 1371 y scrollTop 0. Confirma overflow horizontal y ausencia de truncamiento inaccesible en esta fixture. No demuestra coordenadas fijas del panel de código ni todos los grafos posibles. Runtime V3 sin cambios.

Conclusión: candidato verificado en alcance descrito, no publicado ni desplegado por este expediente al cierre. Ocho controles Node V3 PASS; integridad estricta de fuente y versiones de assets verificadas en sus bytes finales; crecimiento 15→16 conectado y22 nodos observados en navegador; replay vacío recuperó coordenada exacta [210,70]; accesibilidad de 22 final PASS. Los fallos del arnés anteriores se conservan y no se atribuyen al producto. CI global no certificado; el límite de 64 topologías sigue informado. No se afirma haber corregido un fallo funcional del player que la reproducción inicial no encontró.
