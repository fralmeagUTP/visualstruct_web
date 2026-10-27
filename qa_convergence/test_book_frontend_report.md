# Frontend Graph: contrato del libro — 2026-10-27

Archivos: `static/js/graph.js`, `templates/graph/structure.html`. No C/H, motores ni endpoints modificados en esta fase. Copia convergencia únicamente.

- Resultado distingue estado0..7, retornoNULL+OK válido, costo0 frente salida no escrita; erroresMST no muestran peso/bosque exitoso. Lista de arcos real sustenta ruta/costo, no se reconstruye otro algoritmo.
- Código completo canónico:19enlaces de operación enfocan definición exacta con scroll local. Detector del título admite acento en «Código C» para conservar resaltado y main literal.
- Historial suspendido no pasa por renderer vacío: no inventa nodos/counts. Exporta endpoint original sin replay; reset requiere confirmación; main queda bloqueado con motivo. También bloquea main por diagnóstico privado aunque la sesión no esté suspendida.
- Grafo asimétrico pese política no dirigida: advertencia y flechas sobre arcos C reales, sin inversas inventadas. BFS final destaca orden de visita, no interpreta pares consecutivos como aristas de árbol.
- Cada ejecución comunica modo normal/step. Rechazo preserve_session no reemplaza traza ni estado. Normal sin traza borra jugador/cursor previos y muestra motivo sinpasos, estado real y stdout exacto separado de mensajes host.
- Creación usa handler común (codec+preserve+busy). Estado preparado no anticipa resultado final; back mantiene resultado pendiente.
- Fases de instrucciones presentadas en español; memoria/JSON técnico intactos, sin mutar fixtures. Distancia ausente no se etiqueta infinito matemático; auxiliar BFS indica índicesTrabajo.prev.

## Pruebas
`node --check static/js/graph.js`
`node qa_convergence/test_book_frontend.js`
`node qa_convergence/test_book_frontend_execution.js`
`node qa_convergence/test_book_frontend_stdout.js`

PASS:8 resultados reales,19 definiciones C,18 frames reales congelados con todos IDs retenidos, suspensión/export/resetcancelado-confirmado, mainbloqueado-restaurado, mainrenderer, modos, handlerreal rechazo/sintrace/falloC/concurrencia, stdoutUTF8/repetido/líneasvacías. GETFlask `/graph/graph/construccion`200 con endpoint historial y linkmain correctos. Gateafter0.

## Límites
Predicción/comparación no están expuestas por template actual; no se añadieron paneles ni se certificaron esos controles. Formatter comparación existente ya no inventa coste o invariante. QA5054/píxeles/clics/descargas depende de auditor independiente; estos tests no son aprobación visual. Presupuesto4000 pertenece backend; frontend probado con respuestas del contrato, no certifica rendimiento ilimitado.

## Revisión puntual 10:26UTC — GB07 / primeros casos UI5054
- `memory_display` seguro priorizado, referencias retiradas indeterminadas/no utilizables con identidad histórica; no afirma cero punteros colgantes si no se verificó. Fixture real E2 trasfree congelado PASS; raw memoria no modificado.
- Frontera api_publication identificada como aplicación, no instrucciónC. Resumen agregado write/return por campos, texto técnico íntegro sigue disponible.
- Dos nodos se disponen horizontalmente; nota duplicada larga en disclosure, CSS exclusivamenteGraph limita altura al abrir. Prueba geometría conserva nodos/costo; legibilidad en píxeles pendiente retest auditor.
- list_edges conserva agrupación de cada tupla como origen→destino(costo) y propiedad prestada explícita.
- `node qa_convergence/test_book_frontend_retired.js` PASS fixture contractual+real, inmutabilidad, etiquetasseguras, geometría2nodos, agrupaciónarcos. Gateafter0.

Auditor visual independiente, reporte10:27UTC: retest GBUI001 dos nodos horizontal con valores20px/costo19px completos juntoC/memoria PASS; arcos prestados agrupados PASS; publicaciónapp PASS; GB07 free28/55 muestra aliasE1/E2 indeterminados no utilizables, incluida cabeza temporalcaller antespublicación. Esto valida esos casos reales, no todos grafos/tamaños. Residual expresión de referencia agregada cruda poco amigable, no incorrecta; sin parche cosmético adicional.

## Iteración medida 10:37UTC — GBUI001/002
- Radio3/4 ypadding adaptados; auditor confirma3nodos15px y pesoslargos externos legibles (sin generalizar6/15).
- Cajas de pesos evitan cajasnodo y otras etiquetas, usando ancho sobrante y guías punteadas, title fuente→destino. Todosdígitos exactos; no cambiaaltoviewBox. Matrices3costoslargos/negativos/cero verificadas conbbox y asociación.
- Lazo real antes era línea longitud0: curvaSVG visible ahora, flecha si dirigido y costoexacto; controlpoints/bounds seguros horizontalmente, no confundir selfpathNULL+OK.
- Memoria compacta prioriza campos de agregado referidos por línea y condiciónC completa (multilinea), no todosloscampos indiscriminadamente. FixtureDijkstra t.usado/t.alcanzable/t.dist muestraM3/M4/M5 primero; no eliminaotrosIDs ni cambiaframes.
- Handler normal con errorC sintraza agrega historial visible mediante execution_started real, no sólo success. Prueba respuestaerror/presupuesto/no-traza PASS.
- Seis suitesNode +syntaxPASS; gateafter0. RetestUI campos/lazo y6/15 pendiente.

## Grafos mayores — 10:49UTC
Auditor midió6v9aristas: SVG514×138, viewBox324×256, texto8px. Se activa ahora scroll interno de imagen cuando escala<0.9; tamañoSVG mínimo1:1, sin flexshrink ni centrado que produzca zonas negativas inaccesibles, con aviso y tabindex. Captura/restaura panantes/después de cada innerHTML; no modifica scroll del documento. `test_book_graph_pan.js` cubre geometría2/3/6/15, tamaño mínimo ypan conservado. Siete suitesNode+syntaxPASS, gateafter0; retestpixel6/15 yJPG ampliado pendiente.

10:50UTC: presupuesto4000 real verificado por auditor (rechazo conservaJSONbyteexacto; normalKruskal15v/14aristas devuelve141 sintraza). Comprender/metadata ahora dicen llamadaC normal terminada/no pasos guardados, no preparación sin ejecutar. Fixturenormalerror sintraza tambiénPASS. Motivo backendnormal lo adapta lead por separado. Captura de6/15panlegible pendiente.

10:53UTC auditor visual independiente:15v valores16px/pesos15px, aviso ypanlocal PASS; consulta10frames mantiene pan235px durante11estados0..10 y documentoY644 constante, código+imagen+memoria juntos. No se afirma todos15simultáneos: se requiere pan explícito. Runtime confirmó expansión de todosdescendientesHTML en clonexport compatible; JPEG15real aún en verificación.

10:56UTC auditor: GBUI002 Dijkstra192/630 usado/alcanzable priorizaM3/M4visibles;207/630 dist priorizaM5/tcompacto sólo dist, líneaC completa yY781constante PASS.6nodos también16px/15px conpanlocal PASS. Aviso normal15sintraza trasrestart10:54 PASS.

Cierre de loops propios10:56UTC: lead transmite confirmación auditor JPEG15real10:54:45 completo con15v/43reservas. Todos retests de estos parches cerrados; no se añaden más cambios. Revisión consolidada/smokes/paquete quedan en coordinación, sin afirmar cierre global de la aplicación.
