# Manual de usuario

Actualización del flujo y contratos: **2026-10-04**. Los informes de QA enlazados conservan sus propias fechas y alcances.

## Objetivo y módulos

VisualStruct permite practicar Pila, Cola, Cola de prioridad, Lista enlazada, Lista circular, Sublista, ABB, AVL, Rojo-Negro, Montículo binario, Grafos, Hash y once métodos de Ordenamiento. La representación visual acompaña el código C real de `docs/tads_C`; cuando una opción no tiene método C, se identifica el código auxiliar o fallback correspondiente.

## Arranque local

Desde la raíz del proyecto `D:\MisProyectos\Web_VisualEstruct`, con Python 3.10+ y las dependencias del proyecto:

```powershell
.\start_local.bat
```

Ese script usa `http://127.0.0.1:5050/`. El preview de la auditoría ya iniciado usa `http://127.0.0.1:5051/`; su manual está en `/help/manual`. Usa la URL que indique tu servidor. No inicies otra instancia sobre un puerto ocupado ni cierres procesos Python ajenos. Si necesitas un puerto distinto para una instancia propia, configura `FLASK_PORT` al ejecutar `run.py`; `start_local.bat` fija 5050.

## Cinco secciones y controles

1. **Preparar y controlar ejecución:** selecciona operación, completa sus entradas y elige el modo.
2. **Visualizar y ejecutar:** observa estado, variables, memoria y evento activo, en las vistas disponibles.
3. **Relacionar con código:** consulta el C de la operación y sus auxiliares.
4. **Comprender:** utiliza explicaciones y actividades del módulo.
5. **Resultados de ejecución:** consulta resultado, consola e historial cuando corresponda.

**Ejecutar operación** inicia una operación nueva. Con **Paso a paso** activo, **Paso anterior** y **Siguiente paso** recorren la traza preparada; aparecen y se deshabilitan según modo y posición. **Cerrar paso a paso** muestra el final de la misma ejecución, sin otra operación. Cambiar modo o navegar no equivale a Reiniciar. Reactivar el modo reutiliza una traza conservada cuando exista; una ejecución rápida sin traza requiere activar el modo antes de una nueva operación. Los controles adicionales se describen en cada pantalla, sin imponer un número fijo.

La línea resaltada acaba de ejecutarse y el dibujo muestra su estado posterior; paso 0 es anterior al primer evento. Declaraciones, condiciones, llamadas y retornos pueden conservar la estructura. La consola C corresponde a `printf` ejecutados; mensajes de la aplicación y resúmenes del main se distinguen de esa salida. Las reservas temporales y los nodos liberados se muestran según su vida, sin anticipar efectos.

La barra superior permite navegación, Manual, Ayudas, detalles técnicos y exportar JPG cuando el módulo lo habilita. Calidad y escala afectan a la exportación de imagen, no a los datos ni a la ejecución.

## Entradas y contratos

- Secuenciales y jerárquicos usan valores enteros; respeta el formato y límites de cada operación. Una reserva C puede fallar; un retorno sentinel como−1 no vuelve inválido ese dato almacenado.
- En Grafos, los identificadores y pesos son enteros representables Cint32. Un peso 2.0 se normaliza a 2; 2.5, infinitos y valores fuera de rango se rechazan. La API permite modalidad dirigida/no dirigida; el C guarda listas de vértices y arcos, sin una bandera dirigida. Las fases son Construcción, Recorridos, Caminos mínimos y Expansión mínima. El máximo admitido es de 15 por decision actual del usuario, en lugar de 200 vértices; no se amplía aquí.
- Hash usa claves y valores **enteros** con capacidad **fija** de buckets durante las operaciones. Una clave nueva puede colisionar y se encadena; actualizar una clave no crea otro nodo ni rehash. Crear requiere capacidad positiva y válida para la operación.
- Ordenamiento admite 1..80 enteros int32 en la interfaz. Los once métodos son intercambio, selección, inserción, burbuja, Shell, Quicksort, Mergesort, Heapsort, Counting Sort, Binsort y Radix. Counting/Binsort requieren `k=max-min+1<=1000000`; ese límite es el intervalo inclusivo de valores, no el número de elementos. Binsort delega en Counting. Los métodos con retorno de estado usan `ORDENAMIENTO_OK=1` y `ORDENAMIENTO_ERROR=0`; otros métodos C retornan void. Las reservas y tamaños representables conservan sus propios requisitos.

Un rechazo de validación no ejecuta el algoritmo. Un error detectado durante C, como un ciclo negativo alcanzable en Bellman-Ford, puede tener una traza causal de error y no añade una llamada exitosa al main.

## Historial, programas C y memoria

Las operaciones aceptadas y las consultas explícitas que el módulo conserva, incluidas repeticiones iguales, forman el historial ejecutable. Una consulta completada de Validar RN con resultado falso sigue siendo una consulta válida; no equivale a errorHTTP. Al recargar, se reconstruye el estado y se conservan las consultas sin volver a despacharlas como operaciones del historial. La reconstrucción puede consultar metadata readonly internamente. Reiniciar y Limpiar tienen el comportamiento de su pantalla; no se deben confundir con avanzar o cerrar la traza.

Ayuda ofrece el C/H completo de cada TAD. Son bibliotecas, no un main. Los ejemplos principales mostrados en historial se copian o descargan donde la pantalla ofrezca ese control. Para un fragmento, añade los includes indicados; compila el main con el C del TAD y sus dependencias. Grafos necesita también `tad_cola.c/.h`. Por ejemplo:

```powershell
gcc -std=c17 -Wall -Wextra -Wpedantic main.c tad_grafo.c tad_cola.c -o ejemplo.exe
```

