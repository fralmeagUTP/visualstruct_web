# Diseño preservado y criterios de revisión

1. La fuente es el C canónico del intérprete. graph_algorithm_code_scopes construye rangos y cierre transitivo de llamadas desde cada entrada C. Ordena las funciones por su posición en fuente.
2. El panel conserva todas las filas e índices originales; oculta únicamente filas ajenas al alcance. No concatena snippets ni renumera el documento. El intérprete mantiene su acceso posicional rows[line_index].
3. El índice de funciones usa la misma selección. El filtro se reaplica al elegir operación, cargar traza y recorrer cursores. Un paso sin línea C no debe inventar resaltado.
4. Para resultados propios, se incluye limpieza por caller: grafo_liberar_vertices en BFS/DFS y grafo_liberar_arcos en Dijkstra/Bellman-Ford/Prim/Kruskal. No se añade limpieza de otra categoría.
5. «Pertinente» significa alcanzable por llamadas estáticas de la operación y su limpieza necesaria. Puede incluir una rama/helper que no se ejecuta con la entrada concreta. El resaltado, en cambio, sigue solo las instrucciones realmente ejecutadas. No se promete filtrado dinámico de cada rama.
6. Las definiciones del TAD permanecen en su panel; la selección no altera C/H descargable, fuente de traza, memoria, historial ni resultados. No cambia presentación de operaciones fuera de las diez.
7. La referencia Pilas/apilar y Árboles/eliminar se conserva como criterio: operación y subrutinas relacionadas, navegación sincronizada. No se afirma una auditoría comparativa nueva de Pilas o Árboles.

Cambios posteriores de resaltado MST en api_publication y ajuste de consola son alcances distintos. Su éxito no constituye una nueva prueba de las diez operaciones de opción 3.
