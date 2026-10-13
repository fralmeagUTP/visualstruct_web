# Graph10 reparacion MEDIUM: verificacion finita 2026-10-04

Proyecto canonico D:\MisProyectos\Web_VisualEstruct; change audit-local-quality-and-unified-controls; operacion audit.canonical-correspondence; asignacion coordination-graph10-repair-medium-20261004. No cierres globales ni archive.

## Resultado y alcance

Diez operaciones reparadas: create_graph, clear_graph, insert_edge, remove_edge, exists_vertex, exists_edge, edge_weight, list_vertices, list_edges, generate_random_graph. Dispatcher exacto a construction_instruction.py, parser aislado con cuerpos C fingerprinted, cortocircuito/retornos/ambitos tipados/memoria causal. Consultas retornan cabezas prestadas o escalar; publicacion API y rechazo se distinguen de instrucciones C. Arcos muestran helpers reales y caller inverso no dirigido. Creacion/limpieza muestran liberacion del propietario antes de reemplazar; random solo materializa caller, no inventa RNG C.

Graph UI muestra memoria/retorno, conserva frame inicial y resultado pendiente. Aplicar tipo ya navega su traza sin ejecutar selector ajeno y no anticipa resultado. Counting restaura caption/aria del modo activo; correccion de control al completar navegacion solicitada, sin algoritmo ni C.

Producto: nuevo app/domain/graph/construction_instruction.py; cambios acotados app/services/execution_trace_service.py, static/js/graph.js y static/js/sorting.js. Los before de dos archivos se reconstruyeron por inversa de los cambios y coinciden byte a byte con hashes capturados antes; Sorting before se guardo directamente. Diffs y verificaciones en evidence/visible-graph10-repair-medium.242/245archivos previos intactos; C/H, adapters, graph_main_service, parser/numeric/vertex/neighbors/BFS/DFS y contratos intactos. No Graph6 ni cuatro callers C17 recuperados repetidos.

## Evidencia efectiva

- 24IDs permanentes distintos pasan:23en7.32s y nuevo frame-focal1en0.52s, sin segunda suite completa; diez IDs rojos originales y catorce invariantes nuevos (incluidos tres fallos de reserva simbolicos, no OOM real ni contrato API nuevo).
- 24fixtures C17 strict sin advertencias: dos capas sobre los mismos IDs, no48casos;371 registros de condiciones/retornos/efectos y150snapshots de grafo tras escritura/free/printf. Solo nodos vivos publicados e inicializados se recorren; no sanitizadores ni certificado todos los caminos. Estados finales/ownership y ramas coinciden.
- 10contextos Graph,166boundariesDOMseleccionados en ambos sentidos. Siete acciones visibles:14clicksSiguiente/7Anterior; tres operaciones API-only (exists_vertex/exists_edge/clear_graph) usan carga renderer explicita, no opciones UI inventadas. Replay0POST/erroresJS0.
- Navegacion real Pila/ABB/Hash y Counting: seis jumps, next/prev, replay/pause y modo rapido-final/paso-inicial. Counting restaura cinta compacta aceptada y sirve nuevas paginas HTTP privadas; no ejecuta sort. Reports previos16contextos/75acciones/88selecciones sinPOST preservados.

## Pendientes delimitados

1. EXPORT-SORTING-EMPTY-JPEG: defecto confirmado. Target DOM/screenshot contiene texto de arreglo vacio, JPEG global996x38blanco. Sorting-empty-JPEG-DOM.json documenta geometria y margen16px del p; probable clipping en clone/foreignObject al perder colapso de margenes, aun sin reparacion. No es target vacio esperado. Modulo exporta region mayor y es no uniforme. Preparar reparacion de preservacion de geometria del clone y verificar solo este caso y vecinos afectados; no necesita nueva semantica/C.
2. Coordinacion: revisar esta verificacion finita/diff/matriz actual y consolidar integracion16 despues del exporter. No marcar11/12/16 por conteo.
3. QA18: asignacion final sobre fuentes estables; activar nuevo backend en preview de forma coordinada antes de QA. PID8696/hijo4332 permanece intacto, no solicitudes/reinicio de preview ni cookies/sesiones del usuario. Verificacion actual usa servidores privados canonicos D, no implica proceso preview con backend nuevo.
4. Entrega19: agregado final tras QA;17/22conservado.

Fuentes actuales: evidence/visible-graph10-repair-medium/{summary.json,graph10-current-dispositions.json,control109-current-dispositions.json,aggregate-correspondence-after-graph10-repair-medium.json,protected-product-after.json,regressions-final.log,native-write-effects/native-report.json,browser-report.json,remaining-control-report.json,counting-replay-pause-report.json,sorting-empty-JPEG-DOM.json}. Fuentes antiguas y logs fallidos conservados; observador/instrumentacion no se confunden con defectos del producto.


Revision final de campos: graph10-final-frame-presentation-review-medium.md. Funcion activa y callers suspendidos corregidos en frames nuevos;1regresion adicional y un recheckDOMinsert_edge focal, no nueva operacion ni suma11contextos unicos. Native24 y suites previas no repetidos. Source/phase inicial aclarados.
