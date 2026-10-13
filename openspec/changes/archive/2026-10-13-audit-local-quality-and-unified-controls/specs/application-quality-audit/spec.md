## ADDED Requirements

### Requirement: Sincronía educativa por instrucción en Visualizar y ejecutar
La sección 2 MUST explicar cada instrucción C ejecutada con línea/función, evento real, estado antes/después, consola y representación sincronizados. Resaltado MUST significar instrucción justo ejecutada y vista posterior; frame inicial indica antes de ejecutar. Auditar matriz TAD/operación/vista individual o enlazada/dirección adelante o atrás, justificando no aplicables.
#### Scenario: Reserva y cambio de enlace
- **GIVEN** operación con malloc, asignación de punteros y free aplicables
- **WHEN** se navega cada instrucción en las vistas disponibles
- **THEN** aparecen exactamente sus efectos causales, identidad/enlaces previos/posteriores; ningún nodo o liberación futura se anticipa.
#### Scenario: Instrucción sin mutación estructural
- **GIVEN** condición, iteración, consulta, llamada o retorno sin cambio estructural
- **WHEN** se muestra su frame
- **THEN** se explica el efecto lógico y conserva estado correcto sin fabricar mutación; rama/iteración/pila de llamadas corresponden al C ejecutado.
#### Scenario: Retroceso exacto y consola
- **GIVEN** traza con printf y mutaciones intermedias
- **WHEN** se avanza y retrocede por la misma instrucción en vista individual y enlazada
- **THEN** línea, variables, punteros, estado, consola y explicación restauran exactamente ese frame, sin datos futuros ni operación mutante.

#### Scenario: Resultado de consulta sin anticipación
- **GIVEN** consulta reproducida por pasos y un mensaje de resultado final calculado por el backend
- **WHEN** la reproducción está en el estado inicial, incompleta o retrocede desde su final
- **THEN** la interfaz SHALL indicar resultado pendiente, sin anunciar el resultado futuro; al completar muestra el mensaje real, y cambiar de modo no ejecuta otra operación.

### Requirement: Aprobación antes de ejecución
El trabajo MUST limitarse a lectura y borrador hasta aprobación explícita.
#### Scenario: Borrador pendiente
- **GIVEN** esta propuesta sin aprobar
- **WHEN** se prepara la revisión
- **THEN** no se inicia preview, validación funcional ni cambios UI/código.

### Requirement: Inventario y evidencia completa
La auditoría MUST registrar cada opción real y enlazar requisito, caso, revisión, entorno, resultado esperado/observado y evidencia. Estados: no ejecutado, aprobado, fallido, bloqueado o no aplicable justificado.
#### Scenario: Opción sin prueba existente
- **WHEN** aparece una operación no cubierta en inventario
- **THEN** obtiene caso explícito o límite documentado; una suite verde no la aprueba automáticamente.

### Requirement: Fidelidad causal del C
La auditoría MUST contrastar fuentes C ejecutadas con Python, traza, línea/función activa, consola y estado visual en cada evento relevante; separar C real de fallback y entradas fuera del dominio definido.
#### Scenario: Mutación con rama y memoria
- **GIVEN** casos vacío, unitario, duplicados, valores límite y fallo de reserva aplicables
- **WHEN** se ejecutan con harness instrumentado y navegador
- **THEN** se cotejan ramas/iteraciones, asignaciones, punteros/alias, malloc/free, recursión, invariantes y estados intermedios; no se acepta solo igualdad final ni se inventa comportamiento para UB.

