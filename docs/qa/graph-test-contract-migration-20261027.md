# Canonical graph test reconciliation, 2026-10-27

The active graph engine executes the unchanged, byte-exact book C source through BookSession. Historical tests now exercise that contract; archived traces and retired interpreter modules remain explicitly historical. Protected C/H files were not edited by this migration.

Independent native probes compile the canonical source unchanged, adding allocation hooks in the compiled translation unit and caller-only observation where required. They compare endpoint status, result order, marks, short-circuit behavior and cleanup with the model. Model instruction assertions separately validate actual source coordinates, events, frames, temporal heap and lossless trace encoding; they do not claim native per-instruction equivalence.

Retained cases include native vertex fifteen-case inventory, six neighbor allocation cases, eight incident-caller cases, atomic Prim/Dijkstra exhaustive allocation slots, disconnected/asymmetric/absent/negative states, borrowed-memory protection, all original numeric snapshot inventories and BFS boundary repetitions. Canonical allocation counts differ from the retired implementation; every actual allocation failure is swept dynamically.

Canonical histories are marked graph-book/v1. Real C failures remain recorded; rejected host input leaves history unchanged. Legacy histories remain preserved and suspended. Canonical history replay intentionally reexecutes recorded queries; obsolete metadata cannot override the computed marks.

## Bounded local verification

- Atomic successors and seven additional status cases: 25 passed (4.69s).
- History plus initial atomic suite: 46 passed (450.91s), including native ten-case mark sequence (273s).
- Adapters and native negative-vertex cases: 13 passed (22s).
- Graph-only didactic findings: 6 passed (5.44s); unrelated cases unchanged.
- Snapshot pool, boundary equivalence and revision-cache suite: 46 passed (271.99s).
- Construction, four-algorithm instruction contract and vertex instruction: 30 passed (14.94s).
- Native vertex inventory: 15 passed (17.31s).
- Neighbor instruction: 5 passed (2.34s); independent native neighbor test covers six cases, passed (1.64s).
- Routes and default-weight caller: 16 passed (57.03s).
- Shared main: 7 passed (44.43s).
- Incident caller: 8 passed (30.94s).

Counts above overlap where stated and must not be summed into a unique total. Raw run logs remain local in the parent task directory (graph-*-migration.log and graph-construction-four-validation.log); complete CI remains the integration coordinator responsibility. Browser assertions are reported by the E2E owner separately.

## Subsequent residual verification

Educational capacity fixtures now distinguish marked canonical histories from preserved suspended legacy16/seeded31 histories. Legacy main download correctly returns409 without source reinterpretation. Canonical cycle failures remain in history and replay actual C. The capacity/pedagogy residual batch verified32 passing cases before unrelated obsolete pedagogy assertions stopped the run. Phase3 result/validation and Python JSON typed boundary tests were subsequently reconciled; the final tail batch passed37 cases with only two borrowed-list memory-field checks remaining at that snapshot (fixed in the subsequent focused guard run). Initial failures remain in graph-remaining-domain.log, graph-residual-final.log, graph-pedagogy-residual.log and graph-final-tail*.log for traceability.

Traversal, numeric documentation/history and numeric JSON boundary extension evidence is recorded separately in graph-traversal-test-migration-20261027.md (130 unique passing cases before the later pedagogy extension).

Final borrowed-pointer guard verification: all10 passed in10.31s (graph-unresolved-verified.log). The canonical returned pointer remains present in live heap_nodes, query allocations and frees stayzero, and ownership is borrowed.
