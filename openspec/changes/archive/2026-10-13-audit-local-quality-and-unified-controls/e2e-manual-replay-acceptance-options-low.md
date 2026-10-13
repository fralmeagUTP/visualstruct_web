# E2E manual replay acceptance options LOW (decision pending)

New instruction parent01a0fe61; exact main ba3b0870a639489d5a593a084780a3f749f45a66. This is a proposal, not accepted changed coverage. No E2E/action/timeout/product edit applied.

## Observed cost boundaries

The failing-to-finish case already uses only4vertices/4edges, not the admitted15 cap or prior8-vertex audit scenario. It includes a real alternative weighted path (1->4 weight15 vs1->2->3->4 weight9). Reducing to2vertices/1edge would remove alternative-path and multihop coverage, so it is not proposed as an equivalent fixture.

CI case start04:33:57Z. Eight manual build traces11/14/17/20/171/176/180/225 ended04:39:38Z (~5m41). BFS541steps ended04:45:31Z (~5m53). Next actual POST200 took~7s, then1524-step manual replay advanced775steps by04:52:29Z (~6m50), still moving when cumulative job cancelled. From test order next phase is Dijkstra (inference). These are full test/browser replay elapsed times, not isolated Graph algorithm timings or SLA verdicts. No asserted15-second browser deadline and no Sorting SLA introduced. Final sampler supplies no actionable app/browser location. Later Prim not reached; remaining costs not measured.

## Contract and preferred conservative option A

visual-playback-ui requires full trace reproduction, each Next advancing line by line, synchronized C/state and fast/final equivalence. Audit spec requires exact reverse restoration and no future result; trace correctness cannot be replaced by a final-state-only assertion.

Prefer preserve original4vertex/4edge data and all Cframes/manual actions/assertions, but explicitly split this cumulative multi-phase acceptance case into independently scheduled phase cases/jobs (construction, BFS, Dijkstra, Prim), each retaining20min limit. Setup after construction would use genuine authorized API mutations or documented shared fixture, not synthetic DOM state; final UI phase switching/order would need a separate cross-phase integration assertion retaining current semantics. This changes test decomposition/acceptance boundaries, so coordination decision is required before editing. Job sharding alone by whole existingtest cannot solve a case already exceeding20min; phase decomposition is essential. No claim all cases will fit20min based on unmeasured Prim/remainder.

Coverage mapping required before implementation: every original graph data entry/assert/phase selection/status/result check maps to at least one new case; construction manual publish checks remain; BFS/Dijkstra/Prim retain complete line-by-line navigation and final actual result. Verify all source/state/event/console/memory contracts independently where required. No unverified frame skipping or algorithm replacement.

## Alternative B (stronger acceptance change)

Separate exhaustive backend trace/C correctness for the same4vertex input from representative actual UI navigation (start/next/previous/condition/store/final) and fast/manual final equivalence. This is allowed only after explicit acceptance of the changed browser coverage. Representative DOM checks cannot certify every browser frame; exhaustive backend snapshots cannot certify exhaustive DOM rendering. A coverage matrix and independent adverse-frame controls are required, and the gap must remain explicit. No change implemented.

Decision requested: A preserves exhaustive browser navigation while decomposing jobs; B changes browser acceptance to representative navigation with exhaustive separate trace checks. Both retain educational algorithms, real actions, correctness assertions and20min policy. Neither is authorization to publish. Current87CI failures remain, SortingA/B excluded.