Mantén los headers en ese directorio. El main calcula resultados llamando a C; no debe imprimir respuestas prefabricadas. Copiar un puntero o una estructura con cabezas comparte las reservas, no crea un propietario independiente. Libera únicamente las reservas propias según cada contrato y no uses aliases después de free. Las identidades de la visualización son simbólicas.

## Particularidades de estructuras

Lista admite datos repetidos y Buscar elemento recorre todas las coincidencias; `lista_eliminar_repetidos` elimina todas las ocurrencias del valor solicitado. Cola de prioridad conserva la cadena de llegada: atiende el menor número de prioridad y desempata por llegada, aunque el candidato no sea el primer nodo físico. Lista circular cierra el anillo al terminar una operación consistente; las escrituras intermedias pueden romper temporalmente ese cierre. Sublista modifica el primer padre/hijo coincidente, y eliminar un padre libera antes sus hijos.

ABB mantiene orden estricto; Buscar C devuelve un alias prestado, mientras la interfaz muestra un booleano. AVL usa FE=altura(derecha)-altura(izquierda), con padres consistentes y estados transitorios de rotación; su auxiliar mostrado de Validar calcula equilibrio por alturas y no certifica el FE almacenado ni el orden ABB. RN usa NULL conceptual como hoja negra, colores legales, raíz negra, regla rojo-rojo y altura negra uniforme, además de orden estricto y enlaces padre/ciclos compartidos sobre objetos vivos. Las invariantes se exigen tras operaciones completas válidas, no a cada escritura de una rotación.

El Montículo de la interfaz es mínimo, con arreglo y árbol sincronizados; el C admite selectores mínimo/máximo. Insertar/subir y extraer/bajar restablecen su propiedad; consultar raíz o arreglo no cambia esa reserva. Una copia de arreglo es independiente y se libera por el caller; no confundirla con copiar por valor la estructura propietaria.

## Grafos y resultados

BFS minimiza número de arcos, no peso. DFS sigue la lista de arcos y recursión. Dijkstra rechaza cualquier arco negativo, incluso desconectado; usa INT_MAX como infinito, por lo que un costo total igual o superior no se publica como camino. Bellman-Ford separa alcanzabilidad y distancia long long, comprueba sumas y detecta ciclos negativos alcanzables; esos ciclos producen HTTP 400/success=false y diagnóstico de la ejecución real. Prim y Kruskal se ofrecen sólo para grafos no dirigidos y pueden producir bosque al haber desconexión; admiten negativos y extremos int. Prim usa presencia candidata separada del costo. Los empates siguen el orden de las listas C y mejoras estrictas, no un orden numérico supuesto.

Los resultados de recorridos/caminos/bosques son listas nuevas propias del caller. NULL por sí solo no distingue resultado sin arcos, falta de ruta y error/memoria: usa el contexto del algoritmo. El main libera resultados, auxiliares y grafo según sus contratos. Las notas detalladas siguientes conservan ejemplos y límites de la evidencia; las afirmaciones antiguas de fidelidad pendiente se sustituyen sólo para los casos aceptados en la QA vigente enlazada al final.

## Problemas locales y verificación

Si aparece `ERR_CONNECTION_REFUSED`, verifica la URL/puerto y la instancia propia que debería atenderlos. Conserva el preview 5051 de esta auditoría y los procesos ajenos. No resuelvas un puerto ocupado cerrando indiscriminadamente Python.

Las comprobaciones del proyecto se ejecutan desde la raíz con `.\.venv\Scripts\python.exe -m pytest -q` cuando corresponda a la revisión final coordinada. Los cierres de casos, Doxygen y compilación no certifican todas las entradas, otros ABI ni seguridad bajo sanitizadores no disponibles.

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
consolidación canónica sigue su proceso SDD; rango, finitud y paridad tienen
aceptación técnica finita en la evidencia vigente.
No se truncan fracciones ni se amplían tipos C durante esta corrección.

El baseline histórico registró diferencias de empate y límite. La reparación
y QA vigentes aceptaron la paridad y los eventos de arreglos, condiciones y
memoria para los casos registrados. No es una garantía universal de entradas. El historial ya
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
La verificación posterior y QA aceptaron la traza por instrucción para los
casos registrados, conservando los baselines originales y sus límites.

El resultado no vacío es una lista nueva de arcos que libera el llamador; el
grafo conserva su memoria y marcas. NULL también puede indicar camino sin
arcos, destino inalcanzable, entrada inválida o fallo de reserva. No debe
inferirse su causa sin el contexto. Las consultas exitosas repetidas se conservan al recargar sin volver a
ejecutarlas; las fallidas se omiten. El programa generado imprime el resultado
C y libera sus arcos. La fidelidad por instrucción tiene aceptación finita en la QA vigente.
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
inicio ausente y fallo de memoria. La QA vigente acepta instrucción y memoria para casos normales y fallos
controlados registrados; no equivale a OOM real ni certificación universal.


## Kruskal: contrato del C descargado
Kruskal admite pesos enteros negativos y extremos INT_MIN/INT_MAX. No usa
INT_MAX como infinito ni suma costos dentro del algoritmo: devuelve arcos.
El main acumula su costo en long long. El C ordena punteros a los arcos mediante
burbuja estable; no implementa el ordenamiento O(E log E) del modelo ideal.
Con búsquedas lineales de índices y padres, una cota conservadora de este C
es O(E²+EV+V). Los empates conservan el orden de la lista de arcos; la aplicación vigente
reproduce ese contrato en los casos aceptados. Baselines con otro desempate
se conservan como evidencia histórica.

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
libera resultado/grafo. Se conserva el contrato aprobado de enteros, empates C y aplicación no dirigida.
La fidelidad de arrays, Union-Find y memoria tiene aceptación finita vigente.