#### Scenario: Equivalencia con ejecución C nativa
- **GIVEN** los mismos datos, secuencia de operaciones y condiciones definidas de memoria en C y aplicación
- **WHEN** se compila y ejecuta nativamente el C canónico descargado con harness instrumentado
- **THEN** resultados, retornos, errores, salida de consola, estados finales e intermedios y eventos de control/memoria de la aplicación MUST coincidir con el C nativo; diferencias justificadas de presentación se documentan sin cambiar semántica, y entradas con comportamiento indefinido se identifican sin inventar equivalencia.
### Requirement: Documentación del artefacto entregado
Cada C/H descargable y guía MUST auditarse desde su salida efectiva, no solo desde fuentes del repositorio.
#### Scenario: Descargar TAD desde ayuda
- **WHEN** se descarga source/header por `/help/source/<structure_id>/<file_kind>` según blueprint real
- **THEN** se registran URL real, status, nombre, tipo, tamaño, hash y bytes; se compilan juntos con harness y se genera Doxygen del conjunto recibido.
#### Scenario: Documentación incompleta o falsa
- **WHEN** se revisa un símbolo público o método
- **THEN** se comprueban propósito, parámetros, retornos, pre/postcondiciones, propiedad de memoria, errores y complejidad cuando aplica; advertencias y falsedades se registran incluso si Doxygen genera HTML.
#### Scenario: Manual y guía coherentes
- **WHEN** se compara la guía con UI y C descargado
- **THEN** nombres, preparación, controles, ejemplos compilables, tipos, restricciones y memoria coinciden; cada omisión tiene localización y corrección propuesta.

### Requirement: Hallazgos y cierre verificable
Cada hallazgo MUST incluir ID, severidad, reproducción, esperado/observado, evidencia, impacto, requisito, archivo/línea, causa confirmada o hipótesis, acción y prueba final. Crítico: corrupción/semántica central falsa; alto: función principal incorrecta; medio: función parcial/documentación/UI relevante; bajo: presentación menor.
#### Scenario: Herramienta no disponible
- **WHEN** navegador, compilador, sanitizador o Doxygen no puede ejecutarse
- **THEN** se declara bloqueado y se especifica verificación pendiente; no se presenta lectura estática como validación dinámica.

### Requirement: Reconciliación histórica explícita
La propuesta MUST revisar cambios abiertos y archivados y specs actuales sin reabrir automáticamente lo completado.
#### Scenario: Compromiso antiguo incompatible
- **WHEN** una spec conserva botones ahora sustituidos
- **THEN** se propone delta completo y se preserva su contrato semántico; las tareas incompletas quedan rastreadas, no aprobadas por estar archivadas.


## ADDED Requirements

### Requirement: BFS admite identificadores enteros negativos
El C descargable SHALL tratar -1 como identificador válido cuando la guarda de cola no vacía permite extraerlo; la cola vacía SHALL conservar su contrato de error.

#### Scenario: Vértice -1 inicial o alcanzado
- **WHEN** BFS recorre -1 hacia 2, 1 hacia -1, o un autobucle -1
- **THEN** C nativo y backend coinciden en [-1,2], [1,-1] o [-1], respectivamente
- **AND** el control positivo 1 hacia 2 conserva [1,2]

#### Scenario: Cola vacía y origen inexistente
- **WHEN** se extrae de una cola vacía o se solicita BFS de un origen inexistente
- **THEN** permanecen el retorno -1/diagnóstico de cola y el retorno NULL de BFS, respectivamente


## ADDED Requirements

### Requirement: Depuración por dependencia y contrato vigente
La auditoría SHALL identificar raíces de uso en interfaz visible, API vigente, servicios, C/H descargables y sus dependencias antes de eliminar código. Un método oculto SHALL NOT considerarse sin uso únicamente por estar oculto. El código demostrado sin uso ni obligación vigente SHALL retirarse; una ruptura de API contractual ambigua SHALL consultarse antes de aplicarla.

#### Scenario: Inversión legacy de Lista enlazada rechazada
- **GIVEN** invertir está oculto, no es dependencia de los siete métodos visibles y el usuario autoriza retirarlo expresamente
- **WHEN** se depura Lista enlazada
- **THEN** lista_invertir y su declaración, wrapper, operación/API, mapa y renderer específico se retiran
- **AND** no se añade ni revela Invertir en el menú
- **AND** invertir de Lista circular y los helpers necesarios para otras operaciones permanecen intactos

#### Scenario: Helper interno necesario o API ambigua
- **WHEN** una función es llamada por una operación requerida o permanece en un contrato API cuya eliminación no está decidida
- **THEN** se conserva con su dependencia documentada o decisión pendiente, sin borrar por conteo de botones ni por hidden

### Requirement: C y H descargados por estudiantes reflejan métodos requeridos
Los archivos C/H entregados por HTTP SHALL contener operaciones del contrato vigente y dependencias necesarias, SHALL excluir lista_invertir retirada por decisión del usuario y SHALL compilar con firmas coherentes. Doxygen y manual SHALL describir el contrato actual. La depuración SHALL conservar paridad semántica de los métodos restantes y pruebas significativas.

