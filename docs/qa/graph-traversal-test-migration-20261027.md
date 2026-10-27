# Migración de pruebas de recorridos al contrato del libro

Las pruebas anteriores instrumentaban las funciones y estructuras internas de
la revisión histórica: cola enlazada de BFS, `grafo_agregar_recorrido`, firmas
sin `GrafoEstado` y snapshots firmados de marcas. Esa implementación no es la
que ejecuta `graph-book/v1`. No se introduce un adaptador para simularla.

Se conservan los diez casos originales de recorridos y sus repeticiones:
vacío, vértice -1, inicio ausente, rama, desconexión, ciclo, diamante, ciclo de
identificadores negativos, extremos int32 y ejecución repetida. Un oráculo
nativo independiente descarga el C/H actual y los compila sin cambiar sus
bytes; observa orden, estado, marcas, marcas de nodos de resultado y todas las
reservas/liberaciones de la unidad C. Los errores de inicio conservan las
marcas previas, y sólo un recorrido completo publica marcas nuevas.

La fidelidad de instrucciones del modelo se comprueba por separado contra el
archivo canónico: posiciones de fuente, ledger completo, continuidad temporal,
ámbitos, heap, liberaciones y cierre del llamador. No se afirma que estos
controles sean una equivalencia nativa de cada evento con el observador antiguo.

Los diecisiete casos de ownership de `main` conservan el hash de su artefacto
histórico. Se generan y compilan llamadores nuevos para la misma intención
finita con `GrafoEstado` y las funciones canónicas de liberación. Esos programas
nuevos son pruebas de caller/ownership, no nueva evidencia de navegador.

Los nueve casos de transporte DFS conservan sus fixtures históricos y verifican
el trace canónico completo antes/después del codec, referencias corruptas,
tipos y aislamiento frente a mutación de los inputs. La numeración interna de
records no se confunde con semántica C: se exige igualdad de todo el contenido
expandido y empaquetado idempotente.

Los C/H no se editan para documentarlos. `docs/graph-book-api.dox` documenta
externamente los cinco structs y todos sus campos; Doxygen mantiene activados
los controles previos de símbolos no documentados, errores y parámetros, con
la misma exigencia de cero warnings. La documentación complementaria sólo se
incluye cuando el input contiene el C/H del grafo, no para mains u otros TAD.

Validación local finita: 53 pruebas de instrucciones nativas/modelo, helpers,
documentación y callers pasadas; 23 pruebas de transporte pasadas en una segunda
ejecución después de conciliar la numeración de records. La suite completa y
sus checks remotos se informan separadamente.

Once pruebas adicionales de simulacion cubren las llamadas canonicas y el limite publico de 4000 eventos. Diez pasaron juntas y Bellman-Ford paso en una ejecucion enfocada posterior: la fixture densa original conserva rechazo atomico de step y ejecucion normal completa; la inspeccion detallada usa una cadena dirigida de siete vertices que cabe en el presupuesto, sin cambiar el limite. Total: 87 pruebas unicas aprobadas en ejecuciones enfocadas; no se presenta como una sola ejecucion integral.

Extension numerica: los cuatro archivos de documentacion preservan las descargas HTTP exactas, Doxygen sin warnings y contratos publicos vigentes; la prueba nativa Dijkstra comprueba preparar/indiceVertice/sumar_seguro, costos cero/negativos, overflow y liberacion. Los cuatro archivos de historial conservan sus treinta casos originales, ejecutan replay canonico deliberado y distinguen errores de payload (no agregar) de estados C fallidos (agregar y poder recargar). No se reaplican marcas guardadas de una implementacion historica.

Validacion de la extension: documentacion 4/4 (3.88 s); historial 27/30 iniciales y rerun enfocado 5 aprobadas, 7 no seleccionadas (22.03 s), cubriendo las tres correcciones. Son 34 pruebas numericas unicas aprobadas y 121 pruebas unicas en este alcance acumulado, no una ejecucion integral.

Cierre adicional: test_graph_numeric_python_json_boundary.py conserva sus nueve casos y aprueba 9/9 (41.29 s), incluyendo trace logico completo, codec HTTP sin sampling, estados C de ausencia/desconexion/ciclo y path/costo numerico exacto. Las dos suites pedagogicas fases4-6/fases7-9 mantienen sus 14 casos y aprueban en ejecuciones acotadas (13 iniciales, luego BFS/DFS enfocado). Conservan conceptos puros de representacion/grados/memoria y verifican instrucciones reales: cola Trabajo.prev, recursion DFS, seleccion Dijkstra, estado Bellman, raices vivas y continue Kruskal, y fallo Prim desconectado sin reinicio ficticio. _book_frame_oracle valida fuente/eventos/heap/continuidad completos. Total acumulado de este alcance: 144 pruebas unicas aprobadas en ejecuciones enfocadas; no implica un run integral ni CI remoto.