## Ordenamientos: baseline C y límites actuales
Hay once métodos:intercambio,seleccion,insercion,burbuja,shell,quicksort,
mergesort,heapsort,counting_sort,binsort,radixsort. Todos trabajan sobre int;
API admite1..80elementos int32 yrechaza vacío antes del algoritmo. Cvoid
ignora NULL/n0;Merge/Counting/Bin/Radix retornan ERROR en esa entrada. Counting
usa k=max-min+1 computado enlong long,limita k a1000000 antes de reservar;
Binsort delega exactamente. Radix usa magnitudes uint32_t yprotege INT_MIN:
no se reproduce el desbordamiento histórico enel C actual de QA.

Inserción/burbuja/mezcla son estables por comparaciones estrictas/elección
izquierda;intercambio,selección,Shell,Quick,Heap no garantizan estabilidad.
Counting/Bin reconstruyen frecuencias,sinidentidad de registros iguales;
Radix tiene pasadas estables pero revierte elgrupo negativo completo: no
prometer estabilidad general de registros negativos iguales. Un array int
con duplicados sólo prueba resultado/multiconjunto, no identidad estable.

Heap usa stack O(log n) por heapify recursivo;Quick pila O(log n) promedio y
O(n) peor;Merge auxiliar O(n). Los restantes directos sonO(n²) peor,Shelldepende
de gaps;Counting/Bin O(n+k),Radix base10 O(d(n+10)). Las notasC/H concretan
cada contrato;no confundir cota teórica con métricas observadas o tiempo real.

Las ejecuciones exitosas se conservan con efecto de arreglo validado:GET
restaura resultado sin volver a ordenar;repetir Ejecutar ordena el estado
actual. Fallos no seagregan. APIstep reconstruye la última traza desde su
entrada original;UI usa la traza local. Historiales antiguos sin efecto no
pueden recuperar ejecuciones perdidas. El main de historial está disponible en Resultados de ejecución. Los once métodos tienen cierres finitos por instrucción; los contratos numéricos de Grafos están aprobados. Esto no cierra los criterios agregados de la auditoría.


### Main reproducible de Ordenamientos

En la quinta seccion, **Resultados de ejecucion**, activa los detalles tecnicos y abre el historial. Alli puedes copiar o descargar `main.c`, `tad_ordenamiento.c` y `tad_ordenamiento.h`. Los enlaces usan las descargas existentes; no hay otro boton de ejecucion. Compila el programa completo:

```sh
gcc -std=c17 -Wall -Wextra -pedantic main.c tad_ordenamiento.c -o ordenamiento
```

El programa reproduce solo creaciones y runs aceptados, en orden: una recreacion reemplaza los datos y dos ejecuciones iguales siguen siendo dos llamadas. Seleccionar un metodo sin ejecutar deja un comentario; los fallos de entrada no agregan llamadas. GET, recarga y navegacion no vuelven a ordenar ni a generar aleatorios guardados. Los valores aleatorios estan materializados; no se usa rand de C para reproducir una semilla Python. La exportacion JSON existente incluye el mismo main.

El arreglo del caller tiene almacenamiento automatico para80elementos, sin malloc/free. Los metodos del TAD liberan sus auxiliares cuando aplica. Siete firmas son void; Merge/Counting/Bin/Radix retornan int: el main comprueba ORDENAMIENTO_OK y termina con codigo1 ante un fallo nativo, incluida memoria, sin imprimir un arreglo exitoso futuro. Las salidas se calculan mediante las llamadas C reales, no son textos copiados del resultado de Python. Dominio de la aplicacion: enteros int32 y1..80elementos; Counting/Bin rechazan rango mayor que1000000. El main vacio imprime[]. La compilacion exige int32 para reproducir limitesINT_MIN/INT_MAX.

Verificar este caller no verifica las instrucciones internas de los once metodos. Intercambio, Seleccion e Insercion tienen verificaciones por instruccion acotadas a seis entradas de hasta cuatro valores y sus guardas registradas; Burbuja mejorada tiene siete entradas de hasta cuatro valores y sus guardas registradas. Shell tiene seis entradas registradas de hasta cuatro valores con verificacion por instruccion. Quick sort tiene seis entradas registradas de hasta cuatro valores con verificacion por instruccion. Merge sort tiene seis entradas registradas con verificacion por instruccion. Los cuatro métodos restantes tienen cierres finitos posteriores enlazados en esta guía. Esto no declara cobertura de todas las entradas ni estabilidad de identidades etiquetadas.


### Leer los desplazamientos de Insercion

Durante `arreglo[j] = arreglo[j - 1]`, el arreglo conserva los dos valores reales que quedan tras la escritura; no hay una celda vacia. El valor desplazado que falta en ese estado permanece en el local `int clave`, visible en temporales y variables. La estrategia muestra **Clave** e **Indice j** del frame actual. `--j` es un paso separado y no cambia el arreglo; `arreglo[j] = clave` completa la insercion.

La condicion `j > 0 && arreglo[j - 1] > clave` muestra sus operandos en orden y el resultado compuesto. Si `j==0`, no se consulta `arreglo[j - 1]`. Al cerrar la pasada desaparecen sus locales `clave/j`; `i` continua hasta el retorno. El prefijo de pasadas terminadas esta ordenado, pero una clave futura aun puede desplazarlo. Avanzar, retroceder y cambiar de modo restauran la misma traza sin nueva ejecucion.


### Burbuja mejorada y sus metricas

El catalogo de Ordenamientos contiene una variante de Burbuja: **Burbuja mejorada**, `ordenar_burbuja`. Compara vecinos y reduce el segmento pendiente tras cada pasada. Si una pasada termina sin intercambios, la bandera `hubo_intercambio` queda en cero y el C sale mediante `break`.