#### Scenario: Descarga real después de retirar inversión
- **WHEN** un estudiante descarga fuente y cabecera de Lista enlazada
- **THEN** ambos archivos carecen de lista_invertir
- **AND** los siete métodos visibles permanecen documentados y compilables
- **AND** sus operaciones y errores conservan estado, enlaces y comportamiento esperado

#### Scenario: Evidencia histórica y conteo de operaciones
- **WHEN** se actualiza inventario después de depuración
- **THEN** se distinguen operaciones ofrecidas por UI, APIs ocultas e internals, sin presentar el total de metadata como opciones visibles
- **AND** evidencia histórica se conserva marcada como alcance retirado, sin simular cobertura actual de funciones eliminadas


### Requirement: Historial C conserva operaciones reales repetidas
El sistema SHALL conservar en el main de ejemplo cada operación real ejecutada con éxito, aunque sus datos coincidan con la operación anterior. Los eventos UI duplicados durante una petición pendiente SHALL producir una sola operación; avanzar, retroceder y recargar SHALL conservar cardinalidad sin ejecutar otra operación.

#### Scenario: Dos inserciones válidas iguales
- **GIVEN** dos inserciones consecutivas del entero7 en Lista o Circular
- **WHEN** se copia el main antes y después de recargar y se compila con el C/H descargado
- **THEN** existen dos llamadas de inserción y el programa reproduce ambos nodos7

#### Scenario: Eventos de ejecución concurrentes
- **GIVEN** una petición de Ejecutar operación pendiente
- **WHEN** llega un evento UI repetido antes de terminar esa petición
- **THEN** se envía una sola operación, y una ejecución posterior terminada conserva su propio registro aunque repita los datos


#### Scenario: Consultas exitosas conservadas en el main tras recargar
- **GIVEN** búsquedas exitosas repetidas o sin coincidencias en Lista o Circular
- **WHEN** el estudiante recarga y copia el main con los C/H descargados
- **THEN** conserva cada búsqueda en orden, las llamadas tienen la firma C real y compilan; reconstruir el estado no reejecuta las consultas históricas
- **AND** una consulta fallida no agrega entradas y eventos UI duplicados durante una petición pendiente no duplican operaciones


#### Scenario: Consulta Sublista en límite de copia real
- **GIVEN** una rama con1025hijos y límite existente de1024copias de la aplicación
- **WHEN** el estudiante consulta y ejecuta el main generado con C/H descargados
- **THEN** ambos resultados contienen los mismos1024valores y permanecen1025hijos en la estructura
- **AND** la guía diferencia límite de la aplicación y capacidad del TAD C público

#### Scenario: Listar rama vacía en Sublista
- **GIVEN** un padre válido sin hijos y destino/capacidad válidos
- **WHEN** se representa la consulta instrucción por instrucción
- **THEN** se asigna actual=NULL, se evalúa whilefalse y se retorna usados=0, sin inventar un retorno temprano de la guarda


### Requirement: Main ABB reproduce Contar hojas con auxiliar canónico
El sistema SHALL integrar una sola definición del auxiliar canónico mostrado de Contar hojas antes del main cuando el historial exitoso lo requiera, SHALL llamar abb_contarHojas e imprimir su resultado calculado, y SHALL mantener C/H públicos intactos bajo la solución compatible autorizada. Guía y Doxygen SHALL distinguir este auxiliar del contrato público descargado. Esta colocación complementaria explícita aplica a Hojas ABB; no autoriza cambios en Validar ni permite sustituir otros métodos por cálculos diferentes.

#### Scenario: Hojas difiere de niveles
- **GIVEN** un ABB equilibrado de siete nodos con cuatro hojas y tres niveles
- **WHEN** el estudiante compila el main realmente mostrado junto al C/H realmente descargado
- **THEN** obtiene cuatro hojas mediante abb_contarHojas, sin sustituirlo por abb_contarNiveles ni imprimir una respuesta web como prueba del cálculo C
- **AND** el helper aparece una sola vez con documentación correcta y no altera el algoritmo ni los enlaces

