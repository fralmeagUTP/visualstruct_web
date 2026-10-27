# Entrada múltiple — verificación focal

Copia aislada desde `visualstruct_vista_clase_v1_20261027/app`. Las pruebas de este cambio no certifican las cifras históricas de pytest/cobertura del README original.

## Pruebas propias
- `node qa_multiple/test_queue.js`: sintaxis/posición, int32, límite 50, duplicados de ocho TAD; normal/paso a paso, transición explícita, Detener con request pendiente, doble inicio, rechazo parcial, respuesta incierta y ausencia de reintentos.
- `node qa_multiple/test_dom_lock.js`: montaje real con DOM mínimo; captura de mutaciones, restauración de botones dinámicos, doble clic tardío, resumen después de reset, edición inválida.
- `node --check static/js/{multiple_input,sequential,hierarchical}.js` por archivo.
- Regresión v1: cinco scripts de `qa_classroom_v1`, ocho canónicos de `qa_convergence`, y selección no-grafo de `qa/` (se conservan logs exactos en la entrega).
- `qa_classroom_v1/test_raw_main_compile.py`: nueve payloads main reales compilan C17 con warnings como errores y ejecutan.
- `qa_classroom_v1/test_templates.py`: cinco familias, IDs únicos e imports compartidos.

## Límites conocidos y evidencia negativa
`qa/test_real_stdout.js` incluye un extractor textual histórico del grafo que arroja SyntaxError en el último caso. Se reprodujo el mismo fallo sobre v1 sin modificar; no se cambió el test para esconderlo. La suite canónica vigente del grafo pasa. Primer intento de regresión no encontró fixtures externos de v1: se conservaron ambos logs y se copiaron los fixtures originales a la carpeta hermana antes de repetir. No se afirma pase de la suite histórica ausente de 530 pruebas.

QA de navegador y pruebas independientes pertenecen a `../qa_independent` en la raíz de trabajo, no a este autor. El servidor de escritorio5056 usa cookie/cache separados; 5055/tab29 permanecen ajenos.

`node qa_multiple/test_generation.js` reproduce el intervalo entre requests normales: detener e iniciar otro lote invalida la continuación antigua. La variante sin ambas guardas de generación falla esta aserción; el candidato la pasa. Esta revisión adicional reemplaza el sello provisional, no cambia las fuentes TAD.
