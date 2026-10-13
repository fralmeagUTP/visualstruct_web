# Revisión independiente: captura DFS por ramas propias

Proyecto canónico D:\MisProyectos\Web_VisualEstruct, 2026-10-06 UTC. Change review-sorting-projection-diff-coverage-quality; operación audit.dfs-owned-branch-capture-independent-quality; assignment coordination-dfs-owned-branch-capture-independent-qa-low-20261006. Lectura estática y procesamiento de evidencia guardada, sin imports de aplicación, pruebas, HTTP, DFS30, adopción ni cambio de recursos. Se conserva y referencia [QA del predecesor](../dfs-owned-snapshot-publication-independent-review/review.md).

## Dictamen

Aceptación focal de compatibilidad, inventario de escrituras y contadores del candidato privado aa869a73f02a45a8c842bc1c0df4496bc2af5aa9cc58c34b7bcc233564f17d75. No encontré defecto material de invalidación para el modelo actual. Riesgo relevante: corrección ligada a un inventario manual de escritores, no observación automática de toda mutación futura. Exige actualizar invalidaciones y pruebas cuando cambie un escritor.

Los ahorros de trabajo son una hipótesis concreta que puede ensayarse con nueva autorización; por sí solos no prueban margen temporal para DFS30 ni justifican una serie de reintentos hasta obtener éxito. Si la finalidad fuera únicamente demostrar que ahora termina en 60 segundos, la evidencia disponible es insuficiente para prometerlo. Todos los timeouts anteriores siguen siendo fallos operativos conservados. DFS y los cuatro algoritmos numéricos Graph permanecen pendientes; 20/22 no cambia.

## Evidencia verificada

342 inputs coinciden por SHA-256; 249 fuentes canónicas before/after son idénticas. Ambos diffs corresponden exactamente a sus fuentes: canónico a ramas y privado owned a ramas. Tras eliminar únicamente kwargs privados de dirty/stack/revisions, llamada touch y tracking de changed_frames, las funciones originales distintas son build_dfs_trace y snapshot; helpers del modelo, emit y rechazo quedan idénticos en AST. No se eliminó ninguna mutación del modelo para obtener esa igualdad. Comprobaciones propias (evidencia local: `openspec/changes/archive/2026-10-13-review-sorting-projection-diff-coverage-quality/evidence/dfs-owned-branch-capture-independent-review/checks.json`).

Se descomprimieron y parsearon nueve JSON, verificando bytes y SHA: 1131 pasos, incluidos los 1 de rechazo API; no nueve casos más los seis anteriores. Todos los bytes coinciden con los nueve traces del predecesor. Sus seis fixtures originales también conservan la equivalencia ya verificada en QA anterior. Recalculadas directamente las discontinuidades de instruction_state: siete éxitos contienen exactamente returned antes de leave y published antes de caller; raw NULL y rechazo API no tienen esos cambios. No hay reconstrucción artificial old=previous-new.

Los resultados suman 2260 contrastes de snapshot contra el modelo mutable, dos por cada uno de 1130 eventos C-model. El script del autor obtiene heap, frames, retired, discovery, parents, contadores y selectores reales del contexto de snapshot y reconstruye con deepcopy independiente las ramas completas. Graph usa owned_graph: esa parte depende de la demostración estática de inmutabilidad v/a, no de una prueba dinámica independiente de cambios en graph. Comparación typed/key-order/JSON, alias y ejecución de validadores se aceptan como evidencia del autor con scripts y resultados sellados; no se volvieron a ejecutar aquí. La lectura de JSON no recupera identidades Python ni es un rerun del oráculo.

## Cobertura de escrituras e invalidación

Se leyó el código completo, contrastándolo con write-inventory.md. Para el modelo actual, todas las escrituras relevantes están cubiertas:

- Seed vertex/arc: dirty_nodes inicial contiene todas las claves. Las cadenas vhead/ahead y graph v/a quedan constantes una vez sembradas; no hay inserción/eliminación posterior de vértices ni cambios en next/value de un vértice. queue delante/atrás no se modifica en DFS.
- enter/leave: append/pop de frames incrementa revisión de stack; nuevo frame queda dirty. put, declaración call y successors, escritura de parámetros g y scope_exit marcan el frame concreto. Los IDs frame son monótonos y no se reutilizan.
- allocate: nuevo nodo, campos y local receptor invalidan heap y frame. write invalida el nodo y revisión heap; sólo mark de un vertex invalida graph_marks, lo que coincide con los únicos campos de vértice que se escriben después del seed.
- free: pop de heap y fila retirada incrementan heap/retired; cualquier alias de parámetros/locales reescrito se agrega a changed_frames e invalida frames. Las filas retired son nuevos dict de claves/valores escalares y después sólo se añaden filas, sin modificar anteriores. Cachear cada fila una vez es válido para este código.
- append del primer resultado modifica dfs.locals.recorrido y marca el root frame. Siguientes enlaces pasan por write. result/successor chains usan el selector actual más revisión heap; un cambio de local suces/recorrido cambia selector aunque heap permanezca igual.
- mark completion modifica g del frame, discovery y parents: frame dirty y revisión progress. No existen otros escritores de discovery/parents.
- Fuera de emit: dfs=enter se consulta directamente en root/head_storage; returned y published se incluyen como escalares frescos en cada snapshot. allocations/frees, actual activo, live del head y console también se calculan de nuevo. No dependen de la revisión del evento anterior.