Cada intercambio contabiliza tres movimientos: guardar `temporal`, escribir `*a` y escribir `*b`. La metrica cambia al ejecutar cada asignacion, tambien durante el estado duplicado provisional. Una pasada sin intercambio aporta comparaciones pero cero movimientos. La verificacion por instruccion de Burbuja cubre siete entradas registradas de hasta cuatro valores. Las 330 observaciones del C coinciden con los estados de la traza, incluyendo controles, locales y escrituras parciales. Este cierre es acotado; no afirma cobertura de todas las entradas ni de identidades etiquetadas.

La bandera se declara sin inicializar y se asigna cero al iniciar cada pasada. Durante el primer intercambio sigue en cero: solo pasa a uno tras retornar del helper y ejecutar su asignacion C. Los indices pasada y j y la bandera permanecen en su scope de funcion entre pasadas. El helper muestra los dos punteros reales a vecinos y su local temporal; estos locales desaparecen al retornar. Una prueba interna falsa no muestra vecinos fuera de limites. Tras una pasada sin intercambios, break termina el bucle exterior sin incrementar pasada ni evaluar otra condicion exterior. El retorno retira los locales. Avanzar, retroceder y cambiar de modo restauran los mismos estados sin agregar ejecuciones.


### Leer la traza de Shell

Shell usa intervalos n/2, n/4 y asi hasta uno, insertando cada elemento dentro de su grupo por intervalo. La estrategia muestra el intervalo numerico, i, j, temporal y los indices del grupo activo. La declaracion de intervalo y la de i muestran sin inicializar hasta ejecutar su asignacion C; el retorno retira los locales.

Durante arreglo[j] = arreglo[j - intervalo] se muestran valores duplicados reales. El valor pendiente permanece en int temporal; no hay una celda vacia. j -= intervalo es otra instruccion, sin escribir el arreglo. La condicion j >= intervalo && arreglo[j - intervalo] > temporal muestra primero el indice y solo consulta el arreglo si ese operando es verdadero. La comparacion se contabiliza solo cuando se ejecuta.

j y temporal pertenecen al cuerpo de i y desaparecen antes de ++i. i pertenece al cuerpo del intervalo y desaparece antes de intervalo /= 2. Al terminar ese cuerpo todos sus grupos estan ordenados por el intervalo; sus valores aun pueden cambiar con un intervalo posterior. Los colores de valores definitivos se reservan para el retorno final. Avance, retroceso y cambio de modo restauran la misma traza sin otra ejecucion.

El cierre registrado de Shell comprende seis entradas de hasta cuatro valores y sus guardas nativas,322observacionesC. No afirma cobertura de todas las entradas ni estabilidad de identidades etiquetadas. Se conservan los cuatro cierres acotados anteriores; Quick sort tambien tiene su cierre acotado; Merge sort tambien tiene cierre acotado; los cuatro métodos restantes tienen cierres finitos posteriores.


### Leer la recursion de Quick sort

Quick sort usa un pivote entero local y dos indices int. La estrategia muestra los parametros primero/ultimo, i/j, el valor local de pivote y profundidad de la activacion actual. La particion esta dentro de quicksort_recursivo; no hay una funcion particion aparte. La pila muestra cada activacion con sus propios parametros y los scopes numerados distinguen locales de padres e hijos. El caller conserva sus variables mientras el hijo ejecuta; el retorno retira solo los locales del hijo.

Los scans muestran la comparacion real con el pivote guardado, seguido de ++i o --j cuando corresponde. El while exterior y el if i<=j se representan separadamente. Despues de intercambiar, ++i y --j son dos instrucciones; j puede valer -1 como int, sin que ese estado autorice consultar arreglo[-1]. Las guardas primero<j e i<ultimo deciden las llamadas recursivas.

Cada intercambio ejecuta tres asignaciones, incluso si a y b apuntan al mismo entero. Ambos alias se muestran en la pila y punteros; temporal permanece disponible durante las escrituras parciales y se retira al retornar. Con [7], el C y la traza llaman al helper, realizan el auto-intercambio y cuentan tres comparaciones, un intercambio y tres movimientos. No se imprime una salida printf del TAD. Los programas descargados calculan sus salidas mediante C.

Avance, retroceso y cambios de modo restauran la misma traza sin nuevas llamadas. El cierre registrado comprende seis entradas de hasta cuatro valores,386observacionesC y sus guardas nativas; no afirma todas las entradas ni estabilidad de identidades etiquetadas. Se conservan los cinco cierres anteriores; Merge sort tambien tiene cierre acotado; los cuatro métodos restantes tienen cierres finitos posteriores. El dominio de aplicacion1..80 evita cast y suma de indices no representables; no se ha auditado huge-n fuera de ese dominio.


### Merge sort: baseline LOW histórico (2026-10-02)

El baseline conservado registró seis resultados/métricas coincidentes, pero una traza de63cuadros frente652observacionesC. Mostraba valores prematuros del auxiliar y omitía activaciones recursivas y escrituras individuales. Las once regresiones causales originales y sus logs se preservan. Ese baseline no constituía cierre por instrucción; el bloque posterior se describe a continuación.

### Merge sort: reserva, recursión y mezcla por instrucción

La vista representa los parámetros size_t de cada activación, el medio declarado después de la guarda y los locales i/j/k de mezclar. Conserva ancestros suspendidos, llamadas, retornos y retirada de scopes. El caso n1 también reserva, llama al caso base y libera. Las condiciones && respetan cortocircuito; <= elige la rama izquierda al empatar.

El auxiliar tiene tamaño n y empieza con celdas «sin inicializar»; cada escritura define únicamente su destino. Cada asignación con postincrementos se presenta completa, sin atribuir un orden de evaluación no fijado por C. La copia de vuelta modifica una celda por cuadro. free termina la vida de la reserva sin afirmar que C asigna NULL, y el retorno final confirma el resultado. La UI indica «sin contador ordinal» porque estos ciclos no declaran tal contador; i/j/k muestran sus valores C. El TAD no produce printf en esta ruta.