#### Scenario: Vacío y consultas repetidas tras recargar
- **WHEN** Contar hojas se ejecuta exitosamente varias veces, incluso en árbol vacío, y se recarga
- **THEN** cada consulta permanece en orden en el main y produce el conteo esperado, con una única definición del auxiliar
- **AND** reconstruir la sesión no reejecuta esas consultas y una operación fallida conserva su error sin convertirse en una llamada ejecutable del main


### Requirement: Main AVL reproduce consultas exitosas con auxiliares canónicos
El sistema SHALL conservar en orden las consultas AVL exitosas y repetidas, SHALL generar llamadas y salidas calculadas por C para Buscar, Mínimo, Máximo, Altura, Inorden y el auxiliar mostrado de equilibrio por alturas, y SHALL integrar una sola definición de cada auxiliar mostrado que no pertenece al C/H público cuando lo requiera ese main. SHALL mantener los C/H y algoritmos de rotación sin cambios bajo esta reparación compatible de reproducción. SHALL documentar la propiedad del auxiliar y no presentar resultados copiados de la web como cálculos nativos. SHALL conservar rechazos sin ejecutar sus llamadas, normalizar enteros decimales representables en C y reconstruir la sesión sin reejecutar consultas.

#### Scenario: Consultas repetidas conservadas al recargar
- **GIVEN** dos consultas AVL idénticas y exitosas, intercaladas o adyacentes a otras operaciones
- **WHEN** el usuario recarga y compila el main realmente generado con los archivos realmente descargados
- **THEN** ambas consultas permanecen en orden y sus resultados se calculan en C, usando una sola definición por auxiliar requerido
- **AND** GET/reconstrucción no despacha otra vez las consultas ni provoca POST adicional

#### Scenario: Inorden no es la visualización textual rotada
- **GIVEN** los valores 10, 5 y 15
- **WHEN** el estudiante ejecuta el main de una consulta Inorden
- **THEN** obtiene 5, 10 y 15 mediante avl_inorden, sin sustituirla por avl_verArbol ni usar un printf del resultado web como oráculo

#### Scenario: Errores y valores con ceros iniciales
- **WHEN** Mínimo/Máximo en vacío o una operación inválida es rechazada
- **THEN** el main anota el rechazo sin ejecutar su llamada ni infringir la precondición no-NULL de avl_minimo
- **AND** un valor decimal exitoso como 08 se genera como 8, y las variables de consultas se consumen para compilar sin warnings con las opciones acordadas

#### Scenario: Validación auxiliar tiene alcance preciso
- **WHEN** el main usa el auxiliar canónico avl_validar_fes mostrado por la aplicación
- **THEN** la salida y la documentación identifican equilibrio por alturas y no lo presentan como certificación del FE almacenado
- **AND** esta reparación no resuelve la decisión semántica pendiente de rotaciones AVL ni Validar ABB


### Requirement: Heap full-copy downloadable caller and successful consultation history
The application SHALL show and generate a heap-copy caller that copies the current complete internal array, owns/releases its destination and does not silently truncate at a fixed pedagogical capacity. Successful repeated heap consultations SHALL remain in executable history across reload without redispatch during state restoration. The caller SHALL report native computed query values and preserve decimal typed integer semantics.

#### Scenario: Copy exceeds the former fixed destination
- **WHEN** Ver arreglo is generated with 255,256,257 or513 current values
- **THEN** displayed/generated C copies all values in internal heap order, compiles with actual downloaded C/H and frees the independent destination
- **AND** an empty copy uses no zero-length array or positive allocation

#### Scenario: Caller copy allocation fails
- **WHEN** the positive-size destination cannot be allocated
- **THEN** generated main destroys its heap and returns failure without a partial copy output

#### Scenario: Repeated consultations survive reload
- **WHEN** successful Raiz and Ver arreglo consultations repeat and the page reloads
- **THEN** executable successful history preserves their order/count and computed native outputs
- **AND** restoring the state does not redispatch consultations or send replay POST requests
- **AND** failed local annotations are excluded from executable native calls


### Requirement: AVL helper validation contract remains distinct from backend metadata
The application SHALL label the shown AVL validation helper result as equilibrium by calculated heights, independently of backend ordering-and-equilibrium metadata, and SHALL document a selected legal operand evaluation order without claiming C mandates it.

#### Scenario: Balanced topology violates ordering
- **WHEN** an isolated finite balanced topology violates BST ordering
- **THEN** the shown height-only helper result may be 1 while backend metadata is false, and each result is labeled with its actual contract without changing either algorithm

