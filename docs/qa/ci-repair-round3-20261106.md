# CI repair, third review: 6 November 2026

## Scope and exact base

This review is based on `46f2520eda22c5029afb6ab288abcc8a7815d03a`, tree `77fbe3c8bdc7aa76a5baf88b10b8b2d26899865a`, in draft PR #7. It is not a deployment or a claim of globally passing CI. Main and the VPS are unchanged by this round.

## Completed base CI

All four workflows for this exact head reached a terminal result:

- [C17 and sanitizers](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42298623052): success.
- [Caller/code-reader](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42298623119): success, 57 passed.
- [E2E](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42298623185): failure. General Chromium selected 565 cases: 535 passed and 30 failed, all in the call phase. Graph-algorithms and Firefox succeeded. Across the 555 IDs shared with f1, 190 failures became passes, 30 remained failures and 335 remained passing. Ten new cases passed. No shared case changed from passing to failing and no previous case was removed. All four Chromium JSONL streams exactly match their execution summaries.
- [Unit/Integration](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42298623219): failure. Completed unit partitions 0, 1 and 3 report 5067 passes and five failures. Partition 2 aborted with INTERNALERROR and has no final summary. Completed coverage partitions 0, 1 and 3 report 5201 call passes, 14 call failures and one setup failure across 5216 selected IDs. Coverage partition 2 also aborted without a final summary or coverage part. Coverage-gates was skipped. These are not complete suite or coverage unions.

The completed unit/coverage summaries and their official JSONL streams disagree because some tests left temporary environment/cwd changes active while report hooks ran. Both original sources are retained. The three completed coverage partitions lack 67 JSONL events; each missing ID/phase is covered by the repaired diagnostic controls. This repair does not retroactively make the original incomplete partitions complete.

Graph reconstruction p95 is now attributable: 219.441 ms in CI against the unchanged 200 ms limit, with five iterations of 300 operations. Other measured families remained below the limit. Local measurements are not a substitute for the CI result.

## Changes and guarantees

- Temporary environment, current-directory and monkeypatch changes in diagnostic tests are restored before pytest report hooks. RBT capture setup no longer changes cwd across setup/call phases. The real partition plugin, absolute and relative paths, four-way distribution and exceptional exits are tested. The plugin and its verifier are unchanged.
- Hash heading consumers check the exact allowed semantic title, identity, structure and order, including duplicate-attribute negatives, rather than requiring the superseded literal.
- ABB deletion callers observe the live tree before the original cleanup; cleanup and displayed caller source are retained. ABB validation compares exact node identities independently of focus-driven card order. AVL/RN historical-record labels and ABB instruction labels follow the delivered spelling. Sublista observers begin from the actual initial context label and retain replay, scopes, pointers, native callers and ownership checks.
- Pila tests preserve the original case and add three viewport/mode combinations. Controls remain after preparation and before the workspace. JPEG checks cover the complete classroom region and retain an independent legacy raw-scope comparison. Real DOM extraction rejects hidden, clipped, transparent, zero-area and missing content; geometry is compared with independent source/painter bounds, not self-reported export metadata.
- Sorting consumers compare exact current-frame API call-stack rows with the DOM, including function, parameters and continuation. An empty placeholder cannot count as an active call. Negative controls reject missing, duplicate, stale and wrong rows, plus active rows after scope end. Final empty memory/variables and the ten strategy families remain checked.
- A separately diagnosed product defect affects CPython 3.12: a constructor failure can report the offset of a CALL's inline CACHE rather than the CALL itself. The classifier now accepts only the CALL and its contiguous hidden cache offsets, excluding the next visible instruction. The ten existing node-construction paths preserve HTTP 400, error privacy, heap/session state and canonical failure traces. Wrong-function, replay, later-call and metadata failures must not be relabelled. Canonical C/H and trace generators are unchanged. This does not certify hypothetical future constructors with nested calls inside their argument expressions.
- A focused independent Python 3.12 CI job matches the Dockerfile's Python minor version and runs the allocation regression. It does not claim execution of the Docker image. The existing Python 3.10 matrix remains intact.
- A separate, cancellation-aware Graph profile step collects only whitelisted numeric/static-function data on the selected partition after the unchanged performance gate. It emits no raw paths, environment, source or exception text. Profiling is diagnostic, not a claimed performance fix. The threshold, operation count, iterations and benchmark remain unchanged.