Avance, retroceso, fast->step y recarga conservan la misma ejecución sin redispatch y mantienen el caller descargado. Los siete programas únicos registrados (seis entradas +vacío) compilan en C17 y generan Doxygen sin advertencias; las seis llamadas equilibran una reserva/liberación cada una. Los callers manejan ORDENAMIENTO_ERROR ante fallo de primera reserva sin imprimir éxito. Guardas nativas n0/NULL y fallo de reserva se verificaron por separado de la UI vacía rechazada; el backend normal no simula agotamiento real de malloc.

El cierre comprende exclusivamente seis entradas de hasta cuatro valores,652observacionesC y1304restauracionesUI. No demuestra todas las entradas, estabilidad de identidades etiquetadas ni huge-n fuera del dominio1..80. Evidencia: openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-mergesort-instructions/README.md. Este fue el séptimo cierre registrado; Heap, Counting, Bin y Radix tienen cierres finitos posteriores.


### Heap sort: alcance del baseline LOW histórico

Heap sort es ordenar_heapsort del TAD de Ordenamientos, con helpers heapify e intercambiar; es independiente del TAD Heap binario. Los seis casos registrados coinciden en resultado, comparaciones, intercambios y movimientos. Se contabilizan tres movimientos por llamada al helper incluso con valores iguales, sin salida printf del TAD. Los alias de la guarda y los parámetros del helper se representan desde sus índices reales. No usa memoria dinámica; el espacio auxiliar pertenece a la pila recursiva.

En ese baseline histórico, la traza omitía controles for, asignaciones de mayor, activaciones/retornos recursivos y scopes. La estrategia dibuja también el sufijo ya extraído dentro del árbol; no debe tomarse como certificado del heap activo. Se registraron doce regresiones causales y un bloque MEDIUM; su resolución posterior se describe a continuación. Coincidir en métricas no convierte Heap sort en el octavo cierre por instrucción.

Los cuatro callers descargados actuales compilan en C17 y pasan Doxygen, con tres llamadas reales y cero reservas dinámicas. Guardas nativas n0/NULL y aNULL/bNULL se probaron por separado de la UI vacía rechazada. Detalle y límites: openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-heapsort-baseline-low/README.md.


### Heap sort: instrucciones verificadas en seis casos (2026-10-02)

El bloque MEDIUM muestra los controles reales de ordenar_heapsort, las activaciones recursivas de heapify y las tres asignaciones de intercambiar. El árbol usa solo heap_n; el sufijo confirmado se presenta aparte tras cada extracción terminada. La propiedad max-heap refleja el estado actual y puede incumplirse durante construcción o intercambio parcial. Temporal permanece sin inicializar hasta su lectura real; no hay printf ni reserva dinámica en este TAD. Replay y JSON preservan cursor/estado/main sin ejecutar de nuevo; cursor -1 representa el estado previo. El baseline LOW anterior es histórico. Cierre limitado a los seis casos y evidencia visible-sorting-heapsort-instructions; no prueba universal para todos los arreglos.


### Counting sort: baseline LOW histórico (2026-10-02)

> Fotografía histórica: las limitaciones y tareas pendientes descritas aquí quedaron sustituidas por los cierres consolidados posteriores; no describen la traza vigente.

El TAD acepta rango max-min+1 hasta1000000, reserva frecuencias con calloc y libera conteo al terminar; devuelve ERROR ante rango rechazado o reserva fallida. En los seis casos pequeños registrados, la traza agregada cuenta ambas comparaciones de mínimo/máximo y las escrituras de frecuencia, resultado y consumo (2(n-1)comparaciones/3nmovimientos). No hay printf en el TAD. Fast->step,replay/JSON/historial reutilizan la misma ejecución. La traza aún agrupa escritura ydecremento yno expone todos los controles/scopes ni free: fidelidad porinstrucción pendiente, doce regresiones activas. Las fronteras grandes se verificaron solo en Csize_t64; no se ejecutó variante32bit potencialmente insegura. Ver evidencia visible-sorting-counting-baseline-low yplan sorting-counting-instruction-review-plan.md; no cierre universal.


### Counting sort: fotografía MEDIUM inicial de seis casos (2026-10-02)

> Fotografía histórica: las limitaciones y tareas pendientes descritas aquí quedaron sustituidas por los cierres consolidados posteriores; no describen la traza vigente.

En seis casos n<=4/rango<=4, la nueva traza muestra 416 eventos C: mínimo/máximo mediante aliases a locales, controles reales, calloc con frecuencias cero, escritura con indice++ ydecremento posterior separados, free yretirolexical. Las doce regresiones del baseline se resolvieron sin modificar tests originales. La UI distingue sin declarar/sin inicializar/fuera de alcance y restaura estado/main/JSON sin ejecutar otra vez. El frame parcial de escritura conserva frecuencia hasta --conteo[i].

Este cierre no cubre todoel dominio. Para evitar copias O(k²), fuera de n<=4/rango<=4 se mantiene la traza agregada existente; la app sigueaceptando hasta80elementos y rango1000000. Recorder escalable y fidelidad de entradasamplias pendientes. El oráculo estáverificado con size_t64; no se ejecutó variante32bit potencialmente insegura ni ramo SIZE_MAXverdadero. Ver evidence/visible-sorting-counting-instructions ysorting-counting-resource-bound-decision.md; no prueba universal de memoriaagotada/estabilidad.


### Fotografía anterior de Counting: parcial antes de integración ampliada

> Fotografía histórica: las limitaciones y tareas pendientes descritas aquí quedaron sustituidas por los cierres consolidados posteriores; no describen la traza vigente.

