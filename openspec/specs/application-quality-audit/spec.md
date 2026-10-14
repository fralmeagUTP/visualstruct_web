# application-quality-audit Specification

## Purpose
Define contratos auditados de código C/H, historial/callers reales, memoria, visualización, validación y trazabilidad de calidad dentro de los dominios finitos aprobados. Conserva sucesores aceptados y evidencia histórica; C1 12/12 no es garantía universal. Sorting conserva tiempos informativos; Graph mide HTTP completo y admite sólo fixtures temporales observados, incluido BFS8.
## Requirements
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
The audit MUST preserve C-RBT-VALIDAR-LIMIT-01 as historical evidence. The explicitly accepted V3 successor checks black height, parent integrity and cycles within its supported finite contract; the prior root/order/red-red limitation MUST NOT remain an unresolved product decision after that acceptance. Scope limits for arbitrary/dangling pointers, other ABI and universal cases MUST remain explicit. Validator acceptance MUST NOT substitute insertion recolor or deletion causal witnesses.

#### Scenario: All visible methods have recorded playback evidence
- **WHEN** Rojo-negro recorded methods and V3 have accepted successor evidence
- **THEN** the historical limitation remains traceable as resolved within that scope
- **AND** insertion browser final uses visible-red-black-insert-final-low/README.md while validator evidence stays separate

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

Graph SHALL retain the maximum15seconds agreement measured as a plain full HTTP request, from before POST until complete response consumption and JSON decoding including the faithful trace, history reconstruction, validation, packing and serialization. Fixture preparation, browser rendering and manual replay are outside this interval; coverage/tracemalloc/profilers SHALL NOT supply plain gate results. The current vertex cap15 remains; a PASS is scoped to its explicit measured fixture, never a guarantee for every15vertex input or all algorithms. BFS8undirectedchain/start1 has one accepted1.4915286s request; historical pure/expanded-render/instrumented timings SHALL NOT be relabeled as that measurement. Other technical limits, trace codecs/paging, coverage83/85 and300replay p95<200ms SHALL remain unchanged.

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
- **GIVEN** one declared Graph fixture with plain HTTP duration measured from before POST until the complete response and faithful trace are consumed and JSON-decoded
- **WHEN** its measured duration is at most15seconds
- **THEN** that fixture alone has a finite timing PASS, with source/input/environment/resources preserved
- **AND** instrumented, incomplete, pure-kernel or browser-expanded timings do not substitute that measurement or certify other inputs/algorithms

#### Scenario: Preserve educational behavior and navigation
- WHEN evaluating any timing layer
- THEN conditions, scopes, aliases, before/after values, printf, ownership, validations and admitted-domain safeguards SHALL NOT be dropped or changed to improve reported speed
- AND human Next/Previous waiting SHALL NOT be counted as algorithm execution time

### Requirement: Asignación explícita a casos ejecutables
El verificador estricto de inventario MUST rechazar opciones sin asignación explícita a una función de prueba existente dentro de tests/, con entrada, resultado esperado y capa. Los controles anónimos MUST figurar como pendientes y los controles MUST asignarse a E2E. Los IDs generados MUST NOT certificar ejecución ni cobertura.

#### Scenario: operación nueva sin prueba
- **GIVEN** un inventario con una operación sin asignación
- **WHEN** se aplica el gate estricto
- **THEN** el gate falla aunque esa operación tenga un case_id generado

#### Scenario: control sin E2E
- **GIVEN** un control HTML sin identificador
- **WHEN** se recolecta el inventario estricto
- **THEN** el control se incluye y el gate falla hasta asignar una prueba E2E con datos y esperado