#### Scenario: Recursive validation replay
- **WHEN** the student advances or rewinds the AVL validator
- **THEN** the shown helper and nested-height frames, initialized locals, source boundary and return result agree with native observations, nodes remain unchanged, and future caller results are hidden until return


### Requirement: AVL insertion teaches actual transient allocation and rotation states
The application SHALL preserve the executed insertion and rotation statement boundaries, stable reservation identities, initialized-field states and actual parent/child/FE values in the available visualization and memory views, without certifying transient graphs as valid AVL or converting a void C call into a native success result.

#### Scenario: Partially initialized allocation and rotation publication
- **WHEN** the student advances or rewinds a successful AVL insertion through allocation, initialization or a simple/double rotation
- **THEN** all live reservations, including temporarily detached fragments, retain their identities and show only fields already initialized by the corresponding C instruction, with the actual nested scopes and highlighted source boundary

#### Scenario: Stable generated history after reload
- **WHEN** a successful AVL insertion history is downloaded before and after page reload
- **THEN** its C invocations and deterministic invocation output remain identical, without replaying requests or claiming that avl_insertar returned a success status


### Requirement: AVL deletion preserves actual reservation lifetimes and rejection boundaries
The application SHALL represent the actual AVL deletion value exchange, physical successor release, partial link publication, lexical scopes and nested calls without fabricating native execution for application-rejected operations.

#### Scenario: Two-child deletion and rewind
- **WHEN** a successful two-child deletion advances or rewinds across value exchange, unlink and free
- **THEN** the found reservation retains its identity, only the actual physical successor is retired, cached aliases are marked unusable and replay performs no mutation request

#### Scenario: Application rejection before native invocation
- **WHEN** an empty-tree or absent-value deletion is rejected by the application
- **THEN** the trace explains the application precondition, preserves state and history and shows no executed native call, allocation, free or printf


### Requirement: Rojo-negro query history computes the actual visible consultation contract
The application SHALL reproduce successful visible Inorden, Altura and Validar consultations through canonical documented C functions and main helpers using the actual downloaded structure fields, preserve repetitions across reload without reexecuting queries, and distinguish the implemented validator checks from unimplemented invariants.

#### Scenario: Repeated consultations and reload
- **WHEN** the student repeats a successful consultation before or after clearing or reloading the tree
- **THEN** each successful invocation remains in the executable history, C computes its result, reload performs no query execution and the actual main compiles with the downloaded C/H

#### Scenario: Validator scope and rejected deletion
- **WHEN** the student reads the validator or downloads a history containing an application-rejected absent deletion
- **THEN** the guide identifies the approved complete rbt_validar contract (five RN rules, strict order, parent identity and finite live-object cycles/shared links), preserves its live-reference and finite-evidence limits, and the rejected deletion is not fabricated as an executed successful C call


### Requirement: Rojo-negro queries preserve actual instruction and caller boundaries
The application SHALL synchronize Inorden, Altura, Validar and Buscar with the actual shown C event boundary, recursive scopes, native return kind and printf sequence in both available tree-link and individual-reservation representations, without leaking pending caller results or mutating during replay.

#### Scenario: Recursive query and bidirectional replay
- **WHEN** a student advances or rewinds across recursive call entry, completion or return
- **THEN** the highlighted line identifies that just-reached event, suspended and terminated scopes are distinguished, typed locals and aliases match native execution, output includes only executed printf and replay performs no mutation request

#### Scenario: Limited validator and skipped operands
- **WHEN** a root-color, order or red-red condition rejects a test-only tree or a left recursive validation operand returns zero
- **THEN** the corresponding right call is omitted by short circuit and the caller result is exposed only at return; intermediate rebalance states are not certified as stable valid RN, while an explicit completed validation uses the approved exported rbt_validar contract


### Requirement: Rojo-negro cleanup history preserves ownership and real repeated invocations
The application SHALL preserve each requested successful cleanup in executable history, distinguish postorder reservation release from the caller's separate root overwrite, and document the by-value native ownership contract without treating conceptual NULL leaves as allocated NIL objects.

