# Matriz y evidencia existente

No se ejecutaron pruebas nuevas para redactar este registro. La tabla vincula los casos ya existentes en tests/test_graph_algorithm_code_scope.py; no crea diez aprobaciones nuevas.

| Operación UI | Clave | Entrada C | Limpieza de resultado propio |
|---|---|---|---|
| BFS | run_bfs | grafo_bfs | grafo_liberar_vertices |
| DFS | run_dfs | grafo_dfs | grafo_liberar_vertices |
| Dijkstra | run_dijkstra | grafo_dijkstra | grafo_liberar_arcos |
| Bellman-Ford | run_bellman_ford | grafo_bellman_ford | grafo_liberar_arcos |
| Prim | run_prim | grafo_prim | grafo_liberar_arcos |
| Kruskal | run_kruskal | grafo_kruskal | grafo_liberar_arcos |
| Insertar vértice | insert_vertex | grafo_insertar_vertice | No se añade limpieza de resultado de algoritmo |
| Eliminar vértice | remove_vertex | grafo_eliminar_vertice | No se añade limpieza de resultado de algoritmo |
| Insertar arista | insert_edge | grafo_insertar_arco | No se añade limpieza de resultado de algoritmo |
| Eliminar arista | remove_edge | grafo_eliminar_arco | No se añade limpieza de resultado de algoritmo |

Para cada fila existen dos casos parametrizados: test_scope_covers_every_executed_c_line_without_other_algorithms y test_browser_filter_selection_load_and_bidirectional_steps. Seis casos adicionales test_missing_start_or_empty_graph_keeps_only_real_c_steps cubren algoritmos en grafo vacío/inicio inexistente.

## Evidencia histórica observada
El expediente graph-operation-code-20261111/evidence/result.json registra 26 pruebas de la suite (16 fuente/traza y 10 Chromium), 74 regresiones (61 API/rutas/límite/retorno y 13 CCodeService), 100 pruebas focales únicas y 6924 posiciones bidireccionales, 226.56 s para la suite. verification.md limita navegador a grafo no dirigido de dos vértices y una arista.

El test navegador observa visibilidad computada, índice, carga, botones siguiente/anterior, seek en ambas direcciones, reset, alternancia de comentarios, selección alternativa y ausencia de POST adicionales. Las expectativas de rangos/funciones se basan en los metadatos de alcance del propio sistema; la correspondencia de línea usa fuente canónica. Esto no equivale a un oráculo independiente completo de pertinencia semántica para todos los grafos.

La tarea graph-code marcada completa corresponde a ese alcance finito histórico. No se modifica ni se convierte en cierre global.

## Publicación y secuencia posterior
publish-graph-scope-20261111/result.json registra publicación de siete archivos en 4521915ba4934b21e94ce4112699b184e8f24cc3, referencias remotas verificadas, runtime equivalente al manifiesto desplegado, sin merge ni publicación del índice local. Esto sucede después del published=false/deployed=false del registro de QA inicial.

El checkpoint de coordinación del 12 de noviembre registra graph-scope operativo y salud verificada en ese momento. Su checkpoint de render posterior registra publicación 8186a4f4e9b7b5419942bba034f7d9e78dfd958d para MST/consola, seis archivos, CI nuevo pendiente y despliegue en curso. Es evidencia reportada por coordinación, no una consulta remota nueva de este trabajo. No se afirma aquí despliegue 8186 completado ni diez pruebas repetidas sobre 8186.

## Límites y próximos pasos
No certifica suite global, cobertura global, CI verde, merge, todas las topologías, casos grandes ni equivalencia temporal universal. Queda adjuntar verificación de opción 3 sobre release final y mantener el seguimiento CI separado. Los fallos generales conocidos no quedan resueltos por este documento. No archivar ni actualizar specs globales automáticamente.
