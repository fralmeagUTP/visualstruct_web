# Guía docente del laboratorio de grafos

1. Prepare un caso guiado y pida identificar tipo de grafo, peso y componente alcanzable.
2. Active modo práctica y solicite una predicción antes de cada extracción, relajación o decisión MST.
3. Exija justificar la respuesta mediante auxiliar, condición C e invariante, no solo mediante el dibujo.
4. Compare BFS/DFS, Dijkstra/Bellman-Ford o Prim/Kruskal sin cambiar la entrada.
5. Cierre con un contraejemplo: peso negativo, destino inalcanzable, ciclo negativo o grafo desconectado.
6. Exporte el resumen JSON como evidencia de la sesión.

Atajos: `Alt+→` siguiente, `Alt+←` anterior, `Alt+Inicio` inicio, `Alt+Fin` final y `Alt+P` pausa.


### BFS: instruccion, cola y programa principal

La linea resaltada acaba de ejecutarse; el frame inicial es anterior a cualquier
llamada. BFS muestra las funciones C reales de grafo y cola, variables por ambito,
reservas temporales separadas del grafo, enlaces parciales y marcas compartidas.
Se marca al encolar, no al extraer; descubrir un vertice no significa que ya este
en el recorrido devuelto. `-1` es un identificador valido. El recorrido solo cubre
la componente alcanzable y depende del orden de insercion de arcos. Ignora pesos:
minimiza cantidad de arcos, no costo. El C de este TAD hace barridos de listas;
su cota es O(V*(V+E)), distinta de la BFS ideal O(V+E) con acceso directo.

`Paso anterior` restaura el frame y oculta resultados futuros; no ejecuta otro
POST ni vuelve a liberar nodos. Una declaracion o condicion puede no alterar el
dibujo del grafo: observe variables, cola y memoria. Las identidades mostradas son
simbolicas, no direcciones de una ejecucion nativa real. Tras free, el registro
historico no se puede usar como puntero. En la ruta normal BFS no imprime printf;
la consola no debe inventar visitas. La confirmacion de la app aparece al completar
la traza y es distinta del printf del programa principal.

Cada BFS exitoso, tambien dos llamadas iguales consecutivas, queda en el historial.
Recargar reconstruye la topologia sin volver a ejecutar consultas BFS historicas;
sus marcas/cola son efectos temporales de la ejecucion, no nueva topologia persistida.
Un inicio inexistente se rechaza en la app y no se agrega al main. En C crudo, BFS
desmarca primero y retorna NULL si inicio falta; son guardas distintas.

El main incluye `tad_grafo.h`, stdio y stdlib, ejecuta cada llamada guardada, imprime
los datos realmente devueltos y libera cada lista BFS y el grafo final. Descargue
tad_grafo.c/.h y su dependencia tad_cola.c/.h y compile juntos con C17. La falta de
memoria nativa puede producir listas parciales/NULL o marcas de vertices no procesados;
la simulacion actual modela asignaciones normales, sin inyectar esos fallos.


## DFS: contrato del C y caller descargado
DFS comprueba primero si existe el inicio; una llamada C con inicio inexistente
retorna NULL sin limpiar las marcas anteriores. La UI rechaza ese inicio antes
de ejecutar el TAD. Un inicio válido (también -1) limpia marcas y visita usando
recursión real y el orden de la lista de arcos, no orden numérico. Los nodos de
resultado son nuevos y tienen marcado=0, distintos de las marcas del grafo.
Cada frame libera sus sucesores temporales; el caller libera el resultado.
Dos llamadas iguales consecutivas exitosas se conservan; recargar reconstruye
topología sin ejecutar consultas históricas. El main imprime el resultado
calculado por grafo_dfs y libera su lista, en lugar de imprimir texto precalculado.
La cota del C de listas es O(V*(V+E)), además de profundidad recursiva hasta V.
Las reservas pueden fallar y producir resultados parciales; los casos de QA
normales no simulan esas fallas. La revisión por instrucción y reproducción
se verificó en diez casos nativos y ocho casos de navegador registrados; no
abarca todos los grafos, todos los caminos ni fallos de reserva de memoria.
Al recargar, las consultas nuevas conservan sus marcas mediante efectos
capturados y validados, sin volver a ejecutar consultas del historial. Las
mutaciones posteriores conservan las marcas de los vértices existentes; un
vértice recién creado empieza sin marcar. Un historial antiguo sin esos efectos
no permite recuperar marcas anteriores: no se inventan ni se repiten consultas.
Después de ejecutar en modo rápido puede abrir Paso a paso para recorrer la
misma ejecución hacia adelante o atrás; eso no ejecuta otra operación.