El cache guarda exclusivamente publicaciones detached del pool: owned_nodes y owned_frames están indexados por IDs simbólicos no reutilizados; branches por revisiones/selectores; no por identidad de mutables del emisor. owned_retired es un acumulador privado cuya lista se clona al publicar, sin modificar roots ya retornados. Los mapas de nodos/frames retirados pueden conservar referencias hasta el fin de la llamada: la métrica de salida no mide ese coste temporal. Cada snapshot recomputa su root y head_storage, y emit mantiene las dos capturas y todas las validaciones/eventos aunque una escritura produzca el mismo valor.

El cache de cadenas vuelve a recorrer heap cuando cambia revisión, sin leer nodos liberados. La guardia node(key) mantiene su aserción live. Este inventario no certifica fallos de malloc, escritores añadidos, callbacks mutadores ni concurrencia sobre el modelo.

## Historia, consumidores y errores

El harness conserva sellos SHA de raíces históricas, live/retired membership y comparación completa de salida. El fixture de alias exige el mismo grafo completo de identidades compuestas que el predecesor y roots memory/visual compartidos propios; borrar los 19 contenedores de before/after no modifica la salida. La separación del primer step/pedagogy para initial_frame sigue intacta. No se cambian instrucciones C, frees, orden, recursión, narración, formato público dict/list ni codec.

El inventario de consumidores previamente revisado sigue vinculado a fuentes sin cambios: validador y servicio read-only, ruta pack/expansión, _json_safe/JSON, sesión que guarda historial copiado y frontend que congela los records decodificados. La nueva captura cambia preparación interna, no sus datos ni alias publicados; no aparece una escritura compartida nueva en esa cadena soportada. Se conserva la limitación de consumidores externos que muten outputs y ausencia de browser nuevo.

El control de rechazo API ahora captura únicamente VerticeNoEncontradoError y falla en else ante aceptación inesperada, corrigiendo la cautela del harness anterior. La AST de rechazo está intacta. Sus controles negativos históricos no se suman como ejecuciones nuevas. Esta prueba no cubre una taxonomía exhaustiva de excepciones ni asignación fallida.

## Contadores y siguiente ensayo útil

La suma propia confirma 663754 a 410049 visitas recursivas: 253705 menos, 38.2227 %. Las llamadas deepcopy del módulo pasan de 28938 a 1633: 27305 menos, 94.3569 %. No son bytes copiados ni nodos internos de deepcopy; intern sigue construyendo records cambiados y aumentan las llamadas raíz. El trabajo del oráculo y los sellos cuadráticos no está incluido en esos contadores ni es tiempo de aplicación. Objetos únicos/compuestos y sys.getsizeof retenido son iguales por caso; cache/pool temporales, pico y serialización no medidos.

No se conoce cuánto del tiempo censurado de DFS30 corresponde a las ramas ahora evitadas. Siguen existiendo variables/pedagogía por paso, visual deepcopy, scans de referencias, recorridos de cadenas al cambiar heap, validación global y un pool nuevo en transporte. Por ello no extrapolar 38 % a latencia ni asumir que otro límite de 60 s bastará.

Un ensayo útil, sólo tras nueva autorización, sería una única petición privada del mismo caso representativo (30 vértices/29 aristas, no dirigido, peso 1, inicio 1), exacto hash revisado y fuente canónica sellada. Worker real verificado dentro del Job de 2147483648 bytes antes de imports; overlay sólo del builder, C/rechazo/validadores/codec normales. Preparación fuera del intervalo; sin oráculo fresco, sellado histórico, contador de visitas ni profiler dentro del intervalo. Guardar preparación, comienzo/fin, desenlace completo o censura al límite operativo autorizado, sin retries ni aumento de recursos.

Si completa, conservar respuesta SHA/tamaño, traza íntegra, final/recorrido, continuidad, frees/ownership e historial; expansión/validación de artefacto después del intervalo. Si no completa, guardar explícitamente ausencia de respuesta y fase desconocida si no existe evidencia de fase; el resultado sirve para rechazar la hipótesis operativa, no para cerrar memoria o justificar otro intento idéntico. Una eventual medición de fase exige bloque propio autorizado y no se mezcla con el ensayo plain. Ni este dictamen ni un éxito aislado autorizan adopción o cierre global. C nativo puro y HTTP permanecen separados; no hay SLA 15 s para HTTP DFS ni Sorting.

Guardas before/after y conservación final quedan en esta carpeta. Sólo se escribieron evidencia y tracker propios; originales, checkpoints ajenos, preview y producto se preservaron.
