# Criterios finitos por fallo

**Terminología:** en la aplicación, «ejecución C» significa reproducir instrucciones de la fuente C mediante el intérprete/simulador; no compilar ni ejecutar código nativo en el servidor. Las compilaciones y ejecuciones C nativas de esta entrega se realizan en QA independiente. Rechazo pre-C significa rechazo antes de iniciar esa reproducción.

| ID | Reproducción / criterio de aceptación | Evidencia |
|---|---|---|
| VS-01 | Algoritmo desconocido run/step →400 didáctico, historial intacto;11 algoritmos válidos siguen funcionando | qa/test_sorting_regressions.py |
| VS-02 | Pausa/interrupción mantiene resaltado, estado y cursor del mismo paso; cargar vacío elimina restos | qa/test_trace_player.js |
| VS-03 | Clear/cambio de algoritmo cancela respuestas paginadas tardías y resaltados viejos | qa/test_trace_player_paged.js |
| VS-04 | Datos int C fuera rango rechazados sin mutación; extremos válidos | QA independiente límites |
| VS-05 | Validación previa no inventa ramas C, malloc ni printf; UI muestra error no ejecución pendiente | QA independiente validación / integración jerárquica |
| VS-06 | Comprender conciso por puntos y operación/paso; referencia completa opcional; no paneles vacíos iniciales | qa/test_contextual_help.js + recorrido UI por familias |

## Cobertura de aceptación
109 operaciones metadata (incluye alias/ocultas) y11algoritmos;103operaciones no-sorting en matriz de423 invocaciones;44 trazas de ordenamiento con chequeos estructurales;55 comparaciones con TAD C nativo; navegación runtime19casos. Cobertura UI definida cerrada a las09:30 UTC por su auditor: cinco familias,95filas PASS_UI y14NOT_EXPOSED;94filas con paso a paso y una preparación sin traza propia. La aceptación UI no se deriva de los tests backend. No equivalen a exhaustividad de todos los caminos posibles ni a suite histórica530.

## VS-07: Código utilizado en clase
Fuentes C/H descargadas deben corresponder a la implementación mostrada. Programas main presentados como reproducibles deben compilar con C/H y dependencias documentadas, ejecutar operaciones del historial sin sustituir consultas por resultados precalculados y liberar propiedad al terminar. Pruebas propias en13TADs; ni modificar fuentes sólo para pasar tests ni atribuir direcciones simbólicas a memoria real. Excepción autorizada y documentada: el cambio separado `cloud-graph-invariant-20261027` corrige una violación real de invariantes ante fallo de reserva con un guard mínimo; conserva firmas y comportamiento normal, sin migrar las APIs del libro.

## Criterios encontrados durante recorrido UI (sin ampliar a funciones nuevas)
| ID | Criterio observable | Evidencia/estado |
|---|---|---|
| VS-08 / UI002 | Ocultar comentarios conserva instrucciones con desreferencia `*a`/`*b` | lexer + revalidación navegador |
| VS-09 / UI003,008,009 | Avanzar no desplaza documento; C e imagen simultáneos y línea completa, sin perder nodo activo | capturas/mediciones sorting, secuencial, jerárquica y grafo; hash en curso |
| VS-10 / UI004,005 | Variables necesarias de Shell y memoria Radix legibles; reserva/liberación/alias fieles | fixtures reales y retests UI |
| VS-11 / UI006 | Cancelar reset no cambia; confirmar sincroniza algoritmo, código, visual, datos y cursor | tests deferred fetch + UI |
| VS-12 / UI007 | Exportar JPEG descarga bytes poblados o reporta error, no silencio | pruebas transporte + archivos reales abiertos |
| VS-13 / UI011,014,015 | Salida C no incluye mensajes host; snapshots/eventos explícitos conservan repeticiones y espacios; consulta normal visible fuera stdout, paso sólo al final y se oculta al retroceder | revisión independiente14trazas/174cursores + consultas UI |
| VS-14 / UI012 | Narración/condición/invariante en UTF8 correcto | qa/test_spanish_encoding.py + retest UI prioridad31frames PASS |
| VS-15 / UI013 | Resumen no expone flags/modelos internos como variables C; diagnóstico opcional íntegro |400frames/14trazas + retest UI |
| VS-16 | Posición int C no representable rechazada antes de simular; modos relativos opcionales mantienen defaults; histórico intacto | qa/test_c_position_bounds.py + revisión independiente |
| VS-17 | Guías main describen programa completo y dependencia real; acceso comprensible al historial para copiar | pruebas Flask + descargas y main DOM exactos compilados UI |
| VS-18 | Capacidad hash acotada como política del visualizador (no contrato C); rechazo sin mutación, históricos preservados | medición17/32/64/128; backend y revisión independiente PASS; legado129 UI preservado/reset confirmado PASS |

No se exige abrir controles ocultos por el modo piloto mediante automatización: se registra NOT_EXPOSED, no PASS UI. Sus APIs o funciones pueden tener pruebas independientes sin atribuir interacción visual.

## Criterios finales de jerárquicas, grafo y hash
| ID | Criterio observable | Evidencia/estado |
|---|---|---|
| VS-19 / UI016,022 | Árboles/heap conservan relaciones reales y texto legible; JPG expande contenido sin recortar nodos, resultados ni memoria | fixtures176árboles/45heap y JPG reales4jerarquías+grafo |
| VS-20 / UI017,020 | Ámbito terminado no permanece activo; publicación/retorno explica contrato real, NULL no se presenta como lista propia |36casos inserción/1576pasos,6consultasheap,16publicacionesgrafo,7retornosnuméricos |
| VS-21 / UI018 | Predicción apunta al siguiente evento relevante, muestra evidencia tras responder/omitir y no permite duplicar puntuación; comparación dibuja estructuras reales sin mutarlas |79decisiones/30snapshots y revisión independiente/UI |
| VS-22 / UI019 | Texto C renderizado no añade NBSP que impidan compilar; main copiado literalmente del DOM ejecuta con las fuentes descargadas |10casos fuente/4mains jerárquicos UI; clipboard nativo no probado |
| VS-23 / UI021 | Resultado grafo pendiente hasta publicación final, retroceso lo oculta; no reutiliza consulta anterior |580frames y pruebas UI algoritmos |
| VS-24 / UI023 | Error con ejecución C real (búsqueda ausente/fallo malloc simulado) conserva traza; sólo rechazo pre-C omite ejecución |PASS técnico independiente HTTP400 con12/14pasos y retests UI get/malloc; familia cerrada en matriz visual |
