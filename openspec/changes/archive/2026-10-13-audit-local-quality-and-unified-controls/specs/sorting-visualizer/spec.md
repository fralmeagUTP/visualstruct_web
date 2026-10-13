## ADDED Requirements

### Requirement: Main reproducible de Ordenamientos integrado
El sistema SHALL mostrar en el historial de la quinta seccion un main C17 generado desde operaciones aceptadas y conservar las cinco secciones y botones existentes. SHALL entregar los mismos bytes por /help/source/sorting_array/main. La exportacion JSON existente SHALL incluir el main.

#### Scenario: Repeticion y recarga
- **GIVEN** creacion manual, metodo seleccionado y dos runs exitosos iguales
- **WHEN** se recarga o navega la traza y se descarga main.c
- **THEN** conserva dos llamadas cronologicas al metodo C real, no ejecuta otra operacion y su salida nativa coincide con los estados aceptados

#### Scenario: Datos aleatorios y fallo excluido
- **GIVEN** un arreglo generado y un run aceptado, seguido de una validacion fallida
- **WHEN** se reconstruye o descarga el programa
- **THEN** conserva los valores materializados sin randC/nuevo sorteo, omite la operacion fallida y conserva las ejecuciones anteriores

#### Scenario: Firmas y ownership
- **GIVEN** cualquiera de los once metodos y datos int32 dentro de 1..80 elementos y dominio especifico del metodo
- **WHEN** se compila el main con los C/H HTTP
- **THEN** respeta siete retornos void y cuatro int, verifica ORDENAMIENTO_OK donde aplica, imprime resultados calculados por C, mantiene arreglo automatico y el TAD libera sus auxiliares; Doxygen no emite advertencias

#### Scenario: Datos preparados y limites
- **GIVEN** un metodo seleccionado sin run, o un arreglo rechazado por tamano/int/rango
- **WHEN** se muestra el programa
- **THEN** seleccion sin ejecucion queda como comentario, no inventa una llamada exitosa, no escribe fuera de arreglo[80] y no incorpora fallos al historial


### Requirement: Counting exacto con transporte acotado
El sistema SHALL conservar dominio1..80/int32/rango<=1000000 yuna misma semánticaCounting por instrucción para transporte denso o paginado, sin corte de fixtures ni fallback agregado. SHALL conservar todoslos eventos lógicos,scopes/locals/alias/condiciones/source yfree; las frecuenciascalloc no escritas SHALL representar cero implícito exacto. Los controles de otras rutas SHALL conservar su contrato.

#### Scenario: Entrada admitida amplia
- **GIVEN** Counting con más de4valores o rango mayor que4, incluido n80/rango1000000
- **WHEN** se ejecuta
- **THEN** resultado,métricas e historial corresponden a una ejecución, el contador conserva todoslos eventos yHTTP/DOM no materializan un arreglo de frecuencias por cada evento

#### Scenario: Lectura y navegación no mutantes
- **GIVEN** una traza paginada inmutable de sesión disponible
- **WHEN** se consulta página,next/prev/seek/replay/export o se recarga
- **THEN** se decodifica la misma ejecución sin redispatch,nuevohistorial/llamadaC yse descartan respuestas obsoletas al cambiar cursor/traza

#### Scenario: Buckets y exportación
- **GIVEN** una reserva de frecuencias grande viva o posteriormente liberada
- **WHEN** se consulta un índice real oexportaJSON
- **THEN** ventana64permite acceso exacto aceros/buckets ocupados;free retira vida sinlectura yJSON conserva recordscompactos/main/cursor sin enumerar millonesdepasos

#### Scenario: Ownership y almacenamiento local
- **GIVEN** referencias de trazas con sesión,TTL15min ypresupuesto local32trazas/128MiBcontabilizados
- **WHEN** otra sesiónconsulta,o una referencia expira/seevicta/resetea
- **THEN** se informa404/410 sinre-sort ni cambio dehistorial;una consultaGET no renuevaTTL ni mutaestado semántico


### Requirement: Counting errores por instrucción sin operación aceptada
El sistema SHALL devolver HTTP400/success=false ante una guarda Counting rechazada o reserva del modelo fallida, conservando estado aceptado completo, historial y main. SHALL entregar una traza parcial tipada con la guarda causal, retorno ORDENAMIENTO_ERROR (0) en su línea C y retiro de scopes/pila; SHALL distinguir estado de intento y estado aceptado. La traza SHALL marcarse mutates=false. Leer páginas/exportar/reproducir/recargar SHALL reutilizar evidencia inmutable, sin redispatch ni llamada aceptada adicional.

#### Scenario: Rango rechazado
- **GIVEN** entrada int32 de 1..80 valores con rango mayor que1000000 bajo size_t64
- **WHEN** Counting evalúa el límite
- **THEN** conserva el cortocircuito sin evaluar SIZE_MAX, muestra range_guard=true y return ERROR con locales retirados, sin reservar/liberar memoria ni incorporar run al main/historial

#### Scenario: Reserva NULL de QA aislada
- **GIVEN** app TESTING con allocator privado que eleva SimulatedCountingAllocationFailure
- **WHEN** se ejecuta Counting
- **THEN** count_init muestra conteo=NULL inicializado, allocation_guard=true y retornoERROR con cero alloc/free/vivos; UI/export rotulan simulación y real_c_execution=false; ningún campo público habilita esa inyección en producción

#### Scenario: Modelo y transporte diferenciados
- **GIVEN** MemoryError del modelo Python o rechazo del almacén local de trazas
- **WHEN** se informa el fallo
- **THEN** el primero se identifica como fallo del modelo y ruta C equivalente, no como ejecución real del allocator C; el rechazo de transporte no fabrica un retorno nativo ERROR ni traza de fallo C


