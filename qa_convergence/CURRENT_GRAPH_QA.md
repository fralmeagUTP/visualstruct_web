# Pruebas actuales de publicación y fallos de reserva

Estas pruebas adicionales usan graph-book/v1 y los C/H canónicos. No reemplazan ni
certifican retrospectivamente los tests históricos de qa/test_graph_*. Los cinco
archivos históricos, incluido qa/graph_edge_allocation.c, permanecen sin cambios.
La separación ya está establecida en README.md de esta carpeta.

Ejecutar desde la raíz:

```sh
python -m pytest -q qa_convergence/test_current_graph_edge_allocation.py qa_convergence/test_current_graph_numeric_receipt.py qa_convergence/test_current_graph_vertex_publication.py qa_convergence/test_current_graph_query_publication.py
```

Garantías actuales:

- Treinta escenarios nativos C17 con fallos malloc, extremos válidos, atomicidad,
  estado GrafoEstado, costo separado y cero reservas vivas tras grafo_destruir.
  Los mismos treinta escenarios se comparan con el intérprete canónico.
- Recibos de listas propias/NULL se inspeccionan en caller_receipt, antes del
  printf del caller y la liberación explícita. La publicación API final no se
  confunde con ese retorno intermedio.
- Flags int, costo con parámetro de salida y listas prestadas conservan tipos,
  identidad y resultados. Un costo ausente ejecuta C y se registra en historial.
- Cambiar exclusivamente la función de narración no altera fuente, eventos,
  estados, memoria, resultados ni stdout de la ejecución actual. Es una prueba
  de aislamiento de presentación, no equivalencia con una preimagen histórica.

Límites históricos: numeric-null-baseline.py, graph-vertex-note-baseline.py y
graph-query-note-baseline.py externos no están en el repositorio ni en el catálogo
de inputs publicados. Su equivalencia histórica no es verificable aquí. Además,
los mocks originales interceptan motores retirados que el nuevo servicio ya no
invoca. Un resultado verde obtenido así no probaría equivalencia entre motores.
No se recrearon esos archivos, no se cambiaron hashes canónicos y no se añadieron
skip/xfail ni reglas de exclusión para ocultar pruebas históricas.