## Integrated validation

- The final 29-path implementation snapshot passed 194 focused controls in 59.93 seconds under Python 3.12, with pytest-cov and the real partition plugin. The relative official output contains exactly 582 events, identical in order and content to the summary, with setup/call/teardown passed for every selected ID. NODE_PATH was unset. Local Node packages matched all 39 package version/resolved/integrity tuples in the pinned qa lock and were placed in the CI-style qa/node_modules layout; an offline clean install was unavailable, so this is not a claim of a fresh npm ci or Actions execution.
- A separate recovery run executed exactly the 1690 original IDs selected by the aborted unit partition: all passed in 868.94 seconds, with 5070 complete official events. This used the earlier 20-path allocation-repair snapshot, excluding the later runtime job and remaining-consumer edits; it is not presented as the full final candidate or as Python 3.10 CI. The final focused run covers those later additions.
- Independent review reproduced the real Sorting observer across 1352 frames of ten families, rejected 1322 active-frame placeholder substitutions and 80 additional corruptions, and retained all 37 original cases in the reviewed consumer subset. Native C17, ownership and DOM checks beyond the first failing browser assertions passed for ABB, RN and Sublista. These are finite supporting checks, not complete browser passes.
- Full collection retains all 7529 base IDs and adds 106, for 7635 total. General Chromium retains its 565 base IDs and adds three Pila viewport/mode cases, for 568. No previous ID was removed. Collection is not execution.
- All 26 canonical C/H sources and 282 of 283 tracked application/template/static/C-source paths are byte-identical to the base. The sole product change is the allocation-failure classifier described above. Existing CI partition logic, performance gate and historical evidence inventory remain unchanged. All changed Python files parse with Python 3.10 syntax; runtime execution here was Python 3.12, while exact-head CI must validate the supported matrix.

These checks overlap and are not additive unique suite totals. This report is documentation added after the implementation snapshot; it introduces no runtime behavior.

## Visual evidence from the exact base

All 24 synthetic PNGs from the base CI were inspected. Desktop and narrow views retain the descriptive preparation stages and controls. The single learning-level control remains in the code stage, keeps its selected value across hide/reopen and resize, and shows focus. Visible RN NULL links agree with the memory fields and do not become allocated NULL cards. Sorting controls remain legible at narrow width.

These screenshots have limits: larger RN diagrams require panning, some lower leaves fall outside the captured viewport, and long narrow Hash text is clipped within its scroll/pan surface. Static captures alone do not verify every off-screen element. A minor adjacent Hash counter/empty-trace text spacing issue was noted without changing the scope. These images validate the base only, not the new candidate's browser execution.

## Remaining gates and limits

The eight C1/role-workflow provenance gates, two Heap historical preservation gates, nine archived pre-book Graph gates and one Binsort historical DFS-review binding remain explicit and unchanged. The protected preimages were not fabricated, pins were not replaced, and these gates were not skipped or disabled. See `ci-known-gates-round2-20261106.json` for the preserved inventory. No additional exhaustive archive search is claimed.

The 200 ms Graph p95 gate still requires a new exact-commit CI result. Local Chromium remains blocked by the environment's socket restriction; browser navigation, real layout, JPEG raster/pixel identity and the complete 30 repaired browser cases are NOT_RUN locally. API, strict C17 and jsdom evidence do not substitute for those checks. New-head CI, diagnostic stream integrity and any new screenshots must be reviewed before considering merge or deployment.