La verificación de seis casos pequeños no completa la fidelidad del método. El corte interno n<=4/rango<=4 no es un límite UI aprobado: entradas ordinarias admitidas fuera de él siguen usando traza agregada. La app conserva hasta80enteros int32 y rangoCounting<=1000000. La revisión actual reconoce Counting parcial y propone representación exacta escalable (frecuencias sparse/deltas/eventos paginados/ventana de buckets), sin rechazar entradas válidas. No se ha implementado aún; ver sorting-counting-scope-correction-decision.md ysorting-counting-expanded-fidelity-plan.md.


### Counting: navegación ampliada implementada (2026-10-02)

> Fotografía histórica: las limitaciones y tareas pendientes descritas aquí quedaron sustituidas por los cierres consolidados posteriores; no describen la traza vigente.

La integración nueva sustituye la fotografía anterior del corte de cuatro: todas las entradas admitidas usan el mismo núcleo por instrucción. Se conservan1..80enteros int32 y rango max-min+1<=1000000. Las trazas pequeñas conservan el transporte completo; las grandes cargan páginas de eventos exactos sin volver a ordenar. En modo paso a paso, Counting permite Ir al paso (0 es antes de la llamada), Anterior/Siguiente yReproducir traza/Pausar. El contador incluye todos los eventos del rango, también controles de frecuencias cero.

Conteo se muestra en ventana64celdas: el campo Ir al índice de conteo permite consultar cualquier índice real, incluido un hueco grande cuyo valor implícito es cero; Seguir índice activo vuelve a la ventana de la instrucción. No se confunde memoria liberada con una frecuencia cero. La variable i, la pila/helper, alias, condición ylíneaC corresponden al evento activo; escritura del arreglo ydecremento de frecuencia siguen separados.

La recarga en la misma pestaña recupera cursor/modo yreferencia de traza sin nueva operación; Exportar resumenJSON agrega representación compacta completa ymain, evitando listar millones de snapshots. No hay importadorJSON nuevo. El almacenamiento de trazas es local al proceso, acotado, por sesión yconTTL15min desde su creación; expiración/evicción o reinicio del servidor puede dejar una referencia indisponible yse informa sin volver a ejecutar Counting. La historia/resultados aceptados siguen disponibles. GET de página ylegacy /step no agregan llamadas al main ni entradas dehistorial.

Integración verificada en35IDs locales ydos casos browser k1000000/n2,n80; el método permanece parcial para auditoría global, pendientes oráculosC completos fuera4 yfault probes. No demuestra todoslos caminos ni C32bit. Evidencia: openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-counting-integration/README.md. Los apartados anteriores fechados se conservan como historia, no como estado vigente.


### Counting: verificación posterior de oráculos yfallos (2026-10-02)

> Fotografía histórica: las limitaciones y tareas pendientes descritas aquí quedaron sustituidas por los cierres consolidados posteriores; no describen la traza vigente.

La evidenciaLOW posterior completa ocho oráculosC fuera4 yverifica losmáximos mediante digeststreaming con muestras; checksum dearrays/frecuencias tiene límite decolisiones yno acredita todoslosinputs. Fallos de reserva simulada yalmacén devuelven400/estado/historial/mainprevios; un fallo de página noavanza cursor ySiguiente reintenta la misma instrucción. Respuestas detracesanteriores en vuelo no sustituyen unanueva. Counting sigueparcial: la respuesta deerror controlada noexpone todavía su traza didáctica deguardas/retornoC. MEDIUM delimitado en sorting-counting-error-instruction-gap-low.md; evidencia visible-sorting-counting-native-fault-low. Las notas de pendientes anteriores se conservan como fotografía fechada, no estado vigente.


### Counting: inspeccionar una llamada fallida (2026-10-02T19:57:09.908110+00:00)

Si el rango se rechaza, Counting conserva el arreglo aceptado, el historial y el main. La traza permite recorrer la guarda verdadera y el retorno ORDENAMIENTO_ERROR (0), con los parámetros y locales retirados. El aviso identifica que se está viendo una llamada fallida. La exportación JSON separa el estado aceptado del estado de ese intento; navegar o recargar no ejecuta otra llamada.

La reservaNULL de QA usa una inyección aislada y lleva el rótulo «Fallo simulado de calloc»; no representa agotamiento real de memoria. Un fallo del modelo Python se identifica por separado y no afirma ejecutar el allocator C. Los fallos de transporte/almacenamiento de la traza tampoco se presentan como un retorno nativo.

Los caminos/casos de error registrados están verificados; no es certificación exhaustiva de toda entrada, plataforma32bit ni OOMglobal. Evidencia y alcance: openspec/changes/audit-local-quality-and-unified-controls/sorting-counting-error-instructions-checkpoint.md. Los checkpoints anteriores se conservan como fotografías fechadas.


### Counting: revisión consolidada (2026-10-02T20:08:31.886208+00:00)

Counting queda verificado en el dominio UI de1..80 enterosint32 sobre el entorno size_t64 observado: conserva instrucciones para rangos de éxito hasta1000000, con transporte denso o paginado según presupuesto. El corte antiguo de cuatro valores/rango cuatro está retirado. La representación dispersa conserva ceros implícitos y cada control de bucket vacío; el rechazo de rango y la reservaNULL controlada permiten inspeccionar la llamada fallida sin alterar el estado aceptado.

Este fue el noveno cierre finito; los cierres posteriores de Binsort y Radix completan los once métodos bajo casos explícitos. No es prueba exhaustiva de entradas, soporte32bit ni recuperación de OOMglobal; los fallos de reserva usados en QA se identifican como simulados. Decisión y trazabilidad: openspec/changes/audit-local-quality-and-unified-controls/sorting-counting-consolidated-closure-decision.md. Las declaracionesPARCIAL anteriores permanecen como fotografías históricas y quedan superadas por esta revisión.


### Binsort: baseline histórico y frontera inicial (2026-10-02T20:48:10.676126+00:00)