### Requirement: Binsort fiel como wrapper de Counting
El sistema SHALL conservar el dominio UI1..80/int32 y éxito k<=1000000 bajo size_t64, componiendo entrada, expresión de llamada, eventos exactos del delegado y retorno Bin. SHALL mantener arreglo/n de Bin suspendidos durante el callee y retirar sus scopes sólo en su propio retorno, sin variables del observador C ni consola ficticia. Dense y paged SHALL representar el mismo tape y los tramos vacíos todos sus controles exactos, sin fallback por fixtures. Los contratos de los nueve métodos previamente verificados SHALL permanecer.

#### Scenario: Delegación y replay
- **GIVEN** una aceptación Binsort incluida n80/rango1000000
- **WHEN** se navega /step,pages,seek,replay,GET/reload o exporta
- **THEN** conserva identidad Bin y alias del mismo arreglo, no redispatch ni run/llamadaC adicional, y usa almacenamiento/ownership/TTL/páginas/DOM acotados del codec compartido; sin traza no ejecuta por navegar

#### Scenario: Error del delegado
- **GIVEN** guarda de rango, NULL de QA aislada o fallo de modelo
- **WHEN** el delegado retorna ERROR equivalente
- **THEN** Bin conserva sus parámetros hasta retornar0 en return ordenar_counting_sort(...), muestra intento no mutante y conserva estado aceptado completo/main/historial; simulación TESTING y fallo de modelo se distinguen de ejecución C real y rechazo de transporte


### Requirement: Radix preserva instrucciones, scopes y memoria de magnitudes
El sistema SHALL conservar C/H y dominioUI1..80/int32 mediante magnitudes uint32_t y guardas existentes exp/INT_MIN. SHALL presentar sentencias/controles/declaraciones/retornos del wrapper y helper, caller suspendido y callee real, locales según alcance/initialized, alias/reservas y anteriores sin leer celdas indeterminadas/liberadas. Comparisons mide max_value_comparisons y moves escrituras work/count/digit_output/caller; guardas/reservas separadas. Consola vacía para C sin printf.

#### Scenario: Éxito y transporte
- **GIVEN** entrada Radix admitida incluidos80extremosint32
- **WHEN** se ejecuta y navega dense/paged/step/GET/reload/export
- **THEN** conserva todos los eventos C-equivalentes y líneas reales con checkpoints128/deltas/páginas<=128/ownership/TTL, sin redispatch ni nuevo historial por navegar

#### Scenario: Error y aceptación
- **GIVEN** allocator privadoTESTING simulandoNULL, MemoryError externo del modelo o rechazo store
- **WHEN** se informa error
- **THEN** responde400 conservando estado/main/historial aceptado; simulación muestra cleanup/retornoERROR equivalente sin afirmar allocatorC real; MemoryError externo no fabrica retornoC y store se informa separado

#### Scenario: Presupuesto histórico pendiente
- **GIVEN** gate histórico len(steps)<5000 y11408eventos C completos del mismo input
- **WHEN** se revisa evidencia
- **THEN** conserva prueba/IDs y rojo explícito hasta decisión, sin omitir instrucciones/xfail/denominadores falsos ni cerrar método

### Requirement: Explicit complete supported C before sorting execution
For a mapped algorithm the adapter SHALL require an explicitly supplied complete teaching C snippet containing the current approved algorithm and reachable helpers. Missing, null, blank, incomplete or explicitly unsupported empty-function source SHALL fail clearly before SortingInterpreter construction/execution, C events, allocation, mutation or successful history. No absent input SHALL be replaced by canonical C or pseudocode. The canonical mapping MAY be read only to compare supplied required function bodies. This is not an arbitrary C interpreter/compiler; it verifies the supported teaching snippets. Leading indentation, blank lines and comments that preserve the native instruction layout SHALL NOT change approval. Existing line localizers require the supported native statement layout; unsupported formatting SHALL fail before execution rather than execute and then fabricate source mappings. Algorithms, C events and timing policy SHALL remain unchanged.

#### Scenario: Missing or explicitly empty body
- GIVEN a valid array and mapped algorithm
- WHEN source is omitted, null, whitespace or an empty/unsupported body
- THEN a clear controlled source error occurs before any interpreter is constructed
- AND accepted state, result, trace and history remain unchanged

#### Scenario: Legitimate full C consumers
- GIVEN explicit current C for the algorithm and its required helpers
- WHEN fast or step mode runs
- THEN the existing algorithm executes with that actual supplied source
- AND all correctness, source and event assertions remain applicable

#### Scenario: Canonical provider failure
- GIVEN a persisted valid array and missing/empty canonical C provider
- WHEN the public service attempts run
- THEN HTTP400 and successFalse report source failure
- AND no successful run history, C events or fabricated result is persisted

#### Scenario: Previous accepted operation
- GIVEN a previous accepted result and trace
- WHEN the next source is invalid
- THEN previous array, result and trace remain unchanged
- AND no new interpreter or execution events are created

#### Scenario: Preprocessing is outside supported teaching snippets
- **GIVEN** a native sorting snippet that requires no preprocessing
- **WHEN** supplied source contains a preprocessing directive, including conditional inclusion, macros, digraph/trigraph spellings or escaped-newline continuations
- **THEN** admission SHALL reject it explicitly before interpreter construction, events, state changes or successful history
- **AND** the application SHALL NOT claim arbitrary C preprocessing support; valid general C programs requiring preprocessing are outside this supported subset
- **AND** directive text appearing only in comments SHALL NOT be treated as active preprocessing