#### Scenario: Cleanup repeated after root overwrite
- **WHEN** a student requests cleanup twice and reloads the history
- **THEN** both C calls remain in the main, each is followed by the caller-side NULL assignment, reload adds no request and native execution releases each original reservation exactly once

#### Scenario: Native lifetime projection remains pending until verified
- **WHEN** cleanup instruction fidelity is audited
- **THEN** native cached identities, recursive scopes and unusable references are compared independently, and successful empty endpoints or zero Doxygen warnings alone do not close instruction visualization coverage


### Requirement: Rojo-negro insertion preserves the supported signed C int domain
The application SHALL accept Insertar values only in the supported 32-bit signed C int range [-2147483648,2147483647], reject other integers explicitly before mutation or history persistence, and never silently truncate or animate an unexecuted C call.

#### Scenario: Exact bounds and explicit rejection
- **WHEN** a student inserts either bound or submits an integer immediately outside it
- **THEN** each bound is retained exactly; an outside value leaves the tree and successful history unchanged, displays the range error and records application rejection without malloc, writes, printf or TAD return

#### Scenario: Reconstruction cannot turn invalid old input into executable C
- **WHEN** stored history contains an out-of-range insertion
- **THEN** reconstruction excludes that invalid operation without truncating it, preserves the valid operations and does not redispatch preserved pure consultations

### Requirement: Actual Rojo-negro main releases owned reserves outside student history
The generated main SHALL preserve the student's successful operations and stdout, then execute rbt_liberar(arbol) and assign NULL to the caller root before exit. This final resource cleanup SHALL be documented as caller responsibility, not as an additional student operation, and verified against the actual HTTP-downloaded C/H.

#### Scenario: Populated, empty and repeated cleanup histories
- **WHEN** a main is generated before or after reload for a populated or empty tree, including repeated cleanup and subsequent insertion
- **THEN** the successful operation sequence remains identical; the final caller cleanup adds no printf or history entry, each allocated reserve is freed exactly once and no live reserve remains at exit in the observed programs

#### Scenario: Final generated program remains reviewable
- **WHEN** the actual displayed main is compiled with the downloaded C/H
- **THEN** it passes strict C17 and Doxygen checks, its output matches the recorded successful operations and ownership is measured with an independent allocation/free observer rather than inferred from compilation


### Requirement: Rojo-negro deletion preserves its documented native lifetime and rejection contract
The audit SHALL distinguish native void empty/absent no-ops from application rejection, document writable nonNULL root storage, and compare original-target free, successor identity, cached original color, transplant links and repair scopes using independent native observations.

#### Scenario: Application rejects before deletion
- **WHEN** a delete is rejected as absent, empty or malformed
- **THEN** state and successful history stay unchanged and the instruction presentation explicitly identifies application rejection without inventing rbt_eliminar invocation, free, printf or C return

#### Scenario: Required dependencies and ended lifetime
- **WHEN** successful deletion instruction fidelity is reviewed
- **THEN** its actual helper source and typed scopes are available, the original z reserve ends at free, a different successor retains its identity, dead aliases are never sampled as live C pointers, and both views/replay match the recorded event boundaries without another mutation request

### Requirement: Limited Rojo-negro validator remains a global closure finding
The audit SHALL retain C-RBT-VALIDAR-LIMIT-01 as an explicit open quality limitation and decision while current Validar checks root-black, order and red-red only; achieving method playback coverage SHALL NOT silently certify black height, parent integrity or cycles.

#### Scenario: All visible methods have recorded playback evidence
- **WHEN** Rojo-negro eventually reaches7/7 recorded visible methods
- **THEN** validator scope and the outstanding product decision remain visible in the findings and final limits until resolved explicitly, separate from the stronger audit oracle


### Requirement: BFS instruction and history conformance preserves actual ownership
The audit SHALL compare BFS and its actual graph/FIFO helpers against independent downloaded-C observations, distinguish discovered marks from processed output, preserve negative IDs including -1 and disclose allocation/performance/observer limits. Successful calls SHALL persist in generated history without query redispatch during topology rebuild; failures SHALL remain excluded.

#### Scenario: Normal allocation and replay
- **WHEN** a recorded BFS case advances or reverses a completed instruction
- **THEN** FIFO, marks, partial result publication, scopes and retirement match its event, highlighting means just-executed, future results stay hidden and replay sends no POST

