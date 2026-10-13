## ADDED Requirements

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