## Dijkstra: contrato nativo del C descargado
Dijkstra requiere pesos enteros no negativos en el C; cualquier arco negativo,
aunque esté desconectado del inicio, hace que el C retorne NULL. Un camino
al mismo vértice no necesita arcos y también se representa con NULL; no debe
confundirse por sí solo con un error. El resultado no vacío contiene arcos
nuevos y corresponde al llamador liberarlos. El grafo conserva sus marcas.

INT_MAX (2147483647) representa infinito: un costo total igual o mayor no se
publica como camino; las sumas fuera del rango se descartan antes de sumar.
Cuando dos vértices tienen la misma distancia, el C elige el primero en el
orden de su lista almacenada, no necesariamente el menor identificador.
Una distancia igual no sustituye el predecesor. La aplicación actual rechaza
pesos con parte fraccionaria; el archivo C de enteros no ofrece semántica decimal.
El usuario confirmó conservar pesos enteros representables y estas reglas C de
Dijkstra. El delta aprobado en openspec/changes/audit-local-quality-and-unified-controls/
specs/graph-structures/spec.md sustituye el requisito decimal histórico; su
consolidación canónica requiere verificar rango/finitud y la paridad todavía pendiente.
No se truncan fracciones ni se amplían tipos C durante esta corrección.

La comparación QA actual registró diferencias de empate y límite entre C y
aplicación. Los casos por instrucción de sus arreglos, condiciones y memoria
siguen pendientes; no se garantiza aquí paridad completa. El historial ya
conserva cada consulta exitosa sin repetirla al recargar; los fallos se omiten.
El programa generado imprime el camino y costo que devuelve el C y libera
sus arcos. Un retorno NULL se muestra como resultado ambiguo: sin arcos,
sin ruta o error de entrada/memoria, sin inventar un camino calculado.
Los casos normales no inyectan fallos de reserva de memoria.


## Bellman-Ford: negativos y límites del C descargado
Bellman-Ford admite pesos enteros negativos. Un ciclo negativo sólo se detecta
si es alcanzable desde el inicio; los ciclos desconectados no invalidan el
camino de otra componente. El C valida inicio y llegada antes de relajar.
La reparación autorizada separa alcanzabilidad y distancia long long:
INT_MAX es un costo válido y los caminos pueden exceder el rango int.
Comprueba la suma antes de ejecutarla; no descarta ni satura candidatas.
Una caminata menor que (n-1)*INT_MIN demuestra un ciclo negativo y permite
terminar antes de un descenso ilimitado. También comprueba una mejora
adicional tras n-1 pasadas, respetando el orden C de arcos y mejora estricta.
El caso de dos arcos INT_MIN ahora imprime "Se detecto un ciclo negativo."
y retorna NULL. La API responde HTTP 400, success=false, conserva bandera,
diagnóstico y consultas anteriores, y no registra una consulta exitosa nueva.
La comparación funcional no certifica todavía la traza por instrucción.

El resultado no vacío es una lista nueva de arcos que libera el llamador; el
grafo conserva su memoria y marcas. NULL también puede indicar camino sin
arcos, destino inalcanzable, entrada inválida o fallo de reserva. No debe
inferirse su causa sin el contexto. Las consultas exitosas repetidas se conservan al recargar sin volver a
ejecutarlas; las fallidas se omiten. El programa generado imprime el resultado
C y libera sus arcos. La fidelidad por instrucción sigue sin verificar.
Los casos normales no inyectan fallos de reserva; rige el contrato entero int32 aprobado.


