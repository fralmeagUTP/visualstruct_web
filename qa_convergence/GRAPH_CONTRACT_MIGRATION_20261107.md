# Explicit Graph current-acceptance transition

This change implements the reviewed decision to move exactly six active test IDs to the accepted graph-book/v1 contract. It does not restore missing historical evidence, demonstrate equivalence to ConstructionMachine, or claim historical closure. The six IDs and method allowlist are in graph_contract_migration.json; the 39 reviewed obligations, original/proposed guarantees, classifications and executable control modules are in graph_contract_migration_obligations.json. The original proposal classified 10 obligations as preserved, 11 as stronger current guarantees, nine as contract differences and nine as gaps to strengthen. The implementation addresses those gaps under current acceptance, with the explicit wording limit below.

## Custody and excluded gates

Five original Python modules and the prior manifest remain literal .snapshot files under tests/fixtures/graph-history/contract-migration. Their original hashes, the original historical C harness hash, manifest and decision pins remain checked. The .gitattributes -text rule protects snapshot bytes on Windows. Active Python/JSON text permits only LF/CRLF transport normalization; snapshot bytes do not. The guard restores only the six allowed method bodies and allocation setup and requires the rest of each original module to match, with AST verification of excluded bodies and dependencies. It rejects changed imports, inputs, allowed-method expansion and invented equivalence claims.

Three baseline comparisons remain active and unchanged: numeric-null-baseline.py, graph-vertex-note-baseline.py and graph-query-note-baseline.py are absent and their tests still fail FileNotFoundError. They have not been skipped, xfailed, deselected or replaced. No product code, C/H file, workflow or threshold is changed. Historical R8 obligation/review documents remain a record of their pre-transition state; this document and the explicit migration receipt describe the new current-acceptance decision.

## Accepted differences

- Native tests execute canonical status-pointer and cost-output APIs, not retired signatures. BookSession replaces ConstructionMachine for these current oracles; exact historical trace equivalence is not asserted.
- Caller receipt is observed before list cleanup rather than requiring it to be the final step. For vertex and query tests, the final application publication is explicitly non-C and non-mutating. Ownership is checked through current pointer/liveness/cleanup behavior.
- Only synthetic fixtures receive canonical version markers. Real saved history is never silently upgraded; legacy refusal, literal export and explicit reset tests remain exercised.
- Removing an absent vertex uses the canonical C result and preserves existing arcs. Malformed vertex inputs are separately required to reject in application without C execution.
- Insertion narration must identify the correct API and not claim deletion. It need not contain the historical literal word “conserva”. This is truthful current wording, not literal-text preservation. Removal identifies the caller in all narration levels.
- Missing edge cost executes C and yields flag 0 with an uninitialized output cell, not the old input-validation rejection. Present cost yields flag 1 and value 9. Scalar and borrowed-list results remain distinct.
- Help describes the real internal index queue, not a linked external FIFO. API-only auxiliary operations are excluded from all four phase selectors. Rendered help/configuration checks are not a new browser E2E run.

## Executable guarantees and negatives

The original matrices remain exact: 30 allocation scenario/fault pairs, seven numeric cases, five vertex cases and eight query cases. Matrix controls bind actual inputs and expected current result types to the preserved originals. Six reducing/changing mutations are rejected.

Native allocation telemetry is inserted only in a temporary compiled harness copy at an exact unique marker. The repository C harness remains intact. All 30 original output rows match uninstrumented execution. Ten positive fault indices actually reach an allocation failure; 14 positive indices exceed reached calls and are normal-path samples; six fault-zero cases are normal executions. Separate compiled status and atomicity mutants reach their intended semantic assertions. Direct symbolic mutations independently target counts, endpoints, status, cost, state preservation and cleanup.

Publication controls preserve all three narration levels, caller/non-C attribution, NULL versus owned-list distinctions, final no-C/no-mutation boundaries, expected C calls, scalar/list distinctions, cost output semantics and borrowed pointers. Actual malformed vertex inputs are checked plus false-C mutants. Help controls use actual Flask-rendered pages, exact canonical C rendering, capacity and function links, auxiliary labels and actual server-provided selectors; contradictory text retaining otherwise correct words is rejected too.

There are 100 new parametrized controls: 19 custody, seven matrices, 19 allocation and 55 publication/help. Negative controls must fail at named semantic assertions rather than import, setup or compilation failure. Existing R8 controls remain present. These finite adversarial tests prove rejection of the specified corruptions, not every conceivable product defect.

## Validation boundary

Local execution evidence and independent review accompany the frozen patch. Coverage from focal runs is not a full-suite threshold result. Collection is checked against R8 and R7 to establish no lost IDs; Chromium collection is not browser execution. No remote publication, merge, deployment or final project closure is claimed by this migration. The retained missing-baseline failures and other historical gates still require resolution.
