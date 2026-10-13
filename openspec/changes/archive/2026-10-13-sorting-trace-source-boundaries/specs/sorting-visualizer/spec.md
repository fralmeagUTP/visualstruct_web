## ADDED Requirements

### Requirement: Explicit pre-call metadata and native executed source boundaries
The trace SHALL distinguish the single initial snapshot before a C call from executed C events. Only that exact initial position/token, empty function/call stack/variables/pointers and unchanged input MAY have no C line. Actual later instructions and entered lexical scope exits SHALL map to their real source line; no global missing-line exemption is permitted. A false Radix group guard SHALL emit no block-exit event for that group. Entered group exits SHALL retire their locals at their actual closing brace. Native C, arithmetic, allocations, writes and real event order SHALL remain unchanged.

#### Scenario: Initial snapshot and later instruction
- **GIVEN** native sorting C and a valid array
- **WHEN** execution begins
- **THEN** frame0 is the precise pre-call metadata snapshot
- **AND** each subsequent real C event matches an in-range native line and exact source text

#### Scenario: Skipped Radix group
- **GIVEN** positive-only values and zero negative count
- **WHEN** the negative group guard is false
- **THEN** no negative-block exit or locals from that block are emitted
- **AND** positive execution and all real C events remain intact

#### Scenario: Entered group scope exit
- **GIVEN** a true negative or positive group guard
- **WHEN** the block completes
- **THEN** exactly its real closing brace is mapped and its locals retire
- **AND** an unmapped later instruction or unrelated brace is rejected by focal source assertions