#### Scenario: Application rejection versus raw C
- **WHEN** the app rejects a missing or invalid start before calling BFS
- **THEN** validation does not invent BFS scopes, marks, free or printf; successful history stays unchanged and raw native empty/missing behavior is reviewed separately

#### Scenario: Actual student caller
- **WHEN** identical successful BFS calls are followed by reload and main compilation
- **THEN** both calls remain, main prints values actually returned by C and frees its results/final graph, strictC17/Doxygen/ownership evidence is recorded and guide distinguishes the C list-scan bound from ideal complexity


### Requirement: DFS contract and student caller preserve native ownership
DFS SHALL preserve actual C start-validation order, shared graph marks, neighbor-list order and independent unmarked output nodes. Successful calls SHALL remain in generated history without query redispatch on topology rebuild; failures SHALL be omitted. Final-state agreement SHALL NOT substitute for instruction, recursive-frame and replay evidence.

#### Scenario: Valid and missing starts
- **WHEN** the normal-allocation recorded C fixtures execute DFS with valid negative IDs or an absent start
- **THEN** valid calls reset marks before recursion and mark reachable vertices, while absent native starts preserve prior marks; application rejection is distinguished from that native call

#### Scenario: Actual repeated student caller
- **WHEN** two identical successful DFS executions are followed by failure and reload
- **THEN** both successful calls remain, the failed call is absent, no query redispatch occurs during rebuild, and downloaded main computes actual results and frees owned output lists; strict C17 and independent ownership evidence is retained


### Requirement: User-approved timing scope and informative Sorting performance
Sorting methods SHALL have no fixed fifteen-second SLA. Their execution and instructional preparation times SHALL be reported informatively with input size/distribution, method/complexity, environment, source and timing scope, as authorized in criterion18-sorting-informative-three-layer-decision-low.md. Educational algorithms, correctness, exact C instructions/events, historical snapshots, memory/ownership and usability SHALL be preserved; no algorithm SHALL be replaced or steps omitted merely to meet an arbitrary duration. The recorded80-element Sorting scenario SHALL NOT establish a universal user-approved admission maximum.

Algorithm execution, instructional preparation/validation/JSON and browser rendering/manual replay SHALL be distinguished. Native compiled C timing SHALL NOT be presented as timing of the application's Python instructional interpreter. Historical full-request budget outcomes SHALL remain preserved with their sources; they SHALL NOT be rewritten into new PASS results. MemoryError, timeout or missing response SHALL remain operational failures requiring explicit review.

Graph SHALL retain the prior agreement of at most15seconds for algorithm execution only, within its admitted educational domain and current15vertex cap; the Sorting withdrawal SHALL NOT silently remove that agreement. FullHTTP, instrumentation or human playback timings SHALL NOT certify pure Graph execution. Other technical limits, trace codecs/paging, coverage83/85 and300replay p95<200ms SHALL remain unchanged.

#### Scenario: Explain an80-element Sorting observation
- GIVEN current native C results and existing full web-request measurements for a registered80-element scenario
- WHEN reporting timing
- THEN method, actual input, source version and each timing boundary SHALL be shown separately
- AND neither a web request exceeding15seconds nor an informative native timing SHALL create a current Sorting SLA verdict
- AND no guarantee for arbitrary sizes or machines SHALL be inferred

#### Scenario: A large instructional request fails operationally
- GIVEN a MemoryError, timeout or absent complete response during instructional preparation
- WHEN applying the revised Sorting timing policy
- THEN the operational failure SHALL remain pending rather than become acceptable human waiting or an automatic PASS
- AND algorithm correctness SHALL be assessed independently from that failed preparation

#### Scenario: Graph has only full-request or instrumented evidence
- GIVEN a recorded Graph request or profile without isolated algorithm-execution timing
- WHEN assessing the retained algorithm-only15second agreement
- THEN neither pure-algorithm PASS nor FAIL SHALL be inferred from the incomparable request duration
- AND the exact missing input/source/timing SHALL be reported before any new native campaign

#### Scenario: Preserve educational behavior and navigation
- WHEN evaluating any timing layer
- THEN conditions, scopes, aliases, before/after values, printf, ownership, validations and admitted-domain safeguards SHALL NOT be dropped or changed to improve reported speed
- AND human Next/Previous waiting SHALL NOT be counted as algorithm execution time
