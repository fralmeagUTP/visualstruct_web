## ADDED Requirements

### Requirement: Educational graph capacity of fifteen vertices
The application SHALL admit at most15distinct vertices for new operations,
including implicit endpoints and random generation, while preserving downloaded
C/H algorithms/signatures, faithful traces and coverage83/85. The capacity
counts distinct vertices and SHALL NOT constrain labels to the range1..15.

#### Scenario: Reject the sixteenth vertex transactionally
- GIVEN an existing graph with15vertices
- WHEN insertion or implicit endpoints would create vertex16, or generation requests16
- THEN HTTP400 SHALL preserve all graph state, previous result, history and RNG seed
- AND the trace SHALL explicitly mark application rejection with zero C executions
- AND the UI SHALL state the limit without silent truncation

#### Scenario: Preserve a previous larger session
- GIVEN a legitimate persisted history which reconstructs more than15vertices
- WHEN the user reloads, views, queries or downloads its caller
- THEN all existing data/history SHALL remain intact
- AND new insertion and algorithm execution SHALL be blocked while over15
- AND explicit removals, clear, type reset or generation<=15 MAY reduce the graph
- AND normal operations SHALL resume once the graph returns to15

#### Scenario: Verify only eight-node algorithm fixtures
- GIVEN graph-max15-only8-current-user-decision-low.md supersedes the prior30 maximum
- WHEN performing current algorithm functional and visual checks
- THEN only8-node algorithm fixtures SHALL execute, with15-admission/16-rejection checked through validation without full15/16 algorithm traces
- AND allowed15 SHALL NOT imply tested15 or a universal time/usability guarantee
- AND previous30/BF20 benchmarks SHALL remain historical unchanged
- AND visual preparation delay and any pending performance/fidelity criteria SHALL be disclosed without new optimization or invented PASS

## MODIFIED Requirements

### Requirement: Validación de entradas de grafo
Los campos `vertex`, `origin`, `target`, `start` y `end` MUST validarse como enteros. Conforme a graph-approved-integer-dijkstra-contract-decision-low.md y su implementación aceptada, `weight` MUST ser finito, integral y representable en C int de32bits;2.0 se normaliza exactamente a2 y2.5 se rechaza sin truncamiento. Construcción MAY conservar pesos negativos para algoritmos que los admiten; Dijkstra MUST rechazar todo arco negativo, incluso desconectado, según sus reglas C aprobadas.

#### Scenario: peso decimal aceptado
- **GIVEN** un peso decimal integral2.0 dentro del dominio C int
- **WHEN** se inserta una arista
- **THEN** responde200 y almacena el peso entero2; el caso histórico de2.5aceptado queda sustituido por la decisión explícita de pesos enteros

#### Scenario: vértice no entero rechazado
- **WHEN** se ejecuta `insert_vertex` con `{"vertex": "a"}`
- **THEN** responde400 con el mensaje de entero inválido

#### Scenario: peso fraccionario no truncado
- **WHEN** se inserta una arista con peso2.5
- **THEN** responde400 sin aceptar un peso truncado ni alterar el estado/historial aceptados

#### Scenario: peso no finito o fuera de C int
- **WHEN** el peso es no finito o excede[-2147483648,2147483647]
- **THEN** se rechaza antes de invocar C o persistir una operación exitosa