> Fotografía histórica: las limitaciones y tareas pendientes descritas aquí quedaron sustituidas por los cierres consolidados posteriores; no describen la traza vigente.
Binsort en este TAD devuelve el resultado de Counting Sort; no implementa buckets independientes. UI admite 1..80 enterosint32 yhereda rango máximo1000000, con rechazo superior. El baseline confirma resultados y métricasC para ocho entradas, incluidasn80 yrangosmayoresque4. Comparaciones son2(n-1) y movimientos3n; el códigoC del método no imprime mensajes. El main conserva ejecuciones repetidas yexcluye fallos; rápido→pasos conserva la misma traza.
En ese baseline, la traza de Binsort seguía agregada: helper/scopes/guardas/free yretornos completos están pendientes. Tambiénretiene frecuenciasporframe; no se ha certificado una ejecuciónAPIcompleta del límite1m yla correcciónsparse requiereMEDIUM, sinreducireldominio admitido. Cnative límite síverificado ensize_t64seguro. Unfallode reserva del modeloPython se distingue de unfallo realC; QAcallocNULL es inyecciónaislada, noOOMglobal.
Estado:baselineLOWcompleto, Bin/Radixinstrucciónpendiente yCounting9/11vigente. Fuentes: openspec/changes/audit-local-quality-and-unified-controls/sorting-binsort-baseline-checkpoint-low.md ysorting-binsort-instruction-review-plan.md.


### Estado vigente de los once ordenamientos

Los once métodos tienen aceptación finita por instrucción. Counting conserva eventos completos con representación dispersa/paginada para entradas amplias; Binsort reutiliza ese núcleo y muestra su llamada/retorno real; Radix tiene cierre propio. Las fotografías anteriores conservan el recorrido de la auditoría, no tareas vigentes. Véanse `sorting-counting-consolidated-closure-decision.md`, `sorting-binsort-consolidated-closure-decision.md` y `sorting-radix-consolidated-closure-decision.md` en `openspec/changes/audit-local-quality-and-unified-controls`. Cada decisión fija sus casos y límites; ninguna certifica todas las entradas, plataformas o agotamientos de memoria.

## Hash H1: creación e inserción, actualización 2026-10-02

Para estas dos operaciones Hash, este apartado sustituye las indicaciones históricas de 5.1: Ejecutar operación crea una ejecución; Paso a paso permite revisar la misma traza con Paso anterior y Siguiente paso. Cerrar y reactivar el modo, navegar y recargar conservan la ejecución sin enviar otra operación. Reiniciar borra su estado/traza. Cinco secciones organizan los datos, visualización, código, explicación y resultados.

La capacidad es fija y acepta colisiones/carga mayor que1 sin resize. Actualizar una clave conserva cantidad y no reserva un nodo. Las variables tipadas y máscaras muestran los campos aún indeterminados; después de publicar la cabecera puede estar pendiente cantidad++. Las identidades de memoria son simbólicas dentro de la operación.

Descargar main.c reproduce llamadas confirmadas, incluidas repeticiones y consultas registradas en el journal; informa resultados C calculados y libera memoria también ante fallos de reserva. Las operaciones rechazadas no agregan llamadas. La consola de la traza del TAD permanece sin printf porque estas funciones C no imprimen; los mensajes del caller son salida de ese programa independiente. Véase [guía de creación/inserción Hash](qa/hash-creation-insertion-guide.md) para ownership, errores y límites verificados.


## Consultas Hash: checkpoint MEDIUM

Get ausente responde HTTP400; contains ausente retorna false. Las consultas observadas se conservan para main.c en un journal separado del historial mutante. Scopes, salida y replay: [guía de consultas](qa/hash-query-guide.md). Retención y recursos arbitrarios siguen sin certificar.


## Remove Hash: instrucciones y memoria

La traza distingue desvincular, free y cantidad--. Tras free conserva identidad histórica con valor de puntero/campos indeterminados y no utilizables; JSONnull no simula asignaciónNULL de C. Reproducción no vuelve a eliminar. [Guía técnica remove](qa/hash-remove-guide.md), casos finitos/límites; cierre finito LOW registrado en hash-finite-closure-summary-low.md.


### Listados Hash: proyección API y texto C

Las consultas keys/values/items muestran la proyección API por separado del texto de th_formatear. El panel C incluye el helper real, scopes y buffer con bytes indeterminados; retroceder reproduce frames sin enviar otra consulta. Las consultas repetidas quedan en el caller descargado tras recarga. Véase [guía de listados Hash](qa/hash-listings-guide.md) para el alcance finito y las guardas de truncamiento.


### Stats Hash: cálculo C y cociente API

La traza muestra los cuerpos C reales, dos invocaciones y copias distintas de THEstadisticas, y el buffer acotado. El panel separa float C del cociente API existente y de sus formatos; el caller conserva consultas repetidas y calcula ambas representaciones. Véase [guía stats Hash](qa/hash-stats-guide.md) para el alcance registrado y sus límites.


### Hash: vida de memoria al vaciar y destruir

Vaciar conserva capacidad y buckets; destruir libera también ese array, pero el objeto TablaHash sigue vivo. La traza distingue free, puntero indeterminado y escritura NULL; la cantidad sólo cambia al ejecutar su store C. El replay muestra los cinco paneles sin repetir la operación. Véase [guía de vaciado y destrucción](qa/hash-clear-destroy-guide.md) para límites y estados intermedios.


### Rojo-Negro: rango de Insertar y propiedad final del caller

Insertar acepta enteros C de 32 bits, desde `-2147483648` hasta `2147483647`, sin truncarlos. La API rechaza valores fuera de ese rango antes de mutar el árbol, historial o invocar C. El árbol pertenece al caller; al finalizar el programa generado ejecuta `rbt_liberar(arbol); arbol = NULL;` fuera del historial. No se consultan aliases después de liberar.

