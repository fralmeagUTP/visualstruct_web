## ADDED Requirements

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

## MODIFIED Requirements

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

### Requirement: Limited Rojo-negro validator remains a global closure finding
The audit MUST preserve C-RBT-VALIDAR-LIMIT-01 as historical evidence. The explicitly accepted V3 successor checks black height, parent integrity and cycles within its supported finite contract; the prior root/order/red-red limitation MUST NOT remain an unresolved product decision after that acceptance. Scope limits for arbitrary/dangling pointers, other ABI and universal cases MUST remain explicit. Validator acceptance MUST NOT substitute insertion recolor or deletion causal witnesses.

#### Scenario: All visible methods have recorded playback evidence
- **WHEN** Rojo-negro recorded methods and V3 have accepted successor evidence
- **THEN** the historical limitation remains traceable as resolved within that scope
- **AND** insertion browser final uses visible-red-black-insert-final-low/README.md while validator evidence stays separate