## Prim: bosque y límites del C descargado
La API exige un grafo no dirigido y clasifica el resultado desconectado como
bosque, con número de componentes. El C no tiene bandera de dirección:
la representación no dirigida necesita arcos simétricos. El main generado
inserta/elimina ambos sentidos por operación; un bucle se escribe una sola vez.
Prim C reinicia en otros componentes y puede devolver un bosque completo,
no solamente el árbol del inicio. El grafo y sus marcas permanecen intactos.

La reparación autorizada usa presencia de candidato separada del costo:
admite negativos, INT_MIN e INT_MAX. Mantiene la mejora estricta y el primer
índice mínimo en el orden de la lista C de vértices, también al reiniciar
componentes. Python reproduce ese orden y el orden de la lista resultante.
Los pesos de entrada son enteros int32 finitos; 2.0 se normaliza a 2, mientras
2.5, infinito y valores fuera de rango se rechazan sin truncamiento.

Las consultas exitosas repetidas se conservan sin redispatch al recargar;
las rechazadas se omiten. El main imprime arcos/costo devueltos por C y libera
su lista propia y el grafo final. La suma de salida usa long long para evitar
sumar costos int en un acumulador int. NULL no diferencia bosque sin arcos,
inicio ausente y fallo de memoria. QA acotada usa memoria normal, sin inyección
de fallos ni firma de fidelidad por instrucción.


## Kruskal: contrato del C descargado
Kruskal admite pesos enteros negativos y extremos INT_MIN/INT_MAX. No usa
INT_MAX como infinito ni suma costos dentro del algoritmo: devuelve arcos.
El main acumula su costo en long long. El C ordena punteros a los arcos mediante
burbuja estable; no implementa el ordenamiento O(E log E) del modelo ideal.
Con búsquedas lineales de índices y padres, una cota conservadora de este C
es O(E²+EV+V). Los empates conservan orden de la lista de arcos y pueden
seleccionar un MST diferente del backend, aunque el costo coincida.

Union-Find rechaza bucles y el segundo sentido de un arco simétrico cuando
sus extremos ya están unidos. El resultado desconectado es un bosque; la API
actual informa componentes y clasificación. El C considera conexiones sin
bandera de dirección; la API exige no dirigido. El resultado es una lista
nueva propia del caller, mientras los arcos fuente y las marcas se conservan.
NULL puede significar ningún arco seleccionado o error de reserva; no permite
deducir la causa sin contexto. Ante fallo al reservar resultado, el C libera
la lista parcial. QA normal no inyectó dichos fallos.

Historial conserva consultas exitosas repetidas sin redispatch al recargar;
fallos dirigidos se omiten. El main imprime arcos/costo calculados por C y
libera resultado/grafo. No se cambió política decimal, empates ni dirección.
La fidelidad de arrays, Union-Find y memoria por instrucción sigue abierta.


### Prim y Dijkstra: reserva de sucesores atómica

El C utiliza un helper privado exclusivo de Prim/Dijkstra: obtiene todos los
sucesores o libera la lista parcial e informa fallo al algoritmo. Una reserva
fallida aborta la consulta, libera sus auxiliares y devuelve NULL; no se publica
un camino o bosque parcial como mínimo válido. NULL conserva la ambigüedad de
la firma pública entre error y resultado sin arcos. El helper público de
sucesores y los recorridos BFS/DFS conservan su contrato. Las identidades de
reserva mostradas por la traza son simbólicas; comprobarlas no equivale a
simular falta de memoria del navegador o del backend Python.


### Graph: main de sesión y snapshots exactos (2026-10-04)

«Descargar main.c» en Historial técnico entrega por HTTP el mismo texto que
se muestra, producido por un único generador desde las llamadas aceptadas de esta sesión.
Dos consultas iguales exitosas siguen siendo dos llamadas; un ciclo negativo
rechazado no agrega una llamada exitosa. Recarga y descarga reconstruyen la
topología sin ejecutar las consultas históricas. El main imprime los resultados
calculados por C, libera cada lista propia y el grafo anterior al reiniciarlo.
Compilar con tad_grafo.c y tad_cola.c y sus cabeceras, usando C17.

