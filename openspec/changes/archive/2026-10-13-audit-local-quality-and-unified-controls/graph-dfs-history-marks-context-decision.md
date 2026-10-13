# C-DFS-HISTORY-MARKS-01 — cross-call context decision pending

Severity: medium pedagogical/state-context fidelity. Raw downloadable C keeps graph vertex marks between calls until DFS resets them; current service rebuild skips historical query execution and therefore discards those marks. Reproducer and native observation: evidence/visible-graph-dfs-instruction-review/dfs-history-mark-context-gap.json. First final marks[1,1,1,1]; secondAPI entry[0,0,0,0]; native samegraph secondentry[1,1,1,1]. Both orders[1,2,4,3]. Histories correctly retain2calls and avoid query redispatch: do not undo that contract.

Single-call model against suppliedinitialgraph remains verified. Do not claim sequential generated-main before/after context parity or fullDFS closure yet. Recommended bounded correction is validated effect snapshots for historical marks, applied in chronological rebuild without invoking queries; preserve topology, legitimate repeated calls and failure omission. This touches shared graph history and potentially closed BFS/construction contexts, so obtain coordination scope/decision before implementation. No behavior correction or reopening is authorized by writing this proposal alone.


## Authorized LOW correction
Coordination explicitly authorized repair on 2026-10-02: validated mark snapshots, no query redispatch, correct chronological mutation handling/session isolation, necessary BFS-to-DFS shared-history regression. This supersedes the earlier pending-authorization gate. graph.bfs recorded instruction implementation stays closed; shared history before-state regression is newly demonstrated evidence, not an instruction-family rerun.


## Recorded-case resolution
C-DFS-HISTORY-MARKS-01 is corrected for the finite verified sequences above; effect validation/session isolation/native chronological mutation fidelity and replay are evidenced in evidence/visible-graph-dfs-history-context-low. Older histories without authenticated captured marks remain explicitly limited; no historical query redispatch. The original failure evidence is preserved.