### Validar Rojo-Negro completo (contrato V3 aprobado, 2026-10-03)

La consulta utiliza `int rbt_validar(RBT raiz)` del TAD descargable y devuelve
1/True sólo si cumple las cinco reglas RN: colores rojo/negro, raíz negra,
hojas conceptuales NULL negras, ausencia de rojo-rojo y altura negra uniforme.
También exige orden ABB estricto sin duplicados, padre de raíz NULL y enlaces
por identidad sin ciclos ni nodos compartidos. Valida el modelo nativo original;
la vista NIL reconstruida es presentación y no corrige ni valida los padres.

NULL es válido y su altura negra interna vale 1. Las cotas opcionales no usan
INT_MIN/INT_MAX como centinelas ni suman/restan uno a las claves. La suma de
altura negra tiene guarda de overflow. Todas las referencias no NULL examinadas
deben ser objetos vivos y legibles: no se inspeccionan punteros colgantes.
El validador no modifica, reserva, libera, imprime ni repara; False/0 es un
resultado de consulta exitosamente ejecutada, no un error HTTP.

El main llama a la función pública y calcula su salida; no la redefine.
Los auxiliares Inorden y Altura siguen perteneciendo a la aplicación/main.
El caller conserva la propiedad del árbol y lo libera fuera del historial.
El rebalanceo puede infringir propiedades temporalmente: las invariantes se
exigen al terminar inserciones/eliminaciones completas desde un árbol válido,
no después de una rotación aislada. La traza muestra los frames nativos,
cotas, padre esperado, alturas de hijos y retornos sin fabricar mutaciones.


### Cola: Encolar por instrucción

Encolar sigue `cola_encolar(struct Cola *q, int valor)`: `q` recibe la dirección de la cola del llamador. La reserva `malloc` se muestra como una llamada opaca; el nodo temporal conserva su identidad al enlazarse. Los campos `nro` y `sgte` aparecen indeterminados hasta sus escrituras, con máscaras 0, 1 y 3. En una cola vacía se actualiza primero `delante`; en una no vacía se enlaza desde el anterior `atras`. Después se actualiza `atras`. El retorno void termina el ámbito local de `aux`, conservando los extremos y nodos del llamador.

Las dos vistas permiten recorrer y retroceder la misma traza. Recargar conserva la última traza de Encolar compatible con el historial, el valor y el cursor; Siguiente continúa sin volver a encolar. Una operación posterior exitosa o Reiniciar invalida esa traza preparada. Los fallos controlados de reserva y argumento nulo pertenecen a QA privada, sin controles adicionales en la interfaz. El programa `main` de Cola se muestra en el historial; la ruta HTTP de descarga `queue/main` sigue sin estar disponible.


### Cola de prioridad: Encolar por instrucción

Encolar sigue `cp_encolar` y su llamada a `cp_crear_nodo`. Los dos locales llamados `nuevo` pertenecen a ámbitos distintos. El local del parent permanece indeterminado hasta recibir el retorno del helper. `malloc` se presenta como llamada opaca; el objeto reservado adquiere sus campos `valor`, `prioridad` y `sgte` en ese orden, con máscaras 0, 1, 3 y 7. El mismo objeto se publica sin duplicarlo. `cantidad++` sólo modifica el contador; no libera memoria. El retorno bool termina el ámbito local y conserva nodos, extremos y contador del llamador.

La lista conserva el orden de llegada. La selección usa la menor prioridad y el primer nodo en caso de empate. Ambas vistas recorren la misma traza. Recargar restaura la última traza compatible con historial y fuente C, entradas de valor/prioridad, cursor y modo paso a paso. Siguiente continúa sin volver a encolar. Entrada inválida conserva la traza preparada; otra operación exitosa o Reiniciar la invalidan. El C retorna NULL/false silenciosamente ante fallos de reserva/argumento; el main del historial comprueba el resultado y escribe su diagnóstico sin anunciar éxito. Las pruebas de fallos controlados son privadas. El main de Prioridad se muestra en el historial; su ruta de descarga HTTP continúa sin estar disponible.


### Cola: Desencolar por instrucción

`cola_desencolar(struct Cola *q)` devuelve un `int`; no tiene parámetro de salida. El valor -1 puede ser un dato real o el retorno de error: compruebe el estado de la cola antes de extraer. Ante q NULL o cola vacía, C imprime su diagnóstico y retorna -1 sin cambiar enlaces; la API distingue ese fallo de una extracción exitosa de -1.

En paso a paso, `aux` conserva la identidad del primer nodo y `num` copia `nro` antes de `free`. Cambiar `delante` separa el nodo pero no lo libera; `atras` pasa a NULL sólo al retirar el último. Después de free, los aliases al nodo son inutilizables y sus campos sólo aparecen como registro histórico capturado antes de liberar. El retorno entrega la copia int y termina el scope local; el objeto Cola del caller y los nodos restantes siguen vivos.

Ambas vistas muestran los mismos eventos. La recarga conserva la última traza C completada, incluida la guarda de vacío, su modo y cursor; Siguiente no envía otra operación. Los errores de entrada que no ejecutaron C conservan la traza previa. Una operación exitosa posterior o Reset invalida este registro. La reconstrucción interna ordinaria del historial se mantiene. El main mostrado calcula la salida usando C y libera su propiedad al terminar.

La verificación usa casos finitos; no garantiza consumo para cualquier longitud de cola o historial, OOM real ni ausencia universal de fugas.


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

Dictamen y evidencia: [revisión independiente Graph](../openspec/changes/audit-local-quality-and-unified-controls/evidence/independent-review-graph-three-approved-adjustments/review.md), [precisión documental consolidada](../openspec/changes/audit-local-quality-and-unified-controls/graph-qa-documentary-consolidation-addendum-low.md).


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