Las cuatro trazas numéricas transportan subárboles compartidos mediante
`graph-snapshot-pool/v1`, expandidos antes de reproducir. En el navegador,
los records de paso y todos los subárboles del pool están congelados;
la raíz, metadatos, eventos C y arrays `console` ordinarios no están congelados. Se conservan todos los
eventos/pasos, variables, scopes, estados antes/después y printf; no se muestrea
ni se interpola. La reproducción hacia delante/atrás/seek se verificó en
cuatro casos reales. La medición finita de tres vértices reduce JSON86.6–89.5%
y pico Python71.4–78.1%, con tiempo transcurrido24.56–30.47% mayor, medido por perf_counter bajo tracemalloc; no certifica
200 vértices. La prueba standalone del autor se bloqueó técnicamente al
iniciar el driver; ese intento histórico se conserva. Posteriormente el
revisor independiente sí inició Chromium y rechazó 30.148 mutaciones de
records de paso/subárboles compartidos en cinco fixtures, conservando todos
los campos antes/después. Verificó también el player adelante/atrás/seek;
no se presenta como congelación de toda la respuesta JSON.

QA independiente aceptó técnicamente los tres ajustes en alcance finito:
46 IDs de pruebas, seis fixtures nativos críticos y esta prueba de mutación,
sin sumarlos como grafos únicos. En su medición propia secuencial de Prim con
tres vértices, JSON disminuye89.54% y pico Python77.99%; tiempo transcurrido
17.225→21.435s (+24.44%) y CPU de proceso, medida separadamente con process_time,
17.219→21.438s (+24.50%). Estas mediciones CPU pertenecen al revisor, no al
perfil perf_counter del autor. No certifican RSS/heap de navegador,200vértices,
otros compiladores ni la auditoría global. Las notas históricas anteriores
sobre main HTTP/fidelidad se sustituyen sólo para los casos registrados.

Dictamen y evidencia: [revisión independiente Graph](../../openspec/changes/audit-local-quality-and-unified-controls/evidence/independent-review-graph-three-approved-adjustments/review.md), [precisión documental consolidada](../../openspec/changes/audit-local-quality-and-unified-controls/graph-qa-documentary-consolidation-addendum-low.md).


### Limite educativo de grafos: 15 vertices

La aplicacion admite como maximo 15 vertices, por decision actual del usuario del
6 de octubre de 2026. El limite cuenta vertices distintos, no sus identificadores:
pueden ser enteros negativos o mayores que15 dentro del contrato C.
Insertar un vertice o arista que cree el numero16 y generar16 se rechazan antes de
modificar grafo, resultado, semilla o historial. La comparacion admite hasta15.
No se truncan datos. Las sesiones anteriores mayores conservan vertices, aristas,
historial y main descargable; pueden consultarse y reducirse explicitamente.
Inserciones y algoritmos se bloquean mientras se exceda15. El C/H no cambia.

Por instruccion del usuario, las comprobaciones funcionales y visuales actuales
se acotan a8 nodos. La admision15/rechazo16 se verifica sin ejecutar algoritmos
completos de esos tamanos. Admitir15 no certifica rendimiento/usabilidad de15.
La preparacion de trazas visuales puede demorar: BF20 privado previo completo
midio31min1.922s antes de UI; ese caso ahora es evidencia historica, no una entrada
admitida ni una garantia de otros grafos. No se continuan optimizaciones ni se
repiten ensayos largos. Los controles manuales recorren una traza ya preparada.

Las pruebas anteriores con limite30 y100 conservan su evidencia historica.
Reducir el dominio no declara PASS requisitos pendientes de rendimiento,
cobertura, fidelidad completa o visualizacion. No hay adopcion silenciosa del
candidato privado de generacion/transporte.
